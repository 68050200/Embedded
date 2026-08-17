/* ============================================================
   LAB 3 : ฟังก์ชัน
   วิธีรัน: เลือก env:lab3_function ที่แถบล่าง -> กด Upload
   ============================================================ */

#include <stdio.h>

/* ------------------------------------------------------------
   [1] ตัวอย่าง
   ------------------------------------------------------------
   Python : def square(x):        C : int square(int x) {
                return x * x              return x * x;
                                      }
   หมายเหตุ: C ต้องบอก 2 อย่าง
     - ชนิดของค่าที่ "คืนกลับ"  (int ตัวหน้า)
     - ชนิดของ "พารามิเตอร์"    (int x)
   และต้องประกาศฟังก์ชัน "ก่อน" main() เสมอ
*/

int square(int x) {
    return x * x;
}

/* void = ไม่คืนค่า | (void) = ไม่รับพารามิเตอร์ */
void say_hello(void) {
    printf("สวัสดีจากฟังก์ชัน!\n");
}

/* ฟังก์ชันรับ 2 พารามิเตอร์ */
int add(int a, int b) {
    return a + b;
}


/* ------------------------------------------------------------
   [2] ลองทำเอง  -- เขียนฟังก์ชันของคุณตรงนี้ (เหนือ main)
   ------------------------------------------------------------ */

/* TODO 3.1 : เขียนฟังก์ชัน int max_of(int a, int b)
              คืนค่าที่มากกว่าระหว่าง a กับ b                    */

int max_of(int a, int b) {
    if (a>b) {
        return a;
    } else {
        return b;
    }
}

/* TODO 3.2 : เขียนฟังก์ชัน int is_even(int n)
              คืน 1 ถ้า n เป็นเลขคู่ คืน 0 ถ้าเป็นเลขคี่          */
int is_even(int n) {
    if (n % 2 == 0) {
        return 1;
    } else {
        return 0;
    }
}

/* TODO 3.3 : เขียนฟังก์ชัน void print_line(int n)
              พิมพ์เครื่องหมาย - จำนวน n ตัวแล้วขึ้นบรรทัดใหม่     */
void print_line(int n) {
    for (int i = 1; i <= n; i++) {
        printf("-");
    }
    printf("\n");
}

/* ------------------------------------------------------------
   [3] ท้าทาย
   ------------------------------------------------------------ */

/* TODO 3.4 : เขียนฟังก์ชัน int factorial(int n)
              คืนค่า n! เช่น factorial(5) = 120                  */
int factorial(int n) {
    int fac = 1;
    for (int f = 1; f <= n; f++ ) {
        fac *= f;
    }
    return fac;
}

int main(void) {
    printf("--- [1] ตัวอย่าง ---\n");
    printf("square(5) = %d\n", square(5));
    printf("add(3, 4) = %d\n", add(3, 4));
    say_hello();

    printf("\n--- [2] ลองทำเอง ---\n");
    /* เมื่อเขียนฟังก์ชันเสร็จแล้ว ให้ลบ comment บรรทัดล่างเพื่อทดสอบ */

    /* printf("max_of(10, 25) = %d\n", max_of(10, 25)); */
    printf("max_of(10, 25) = %d\n", max_of(10, 25));
    /* printf("is_even(8) = %d\n", is_even(8)); */
    printf("is_even(8) = %d\n", is_even(8));
    /* print_line(20); */
    print_line(20);

    printf("\n--- [3] ท้าทาย ---\n");
    /* printf("factorial(5) = %d\n", factorial(5)); */
    printf("factorial(5) = %d\n", factorial(5));
    return 0;
}
