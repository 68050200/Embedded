/* ============================================================
   Lab ครั้งที่ 12 — State Machine : ไฟจราจรหน้าทางม้าลาย
   51423364 การเขียนโปรแกรมสำหรับระบบสมองกลฝังตัว
   ------------------------------------------------------------
   เปลี่ยนเลข STEP แล้ว Upload  ทำตามลำดับ 0 → 1 → 2 (→ 3 ส่วนเพิ่มเติม)
   ก่อน Upload ทุกครั้ง เขียนคำทายลงใบงานก่อน
   ============================================================ */
#include "lab12.h"

#define STEP 3      /* <<<< 0 1 2 3 */

void setup()
{
    Serial.begin(115200);
    delay(200);
    Serial.printf("\n=== Lab 12  STEP %d ===\n", STEP);
    lightsInit();
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
#endif
}
