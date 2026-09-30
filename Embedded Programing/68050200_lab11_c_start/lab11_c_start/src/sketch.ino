/* ============================================================
   Lab ครั้งที่ 11 — Interrupt และ Hardware Timer : "เลิกใช้ delay()"
   51423364 การเขียนโปรแกรมสำหรับระบบสมองกลฝังตัว
   ------------------------------------------------------------
   วิธีใช้
     1. แก้ STUDENT_ID ใน lab11.h เป็นรหัสนิสิตของตัวเอง
     2. เปลี่ยนเลข STEP ด้านล่างเป็นขั้นที่จะทำ แล้วกด ▶ (Start)
     3. ทำตามลำดับ 0 → 1 → 2 → 3 → 4  อย่าข้าม
     4. ก่อนกด ▶ ทุกครั้ง เขียนคำทายลงใบงานก่อน
   ============================================================ */
#include "lab11.h"

#define STEP 0      /* <<<< เปลี่ยนเลขขั้นที่จะรัน 0 1 2 3 4 5 */

void setup()
{
    Serial.begin(115200);
    delay(200);
    Serial.printf("\n=== Lab 11  STEP %d  รหัส %lu  MY_FREQ = %lu Hz ===\n",
                  STEP, (unsigned long)STUDENT_ID, (unsigned long)MY_FREQ);
    for (int i = 0; i < LED_COUNT; i++) pinMode(LED_BASE + i, OUTPUT);
    pinMode(ALARM_PIN, OUTPUT);

#if   STEP == 0
    step0_setup();
#elif STEP == 1
    step1_setup();
#elif STEP == 2
    step2_setup();
#elif STEP == 3
    step3_setup();
#elif STEP == 4
    step4_setup();
#elif STEP == 5
    step5_setup();
#endif
}

void loop()
{
#if   STEP == 0
    step0_loop();
#elif STEP == 1
    step1_loop();
#elif STEP == 2
    step2_loop();
#elif STEP == 3
    step3_loop();
#elif STEP == 4
    step4_loop();
#elif STEP == 5
    step5_loop();
#endif
}
