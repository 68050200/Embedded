/* ============================================================
   Lab ครั้งที่ 13 — UART และ I2C : บอร์ดคุยกับตัวเอง
   51423364 การเขียนโปรแกรมสำหรับระบบสมองกลฝังตัว
   ------------------------------------------------------------
   1. แก้ GROUP_NO ใน lab13.h เป็นเลขกลุ่ม
   2. เปลี่ยนเลข STEP แล้ว Upload  ทำตามลำดับ 0 → 1 → 2 → 3 (→ 4 ส่วนเพิ่มเติม)
   3. ก่อน Upload ทุกครั้ง เขียนคำทายลงใบงานก่อน
   Serial Monitor 115200  (STEP 1 คลิกในหน้าต่าง Monitor แล้วพิมพ์ กด Enter)
   ============================================================ */
#include "lab13.h"

#define STEP 4      /* <<<< 0 1 2 3 4 */

void setup()
{
    Serial.begin(115200);
    delay(200);
    Serial.printf("\n=== Lab 13  STEP %d  กลุ่ม %d ===\n", STEP, GROUP_NO);
    barInit();
    pwmInit();
    buttonInit();
    tickInit();
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
#endif
}
