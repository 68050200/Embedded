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
  - ไม่เรียก buttonInit() / tickInit() / senderBegin() ของ common.cpp
    เพราะ buttonInit() ผูก ISR ที่ GPIO0 ซ้ำกับ inputInit()
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

static volatile uint32_t resetCount = 0, lastResetEdge = 0;
static uint32_t          resetSeen = 0;

static void IRAM_ATTR onCoin(void)
{
    bool     pressed = ((REG_READ(GPIO_IN_REG) >> COIN_PIN) & 1u) == 0;   /* active-low */
    uint32_t now     = hwTick;

    if (pressed) {
        if (!coinDown) { coinDown = true; coinDownTick = now; }
    } else if (coinDown) {
        coinDown = false;
        uint32_t dur = now - coinDownTick;
        if (dur < COIN_DEBOUNCE_TICKS) return;          /* bounce */
        if (dur >= FAULT_TICKS)        return;          /* กดค้าง = FAULT ไม่นับเป็นเหรียญ */
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
static uint32_t heldSince  = 0;
static bool     wasHeld    = false;

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

bool coinStuck(void)
{
    if (!coinHeld()) { wasHeld = false; return false; }
    if (!wasHeld)    { wasHeld = true; heldSince = tickNow(); }
    return (tickNow() - heldSince) >= FAULT_TICKS;
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
    lcdTop(product);
    lcdLine(1, "Insert coin");
#if SHOW_SERIAL
    Serial.printf("[LCD] %s %uB | Insert coin\n", PRODUCT_NAME[product], (unsigned)PRODUCT_PRICE[product]);
#endif
}

void showCounting(uint8_t product, uint16_t balance)
{
    char buf[17];
    lcdTop(product);
    snprintf(buf, sizeof buf, "Coin: %uB", (unsigned)balance);
    lcdLine(1, buf);
#if SHOW_SERIAL
    Serial.printf("[LCD] %s %uB | %s\n", PRODUCT_NAME[product], (unsigned)PRODUCT_PRICE[product], buf);
#endif
}

void showVending(void)
{
    lcdLine(0, "VENDING...");
    lcdLine(1, "");
#if SHOW_SERIAL
    Serial.println("[LCD] VENDING...");
#endif
}

void showChange(uint16_t amount)
{
    char buf[17];
    snprintf(buf, sizeof buf, "Change: %uB", (unsigned)amount);
    lcdLine(0, "Thank you!");
    lcdLine(1, buf);
#if SHOW_SERIAL
    Serial.printf("[LCD] %s\n", buf);
#endif
}

void showRefund(uint16_t amount)
{
    char buf[17];
    snprintf(buf, sizeof buf, "Refund: %uB", (unsigned)amount);
    lcdLine(0, "TIMEOUT");
    lcdLine(1, buf);
#if SHOW_SERIAL
    Serial.printf("[LCD] %s\n", buf);
#endif
}

void showFault(void)
{
    lcdLine(0, "System Error");
    lcdLine(1, "Press BOOT");
#if SHOW_SERIAL
    Serial.println("[LCD] ERR");
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

static const char *const STATE_NAME[S_COUNT] = {
    "IDLE", "COUNTING", "VEND", "CHANGE", "TIMEOUT_REFUND", "FAULT"
};

void go(State next)
{
    State prev = state;
    Serial.printf("[FSM] %s -> %s\n", STATE_NAME[prev], STATE_NAME[next]);
    state = next;

    switch (next) {
    case S_IDLE:
        balance = 0;
        payback = 0;
        ledRefundOff();
        ledFault(false);
        showIdle(product);
        shownProduct = product;
        break;

    case S_COUNTING:
        /* product ถูกล็อก: loop ไม่เรียก productIndex() ใน state นี้ */
        idleTimerRestart();
        showCounting(product, balance);
        break;

    case S_VEND:
        payback = (uint16_t)(balance - PRODUCT_PRICE[product]);
        stateTimerRestart();
        showVending();
        break;

    case S_CHANGE:
        showChange(payback);
        blinkStart((uint8_t)payback);
        break;

    case S_TIMEOUT_REFUND:
        payback = balance;
        showRefund(payback);
        blinkStart((uint8_t)payback);
        break;

    case S_FAULT:
        ledFault(true);
        /* คืนเงินที่ค้าง (กฎข้อ 6)
           - มาจาก COUNTING : คืนยอดที่หยอดทั้งหมด
           - มาจาก VEND     : คืนส่วนทอน (payback คำนวณไว้แล้ว)
           - มาจาก CHANGE / TIMEOUT_REFUND : กะพริบค้างอยู่แล้ว ปล่อยให้ทำต่อ (loop เรียก blinkDone() ใน FAULT) */
        if (prev == S_COUNTING) {
            payback = balance;
            blinkStart((uint8_t)payback);
        } else if (prev == S_VEND) {
            blinkStart((uint8_t)payback);
        }
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

    if (state == S_FAULT) {
        blinkDone();                               /* ให้การกะพริบคืนเงินเดินต่อใน FAULT */
        if (rst) ev = EV_RESET;                    /* E7 เฉพาะ FAULT */
    } else if (coinStuck()) {
        ev = EV_FAULT;                             /* E6 */
    } else if (state == S_IDLE || state == S_COUNTING) {
        if (coin) {                                /* E1 */
            balance += coin;
            idleTimerRestart();
            Serial.printf("[E1] coin +%uB balance=%uB\n", (unsigned)coin, (unsigned)balance);
            ev = (balance >= PRODUCT_PRICE[product]) ? EV_ENOUGH : EV_COIN;   /* E2 ตรวจหลัง E1 เท่านั้น */
        } else if (state == S_COUNTING && idleTimeout()) {
            ev = EV_IDLE_TMO;                      /* E3 */
        }
    } else if (state == S_VEND) {
        if (vendDone()) ev = EV_VEND_DONE;         /* E4 */
    } else {                                       /* S_CHANGE / S_TIMEOUT_REFUND */
        if (blinkDone()) ev = EV_BLINK_DONE;       /* E5 */
    }

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
        else if (ev == EV_VEND_DONE) go(S_CHANGE);
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