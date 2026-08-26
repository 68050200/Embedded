/* ============================================================
   โจทย์ท้าทายรวม : Mini Data Logger
   ------------------------------------------------------------
   สำหรับคนที่ทำ Lab 1-5 เสร็จก่อนเวลา
   งานนี้ใช้ทั้ง struct + array of struct + bit-field + function pointer
   พร้อมกันในโปรแกรมเดียว เหมือนที่เขียนกันจริงในเฟิร์มแวร์

   โครงร่างเตรียมไว้ให้แล้ว หน้าที่ของนิสิตคือเติมส่วนที่เขียนว่า TODO
   ============================================================ */

#include <stdio.h>
#include <stdint.h>
#include "labs.h"

/* สถานะของแต่ละจุดวัด บีบให้เหลือ 1 ไบต์ด้วย bit-field */
typedef struct {
    uint8_t online   : 1;   /* ออนไลน์อยู่หรือไม่           */
    uint8_t alarm    : 1;   /* เกินค่าเตือนหรือไม่          */
    uint8_t sensorId : 3;   /* หมายเลขเซนเซอร์ 0-7          */
    uint8_t quality  : 3;   /* คุณภาพสัญญาณ 0-7             */
} NodeStatus;

typedef struct {
    float      temp;        /* องศาเซลเซียส */
    NodeStatus st;
} Node;

typedef float (*Converter)(float);

static float toF(float c) { return c * 9.0f / 5.0f + 32.0f; }

/* ---------- TODO A ----------
   เขียนฟังก์ชัน
       int countAlarm(const Node *arr, int n)
   นับว่ามีกี่จุดที่ st.alarm เป็น 1
   -------------------------------------------------- */


/* ---------- TODO B ----------
   เขียนฟังก์ชัน
       void raiseAlarms(Node *arr, int n, float limit)
   ถ้า temp ของจุดใดเกิน limit ให้ตั้ง st.alarm = 1
   -------------------------------------------------- */


/* ---------- TODO C ----------
   เขียนฟังก์ชัน
       void report(const Node *arr, int n, Converter fn, const char *unit)
   พิมพ์รายงานทุกจุด โดยแปลงอุณหภูมิด้วย fn ก่อนพิมพ์
   รูปแบบที่ต้องการ เช่น
       [id 3] 31.5 C  online=1 alarm=0 quality=6
   -------------------------------------------------- */


void challenge_run(void)
{
    printf("\n===== Challenge : Mini Data Logger =====\n");

    Node net[5] = {
        { 28.4f, {1, 0, 0, 6} },
        { 35.9f, {1, 0, 1, 5} },
        { 22.1f, {0, 0, 2, 2} },
        { 41.2f, {1, 0, 3, 7} },
        { 30.0f, {1, 0, 4, 4} },
    };
    int n = 5;

    printf("sizeof(NodeStatus) = %d bytes   sizeof(Node) = %d bytes\n",
           (int)sizeof(NodeStatus), (int)sizeof(Node));

    /* เมื่อเขียน TODO A-C เสร็จ ให้ลบเครื่องหมายคอมเมนต์ข้างล่างออก
       ผลที่ควรได้ : เกิน 35.0 มี 2 จุด คือ id 1 (35.9) และ id 3 (41.2)

    raiseAlarms(net, n, 35.0f);
    printf("nodes in alarm = %d\n", countAlarm(net, n));
    report(net, n, toF, "F");
    */

    (void)net; (void)n; (void)toF;   /* กันคอมไพเลอร์เตือนก่อนเติมโค้ด */
}

/* ============================================================
   ตรวจด้วยตัวเอง  (โจทย์ท้าทายรวม)
   ------------------------------------------------------------
   sizeof(NodeStatus) = 1 byte    sizeof(Node) = 8 bytes
   nodes in alarm = 2             (id 1 ที่ 35.9 และ id 3 ที่ 41.2)
   รายงานต้องมี 5 บรรทัด เรียงตาม id 0 ถึง 4
   ค่าที่แปลงเป็น F :  83.1   96.6   71.8   106.2   86.0
   ============================================================ */
