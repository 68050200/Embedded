/*
===================================================================================

GROUP 9 Final Project : ตู้หยอดเหรียญ
51423364 การเขียนโปรแกรมสำหรับระบบสมองกลฝังตัว

1	นายชิษณุพงศ์ วิเชียรกุล	68050200
2	นายกิตติภน ภาษีชา	68050392
3	นายณัชพล วงศ์ยัง	68050393
4	นายธีรธน จันทบุตร	68050395

===================================================================================
  - ห้ามใช้ millis() / delay()  ใช้ tick เท่านั้น (1 tick = TICK_MS = 10 ms)
    (ยกเว้น delayMicroseconds() ใน lcdInit() / คำสั่ง clear ของ LCD ซึ่งเป็นการรอระดับ µs-ms ของตัวจอเอง)
  - ไม่เรียก tickInit() / senderBegin() ของ common.cpp
    (ใช้ timerInit() / uartInit() ของโปรเจกต์แทน ; common.cpp ไม่มีโค้ดปุ่มแล้ว
    ปุ่มทั้งหมดจัดการใน inputInit())
===================================================================================
*/

#include "PROJECT_G9.h"
#include "soc/gpio_reg.h"

/* ---------------- ค่าคงที่ภายในไฟล์ ---------------- */
#define COIN_DEBOUNCE_TICKS   3      /* กดสั้นกว่านี้ (~30 ms) ถือเป็น bounce ทิ้ง */
#define RESET_DEBOUNCE_TICKS  5      /* ต้องนิ่งอย่างน้อย ~50 ms ก่อนนับการกด reset */
#define LCD_BL                0x08   /* backlight bit ของ PCF8574 */
#define ADC_SAMPLES           8
#define POT_HYST              80     /* hysteresis ที่ขอบแต่ละช่วง (หน่วย ADC count) */
#define SHOW_SERIAL           1      /* 1 = showXxx พิมพ์ลง Serial ด้วย (ช่วย debug) */
#define STOCK_INIT            2      /* สต็อกเริ่มต้นของสินค้าทุกชนิด (เติมของ = กดรีสตาร์ทบอร์ด) */

/* log ทุกบรรทัดมีเวลา (ms) นำหน้า  นับจาก tick ของ loop */
#define LOGT(fmt, ...) Serial.printf("[%lu ms] " fmt "\n", (unsigned long)(tickNow() * TICK_MS), ##__VA_ARGS__)

/* สต็อกสินค้า เก็บใน RAM -> รีสตาร์ทบอร์ดแล้วกลับเป็น STOCK_INIT เอง */
static uint8_t stock[PRODUCT_COUNT] = { STOCK_INIT, STOCK_INIT, STOCK_INIT, STOCK_INIT };

/* ตัวนับ tick จาก hardware timer (ISR เพิ่มค่า)
   - hwTick   : นับใน ISR  (ใช้วัดความยาวการกดปุ่มใน ISR ได้โดยไม่ต้องเรียกฟังก์ชันนอก IRAM)
   - tickSeen : tick ที่ loop ประมวลผลแล้ว = ค่าที่ tickNow() คืน */
static volatile uint32_t hwTick   = 0;
static uint32_t          tickSeen = 0;

static void IRAM_ATTR onTick(void) { hwTick++; }

/* ===== โซน 2 : ISR ปุ่ม  =================================
   ================================================================ */

#define COINQ 8
static volatile uint8_t  coinQ[COINQ];
static volatile uint8_t  qHead = 0, qTail = 0;
static volatile bool     coinDown = false;
static volatile uint32_t coinDownTick = 0;
static volatile bool     faultLatch   = false;   /* ISR เห็นการกดค้าง >= FAULT_TICKS ตอนปล่อย (loop ยังไม่ทันรายงาน) */
static volatile bool     stuckReported = false;  /* coinStuck() รายงาน FAULT ของการกดครั้งนี้ไปแล้ว */

static volatile uint32_t resetCount = 0, lastResetEdge = 0;
static uint32_t          resetSeen = 0;

static void IRAM_ATTR onCoin(void)
{
    bool     pressed = ((REG_READ(GPIO_IN_REG) >> COIN_PIN) & 1u) == 0;   /* active-low */
    uint32_t now     = hwTick;

    if (pressed) {
        if (!coinDown) { coinDown = true; coinDownTick = now; faultLatch = false; stuckReported = false; }
    } else if (coinDown) {
        coinDown = false;
        uint32_t dur = now - coinDownTick;
        if (dur < COIN_DEBOUNCE_TICKS) return;          /* bounce */
        if (dur >= FAULT_TICKS) {                       /* กดค้าง = FAULT ไม่นับเป็นเหรียญ */
            if (!stuckReported) faultLatch = true;      /* กันกรณีปล่อยก่อน loop ทันเห็น -> ไม่ให้ตกหล่น */
            return;
        }
        uint8_t v = (dur >= COIN_LONG_TICKS) ? 5 : 1;
        uint8_t n = (uint8_t)((qHead + 1) % COINQ);
        if (n != qTail) { coinQ[qHead] = v; qHead = n; }
    }
}

static void IRAM_ATTR onReset(void)
{
    bool     pressed = ((REG_READ(GPIO_IN_REG) >> RESET_PIN) & 1u) == 0;
    uint32_t now     = hwTick;
    bool     quiet   = (now - lastResetEdge) >= RESET_DEBOUNCE_TICKS;
    lastResetEdge = now;                                 /* ทุก edge รีสตาร์ทหน้าต่าง debounce */
    if (pressed && quiet) resetCount++;
}

void inputInit(void)
{
    pinMode(COIN_PIN,  INPUT_PULLUP);
    pinMode(RESET_PIN, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(COIN_PIN),  onCoin,  CHANGE);
    attachInterrupt(digitalPinToInterrupt(RESET_PIN), onReset, CHANGE);
}

uint8_t takeCoin(void)
{
    if (qTail == qHead) return 0;
    uint8_t v = coinQ[qTail];
    qTail = (uint8_t)((qTail + 1) % COINQ);
    return v;
}

bool takeReset(void)
{
    if (resetCount == resetSeen) return false;
    resetSeen = resetCount;
    return true;
}

bool coinHeld(void)
{
    return coinDown;
}

/* ===== โซน 3 : Timer tick ================================
   ================================================================ */

static uint32_t idleStart  = 0;
static uint32_t stateStart = 0;

static uint8_t  blinkLeft  = 0;       /* จำนวนครั้งที่ยังกะพริบไม่ครบ */
static bool     blinkOn    = false;
static uint32_t blinkLast  = 0;

void timerInit(void)
{
    timerSetup(TICK_MS * 1000u, onTick);
    pinMode(LED_REFUND_PIN, OUTPUT);
    pinMode(LED_FAULT_PIN,  OUTPUT);
    digitalWrite(LED_REFUND_PIN, LOW);
    digitalWrite(LED_FAULT_PIN,  LOW);
}

bool tickPending(void)
{
    if (hwTick == tickSeen) return false;
    tickSeen++;
    return true;
}

uint32_t tickNow(void)
{
    return tickSeen;
}

void idleTimerRestart(void)
{
    idleStart = tickNow();
}

bool idleTimeout(void)
{
    return (tickNow() - idleStart) >= TIMEOUT_TICKS;
}

/* E6 : ใช้เกณฑ์เดียวกับ ISR (hwTick - coinDownTick >= FAULT_TICKS) และไม่เก็บสถานะค้างข้ามรอบ
   - กดค้างจนครบ 3 s ขณะยังกดอยู่  -> true
   - ปล่อยหลังครบ 3 s ก่อน loop ทันเห็น -> faultLatch ของ ISR ทำให้ true (ไม่ตกหล่นที่ช่วง 3.00-3.03 s) */
bool coinStuck(void)
{
    if (faultLatch) {
        faultLatch = false;
        stuckReported = true;
        return true;
    }
    if (!coinDown || stuckReported) return false;
    if ((hwTick - coinDownTick) >= FAULT_TICKS) {
        stuckReported = true;
        return true;
    }
    return false;
}

void stateTimerRestart(void)
{
    stateStart = tickNow();
}

bool vendDone(void)
{
    return (tickNow() - stateStart) >= VEND_TICKS;
}

void blinkStart(uint8_t times)
{
    blinkLeft = times;
    blinkOn   = false;
    if (times > 0) {
        digitalWrite(LED_REFUND_PIN, HIGH);
        blinkOn   = true;
        blinkLast = tickNow();
    } else {
        digitalWrite(LED_REFUND_PIN, LOW);
    }
}

bool blinkDone(void)
{
    if (blinkLeft == 0) return true;

    if ((tickNow() - blinkLast) >= BLINK_TICKS) {
        blinkLast = tickNow();
        if (blinkOn) {                       /* จบช่วงติด -> ดับ นับเป็น 1 ครั้ง */
            digitalWrite(LED_REFUND_PIN, LOW);
            blinkOn = false;
            blinkLeft--;
        } else {                             /* จบช่วงดับ -> ติดครั้งถัดไป */
            digitalWrite(LED_REFUND_PIN, HIGH);
            blinkOn = true;
        }
    }
    return blinkLeft == 0;
}

void ledFault(bool on)
{
    digitalWrite(LED_FAULT_PIN, on ? HIGH : LOW);
}

void ledRefundOff(void)
{
    blinkLeft = 0;
    blinkOn   = false;
    digitalWrite(LED_REFUND_PIN, LOW);
}

/* ===== โซน 4 : ADC + LCD + UART ==========================
   ================================================================ */

void adcInit(void)
{
    analogReadResolution(12);
    analogSetPinAttenuation(POT_PIN, ADC_11db);
}

uint8_t productIndex(void)
{
    static int8_t cur = -1;
    uint32_t sum = 0;
    for (int i = 0; i < ADC_SAMPLES; i++) sum += analogRead(POT_PIN);
    int avg = (int)(sum / ADC_SAMPLES);

    const int W = 4096 / PRODUCT_COUNT;
    int target = avg / W;
    if (target >= PRODUCT_COUNT) target = PRODUCT_COUNT - 1;

    if (cur < 0) { cur = (int8_t)target; return (uint8_t)cur; }

    if (target != cur) {
        int lo = cur * W;
        int hi = (cur + 1) * W;
        /* เปลี่ยนช่วงเมื่อค่าเลยขอบไปเกิน POT_HYST เท่านั้น */
        if (avg < lo - POT_HYST || avg >= hi + POT_HYST) cur = (int8_t)target;
    }
    return (uint8_t)cur;
}

/* ---- ไดรเวอร์ LCD 16x2 แบบ I2C backpack (PCF8574) เขียนเอง ไม่ต้องพึ่งไลบรารี ----
   P0=RS P1=RW P2=EN P3=BL P4..P7=D4..D7 */
static void lcdBytes(const uint8_t *d, size_t n)
{
    Wire.beginTransmission(LCD_ADDR);
    Wire.write(d, n);
    Wire.endTransmission();
}

static void lcdNibble(uint8_t n)                 /* n อยู่ใน 4 บิตบน */
{
    uint8_t v = (uint8_t)((n & 0xF0) | LCD_BL);
    uint8_t d[2] = { (uint8_t)(v | 0x04), v };
    lcdBytes(d, 2);
}

static void lcdSend(uint8_t v, bool rs)
{
    uint8_t r  = rs ? 0x01 : 0x00;
    uint8_t hi = (uint8_t)((v & 0xF0) | LCD_BL | r);
    uint8_t lo = (uint8_t)(((v << 4) & 0xF0) | LCD_BL | r);
    uint8_t d[4] = { (uint8_t)(hi | 0x04), hi, (uint8_t)(lo | 0x04), lo };
    lcdBytes(d, 4);
}

static void lcdLine(uint8_t row, const char *s)
{
    char buf[17];
    snprintf(buf, sizeof buf, "%-16s", s);
    lcdSend((uint8_t)(0x80 | (row ? 0x40 : 0x00)), false);
    for (int i = 0; i < 16; i++) lcdSend((uint8_t)buf[i], true);
}

static void lcdTop(uint8_t p)
{
    if (p >= PRODUCT_COUNT) p = 0;
    char price[8];
    snprintf(price, sizeof price, "%uB", (unsigned)PRODUCT_PRICE[p]);
    int pad = 16 - (int)strlen(PRODUCT_NAME[p]) - (int)strlen(price);
    if (pad < 1) pad = 1;
    char buf[40];
    snprintf(buf, sizeof buf, "%s%*s%s", PRODUCT_NAME[p], pad, "", price);
    lcdLine(0, buf);
}

void lcdInit(void)
{
    Wire.begin(I2C_SDA, I2C_SCL, I2C_HZ);
    delayMicroseconds(50000);                    /* รอจอ power-up ~50 ms */
    lcdNibble(0x30); delayMicroseconds(5000);
    lcdNibble(0x30); delayMicroseconds(200);
    lcdNibble(0x30); delayMicroseconds(200);
    lcdNibble(0x20); delayMicroseconds(200);     /* เข้าโหมด 4 บิต */
    lcdSend(0x28, false);                        /* 4-bit, 2 บรรทัด, 5x8 */
    lcdSend(0x0C, false);                        /* display on, cursor off */
    lcdSend(0x01, false); delayMicroseconds(2000);  /* clear */
    lcdSend(0x06, false);                        /* entry mode */
}

void showIdle(uint8_t product)
{
    const char *l2 = (stock[product] == 0) ? "Sold out" : "Insert coin";   /* สต็อกหมด = ไม่รับเหรียญ */
    lcdTop(product);
    lcdLine(1, l2);
#if SHOW_SERIAL
    LOGT("[LCD] %s %uB | %s", PRODUCT_NAME[product], (unsigned)PRODUCT_PRICE[product], l2);
#endif
}

void showCounting(uint8_t product, uint16_t balance)
{
    char buf[17];
    lcdTop(product);
    snprintf(buf, sizeof buf, "Coin: %uB", (unsigned)balance);
    lcdLine(1, buf);
#if SHOW_SERIAL
    LOGT("[LCD] %s %uB | %s", PRODUCT_NAME[product], (unsigned)PRODUCT_PRICE[product], buf);
#endif
}

void showVending(void)
{
    lcdLine(0, "VENDING...");
    lcdLine(1, "");
#if SHOW_SERIAL
    LOGT("[LCD] VENDING...");
#endif
}

void showChange(uint16_t amount)
{
    char buf[17];
    snprintf(buf, sizeof buf, "Change: %uB", (unsigned)amount);
    lcdLine(0, "Thank you!");
    lcdLine(1, buf);
#if SHOW_SERIAL
    LOGT("[LCD] %s", buf);
#endif
}

void showRefund(uint16_t amount)
{
    char buf[17];
    snprintf(buf, sizeof buf, "Refund: %uB", (unsigned)amount);
    lcdLine(0, "TIMEOUT");
    lcdLine(1, buf);
#if SHOW_SERIAL
    LOGT("[LCD] %s", buf);
#endif
}

void showFault(void)
{
    lcdLine(0, "System Error");
    lcdLine(1, "Press BOOT");
#if SHOW_SERIAL
    LOGT("[LCD] ERR");
#endif
}

void uartInit(void)
{
    Serial1.begin(115200, SERIAL_8N1, U1_RX, U1_TX);
}

void sendStatusFrame(State s, uint16_t balance, uint8_t product)
{
    static uint8_t seq = 0;
    uint8_t f[8];
    f[0] = FRAME_HDR;                            /* 0xAA */
    f[1] = 5;                                    /* LEN = SEQ,STATE,BAL_H,BAL_L,PRODUCT */
    f[2] = seq++;
    f[3] = (uint8_t)s;
    f[4] = (uint8_t)(balance >> 8);
    f[5] = (uint8_t)(balance & 0xFF);
    f[6] = product;
    f[7] = (uint8_t)(f[1] + f[2] + f[3] + f[4] + f[5] + f[6]);   /* CHK 8 บิต */
    Serial1.write(f, sizeof f);
}

/* ===== โซน 1 : FSM   ==================================== */

static State    state   = S_IDLE;
static uint16_t balance = 0;
static uint8_t  product = 0;
static uint16_t payback = 0;
static uint8_t  shownProduct = 0;               /* สินค้าที่แสดงบนจอใน IDLE ล่าสุด */
static uint16_t rejectPending = 0;              /* ยอดเหรียญที่ถูก reject (สินค้าหมด) และยังรอกะพริบไฟถอน (1B = 1 ครั้ง) */

static const char *const STATE_NAME[S_COUNT] = {
    "IDLE", "COUNTING", "VEND", "CHANGE", "TIMEOUT_REFUND", "FAULT"
};

/* IDLE : ให้ไฟถอนกะพริบของเหรียญที่ถูก reject เดินต่อ
   - รอบเดิมยังกะพริบไม่จบ -> ปล่อยให้จบก่อน (เหรียญใหม่ที่เข้ามาสะสมใน rejectPending)
   - รอบเดิมจบแล้วและเว้นช่วงดับครบ BLINK_TICKS -> เริ่มรอบใหม่ตามยอดที่สะสม */
static void idleRejectBlink(void)
{
    if (!blinkDone()) return;
    if (rejectPending == 0) return;
    if ((tickNow() - blinkLast) < BLINK_TICKS) return;   /* เว้นช่วงดับคั่นระหว่างรอบ */

    uint8_t n = (rejectPending > 255) ? 255 : (uint8_t)rejectPending;
    rejectPending = 0;
    blinkStart(n);
}

void go(State next)
{
    State prev = state;
    LOGT("[FSM] %s -> %s", STATE_NAME[prev], STATE_NAME[next]);
    state = next;

    switch (next) {
    case S_IDLE:
        balance = 0;
        payback = 0;
        rejectPending = 0;
        ledRefundOff();
        ledFault(false);
        product = productIndex();                  /* อ่านสินค้าล่าสุดก่อนโชว์ ไม่ให้จอสลับ 1 tick หลังเข้า IDLE */
        showIdle(product);
        shownProduct = product;
        break;

    case S_COUNTING:
        /* product ถูกล็อก: loop ไม่เรียก productIndex() ใน state นี้ */
        rejectPending = 0;                         /* ตัดกะพริบ reject ที่ค้างจาก IDLE (ถ้ามี) */
        ledRefundOff();
        idleTimerRestart();
        showCounting(product, balance);
        break;

    case S_VEND:
        payback = (uint16_t)(balance - PRODUCT_PRICE[product]);
        stateTimerRestart();
        showVending();
        break;

    case S_CHANGE:
        stateTimerRestart();                       /* นับเวลาแสดงจออย่างน้อย SHOW_MIN_TICKS */
        LOGT("[MONEY] paid=%uB = price %uB + change %uB  (%s)", (unsigned)balance,
             (unsigned)PRODUCT_PRICE[product], (unsigned)payback,
             (balance == PRODUCT_PRICE[product] + payback) ? "OK" : "MISMATCH");
        showChange(payback);
        blinkStart((uint8_t)payback);
        break;

    case S_TIMEOUT_REFUND:
        payback = balance;
        stateTimerRestart();
        LOGT("[MONEY] paid=%uB refund=%uB  (%s)", (unsigned)balance, (unsigned)payback,
             (balance == payback) ? "OK" : "MISMATCH");
        showRefund(payback);
        blinkStart((uint8_t)payback);
        break;

    case S_FAULT:
        ledFault(true);
        rejectPending = 0;
        if (prev == S_IDLE) ledRefundOff();        /* กันไฟกะพริบจากการ reject ค้างตอนเข้า FAULT */

        if (prev == S_COUNTING) {
            payback = balance;
            blinkStart((uint8_t)payback);
        } else if (prev == S_VEND) {
            blinkStart((uint8_t)payback);
        }
        LOGT("[MONEY] fault from %s: paid=%uB refund=%uB", STATE_NAME[prev],
             (unsigned)balance, (unsigned)payback);
        showFault();
        break;

    default:
        break;
    }

    sendStatusFrame(state, balance, product);
}

/* ===== setup / loop ==================================== */

void code_ProjectG9_setup(void)
{
    inputInit();
    timerInit();
    adcInit();
    lcdInit();
    uartInit();

    balance = 0;
    payback = 0;
    product = productIndex();       /* อ่านค่า pot ครั้งแรก จอ IDLE จะได้ตรงสินค้าที่ pot ชี้ทันที */
    go(S_IDLE);
}

void code_ProjectG9_loop(void)
{
    if (!tickPending()) return;

    if (state == S_IDLE) product = productIndex();

    /* อ่านและเคลียร์ flag จาก ISR ทุกรอบ ป้องกันเหตุการณ์เก่าค้างไปทำงานในสถานะที่ไม่รับ */
    uint8_t coin = takeCoin();
    bool    rst  = takeReset();

    Event ev = EV_NONE;

    /* log เหตุการณ์ที่ถูกทิ้ง (เหรียญ/BOOT ที่มาในสถานะที่ไม่รับ) เพื่อให้ตามใน log ได้ครบ */
    if (coin && state != S_IDLE && state != S_COUNTING)
        LOGT("[E1] coin +%uB DROPPED in %s", (unsigned)coin, STATE_NAME[state]);
    if (rst && state != S_FAULT)
        LOGT("[E7] BOOT ignored in %s", STATE_NAME[state]);

    if (state == S_FAULT) {
        bool refundDone = blinkDone();             /* ให้การกะพริบคืนเงินเดินต่อใน FAULT */
        /* E7 : ออกจาก FAULT ได้เมื่อคืนเงินเสร็จ และปล่อยปุ่มเหรียญแล้วเท่านั้น
           (ถ้ากด BOOT ก่อนหน้านั้นจะถูกทิ้ง ต้องกดใหม่) */
        if (coin) LOGT("[E1] coin +%uB DROPPED in FAULT", (unsigned)coin);
        if (rst) {
            if (refundDone && !coinHeld()) { ev = EV_RESET; LOGT("[E7] BOOT accepted"); }
            else LOGT("[E7] BOOT ignored in FAULT (%s)", refundDone ? "coin button still held" : "refund blinking");
        }
    } else if (coinStuck()) {
        ev = EV_FAULT;                             /* E6 */
        LOGT("[E6] coin button held >= %u ms -> FAULT", (unsigned)(FAULT_TICKS * TICK_MS));
    } else if (state == S_IDLE || state == S_COUNTING) {
        if (coin && state == S_IDLE && stock[product] == 0) {
            /* สินค้าที่เลือกหมด : ไม่รับเหรียญ ยอดไม่เปลี่ยน แต่ให้ไฟถอนกะพริบตามมูลค่าเหรียญ (1B = 1 ครั้ง) */
            rejectPending += coin;
            LOGT("[E1] coin +%uB REJECTED: %s sold out -> refund blink x%u", (unsigned)coin,
                 PRODUCT_NAME[product], (unsigned)rejectPending);
        } else if (coin) {                         /* E1 */
            balance += coin;
            idleTimerRestart();
            LOGT("[E1] coin +%uB balance=%uB", (unsigned)coin, (unsigned)balance);
            ev = (balance >= PRODUCT_PRICE[product]) ? EV_ENOUGH : EV_COIN;   /* E2 ตรวจหลัง E1 เท่านั้น */
            if (ev == EV_ENOUGH) LOGT("[E2] balance %uB >= price %uB", (unsigned)balance, (unsigned)PRODUCT_PRICE[product]);
        } else if (state == S_COUNTING && idleTimeout()) {
            ev = EV_IDLE_TMO;                      /* E3 */
            LOGT("[E3] no coin for %u ms -> refund %uB", (unsigned)(TIMEOUT_TICKS * TICK_MS), (unsigned)balance);
        }
    } else if (state == S_VEND) {
        if (vendDone()) { ev = EV_VEND_DONE; LOGT("[E4] vend done"); }   /* E4 */
    } else {                                       /* S_CHANGE / S_TIMEOUT_REFUND */
        /* E5 : กะพริบครบ และจอแสดงมาแล้วอย่างน้อย SHOW_MIN_TICKS (1 s) */
        if (blinkDone() && (tickNow() - stateStart) >= SHOW_MIN_TICKS) {
            ev = EV_BLINK_DONE;
            LOGT("[E5] blink done");
        }
    }

    /* IDLE ไม่มีเหตุการณ์ : ให้ไฟถอนของเหรียญที่ถูก reject กะพริบต่อ */
    if (state == S_IDLE && ev == EV_NONE) idleRejectBlink();

    if (ev == EV_NONE) {
        /* ไม่มีเหตุการณ์: อัปเดตจอเฉพาะเมื่อสินค้าที่ pot ชี้เปลี่ยน (IDLE) */
        if (state == S_IDLE && product != shownProduct) {
            showIdle(product);
            shownProduct = product;
        }
        return;
    }

    switch (state) {
    case S_IDLE:
        if (ev == EV_FAULT) {
            go(S_FAULT);
        } else if (ev == EV_COIN || ev == EV_ENOUGH) {
            go(S_COUNTING);                        /* เหรียญแรกล็อกสินค้า */
            if (ev == EV_ENOUGH) go(S_VEND);
        }
        break;

    case S_COUNTING:
        if (ev == EV_FAULT)          go(S_FAULT);
        else if (ev == EV_ENOUGH)    go(S_VEND);
        else if (ev == EV_COIN) {                  /* บวกยอดแล้ว อัปเดตจอ + ส่งเฟรมยอดใหม่ */
            showCounting(product, balance);
            sendStatusFrame(state, balance, product);
        }
        else if (ev == EV_IDLE_TMO)  go(S_TIMEOUT_REFUND);
        break;

    case S_VEND:
        if (ev == EV_FAULT)          go(S_FAULT);
        else if (ev == EV_VEND_DONE) {
            /* ลดสต็อกเมื่อจ่ายของเสร็จจริงเท่านั้น (ถ้า FAULT ระหว่าง VEND จะไม่ถึงบรรทัดนี้) */
            if (stock[product] > 0) stock[product]--;
            LOGT("[STOCK] %s left=%u%s", PRODUCT_NAME[product], (unsigned)stock[product],
                 stock[product] == 0 ? " (SOLD OUT)" : "");
            go(S_CHANGE);
        }
        break;

    case S_CHANGE:
    case S_TIMEOUT_REFUND:
        if (ev == EV_FAULT)          go(S_FAULT);
        else if (ev == EV_BLINK_DONE) go(S_IDLE);
        break;

    case S_FAULT:
        if (ev == EV_RESET)          go(S_IDLE);
        break;

    default:
        break;
    }
}