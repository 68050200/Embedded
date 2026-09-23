/* ============================================================
   lab10.h  —  ค่าคงที่และต้นแบบฟังก์ชันของ Lab 10 : ADC และ PWM
   51423364  ครั้งที่ 10  ศุกร์ 18 ก.ย. 2569
   ------------------------------------------------------------
   แก้ค่าฮาร์ดแวร์ได้ที่ไฟล์นี้ไฟล์เดียว
   ============================================================ */
#ifndef LAB10_H
#define LAB10_H

#include <stdint.h>

/* ---------- ขาที่ใช้ ---------- */
#define LED_BASE     16     /* แถบไฟครั้งที่ 9  GPIO16..19            */
#define LED_COUNT    4
#define PWM_PIN      2      /* งาน 1, 4  LED บนบอร์ด                  */
#define POT_PIN      34     /* งาน 2, 3  wiper ของ pot  (ADC1_CH6)     */
#define RC_PWM_PIN   4      /* งาน 4    PWM ออก (จัมเปอร์ไป GPIO35)     */
#define RC_ADC_PIN   35     /* งาน 4-5  ADC อ่าน  (ADC1_CH7)           */
#define DAC_PIN      25     /* งาน 5    DAC 8 บิตของ ESP32             */

/* ---------- สเปก ADC ของ ESP32 ---------- */
#define ADC_BITS     12
#define ADC_MAX      4095               /* 2^12 - 1                  */
#define VFS_MV       3300               /* full-scale ที่ใช้คำนวณ    */
#define ADC_LSB_UV   ((VFS_MV * 1000L) / (ADC_MAX + 1))   /* 805 uV  */

/* ---------- สเปก PWM (LEDC) ---------- */
#define PWM_CH       0                  /* HS channel 0 → HS timer 0 */
#define PWM_FREQ     5000               /* Hz                        */
#define PWM_BITS     8
#define PWM_MAX      ((1u << PWM_BITS) - 1u)              /* 255     */
#define LEDC_CLK_HZ  80000000UL         /* APB_CLK                   */

/* ---------- RC filter สำหรับโครงงาน (ดู extras/) ---------- */
#define RC_R_OHM     4700
#define RC_C_NF      1000               /* 1 uF                      */

/* ---------- common.cpp  (ให้มาแล้ว) ---------- */
void     pwmSetup(int pin, uint32_t freq, uint8_t resBits);
void     pwmWrite(int pin, uint32_t duty);
uint32_t barMask(uint8_t level);
void     barShow(uint32_t mask);
uint32_t isqrt32(uint32_t x);
uint32_t ledcTimer0Conf(void);          /* อ่าน LEDC_HSTIMER0_CONF_REG */

/* ---------- ส่วนที่นิสิตเขียน : ชั้นหลัก ---------- */
int32_t  rawToMilliVolt(int raw);                     /* งาน 2  TODO 2.1 */
int      readAveraged(int pin, int n);                /* งาน 3  TODO 3.1 */

/* ---------- ส่วนที่นิสิตเขียน : ส่วนเพิ่มเติม ---------- */
uint32_t ledcFreqFromConf(uint32_t conf);             /* งาน 7  TODO 7.1 */
void     ledcWriteRegister(uint32_t duty);            /* งาน 7  TODO 7.2 */
int32_t  rcRipplePeakMv(uint32_t vccMv, uint32_t fHz,
                        uint32_t rOhm, uint32_t cNf);  /* extras/ ตัวอย่างโครงงาน */

/* ชั้นหลัก 1-5   ส่วนเพิ่มเติม 6-7   challenge 8 */
void task1_run(void);  void task2_run(void);  void task3_run(void);  void task4_run(void);
void task5_run(void);  void task6_run(void);  void task7_run(void);  void task8_run(void);

#endif
