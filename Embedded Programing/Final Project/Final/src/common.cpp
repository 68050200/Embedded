/* ============================================================

    GROUP 9 Final Project : ตู้หยอดเหรียญ
    51423364 การเขียนโปรแกรมสำหรับระบบสมองกลฝังตัว

    1	นายชิษณุพงศ์ วิเชียรกุล	68050200	
    2	นายกิตติภน ภาษีชา	68050392	
    3	นายณัชพล วงศ์ยัง	68050393	
    4	นายธีรธน จันทบุตร	68050395	



   common.cpp  —  ของที่ให้มาแล้ว ไม่ต้องแก้
   
   ------------------------------------------------------------
     bar()            แถบไฟด้วยรีจิสเตอร์ (ครั้งที่ 8–9)
     pwmWrite()       ห่อ LEDC ให้ผ่านทั้ง core 2.x และ 3.x (ครั้งที่ 10)
     ปุ่ม / tick       interrupt + hardware timer (ครั้งที่ 11–12)
     senderFrameTick  "โหนดเซนเซอร์" ที่ส่งเฟรมออกทาง Serial1 (STEP 2)
     sensorSimBegin   "เซนเซอร์อุณหภูมิ I2C" จำลองบน Wire1 (STEP 3–4)

     
   ============================================================ */
#include <Arduino.h>
#include <Wire.h>
#include <esp_arduino_version.h>
#include "soc/gpio_reg.h"
#include "PROJECT_G9.h"

#define ALL_MASK ((uint32_t)(((1u << LED_COUNT) - 1u) << LED_BASE))

/* ---------------- แถบไฟ ---------------- */
void barInit(void)
{
    for (int i = 0; i < LED_COUNT; i++) pinMode(LED_BASE + i, OUTPUT);
    bar(0);
}

void bar(uint8_t level)
{
    if (level > LED_COUNT) level = LED_COUNT;
    uint32_t m = ((1u << level) - 1u) << LED_BASE;
    REG_WRITE(GPIO_OUT_W1TS_REG, m);
    REG_WRITE(GPIO_OUT_W1TC_REG, (~m) & ALL_MASK);
}

/* ---------------- PWM ---------------- */
void pwmInit(void)
{
#if ESP_ARDUINO_VERSION_MAJOR >= 3
    ledcAttach(PWM_PIN, 5000, 8);
#else
    ledcSetup(0, 5000, 8);
    ledcAttachPin(PWM_PIN, 0);
#endif
    pwmWrite(0);
}

void pwmWrite(uint8_t duty)
{
#if ESP_ARDUINO_VERSION_MAJOR >= 3
    ledcWrite(PWM_PIN, duty);
#else
    ledcWrite(0, duty);
#endif
}

/* ---------------- timer / tick ---------------- */
hw_timer_t *timerSetup(uint32_t periodUs, void (*isr)(void))
{
#if ESP_ARDUINO_VERSION_MAJOR >= 3
    hw_timer_t *t = timerBegin(1000000);
    timerAttachInterrupt(t, isr);
    timerAlarm(t, periodUs, true, 0);
#else
    static uint8_t next = 0;
    hw_timer_t *t = timerBegin(next++ & 3, 80, true);
    timerAttachInterrupt(t, isr, true);
    timerAlarmWrite(t, periodUs, true);
    timerAlarmEnable(t);
#endif
    return t;
}

static volatile uint32_t tickCount = 0;
static uint32_t          tickSeen  = 0;
static void IRAM_ATTR onTick(void) { tickCount++; }

void tickInit(void) { timerSetup(TICK_MS * 1000u, onTick); }

bool takeTick(void)
{
    if (tickCount == tickSeen) return false;
    tickSeen++;
    return true;
}

uint32_t nowMs(void) { return tickSeen * TICK_MS; }

/* ---------------- ปุ่ม BOOT ---------------- */
#define DEBOUNCE_MS   30
#define LONG_PRESS_MS 1500
static volatile uint32_t shortCount = 0, longCount = 0;
static volatile uint32_t downMs = 0, lastEdgeMs = 0;
static volatile bool     isDown = false;
static uint32_t shortSeen = 0, longSeen = 0;

static void IRAM_ATTR onButton(void)
{
    uint32_t now = millis();
    if (now - lastEdgeMs < DEBOUNCE_MS) return;
    lastEdgeMs = now;
    bool pressed = ((REG_READ(GPIO_IN_REG) >> BTN_PIN) & 1u) == 0;
    if (pressed && !isDown) { isDown = true; downMs = now; }
    else if (!pressed && isDown) {
        isDown = false;
        if (now - downMs >= LONG_PRESS_MS) longCount++;
        else                               shortCount++;
    }
}

void buttonInit(void)
{
    pinMode(BTN_PIN, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(BTN_PIN), onButton, CHANGE);
}

bool takeShortPress(void)
{
    if (shortCount == shortSeen) return false;
    shortSeen = shortCount;
    return true;
}

bool takeLongPress(void)
{
    if (longCount == longSeen) return false;
    longSeen = longCount;
    return true;
}

/* ---------------- ผู้ส่ง (Serial1) ---------------- */
void senderBegin(uint32_t baud)
{
    Serial1.begin(baud, SERIAL_8N1, U1_RX, U1_TX);
}

/* ส่งเฟรม [AA][03][SEQ][RAW_H][RAW_L][CHK] ทุก 200 ms
   กดปุ่ม BOOT สั้น = เฟรมถัดไปมีไบต์เสีย 1 บิต (จำลองสัญญาณรบกวน)
   กดค้าง           = เฟรมถัดไปขาดหายไป 1 ไบต์ (จำลองสายหลุดชั่วขณะ) */
void senderFrameTick(void)
{
    static uint32_t n = 0;
    static uint8_t  seq = 0;
    static bool     corrupt = false, drop = false;

    if (takeShortPress()) { corrupt = true; Serial.println("   >> (ผู้ส่ง) เฟรมถัดไปจะมีบิตเสีย"); }
    if (takeLongPress())  { drop = true;    Serial.println("   >> (ผู้ส่ง) เฟรมถัดไปจะขาด 1 ไบต์"); }
    if (++n < 200 / TICK_MS) return;
    n = 0;

    uint16_t raw = (uint16_t)analogRead(POT_PIN);
    uint8_t  f[6];
    f[0] = FRAME_HDR;
    f[1] = 3;
    f[2] = seq++;
    f[3] = (uint8_t)(raw >> 8);
    f[4] = (uint8_t)(raw & 0xFF);
    f[5] = (uint8_t)(f[1] + f[2] + f[3] + f[4]);

    if (corrupt) { f[4] ^= 0x04; corrupt = false; }
    if (drop)    { Serial1.write(f, 3); Serial1.write(f + 4, 2); drop = false; return; }
    Serial1.write(f, sizeof f);
}

/* ---------------- เซนเซอร์จำลอง (Wire1 เป็น slave) ----------------
   ทุกครั้งที่ master อ่าน 4 ไบต์ จะได้ [ID][TEMP_H][TEMP_L][SEQ]
   ESP32 รุ่นนี้ต้องเตรียมข้อมูลไว้ "ก่อน" master มาอ่าน
   จึงวัดค่าใหม่ไว้รอทุกครั้งหลังถูกอ่าน → ค่าที่ได้คือผลการวัดครั้งก่อน
   (เซนเซอร์จริงหลายรุ่นก็เป็นแบบนี้ : อ่านได้ผลการแปลงครั้งล่าสุด)        */
int16_t potToCenti(void)
{
    int32_t raw = analogRead(POT_PIN);                 /* 0–4095 */
    return (int16_t)(-2000 + (raw * 10000) / 4095);    /* -20.00 ถึง +80.00 °C */
}

static uint8_t simSeq = 0;

static void simFill(uint8_t *p)
{
    int16_t t = potToCenti();
    p[0] = SENSOR_ID;
    p[1] = (uint8_t)((uint16_t)t >> 8);
    p[2] = (uint8_t)((uint16_t)t & 0xFF);
    p[3] = simSeq++;
}

static void onSimRequest(void)
{
    uint8_t p[SENSOR_LEN];
    simFill(p);
    Wire1.write(p, SENSOR_LEN);
}

void sensorSimBegin(void)
{
    Wire1.onRequest(onSimRequest);
    Wire1.begin((uint8_t)SENSOR_ADDR, SLV_SDA, SLV_SCL, I2C_HZ);
#if CONFIG_IDF_TARGET_ESP32
    uint8_t p[SENSOR_LEN];
    simFill(p);
    Wire1.slaveWrite(p, SENSOR_LEN);                   /* เตรียมข้อมูลชุดแรกไว้รอ */
#endif
}
