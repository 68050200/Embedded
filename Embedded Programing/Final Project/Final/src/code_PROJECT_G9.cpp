

/*
===================================================================================

GROUP 9 Final Project : ตู้หยอดเหรียญ
51423364 การเขียนโปรแกรมสำหรับระบบสมองกลฝังตัว

1	นายชิษณุพงศ์ วิเชียรกุล	68050200	
2	นายกิตติภน ภาษีชา	68050392	
3	นายณัชพล วงศ์ยัง	68050393	
4	นายธีรธน จันทบุตร	68050395	


===================================================================================


  1. แก้เฉพาะโซนของตัวเอง ใช้ชื่อฟังก์ชันตาม PROJECT_G9.h ตรงตัว

  2. ห้ามใช้ millis() / delay()  ใช้ tick เท่านั้น (1 tick = TICK_MS = 10 ms)

  3. เงินทอน/เงินคืน: 1 บาท = LED กะพริบ 1 ครั้ง  -> blinkStart(จำนวนบาท)
  
  4. tickPending() เรียกครั้งเดียวต่อรอบ loop ถ้าได้ true ให้เดินตัวนับเวลาทุกตัวของโซน 3
     (E3, E4, E6, กะพริบ) ในฟังก์ชันนั้นเอง

  5. เฟรม UART:  [AA][LEN][SEQ][STATE][BAL_H][BAL_L][PRODUCT][CHK]
     CHK = ผลรวมของ LEN..PRODUCT เก็บ 8 บิต


  6. เข้า FAULT: คืนเงินที่ค้างอยู่ (ถ้ามี) ด้วยการกะพริบ แล้วค้างที่ FAULT จนกด reset

  7. ISR ทำแค่ตั้ง flag/นับ ห้ามพิมพ์ Serial หรือเรียก LCD ใน ISR

 

 
  หมายเหตุ: บรรทัด return ในฟังก์ชันที่คืนค่า เป็นค่าชั่วคราวให้คอมไพล์ผ่าน แก้ตอนเขียนจริง
===================================================================================
*/
 
#include "PROJECT_G9.h"
 
/* ===== โซน 2 : ISR ปุ่ม  =================================
   ISR ปุ่มเหรียญ GPIO13 + ปุ่ม reset GPIO0, debounce, ตั้ง flag
   -> ส่งออก E1 (กดสั้น 1 บาท / กดยาว 5 บาท) และ E7
   ================================================================ */
 
void inputInit(void)
{
    // pinMode(COIN_PIN, INPUT_PULLUP) และ pinMode(RESET_PIN, INPUT_PULLUP)
    // attachInterrupt ทั้งสองขา (CHANGE)
}
 
uint8_t takeCoin(void)
{
    // มีเหรียญรอ: เคลียร์ flag แล้วคืน 1 (กด < COIN_LONG_TICKS) หรือ 5 (กด >= COIN_LONG_TICKS)
    // วัดความยาวการกดเป็น tick (ใช้ tickNow() ของโซน 3) ไม่ใช้ millis()
    // กดค้างถึง FAULT_TICKS ไม่นับเป็นเหรียญ
    // ไม่มีเหรียญ: คืน 0
    return 0;
}
 
bool takeReset(void)
{
    // ISR + debounce ของ GPIO0  คืน true 1 ครั้งต่อการกด
    return false;
}
 
bool coinHeld(void)
{
    // คืน true ถ้าปุ่มเหรียญกำลังถูกกดอยู่ตอนนี้ (อ่านจาก flag ของ ISR)
    return false;
}
 
/* ===== โซน 3 : Timer tick ================================
   hardware timer tick (TICK_MS = 10), จับเวลา E3 (10 s),
   ตรวจกดค้าง E6 (3 s -> FAULT), นับ tick ให้ VEND_TICKS
   และจังหวะกะพริบ LED GPIO4 / LED FAULT GPIO2
   ================================================================ */
 
void timerInit(void)
{
    // timerSetup(TICK_MS * 1000u, onTick)  (ใช้ตัวช่วยใน common.cpp ได้)
    // pinMode(LED_REFUND_PIN, OUTPUT) และ pinMode(LED_FAULT_PIN, OUTPUT) แล้วดับทั้งคู่
}
 
bool tickPending(void)
{
    // ไม่มี tick ใหม่: คืน false
    // มี tick ใหม่: เดินตัวนับทุกตัว (E3, E4, E6 เมื่อ coinHeld(), จังหวะกะพริบ) แล้วคืน true
    return false;
}
 
uint32_t tickNow(void)
{
    // คืนจำนวน tick ตั้งแต่เปิดเครื่อง
    return 0;
}
 
void idleTimerRestart(void)
{
    // เริ่มนับ E3 ใหม่จาก 0 (เรียกทุกครั้งที่เกิด E1)
}
 
bool idleTimeout(void)
{
    // true เมื่อนับครบ TIMEOUT_TICKS (ใช้ใน COUNTING เท่านั้น)
    return false;
}
 
bool coinStuck(void)
{
    // true เมื่อ coinHeld() ต่อเนื่องครบ FAULT_TICKS (ต้องมากกว่า COIN_LONG_TICKS)
    return false;
}
 
void stateTimerRestart(void)
{
    // เริ่มนับเวลาในสถานะ VEND จาก 0
}
 
bool vendDone(void)
{
    // true เมื่อนับครบ VEND_TICKS
    return false;
}
 
void blinkStart(uint8_t times)
{
    // เริ่มกะพริบ LED GPIO4 จำนวน times ครั้ง (ครึ่งคาบ BLINK_TICKS)
}
 
bool blinkDone(void)
{
    // true เมื่อกะพริบครบทุกครั้ง (times = 0 ให้ true ทันที)
    return true;
}
 
void ledFault(bool on)
{
    // เปิด/ปิด LED GPIO2 (LED_FAULT_PIN)
}
 
void ledRefundOff(void)
{
    // ดับ LED GPIO4 และยกเลิกการกะพริบที่ค้าง
}
 
/* ===== โซน 4 : ADC + LCD + UART ==========================
   อ่าน pot GPIO34 (เฉลี่ย + hysteresis) -> สินค้า 4 ช่วง,
   LCD I2C (SDA21/SCL22) ทุกสถานะ, เฟรม UART AA LEN SEQ ... CHK (GPIO26/27)
   MVP: ให้ showXxx พิมพ์ทาง Serial ก่อน แล้วค่อยเปลี่ยนเป็น LCD
   ================================================================ */
 
void adcInit(void)
{
    // ตั้งค่า ADC ของ POT_PIN (ความละเอียด 12 บิต / attenuation ถ้าจำเป็น)
}
 
uint8_t productIndex(void)
{
    // อ่าน POT_PIN เฉลี่ยหลายครั้ง แบ่ง 0–4095 เป็น PRODUCT_COUNT ช่วง
    // ใส่ hysteresis ที่ขอบแต่ละช่วงกันค่าสั่น  คืน 0..PRODUCT_COUNT-1
    return 0;
}
 
void lcdInit(void)
{
    // เริ่ม I2C (I2C_SDA, I2C_SCL, I2C_HZ) และเริ่มจอที่ LCD_ADDR
}
 
void showIdle(void)
{
    // แสดง "Insert coin"
}
 
void showCounting(uint8_t product, uint16_t balance)
{
    // บรรทัดบน: ชื่อสินค้าชิดซ้าย ราคาชิดขวา (PRODUCT_NAME / PRODUCT_PRICE)
    // บรรทัดล่าง: "Coin: xB"
}
 
void showVending(void)
{
    // แสดง "VENDING..."
}
 
void showChange(uint16_t amount)
{
    // แสดงเงินทอน
}
 
void showRefund(uint16_t amount)
{
    // แสดงเงินคืน
}
 
void showFault(void)
{
    // แสดง "ERR"
}
 
void uartInit(void)
{
    // Serial1.begin(115200, SERIAL_8N1, U1_RX, U1_TX)
}
 
void sendStatusFrame(State s, uint16_t balance, uint8_t product)
{
    // ส่ง [AA][LEN][SEQ][STATE][BAL_H][BAL_L][PRODUCT][CHK] ทาง Serial1
    // SEQ เพิ่มทีละ 1 ทุกเฟรม
}
 
/* ===== โซน 1 : FSM   ====================================
   enum State / Event, ตารางสถานะ x เหตุการณ์, go() + log Serial,
   ตัวนับยอด balance, guard E2 (balance >= price), E4, E5, ทอนเงิน
   ================================================================ */
 
/* ตัวแปรที่โซน 1 ต้องมี (ประกาศเป็น static ไว้ตรงนี้):
     state ปัจจุบัน, balance (ยอดที่หยอด), product (สินค้าที่ pot ชี้),
     payback (เงินทอน/คืนที่กำลังจะคืน) */
 
void go(State next)
{
    // log Serial: "[FSM] สถานะเดิม -> สถานะใหม่"
    // เก็บสถานะใหม่ แล้วทำงานตอนเข้าสถานะ:
    //   S_IDLE           : balance = 0, ledRefundOff(), showIdle()
    //   S_COUNTING       : idleTimerRestart(), showCounting(...)
    //   S_VEND           : payback = balance - ราคา, stateTimerRestart(), showVending()
    //   S_CHANGE         : showChange(payback), blinkStart(payback)
    //   S_TIMEOUT_REFUND : payback = balance, showRefund(payback), blinkStart(payback)
    //   S_FAULT          : ledFault(true), คืนเงินที่ค้าง (กฎข้อ 6), showFault()
    // ปิดท้าย: sendStatusFrame(state, balance, product)
}
 
/* ===== setup / loop  (ชิษณุพงศ์) ==================================== */
 
void code_ProjectG9_setup(void)
{
    // 1. inputInit()   ISR ปุ่มเหรียญ GPIO13 + ปุ่ม reset GPIO0      [โซน 2]
    // 2. timerInit()   hardware timer tick + ขา LED GPIO4/GPIO2      [โซน 3]
    // 3. adcInit()     ADC ของ pot                                   [โซน 4]
    // 4. lcdInit()     LCD I2C                                       [โซน 4]
    // 5. uartInit()    UART ส่งเฟรม                                  [โซน 4]
    // 6. ตั้งค่าเริ่มต้นของ FSM: balance = 0, product = 0           [โซน 1]
    // 7. go(S_IDLE)    ต้องอยู่หลัง lcdInit() เพราะแสดง "Insert coin" [โซน 1]
}
 
void code_ProjectG9_loop(void)
{
    // 1. tickPending() ไม่มี tick ให้ออกจากฟังก์ชัน                   [โซน 3]
    // 2. product = productIndex()                                    [โซน 4]
    // 3. รวบรวมเหตุการณ์ตามลำดับความสำคัญ (FAULT ไม่รับ E1/E6):      [โซน 1 เรียกโซน 2, 3]
    //      E7 takeReset()       เฉพาะใน S_FAULT
    //      E6 coinStuck()       ทุกสถานะยกเว้น S_FAULT
    //      E1 takeCoin()        เฉพาะ S_IDLE / S_COUNTING (บวก balance, idleTimerRestart())
    //      E2 balance >= ราคา   ตรวจเฉพาะหลังเกิด E1 เท่านั้น
    //      E3 idleTimeout()     เฉพาะ S_COUNTING
    //      E4 vendDone()        เฉพาะ S_VEND
    //      E5 blinkDone()       เฉพาะ S_CHANGE / S_TIMEOUT_REFUND
    // 4. เปลี่ยนสถานะตามตารางหัวข้อ 6 ของ proposal:                  [โซน 1]
    //      S_IDLE           : E1 -> S_COUNTING          E6 -> S_FAULT
    //      S_COUNTING       : E1 บวกยอด, E2 -> S_VEND, E3 -> S_TIMEOUT_REFUND, E6 -> S_FAULT
    //      S_VEND           : E4 -> S_CHANGE            E6 -> S_FAULT
    //      S_CHANGE         : E5 -> S_IDLE              E6 -> S_FAULT
    //      S_TIMEOUT_REFUND : E5 -> S_IDLE              E6 -> S_FAULT
    //      S_FAULT          : E7 -> S_IDLE
    // 5. อัปเดตจอเมื่อยอดหรือสินค้าเปลี่ยนใน S_COUNTING              [โซน 1, 4]
}
 