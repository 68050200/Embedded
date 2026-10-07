/* ============================================================
   lab12.h  —  ค่าตั้งต้นของ Lab ครั้งที่ 12 : State Machine (FSM)
   51423364 การเขียนโปรแกรมสำหรับระบบสมองกลฝังตัว
   ------------------------------------------------------------
   งาน : ไฟจราจรหน้าทางม้าลาย มีปุ่มกดขอข้าม
   วงจร : ใช้แถบไฟ 4 ดวงของครั้งที่ 9 ต่อเหมือนเดิม ไม่ต้องรื้อ
     ดวง GPIO16 = ไฟเขียว (รถ)
     ดวง GPIO17 = ไฟเหลือง (รถ)
     ดวง GPIO18 = ไฟแดง (รถ)
     ดวง GPIO19 = ไฟคนข้าม (WALK)
     ปุ่ม  = ปุ่ม BOOT บนบอร์ด (GPIO0)  ไม่ต้องต่อเพิ่ม
             กดสั้น = ขอข้ามถนน   กดค้าง ≥ 1.5 s = สลับโหมดกลางคืน
   ============================================================ */
#ifndef LAB12_H
#define LAB12_H

#include <Arduino.h>
#include <stdint.h>

/* ---------- ขา ---------- */
#define LED_BASE     16
#define LED_COUNT    4
#define PIN_GREEN    16
#define PIN_YELLOW   17
#define PIN_RED      18
#define PIN_WALK     19
#define BTN_PIN      0       /* ปุ่ม BOOT */
#define POT_PIN      34      /* ใช้ในส่วนเพิ่มเติม */

/* ---------- เวลา (ms) ย่อให้สั้นเพื่อทดลองในห้อง ---------- */
#define TICK_MS          10      /* timer ทุก 10 ms */
#define T_GREEN_MIN    3000      /* ไฟเขียวรถต้องติดอย่างน้อย 3 s */
#define T_YELLOW       1000
#define T_WALK         4000
#define T_WALK_BLINK   2000      /* ไฟคนข้ามกะพริบเตือนก่อนหมด */
#define T_BLINK_HALF    250      /* กะพริบ 2 Hz */
#define LONG_PRESS_MS  1500
#define DEBOUNCE_MS      30

/* ---------- ของที่ให้มาแล้วใน common.cpp ---------- */
typedef enum { CAR_OFF, CAR_GREEN, CAR_YELLOW, CAR_RED } CarLight;

void     lightsInit(void);
void     lights(CarLight car, bool walk);        /* สั่งไฟทั้ง 4 ดวงในคำสั่งเดียว */
void     buttonInit(void);                        /* interrupt ปุ่ม + แยกกดสั้น/กดค้าง */
bool     takeShortPress(void);                    /* true ครั้งเดียวต่อการกดสั้น 1 ครั้ง */
bool     takeLongPress(void);                     /* true ครั้งเดียวต่อการกดค้าง 1 ครั้ง */
void     tickInit(void);                          /* timer ทุก TICK_MS */
bool     takeTick(void);                          /* true เมื่อถึง tick ใหม่ */
uint32_t nowMs(void);                             /* เวลาตั้งแต่เปิดเครื่อง (ms) นับจาก tick */
void     logChange(const char *from, const char *to, const char *why);
hw_timer_t *timerSetup(uint32_t periodUs, void (*isr)(void));

/* ---------- ฟังก์ชันของแต่ละขั้น ---------- */
void step0_setup(void);  void step0_loop(void);
void step1_setup(void);  void step1_loop(void);
void step2_setup(void);  void step2_loop(void);
void step3_setup(void);  void step3_loop(void);

#endif
