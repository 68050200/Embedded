/* ============================================================
   Lab 2 : struct + ฟังก์ชัน + พอยน์เตอร์  ( . กับ -> )
   ------------------------------------------------------------
   ประเด็นสำคัญของคาบนี้:
     ส่ง struct เข้าฟังก์ชันแบบ "ค่า"   -> ได้สำเนา แก้ข้างในไม่กระทบตัวจริง
     ส่ง struct เข้าฟังก์ชันแบบ "ที่อยู่" -> แก้ตัวจริงได้ และไม่เสียเวลาคัดลอก
   ============================================================ */

#include <stdio.h>
#include "labs.h"

typedef struct {
    int   id;
    float temp;
    float humid;
} Reading;

/* ---------- ส่วนที่ 1 : ตัวอย่างให้อ่านและรัน ---------- */

/* รับสำเนา : ข้างในแก้ได้ แต่ของจริงข้างนอกไม่เปลี่ยน */
static void tryEditByValue(Reading r)
{
    r.temp = 0.0f;
    printf("  (inside tryEditByValue : the copy became %.1f)\n", r.temp);
}

/* รับที่อยู่ : แก้ของจริง ใช้ -> แทน . เพราะ r เก็บ "ที่อยู่" ไม่ใช่ตัวก้อน
   (r->temp มีค่าเท่ากับ (*r).temp เขียนแบบลูกศรอ่านง่ายกว่า) */
static void editByPointer(Reading *r)
{
    r->temp = 0.0f;
}

/* const Reading * = สัญญาว่าจะอ่านอย่างเดียว ไม่แก้ของผู้เรียก
   เป็นมารยาทที่ควรติดตัวไว้ตั้งแต่ตอนนี้ */
static void printReading(const Reading *r)
{
    printf("  id=%d  temp=%6.1f  humid=%5.1f %%\n",
           r->id, r->temp, r->humid);
}

static float maxTemp(const Reading *arr, int n) {
        float m = arr[0].temp;          
    for (int i = 1; i < n; i++) { /*เช็คตัวไหนมากกว่า ถ้ามากกว่าเก็บต่าไว้*/
        if (arr[i].temp > m) {
            m = arr[i].temp;
        }
    }
    return m;
    }

static void toFahrenheit(Reading *r) { 
    r->temp = r->temp * 9.0f / 5.0f + 32.0f; 
} 

static void toFahrenheit2(Reading r) 
{
    r.temp = r.temp * 9.0f / 5.0f + 32.0f;
}
static void sortByTemp(Reading *arr, int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - 1 - i; j++) {
            if (arr[j].temp < arr[j + 1].temp) {
                Reading tmp = arr[j]; 
                arr[j] = arr[j + 1];
                arr[j + 1] = tmp;
            }
        }
    }
}

void lab2_run(void)
{
    printf("\n===== Lab 2 : struct + pointer =====\n");

    Reading x = {7, 31.5f, 60.0f};

    tryEditByValue(x);
    printf("after tryEditByValue : temp = %.1f   (unchanged)\n", x.temp);

    editByPointer(&x);              /* & คือ "เอาที่อยู่ของ x" */
    printf("after editByPointer  : temp = %.1f   (changed)\n", x.temp);

    /* อาเรย์ของ struct : เก็บผลอ่านหลายครั้งไว้ในตัวแปรเดียว */
    Reading log[4] = {
        {1, 28.0f, 65.0f},
        {2, 31.5f, 62.0f},
        {3, 27.2f, 70.0f},
        {4, 33.8f, 55.0f},
    };
    int n = 4;

    printf("all %d readings:\n", n);
    for (int i = 0; i < n; i++) {
        printReading(&log[i]);      /* ส่งที่อยู่ของสมาชิกตัวที่ i */
    }

    float sum = 0.0f;
    for (int i = 0; i < n; i++) {
        sum += log[i].temp;         /* log[i] เป็นตัวก้อน จึงใช้จุด */
    }
    printf("average temp = %.2f C\n", sum / n);

    /* ---------- ส่วนที่ 2 : ลองทำเอง (ส่วนที่ให้คะแนน) ----------

       TODO 2.1  เขียนฟังก์ชัน
                     float maxTemp(const Reading *arr, int n)
                 คืนค่าอุณหภูมิสูงสุดในอาเรย์ แล้วเรียกใช้พร้อมพิมพ์ผล
                 (คำตอบที่ถูกคือ 33.8)*/
    
    float mt = maxTemp(log, n);
    printf("max temp = %.1f C\n", mt);
       /*TODO 2.2  เขียนฟังก์ชัน
                     void toFahrenheit(Reading *r)
                 แปลงฟิลด์ temp ของก้อนที่ชี้อยู่ให้เป็นองศาฟาเรนไฮต์
                 สูตร  F = C * 9.0f / 5.0f + 32.0f
                 แล้ววนแปลงทั้งอาเรย์ log พร้อมพิมพ์ผลใหม่*/
    printf("Fahrenheit = ");
    for (int i = 0; i < n; i++) {
        toFahrenheit(&log[i]);
        printf("%.1f  ", log[i].temp); 
    }
    printf("\n");

   printf("Fahrenheit r = ");
    for (int i = 0; i < n; i++) {
        toFahrenheit2(log[i]);           /* ไม่มี & */
        printf("%.1f  ", log[i].temp);
    }
    printf("\n");
    
      /* TODO 2.3  ตอบในใบงาน : ถ้าเปลี่ยน toFahrenheit ให้รับแบบ Reading r
                 (ไม่มีดอกจัน) ผลลัพธ์จะต่างไปอย่างไร เพราะอะไร
    */
    

    /* ---------- ส่วนที่ 3 : โจทย์ท้าทาย ----------

       CHALLENGE 2  เขียน  void sortByTemp(Reading *arr, int n)
                    เรียงข้อมูลจากอุณหภูมิมากไปน้อยด้วย bubble sort
                    ข้อคิด : สลับ struct ทั้งก้อนทำได้ด้วย
                             Reading tmp = arr[i]; arr[i] = arr[j]; arr[j] = tmp;
    */
    sortByTemp(log, n);
    printf("CHALLENGE 2 sortByTemp\n");
    for (int i = 0; i < n; i++) {
        printReading(&log[i]);
    }
}

/* ============================================================
   ตรวจด้วยตัวเอง  (Lab 2)
   ------------------------------------------------------------
   after tryEditByValue : temp = 31.5   (unchanged)
   after editByPointer  : temp = 0.0    (changed)
   average temp = 30.12 C
   TODO 2.1  maxTemp ต้องได้ 33.8
   TODO 2.2  หลังแปลงเป็น F ต้องได้  82.4  88.7  81.0  92.8
   ============================================================ */
