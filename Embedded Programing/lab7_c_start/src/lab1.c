/* ============================================================
   Lab 1 : struct - จับข้อมูลหลายชนิดมัดรวมเป็นก้อนเดียว
   ------------------------------------------------------------
   Python ที่เราเคยเขียน:
       reading = {"id": 1, "temp": 28.5, "humid": 65.0}
       print(reading["temp"])

   ภาษา C ต้องบอกล่วงหน้าว่าก้อนนี้มีอะไรบ้าง และแต่ละอันชนิดใด
   ============================================================ */

#include <stdio.h>
#include "labs.h"
#include <string.h>
/* ---------- ส่วนที่ 1 : ตัวอย่างให้อ่านและรัน ---------- */

/* ประกาศ "พิมพ์เขียว" ของก้อนข้อมูล 1 ชุด
   typedef ทำให้เรียกสั้น ๆ ว่า SensorReading โดยไม่ต้องพิมพ์ struct ทุกครั้ง */
typedef struct {
    int   id;      /* หมายเลขเซนเซอร์      */
    float temp;    /* อุณหภูมิ (องศาเซลเซียส) */
    float humid;   /* ความชื้นสัมพัทธ์ (%)   */
} SensorReading;

typedef struct {
    int   id;      /* หมายเลขเซนเซอร์      */
    float temp;    /* อุณหภูมิ (องศาเซลเซียส) */
    float humid;   /* ความชื้นสัมพัทธ์ (%)   */
    int battery;
} SensorReading1;

typedef struct {
    SensorReading reading;
    char name[16];
} Station;

void lab1_run(void)
{
    printf("\n===== Lab 1 : struct =====\n");

    /* สร้างตัวแปรจากพิมพ์เขียว แล้วกำหนดค่าทีละฟิลด์ด้วยจุด (.) */
    SensorReading a;
    a.id    = 1;
    a.temp  = 28.5f;
    a.humid = 65.0f;

    /* หรือกำหนดค่าตอนประกาศเลย เรียงตามลำดับฟิลด์ */
    SensorReading b = {2, 30.2f, 58.0f};

    printf("A -> id=%d temp=%.1f humid=%.1f\n", a.id, a.temp, a.humid);
    printf("B -> id=%d temp=%.1f humid=%.1f\n", b.id, b.temp, b.humid);

    /* struct ทั้งก้อนคัดลอกกันได้ด้วยเครื่องหมาย = เดียว
       (ต่างจาก Python ที่ dict จะอ้างถึงก้อนเดิม ไม่ได้ก๊อป) */
    SensorReading c = a;
    c.temp = 99.9f;
    printf("After  C = A  then editing C :  a.temp=%.1f   c.temp=%.1f\n",
           a.temp, c.temp);

    printf("sizeof(SensorReading) = %d bytes\n", (int)sizeof(SensorReading));

    /* ---------- ส่วนที่ 2 : ลองทำเอง (ส่วนที่ให้คะแนน) ----------

       TODO 1.1  เพิ่มฟิลด์ int battery; เข้าไปใน SensorReading ข้างบน
       TODO 1.2  ประกาศตัวแปร SensorReading d ที่มี
                 id = รหัสนิสิต 2 ตัวท้ายของตัวเอง
                 temp = 25.0, humid = 70.0, battery = 88
       TODO 1.3  พิมพ์ค่าทุกฟิลด์ของ d ออกทางหน้าจอ
       TODO 1.4  พิมพ์ sizeof(SensorReading) อีกครั้ง แล้วตอบในใบงานว่า
                 ขนาดเปลี่ยนไปกี่ไบต์ และเพราะอะไร
    */
    
    /* เขียนโค้ดของ TODO 1.2 - 1.4 ต่อจากบรรทัดนี้ */
    SensorReading1 d;
    d.id = 00;
    d.temp = 25.0f;
    d.humid = 70.0f;
    d.battery = 88;
    printf("d -> id=%d temp=%.1f humid=%.1f battery=%d\n", d.id, d.temp, d.humid, d.battery);
    printf("sizeof(SensorReading) = %d bytes\n", (int)sizeof(SensorReading1));

    /* ---------- ส่วนที่ 3 : โจทย์ท้าทาย ----------

       CHALLENGE 1  ประกาศ struct ชื่อ Station ที่ "ข้างใน" มี
                    SensorReading อยู่ 1 ตัว บวกกับ char name[16]
                    แล้วเข้าถึงค่าอุณหภูมิผ่านสองชั้น เช่น st.reading.temp
    */
    Station st;
    strcpy(st.name, "UNA");
    st.reading.id      = 7;
    st.reading.temp    = 32.4f;
    st.reading.humid   = 60.5f;
     printf("Name= %s :id=%d temp=%.1f humid=%.1f \n",
         st.name,
         st.reading.id,
         st.reading.temp,
         st.reading.humid
     );
}

/* ============================================================
   ตรวจด้วยตัวเอง  (Lab 1)
   ------------------------------------------------------------
   ก่อนเพิ่ม battery   sizeof(SensorReading) = 12 bytes
   หลังเพิ่ม battery   sizeof(SensorReading) = 16 bytes
   บรรทัด After C = A  ต้องได้  a.temp=28.5   c.temp=99.9
   ถ้าได้ a.temp=99.9 แปลว่าเข้าใจผิดว่า struct อ้างถึงก้อนเดิม
   ============================================================ */
