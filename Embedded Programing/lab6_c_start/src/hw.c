/* ============================================================
   LAB 4 : ชนิดข้อมูลและขนาดจริง  <- หัวใจของงานฝังตัว
   วิธีรัน: เลือก env:lab4_datatype ที่แถบล่าง -> กด Upload
   ============================================================ */

#include <stdio.h>
#include <stdint.h>     /* ต้อง include เพื่อใช้ uint8_t, int16_t ฯลฯ */

void print_binary(uint8_t v) {
    for (int i = 7; i >= 0; i--) {
        printf("%d", (v >> i) & 1);
    }
}

int sum_range(int start, int end) {
    int sum = 0;
    for (int i = start; i <= end; i++) {
        sum += i;
    }
    return sum;
}
uint8_t set_bit(uint8_t reg, uint8_t pos) {
    reg |= (1 << pos);
    return reg;
}

uint8_t clear_bit(uint8_t reg, uint8_t pos) {
    reg &= ~(1 << pos);
    return reg;
}


int main(void) {

    printf("sum_range(1,5) = %d\n",sum_range(1,5));


    print_binary(0b00000000);
    printf("\n");
    uint8_t reg1 = (set_bit(0b00000000,5));
    printf("set_bit(0b00000000,5) = "); print_binary(reg1); printf(" -> %u\n", reg1);

    uint8_t reg2 = (clear_bit(0b11111111,5));
    printf("clear_bit(0b00011111,5) = "); print_binary(reg2); printf(" -> %u\n", reg2);

    return 0;

}
