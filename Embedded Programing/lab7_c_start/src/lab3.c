/* ============================================================
   Lab 3 : union - ข้อมูลก้อนเดียว มองได้หลายมุม
   ------------------------------------------------------------
   struct = ทุกฟิลด์มีที่อยู่ของตัวเอง  ขนาด = ผลรวมของทุกฟิลด์
   union  = ทุกฟิลด์ "ทับที่กัน"        ขนาด = ฟิลด์ที่ใหญ่ที่สุด

   คาบนี้จะได้เห็นของจริงว่า float 4 ไบต์ที่เราเรียนเรื่อง IEEE 754
   ไปเมื่อสัปดาห์ที่ 5 นั้น หน้าตาระดับบิตเป็นอย่างไร
   ============================================================ */

#include <stdio.h>
#include <stdint.h>
#include "labs.h"

/* ---------- ส่วนที่ 1 : ตัวอย่างให้อ่านและรัน ---------- */

typedef union {
    float    f;      /* มองก้อน 4 ไบต์นี้เป็นจำนวนจริง   */
    uint32_t u;      /* มองก้อนเดิมเป็นจำนวนเต็มไม่มีเครื่องหมาย */
    uint8_t  b[4];   /* มองก้อนเดิมเป็นไบต์ 4 ตัว        */
} FloatView;

/* พิมพ์เลขฐานสองของ 32 บิต โดยเว้นวรรคตามโครงสร้าง IEEE 754
   1 บิตเครื่องหมาย | 8 บิตเลขชี้กำลัง | 23 บิตส่วนเศษ */
static void printBits32(uint32_t v)
{
    for (int i = 31; i >= 0; i--) {
        printf("%d", (int)((v >> i) & 1u));
        if (i == 31 || i == 23) printf(" ");
    }
    printf("\n");
}

static float bytesToFloat(uint8_t b0, uint8_t b1, uint8_t b2, uint8_t b3) {
      FloatView v;
      v.b[0] = b0;
      v.b[1] = b1;
      v.b[2] = b2;
      v.b[3] = b3;
      return v.f;
   }

void lab3_run(void)
{
    printf("\n===== Lab 3 : union =====\n");

    FloatView v;
    v.f = 3.14f;                 /* เขียนเข้าไปในมุมมอง float */

    printf("v.f = %.6f\n", v.f);
    printf("v.u = %u   (hex 0x%08X)\n", v.u, v.u);   /* อ่านออกมาอีกมุม */
    printf("all 32 bits : ");
    printBits32(v.u);
    printf("bytes in memory   : %02X %02X %02X %02X\n",
           v.b[0], v.b[1], v.b[2], v.b[3]);
    printf("(bytes look reversed : this machine is little-endian)\n");

    printf("sizeof(FloatView) = %d bytes   ",   (int)sizeof(FloatView));
    printf("(a struct with the same 3 fields would be much bigger)\n");

    /* ระวัง : union เก็บได้ทีละมุมมองเท่านั้น
       เขียน u ทับแล้ว ค่าเดิมใน f ก็หายไปด้วย เพราะเป็นที่เดียวกัน */
    v.u = 0x40490FDB;
    printf("set v.u = 0x40490FDB  then v.f reads %.6f\n", v.f);

    /* ---------- ส่วนที่ 2 : ลองทำเอง (ส่วนที่ให้คะแนน) ----------

       TODO 3.1  กำหนด v.f = 1.0f แล้วพิมพ์ v.u เป็นฐานสิบหก
                 จดคำตอบลงใบงาน  (ควรได้ 0x3F800000)*/
      v.f = 1.0f;
      printf("v.u ในฐานสิบหก คือ 0x%08X\n", v.u);

       /*TODO 3.2  ใช้ bitwise ที่เรียนไปสัปดาห์ที่แล้ว แกะค่าจาก v.u ของ 3.14f
                     sign     = บิตที่ 31            -> (v.u >> 31) & 0x1
                     exponent = 8 บิตถัดมา (23-30)   -> เขียนเอง
                     mantissa = 23 บิตล่าง           -> เขียนเอง
                 พิมพ์ทั้งสามค่าออกมา*/
      v.f = 3.14f; 
      uint16_t sign     = (v.u >> 31) & 0x1; 
      uint16_t exponent = (v.u >> 23) & 0xFF;
      uint32_t mantissa = v.u & 0x7FFFFF;
      printf("sign = %u exponent = %u mantissa = 0x%06X\n", sign, exponent, mantissa);

       /*TODO 3.3  ตรวจคำตอบ : exponent ที่ได้ ลบ 127 แล้วควรเท่ากับ 1
                 เพราะ 3.14 อยู่ในช่วง 2 ถึง 4  ตอบในใบงานว่าใช่หรือไม่*/
      int result = exponent - 127;
      printf("exponent - 127 =%d \n", result);
       /*TODO 3.4  ตอบในใบงาน : ทำไม sizeof(FloatView) จึงเป็น 4 ไม่ใช่ 12*/
      printf("sizeof(FloatView) = %d\n", (int)sizeof(FloatView));


    /* ---------- ส่วนที่ 3 : โจทย์ท้าทาย ----------

       CHALLENGE 3  เขียนฟังก์ชัน  float bytesToFloat(uint8_t b0, uint8_t b1,
                                                      uint8_t b2, uint8_t b3)
                    ที่ประกอบ 4 ไบต์กลับเป็น float ด้วย union
                    นี่คือสิ่งที่ต้องทำจริงตอนรับค่าจากเซนเซอร์ผ่าน I2C
                    ซึ่งส่งมาทีละไบต์  (จะได้ใช้ในสัปดาห์ที่ 13)
    */
   
    float f = bytesToFloat(0xC3,0xF5,0x48,0x40);
    printf("bytesToFloat = %.6f\n", f);
}

/* ============================================================
   ตรวจด้วยตัวเอง  (Lab 3)
   ------------------------------------------------------------
   v.u ของ 3.14f       = 0x4048F5C3
   all 32 bits         = 0 10000000 10010001111010111000011
   sizeof(FloatView)   = 4 bytes
   TODO 3.1  1.0f      -> 0x3F800000
   TODO 3.2  sign = 0   exponent = 128   mantissa = 0x48F5C3
   TODO 3.3  128 - 127 = 1  ถูกต้อง เพราะ 3.14 อยู่ระหว่าง 2 กับ 4
   ============================================================ */
