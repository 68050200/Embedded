/* ============================================================
   Lab 4 : bit-field - บอกตรง ๆ ว่าฟิลด์นี้ขอกี่บิต
   ------------------------------------------------------------
   บนไมโครคอนโทรลเลอร์ หน่วยความจำมีจำกัด การเก็บสถานะเปิด/ปิด
   ด้วย int ขนาด 4 ไบต์ต่อค่า เป็นการใช้ที่เปลืองมาก

   bit-field ให้เราเขียน  uint8_t power : 1;  แปลว่าฟิลด์นี้ขอแค่ 1 บิต
   ============================================================ */

#include <stdio.h>
#include <stdint.h>
#include "labs.h"

/* ---------- ส่วนที่ 1 : ตัวอย่างให้อ่านและรัน ---------- */

/* แบบเปลือง : ทุกฟิลด์กินคนละ 4 ไบต์ */
typedef struct {
    int power;      /* 0 หรือ 1        */
    int error;      /* 0 หรือ 1        */
    int mode;       /* 0 ถึง 3         */
    int level;      /* 0 ถึง 15        */
} StatusFat;

/* แบบประหยัด : รวมกันแล้วใช้ 1+1+2+4 = 8 บิต พอดีหนึ่งไบต์ */
typedef struct {
    uint8_t power : 1;
    uint8_t error : 1;
    uint8_t mode  : 2;
    uint8_t level : 4;
} StatusSlim;

typedef struct {
    uint8_t red : 1;
    uint8_t green : 1;
    uint8_t blue : 1;
    uint8_t bright : 5;
} LedPanel;
/* ตัวอย่างเรื่อง padding : ลำดับการประกาศมีผลต่อขนาดจริง */
typedef struct { char a; int b; char c; } Loose;   /* เรียงสลับ */
typedef struct { char a; char c; int b; } Tight;   /* จัดกลุ่ม  */

void lab4_run(void)
{
    printf("\n===== Lab 4 : bit-field =====\n");

    printf("sizeof(StatusFat)  = %d bytes\n", (int)sizeof(StatusFat));
    printf("sizeof(StatusSlim) = %d bytes\n", (int)sizeof(StatusSlim));

    StatusSlim s;
    s.power = 1;
    s.error = 0;
    s.mode  = 2;      /* 2 บิตเก็บได้ 0-3 */
    s.level = 9;      /* 4 บิตเก็บได้ 0-15 */

    printf("power=%d error=%d mode=%d level=%d\n",
           s.power, s.error, s.mode, s.level);

    /* จุดที่ต้องระวัง : ใส่ค่าเกินพิสัยของบิต ค่าจะถูกตัดทิ้ง เหลือเฉพาะบิตล่าง
       กรณีที่เขียนค่าคงที่ตรง ๆ แบบข้างล่างนี้ คอมไพเลอร์จะขึ้น warning ให้
       แต่ถ้าค่ามาจากตัวแปรตอนโปรแกรมทำงาน จะถูกตัดเงียบ ๆ โดยไม่เตือนเลย */
    uint8_t wanted = 7;
    s.mode = wanted & 0x3;   /* กันพลาดด้วยการ mask เองก่อนเสมอ */
    s.mode = wanted;         /* บรรทัดนี้คือของจริงที่จะโดนตัด */
    printf("set mode = 7  then it reads back %d   (only 2 bits kept)\n",
           s.mode);

    printf("sizeof(Loose) = %d bytes    sizeof(Tight) = %d bytes\n",
           (int)sizeof(Loose), (int)sizeof(Tight));
    printf("same fields, only the declaration order differs\n");

    /* ---------- ส่วนที่ 2 : ลองทำเอง (ส่วนที่ให้คะแนน) ----------

       TODO 4.1  ประกาศ struct ชื่อ LedPanel ที่ใช้ bit-field เก็บ
                     red    1 บิต
                     green  1 บิต
                     blue   1 บิต
                     bright 5 บิต   (ความสว่าง 0-31)
                 แล้วพิมพ์ sizeof(LedPanel) ควรได้ 1 ไบต์*/
    printf("sizeof(LedPanel) = %d bytes\n",(int)sizeof(LedPanel));
       /*TODO 4.2  สร้างตัวแปร LedPanel p ตั้งค่าให้เป็นสีม่วง (แดง+น้ำเงินติด)
                 ความสว่าง 20  แล้วพิมพ์ทุกฟิลด์ออกมา*/
    LedPanel p;
    p.red = 1;
    p.green = 0;
    p.blue = 1;
    printf("TODO 4.2 p: red=%u green=%u blue=%u bright=%u\n",
       p.red, p.green, p.blue, p.bright);
       /*TODO 4.3  ลองตั้ง p.bright = 40 แล้วอ่านกลับ จดค่าที่ได้ลงใบงาน
                 พร้อมอธิบายว่าทำไมจึงได้ค่านั้น*/
    p.bright = 40; /*ได้ 8 เพราะ เกิน 5 บิต*/
    printf("TODO 4.3 p: red=%u green=%u blue=%u bright=%u\n",
       p.red, p.green, p.blue, p.bright);
       /*TODO 4.4  ตอบในใบงาน : ถ้าต้องเก็บสถานะแบบนี้ของอุปกรณ์ 1000 ตัว
                 แบบ StatusFat กับ StatusSlim ใช้หน่วยความจำต่างกันกี่ไบต์

                 
    */


    /* ---------- ส่วนที่ 3 : โจทย์ท้าทาย ----------

       CHALLENGE 4  ทำสิ่งเดียวกับ StatusSlim แต่ใช้ uint8_t ตัวเดียว
                    บวกกับ bitwise ที่เรียนสัปดาห์ที่แล้ว
                    เขียนฟังก์ชัน setMode / getMode ด้วย << >> & | ~
                    แล้วเทียบว่าวิธีไหนอ่านง่ายกว่ากัน และวิธีไหนคุมได้แน่นอนกว่า
                    (คำใบ้ : มาตรฐาน C ไม่ได้กำหนดว่า bit-field เรียงจากบิตซ้าย
                     หรือขวา ถ้าต้องคุยกับฮาร์ดแวร์จริง bitwise ปลอดภัยกว่า)
    */
}

/* ============================================================
   ตรวจด้วยตัวเอง  (Lab 4)
   ------------------------------------------------------------
   sizeof(StatusFat)  = 16 bytes      sizeof(StatusSlim) = 1 byte
   set mode = 7  อ่านกลับได้ 3        (7 mod 4)
   sizeof(Loose) = 12 bytes           sizeof(Tight) = 8 bytes
   TODO 4.1  sizeof(LedPanel) = 1 byte
   TODO 4.3  bright = 40 อ่านกลับได้ 8   (40 mod 32)
   TODO 4.4  1000 ตัว : 16000 ไบต์ เทียบ 1000 ไบต์ ต่างกัน 15000 ไบต์
   ============================================================ */
