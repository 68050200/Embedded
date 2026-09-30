/* ============================================================
   lab11.h  —  ค่าตั้งต้นของ Lab ครั้งที่ 11 : Interrupt และ Hardware Timer
   51423364 การเขียนโปรแกรมสำหรับระบบสมองกลฝังตัว
   ------------------------------------------------------------
   วงจรใน Wokwi ต่อให้แล้วเหมือนบอร์ดจริงของครั้งที่ 9–10
     แถบไฟ 4 ดวง  GPIO16 17 18 19
     pot          GPIO34
     ปุ่ม A        GPIO25  (ปุ่มสีเขียว กดลง = LOW)
     ปุ่ม B        GPIO4   (ปุ่มสีน้ำเงิน ใช้ในส่วนเพิ่มเติม)
     สาย loopback GPIO26 ─► GPIO27  (สายสีเขียว)
     logic analyzer  D0 = GPIO26  D1 = GPIO27
   ============================================================ */
#ifndef LAB11_H
#define LAB11_H

#include <Arduino.h>
#include <stdint.h>

/* ---------- ใส่รหัสนิสิตของตัวเอง ---------- */
#define STUDENT_ID   68050200UL      /* <<<< แก้เป็นรหัสนิสิตของตัวเองก่อนเริ่ม */
#define MY_TAIL      (STUDENT_ID % 100UL)      /* เลขท้ายสองหลัก */
#define MY_FREQ      (100UL + MY_TAIL)         /* ความถี่ประจำตัว 100–199 Hz */

/* ---------- ขาที่ใช้ ---------- */
#define LED_BASE     16     /* แถบไฟของครั้งที่ 9  GPIO16 17 18 19 */
#define LED_COUNT    4
#define ALARM_PIN    2      /* LED บนบอร์ด */
#define POT_PIN      34     /* pot ของครั้งที่ 10 */
#define BTN_PIN      25     /* ปุ่ม A */
#define BTN2_PIN     4      /* ปุ่ม B (ส่วนเพิ่มเติม) */
#define SIG_OUT_PIN  26     /* ขาส่งสัญญาณออก */
#define SIG_IN_PIN   27     /* ขารับสัญญาณเข้า ต่อสายจาก 26 */

/* ---------- ของที่ให้มาแล้วใน common.cpp ไม่ต้องเขียนเอง ---------- */
void        pwmSetup(int pin, uint32_t freq, uint8_t resBits);   /* ครั้งที่ 10 */
void        pwmWrite(int pin, uint32_t duty);                    /* ครั้งที่ 10 */
uint32_t    barMask(uint8_t level);                              /* ครั้งที่ 9  */
void        barShow(uint32_t mask);                              /* ครั้งที่ 9  */
uint8_t     potLevel(void);            /* อ่าน pot แล้วแปลงเป็นระดับ 0–4 */
hw_timer_t *timerSetup(uint32_t periodUs, void (*isr)(void));    /* ใหม่ */

/* ---------- ฟังก์ชันของแต่ละขั้น ---------- */
void step0_setup(void);  void step0_loop(void);
void step1_setup(void);  void step1_loop(void);
void step2_setup(void);  void step2_loop(void);
void step3_setup(void);  void step3_loop(void);
void step4_setup(void);  void step4_loop(void);
void step5_setup(void);  void step5_loop(void);

#endif /* LAB11_H */
