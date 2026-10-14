/* ============================================================
   lab13.h  —  ค่าตั้งต้นของ Lab ครั้งที่ 13 : UART และ I2C
   51423364 การเขียนโปรแกรมสำหรับระบบสมองกลฝังตัว
   ------------------------------------------------------------
   ไม่มีเซนเซอร์จริง เราให้บอร์ด "คุยกับตัวเอง" แทน
     UART : Serial1 (ผู้ส่ง)  TX GPIO26  --สาย-->  GPIO27 RX  Serial2 (ผู้รับ)
            (สายเส้นเดียวกับครั้งที่ 11 ถ้ายังต่ออยู่ ใช้ได้เลย)
     I2C  : Wire  = master  SDA GPIO21  SCL GPIO22
            Wire1 = "เซนเซอร์จำลอง" (slave)  SDA GPIO32  SCL GPIO33
            ต่อสาย 21 <-> 32  และ  22 <-> 33   (2 เส้น)
     pot GPIO34 = ค่าอุณหภูมิของเซนเซอร์จำลอง
     แถบไฟ GPIO16–19 + ปุ่ม BOOT (GPIO0) เหมือนครั้งที่ 12
   ============================================================ */
#ifndef LAB13_H
#define LAB13_H

#include <Arduino.h>
#include <Wire.h>
#include <stdint.h>

#define GROUP_NO     9       /* <<<< แก้เป็นเลขกลุ่มของตัวเองก่อนเริ่ม (1–31) */

/* ---------- ขา ---------- */
#define LED_BASE     16
#define LED_COUNT    4
#define BTN_PIN      0       /* ปุ่ม BOOT */
#define POT_PIN      34
#define PWM_PIN      2       /* LED บนบอร์ด */

#define U1_TX        26      /* Serial1 ส่ง */
#define U1_RX        14      /* ไม่ได้ใช้ */
#define U2_RX        27      /* Serial2 รับ  ต่อสายจาก 26 */
#define U2_TX        13      /* ไม่ได้ใช้ */

#define I2C_SDA      21      /* master */
#define I2C_SCL      22
#define SLV_SDA      32      /* เซนเซอร์จำลอง ต่อสายจาก 21 */
#define SLV_SCL      33      /*                 ต่อสายจาก 22 */
#define I2C_HZ       100000

/* เซนเซอร์จำลอง "TMP-13" : ที่อยู่ขึ้นกับเลขกลุ่ม ต้อง scan หาเอง */
#define SENSOR_ADDR  (0x40 + (GROUP_NO % 32))
#define SENSOR_ID    0x13    /* ไบต์แรกของทุกครั้งที่อ่าน */
#define SENSOR_LEN   4       /* อ่านทีละ 4 ไบต์: ID, TEMP_H, TEMP_L, SEQ */
                             /* TEMP = int16 หน่วย 0.01 °C  ช่วง -20.00 ถึง +80.00 */

/* ---------- เฟรมข้อมูลของ STEP 2 ---------- */
#define FRAME_HDR    0xAA    /* [0xAA][LEN][DATA...LEN ไบต์][CHK] */
#define FRAME_MAX    16      /* CHK = ผลรวมของ LEN และ DATA ทุกไบต์ เก็บแค่ 8 บิต */
#define FRAME_GAP_MS 50      /* ไบต์ห่างกันเกินนี้ = เฟรมขาด */

#define TICK_MS      10

/* ---------- ของที่ให้มาแล้วใน common.cpp ---------- */
void     barInit(void);
void     bar(uint8_t level);                  /* แถบไฟ 0–4 ดวง */
void     pwmInit(void);
void     pwmWrite(uint8_t duty);              /* LED บนบอร์ด 0–255 */
void     buttonInit(void);
bool     takeShortPress(void);
bool     takeLongPress(void);
void     tickInit(void);
bool     takeTick(void);
uint32_t nowMs(void);
hw_timer_t *timerSetup(uint32_t periodUs, void (*isr)(void));

void     senderBegin(uint32_t baud);          /* Serial1 ส่งออกที่ GPIO26 */
void     senderFrameTick(void);               /* STEP 2: ส่งเฟรมทุก 200 ms (เรียกทุก tick) */
void     sensorSimBegin(void);                /* STEP 3: เปิดเซนเซอร์จำลองบน Wire1 */
int16_t  potToCenti(void);                    /* ค่าอุณหภูมิจริงที่เซนเซอร์จำลองใช้ (ไว้เทียบ) */

/* ---------- ฟังก์ชันของแต่ละขั้น ---------- */
void step0_setup(void);  void step0_loop(void);
void step1_setup(void);  void step1_loop(void);
void step2_setup(void);  void step2_loop(void);
void step3_setup(void);  void step3_loop(void);
void step4_setup(void);  void step4_loop(void);

#endif
