/* ============================================================
        GROUP 9 Final Project : ตู้หยอดเหรียญจำลอง (ESP32)
       51423364 การเขียนโปรแกรมสำหรับระบบสมองกลฝังตัว

       1	นายชิษณุพงศ์ วิเชียรกุล	68050200	FSM
       2	นายกิตติภน ภาษีชา	68050392	ISR ปุ่ม
       3	นายณัชพล วงศ์ยัง	68050393	hardware timer tick
       4	นายธีรธน จันทบุตร	68050395	ADC / LCD / UART
   ------------------------------------------------------------
     ปุ่มเหรียญ GPIO13 (กดสั้น 1 บาท / กดยาว 5 บาท)   ปุ่ม reset GPIO0 (BOOT)
     pot GPIO34 เลือกสินค้า   LED ทอน/คืนเงิน GPIO4   LED FAULT GPIO2
     LCD I2C  SDA GPIO21  SCL GPIO22
     UART เฟรมสถานะ  Serial1 TX GPIO26 --สาย--> GPIO27 RX
   ============================================================ */
#ifndef PROJECT_G9
#define PROJECT_G9

#include <Arduino.h>
#include <Wire.h>
#include <stdint.h>

/* ==================== ขา  ==================== */
#define COIN_PIN        13      /* ปุ่มหยอดเหรียญ  (E1, ISR) */
#define RESET_PIN       0       /* ปุ่ม BOOT = reset (E7, ISR) */
#define POT_PIN         34      /* ADC เลือกสินค้า */
#define LED_REFUND_PIN  4       /* LED ทอน / คืนเงิน */
#define LED_FAULT_PIN   2       /* LED บนบอร์ด = FAULT */

#define I2C_SDA         21      /* LCD */
#define I2C_SCL         22
#define I2C_HZ          100000
#define LCD_ADDR        0x27    /* ตรวจด้วย I2C scan ว่าจอของจริงใช้ 0x27 หรือ 0x3F */

#define U1_TX           26      /* Serial1 ส่งเฟรม */
#define U1_RX           14      /* ไม่ได้ใช้ */
#define U2_RX           27      /* ต่อสายจาก 26 */

/* ==================== เวลา (หน่วย = tick, 1 tick = TICK_MS) ==================== */
#define TICK_MS          10
#define COIN_LONG_TICKS  100    /* กดตั้งแต่ 100 tick (1 s) = 5 บาท, น้อยกว่า = 1 บาท */
#define FAULT_TICKS      300    /* กดค้าง >= 300 tick (3 s) = E6 FAULT (ต้องมากกว่า COIN_LONG_TICKS) */
#define TIMEOUT_TICKS    1000   /* ไม่หยอดเกิน 10 s = E3 */
#define VEND_TICKS       200    /* เวลาแสดง VENDING...  (ค่าเริ่มต้น 2 s ปรับได้) */
#define BLINK_TICKS      25     /* ครึ่งคาบการกะพริบ LED ทอน (ค่าเริ่มต้น 250 ms ปรับได้) */

/* ==================== สินค้า (4 ช่วงของ pot 0–4095) ==================== */
/* ชื่อ/ราคา ไม่เกิน 10 ตัวอักษร */
#define PRODUCT_COUNT   4
static const char    *const PRODUCT_NAME[PRODUCT_COUNT]  = { "Water", "Soda", "Snack", "Juice" };
static const uint8_t        PRODUCT_PRICE[PRODUCT_COUNT] = { 10, 15, 20, 25 };

/* ==================== สถานะและเหตุการณ์ (โซน 1 : FSM) ==================== */
enum State : uint8_t {
    S_IDLE, S_COUNTING, S_VEND, S_CHANGE, S_TIMEOUT_REFUND, S_FAULT,
    S_COUNT
};

enum Event : uint8_t {
    EV_NONE,
    EV_COIN,        /* E1 หยอดเหรียญ */
    EV_ENOUGH,      /* E2 ยอด >= ราคา (ตรวจหลัง E1 เท่านั้น) */
    EV_IDLE_TMO,    /* E3 ไม่หยอดเกิน 10 s */
    EV_VEND_DONE,   /* E4 จ่ายของเสร็จ */
    EV_BLINK_DONE,  /* E5 ทอน/คืนเงินเสร็จ */
    EV_FAULT,       /* E6 กดค้างผิดปกติ */
    EV_RESET        /* E7 reset */
};

/* ==================== ฟังก์ชันของแต่ละโซน (เขียนใน code_PROJECT_G9.cpp) ==================== */

/* ---- โซน 2 : ISR ปุ่ม  ---- */
void     inputInit(void);          /* ผูก ISR ปุ่มเหรียญ + ปุ่ม reset */
uint8_t  takeCoin(void);           /* 0 = ไม่มี, 1 = เหรียญ 1 บาท, 5 = เหรียญ 5 บาท (อ่านแล้วเคลียร์) */
bool     takeReset(void);          /* true 1 ครั้งต่อการกด reset */
bool     coinHeld(void);           /* ปุ่มเหรียญกำลังถูกกดอยู่ (ให้โซน 3 ใช้ตรวจ E6) */

/* ---- โซน 3 : hardware timer tick  ---- */
void     timerInit(void);          /* เริ่ม timer tick TICK_MS */
bool     tickPending(void);        /* true 1 ครั้งต่อ tick */
uint32_t tickNow(void);            /* จำนวน tick ตั้งแต่เปิดเครื่อง */
void     idleTimerRestart(void);   /* เริ่มนับ E3 ใหม่ (เรียกทุกครั้งที่เกิด E1) */
bool     idleTimeout(void);        /* E3 : ครบ TIMEOUT_TICKS */
bool     coinStuck(void);          /* E6 : ปุ่มเหรียญค้าง >= FAULT_TICKS */
void     stateTimerRestart(void);  /* เริ่มนับเวลาในสถานะ (VEND) */
bool     vendDone(void);           /* E4 : ครบ VEND_TICKS */
void     blinkStart(uint8_t times);/* เริ่มกะพริบ LED GPIO4 จำนวน times ครั้ง */
bool     blinkDone(void);          /* E5 : กะพริบครบ */
void     ledFault(bool on);        /* LED GPIO2 */
void     ledRefundOff(void);

/* ---- โซน 4 : ADC / LCD / UART  ---- */
void     adcInit(void);
uint8_t  productIndex(void);       /* 0..PRODUCT_COUNT-1 (เฉลี่ยค่า + hysteresis) */
void     lcdInit(void);
void     showIdle(void);                                   /* "Insert coin" */
void     showCounting(uint8_t product, uint16_t balance);  /* ชื่อ+ราคา / Coin: xB */
void     showVending(void);                                /* "VENDING..." */
void     showChange(uint16_t amount);                      /* เงินทอน */
void     showRefund(uint16_t amount);                      /* เงินคืน */
void     showFault(void);                                  /* "ERR" */
void     uartInit(void);
void     sendStatusFrame(State s, uint16_t balance, uint8_t product);  /* AA LEN SEQ ... CHK */

/* ---- โซน 1 : FSM  ---- */
void     go(State next);           /* เปลี่ยนสถานะ + log Serial + ทำงานตอนเข้าสถานะ */


#define LED_BASE     16
#define LED_COUNT    4
#define BTN_PIN      RESET_PIN
#define PWM_PIN      2
#define SLV_SDA      32
#define SLV_SCL      33
#define SENSOR_ADDR  0x40
#define SENSOR_ID    0x13
#define SENSOR_LEN   4
#define FRAME_HDR    0xAA

void     barInit(void);
void     bar(uint8_t level);
void     pwmInit(void);
void     pwmWrite(uint8_t duty);
void     buttonInit(void);
bool     takeShortPress(void);
bool     takeLongPress(void);
void     tickInit(void);
bool     takeTick(void);
uint32_t nowMs(void);
hw_timer_t *timerSetup(uint32_t periodUs, void (*isr)(void));
void     senderBegin(uint32_t baud);
void     senderFrameTick(void);
void     sensorSimBegin(void);
int16_t  potToCenti(void);

/* ==================== ฟังก์ชันหลัก ==================== */
void code_ProjectG9_setup(void);
void code_ProjectG9_loop(void);

#endif