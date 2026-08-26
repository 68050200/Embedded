/* ============================================================
   51423364 การเขียนโปรแกรมสำหรับระบบสมองกลฝังตัว
   ครั้งที่ 7 : struct / union / bit-field / function pointer
   ------------------------------------------------------------
   คาบนี้ยังไม่ใช้บอร์ด โปรแกรมทั้งหมดรันบนคอมพิวเตอร์ของเราเอง
   ผ่าน PlatformIO ที่ติดตั้งไว้แล้วตั้งแต่สัปดาห์ที่ 6

   วิธีใช้
     1. แก้ตัวเลขในบรรทัด RUN_LAB ข้างล่างให้ตรงกับ Lab ที่กำลังทำ
     2. กดปุ่ม Build แล้ว Upload ที่แถบล่างของ VS Code
        (สำหรับ env native ปุ่ม Upload คือการ "สั่งรันโปรแกรม")
        หรือพิมพ์ในเทอร์มินัลว่า  pio run -t exec
     3. ผลลัพธ์จะขึ้นในหน้าต่างเทอร์มินัลด้านล่างทันที ไม่ต้องเปิด Serial Monitor

   ใส่ 0 เพื่อรันทุก Lab ต่อกันในรอบเดียว
   ============================================================ */

#define RUN_LAB 0        /* <<<<<< แก้ตัวเลขตรงนี้ (0 ถึง 6) */

#include <stdio.h>
#include <stdlib.h>
#include "labs.h"

int main(int argc, char **argv)
{
    /* ถ้าสั่งจากเทอร์มินัลแล้วใส่เลขต่อท้าย จะใช้เลขนั้นแทนค่า RUN_LAB */
    int which = (argc > 1) ? atoi(argv[1]) : RUN_LAB;

    printf("=========================================\n");
    printf(" 51423364 - Lab 7\n");
    printf(" struct / union / bit-field / func ptr\n");
    printf("=========================================\n");

    switch (which) {
        case 1: lab1_run(); break;
        case 2: lab2_run(); break;
        case 3: lab3_run(); break;
        case 4: lab4_run(); break;
        case 5: lab5_run(); break;
        case 6: challenge_run(); break;
        case 0:
            lab1_run(); lab2_run(); lab3_run();
            lab4_run(); lab5_run(); challenge_run();
            break;
        default:
            printf("RUN_LAB must be 0 to 6\n");
            break;
    }

    printf("\n--- end of run ---\n");
    return 0;
}
