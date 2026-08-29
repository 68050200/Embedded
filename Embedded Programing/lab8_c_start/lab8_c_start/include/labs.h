#ifndef LABS_H
#define LABS_H

/* ครั้งที่ 8 : พอยน์เตอร์ หน่วยความจำ และการคุมขาจริงบน ESP32 */

void lab1_run(void);   /* พอยน์เตอร์เบื้องต้น        */
void lab2_run(void);   /* พอยน์เตอร์กับอาเรย์        */
void lab3_run(void);   /* สตริงและ buffer overflow  */
void lab4_run(void);   /* หน่วยความจำบน MCU         */
void lab5_run(void);   /* GPIO ครั้งแรก             */
void lab6_run(void);   /* เขียนรีจิสเตอร์ตรง ๆ      */
void challenge_run(void);

/* ---- ขาที่ใช้ในคาบนี้ แก้ตรงนี้ที่เดียวถ้าบอร์ดของกลุ่มใช้ขาอื่น ---- */
#define LED_PIN     2    /* LED บนบอร์ด ESP32 DevKit ส่วนใหญ่อยู่ที่ GPIO2 */
#define SENSOR_PIN  4    /* ขาอินพุตดิจิทัล ต่อปุ่มหรือเซนเซอร์ดิจิทัล    */

#endif /* LABS_H */
