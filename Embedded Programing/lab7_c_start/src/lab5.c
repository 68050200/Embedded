/* ============================================================
   Lab 5 : function pointer - เก็บ "ฟังก์ชัน" ไว้ในตัวแปร
   ------------------------------------------------------------
   ใน Python เราทำแบบนี้ได้อยู่แล้วโดยไม่รู้ตัว:
       def to_f(c): return c * 9 / 5 + 32
       f = to_f            # เก็บฟังก์ชันไว้ในตัวแปร
       print(f(100))
       table = {"F": to_f, "K": to_k}

   ภาษา C ทำได้เหมือนกัน เพียงแต่ต้องบอกชนิดให้ครบว่า
   "ตัวชี้ไปยังฟังก์ชันที่รับ float แล้วคืน float"
   ============================================================ */

#include <stdio.h>
#include "labs.h"

/* ---------- ส่วนที่ 1 : ตัวอย่างให้อ่านและรัน ---------- */

static float toFahrenheit(float c) { return c * 9.0f / 5.0f + 32.0f; }
static float toKelvin(float c)     { return c + 273.15f; }
static float noChange(float c)     { return c; }

/* อ่านจากในวงเล็บออกนอก :
   Converter คือ ตัวชี้(*) ไปยังฟังก์ชันที่รับ (float) และคืน float */
typedef float (*Converter)(float);

/* ฟังก์ชันที่รับ "ฟังก์ชันอื่น" เข้ามาทำงานให้ เรียกว่ารับ callback */
static void applyToAll(const float *in, float *out, int n, Converter fn)
{
    for (int i = 0; i < n; i++) {
        out[i] = fn(in[i]);      /* เรียกใช้เหมือนฟังก์ชันธรรมดา */
    }
}
static float toRankine(float c) {
     return (c + 273.15f) * 9.0f / 5.0f; }

void lab5_run(void)
{
    printf("\n===== Lab 5 : function pointer =====\n");

    /* เก็บฟังก์ชันไว้ในตัวแปร แล้วเรียกผ่านตัวแปรนั้น */
    Converter f = toFahrenheit;
    printf("100 C = %.2f F\n", f(100.0f));

    f = toKelvin;                /* สลับไปใช้อีกฟังก์ชันได้ทันที */
    printf("100 C = %.2f K\n", f(100.0f));

    /* ตารางฟังก์ชัน : แทน if-else ยาว ๆ ด้วยการเลือกจาก index
       รูปแบบนี้ใช้บ่อยมากในงานฝังตัว เช่น ตารางคำสั่งที่รับมาทาง UART */
    Converter table[3]     = { noChange, toFahrenheit, toKelvin };
    const char *unitName[3] = { "C", "F", "K" };

    float c = 25.0f;
    for (int i = 0; i < 3; i++) {
        printf("25 C in %s = %.2f\n", unitName[i], table[i](c));
    }

    /* ส่งฟังก์ชันเข้าไปให้ฟังก์ชันอื่นใช้ */
    float in[4]  = {0.0f, 25.0f, 37.0f, 100.0f};
    float out[4];
    applyToAll(in, out, 4, toFahrenheit);
    printf("whole array to Fahrenheit :");
    for (int i = 0; i < 4; i++) printf(" %.1f", out[i]);
    printf("\n");

    /* ---------- ส่วนที่ 2 : ลองทำเอง (ส่วนที่ให้คะแนน) ----------

       TODO 5.1  เขียนฟังก์ชัน  float toRankine(float c)
                 สูตร  R = (c + 273.15) * 9 / 5
                 แล้วเพิ่มเข้าไปใน table ให้มี 4 ช่อง พร้อมชื่อหน่วย "R"

       TODO 5.2  วนพิมพ์ผลของ 25 C ในทั้ง 4 หน่วย
                 (ตรวจคำตอบ : 25 C ควรได้ประมาณ 536.67 R)

       TODO 5.3  เรียก applyToAll กับ toKelvin แล้วพิมพ์ผลทั้ง 4 ค่า
    
       TODO 5.4  ตอบในใบงาน : ถ้าไม่ใช้ตารางฟังก์ชัน ต้องเขียน if-else
                 กี่บรรทัด และเวลาจะเพิ่มหน่วยที่ 5 ต้องแก้กี่จุด
    */
   
        /*5.2*/
   

    /* ---------- ส่วนที่ 3 : โจทย์ท้าทาย ----------

       CHALLENGE 5  สร้าง struct ที่เก็บทั้งชื่อหน่วยและฟังก์ชันไว้ด้วยกัน

                        typedef struct {
                            const char *name;
                            Converter   fn;
                        } Unit;

                    แล้วประกาศ Unit units[] = { {"C", noChange}, ... };
                    วนลูปพิมพ์ทีเดียวจบ  นี่คือรูปแบบ "ตารางคำสั่ง"
                    ที่ใช้ในเฟิร์มแวร์จริงเวลารับคำสั่งจากผู้ใช้
    */
}

/* ============================================================
   ตรวจด้วยตัวเอง  (Lab 5)
   ------------------------------------------------------------
   100 C = 212.00 F      100 C = 373.15 K
   TODO 5.1-5.2  25 C = 77.00 F   298.15 K   536.67 R
   TODO 5.3      Kelvin ทั้งชุด : 273.15  298.15  310.15  373.15
   ============================================================ */
