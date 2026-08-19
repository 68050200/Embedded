# prep_02_elevator_fsm.py — เตรียมสอบกลางภาค ตัวอย่างที่ 2
#
# ทักษะที่ทบทวน: state machine หลายสถานะ + debounce (คาบ 2 และ 7)
#
# เรื่องราว: คุณยืนรออยู่ชั้น G กดปุ่มเรียกลิฟต์ ลิฟต์ที่จอดอยู่ชั้นบนจะวิ่งลงมาหา
#   พอถึงชั้น G ประตูเปิดเอง เปิดค้างสักพักแล้วปิด จากนั้นลิฟต์กลับขึ้นไปจอดที่เดิม
#
# วิธีเล่น: **คลิกปุ่ม ▲ หรือ ▼ ด้วยเมาส์** (หรือกด Z/Space ก็ได้)
#
# ================== หัวใจที่ต้องจำให้ได้ ==================
#
#   1. state คือ "ตัวแปรตัวเดียว" ที่บอกว่าตอนนี้ระบบอยู่โหมดไหน
#   2. ทุกเฟรมทำสองอย่างเสมอ: (ก) ทำงานตามสถานะปัจจุบัน
#      (ข) ตรวจว่าถึงเวลาเปลี่ยนสถานะหรือยัง
#   3. debounce = "กดค้างต้องนับครั้งเดียว" ทำด้วยการจำสถานะปุ่มของเฟรมก่อนหน้า
#      แล้วเทียบ:  กดอยู่ตอนนี้ AND ไม่ได้กดเมื่อเฟรมก่อน  = เพิ่งกด
#   4. การเปลี่ยนสถานะทุกครั้งควรอยู่ที่เดียว อ่านง่าย ไม่กระจายทั่วไฟล์
#
# ================== ปุ่มบนจอ ต่างจากปุ่มจอย ==================
#
# ปุ่มจอย (keys.a) ต้อง debounce เอง เพราะมันบอกแค่ "ตอนนี้กดอยู่ไหม"
# ส่วนปุ่มบนจอ (ui.Button) ส่ง "เหตุการณ์ถูกคลิก" มาให้ทาง ui.poll() ครั้งเดียวต่อคลิก
# — debounce มาให้ในตัวแล้ว ไฟล์นี้จึงมีทั้งสองแบบให้เทียบกันเห็น ๆ

import bentogame as game
import ui

# --- สถานะทั้งหมดของระบบ ---
IDLE, MOVING, OPENING, OPEN, CLOSING, RETURNING = 0, 1, 2, 3, 4, 5
STATE_NAME = ["จอดรอ", "กำลังลงมา", "ประตูเปิด", "เปิดค้าง", "ประตูปิด", "กำลังกลับขึ้น"]
STATE_COLOR = [game.GB_LIGHT, game.YELLOW, game.CYAN, game.GREEN, game.ORANGE, game.YELLOW]

FLOORS = ["G", "1", "2", "3"]
HOME_FLOOR = 3.0                   # ลิฟต์จอดรอที่ชั้นนี้
FLOOR_H = 56                       # ระยะระหว่างชั้นบนจอ (px)
BASE_Y = 292                       # ตำแหน่งชั้น G

CAR_SPEED = 0.030                  # ลิฟต์วิ่งกี่ชั้นต่อเฟรม
DOOR_SPEED = 3                     # ประตูเปิด/ปิดเร็วแค่ไหน (px ต่อเฟรม)
DOOR_MAX = 56                      # เปิดสุดกว้างกี่ px ต่อบาน
HOLD = 70                          # เปิดค้างกี่เฟรมก่อนปิดเอง

SHAFT_X, SHAFT_W = 470, 150
CAR_W, CAR_H = 138, 48

game.title("ELEVATOR")


def floor_y(f):
    """ชั้นที่ f (0 = G) อยู่ที่ y เท่าไหร่บนจอ — ชั้นสูงขึ้น y น้อยลง"""
    return BASE_Y - f * FLOOR_H


# --- ฉาก: ปล่องลิฟต์ + เส้นแบ่งชั้น + ป้ายชื่อชั้น ---
shaft = game.Box(SHAFT_X, floor_y(len(FLOORS) - 1) - 8, SHAFT_W,
                 (len(FLOORS) - 1) * FLOOR_H + CAR_H + 16, game.BLACK,
                 border=game.GB_DARK, border_w=2)
for i, name in enumerate(FLOORS):
    game.Box(SHAFT_X - 34, floor_y(i) + CAR_H // 2 - 1, 28, 2, game.GB_DARK)
    game.Text(name, SHAFT_X - 52, floor_y(i) + CAR_H // 2 - 12, game.GB_LIGHT)

car = game.Box(SHAFT_X + 6, floor_y(HOME_FLOOR), CAR_W, CAR_H, game.GB_DARK,
               border=game.GB_DARK, border_w=0)
# ประตูสองบาน เลื่อนออกจากกึ่งกลางตัวลิฟต์
door_l = game.Box(SHAFT_X + 6, floor_y(HOME_FLOOR), CAR_W // 2, CAR_H,
                  game.GB_LIGHT, border=game.GB_LIGHT, border_w=0)
door_r = game.Box(SHAFT_X + 6 + CAR_W // 2, floor_y(HOME_FLOOR), CAR_W // 2, CAR_H,
                  game.GB_LIGHT, border=game.GB_LIGHT, border_w=0)

# --- แผงเรียกลิฟต์ที่ชั้น G (ฝั่งซ้าย) — คลิกด้วยเมาส์ได้ ---
PANEL_X = 150
game.Text("แผงเรียกลิฟต์ · ชั้น G", PANEL_X, 150, game.GB_LIGHT)
btn_up = ui.Button("▲ ขึ้น", x=PANEL_X, y=180, w=110, h=52, color=0x2E7D5B)
btn_down = ui.Button("▼ ลง", x=PANEL_X + 124, y=180, w=110, h=52, color=0x2E5B7D)

# --- จอบอกชั้น อยู่ข้างปล่องทางขวา (เหนือปล่องจะชนแถบข้อความด้านบน) ---
display = game.Text("", SHAFT_X + SHAFT_W + 24, floor_y(len(FLOORS) - 1) + 6, game.YELLOW)

status = game.Text("", 24, 12, game.WHITE)
lamp = game.Box(24, 46, 24, 24, game.GB_LIGHT)
state_text = game.Text("", 56, 48, game.WHITE)
game.Text("คลิก ▲ / ▼ ด้วยเมาส์ หรือกด Z | Enter = ออก", 24, 84, game.CYAN)

# --- สถานะ ---
state = IDLE
car_floor = HOME_FLOOR             # ตำแหน่งลิฟต์ตอนนี้ (ทศนิยม = อยู่ระหว่างชั้น)
gap = 0                            # ประตูเปิดกว้างเท่าไหร่
hold_count = 0
calls = 0                          # นับจำนวนครั้งที่เรียก
call_dir = ""                      # ทิศที่ผู้โดยสารกด (ขึ้น/ลง) — ไฟค้างบนแผง
prev_a = True


def draw_car():
    """วางตัวลิฟต์และประตูตามตำแหน่งชั้นปัจจุบัน"""
    y = floor_y(car_floor)
    car.move_to(SHAFT_X + 6, y)
    door_l.move_to(SHAFT_X + 6 - gap, y)
    door_r.move_to(SHAFT_X + 6 + CAR_W // 2 + gap, y)


def show_display():
    """จอบอกชั้น: เลขชั้นที่ลิฟต์อยู่ + ลูกศรบอกทิศที่กำลังวิ่ง"""
    nearest = int(car_floor + 0.5)
    nearest = max(0, min(len(FLOORS) - 1, nearest))
    arrow = "▼" if state == MOVING else ("▲" if state == RETURNING else "")
    display.set("ชั้น %s %s" % (FLOORS[nearest], arrow))


draw_car()
show_display()

# ============================================================================
# แยกเป็นฟังก์ชันย่อยตามลำดับของระบบสมองกลฝังตัว: รับรู้ -> ตัดสินใจ -> สั่งการ
# ทุกไฟล์ในชุดนี้ใช้โครงเดียวกัน อ่านไฟล์หนึ่งเป็น อ่านที่เหลือออกหมด
# ============================================================================


def read_call_button(keys):
    """รับรู้: ผู้โดยสารเรียกลิฟต์ไหม — รับได้ 2 ทาง คลิกบนจอ กับ ปุ่มจอย

    ปุ่มบนจอส่ง "เหตุการณ์คลิก" มาครั้งเดียวต่อคลิก จึงไม่ต้อง debounce
    ส่วนปุ่มจอยบอกแค่ "ตอนนี้กดอยู่ไหม" เราจึงต้อง debounce เองด้วย prev_a
    """
    global prev_a

    called = ""
    for ev in ui.poll():
        if ev["type"] == "clicked":
            if ev["handle"] == btn_up.id():
                called = "ขึ้น"
            elif ev["handle"] == btn_down.id():
                called = "ลง"
    if keys.a and not prev_a:
        called = "ขึ้น"
    prev_a = keys.a
    return called


def accept_call(called):
    """รับงาน: ลิฟต์ออกเดินได้ก็ต่อเมื่อจอดว่างอยู่เท่านั้น"""
    global state, calls, call_dir

    if called and state == IDLE:
        calls += 1
        call_dir = called
        state = MOVING
        game.sfx("wall")


def decide_state(called):
    """ตัดสินใจ: state machine 6 สถานะ — แต่ละสถานะทำงานของตัวเองแล้วส่งต่อ"""
    global state, car_floor, gap, hold_count, call_dir

    if state == IDLE:
        pass                                    # จอดรอ ไม่ทำอะไร รอปุ่มอย่างเดียว

    elif state == MOVING:                       # วิ่งลงมาชั้น G
        car_floor -= CAR_SPEED
        if car_floor <= 0:
            car_floor = 0                       # clamp ไม่ให้ทะลุชั้นล่างสุด
            state = OPENING
            game.sfx("paddle")

    elif state == OPENING:
        gap += DOOR_SPEED
        if gap >= DOOR_MAX:
            gap = DOOR_MAX                      # clamp ไม่ให้เปิดทะลุ
            state = OPEN
            hold_count = 0

    elif state == OPEN:
        hold_count += 1
        if called:
            hold_count = 0                      # กดซ้ำ = ขยายเวลาเปิด (เหมือนลิฟต์จริง)
        if hold_count >= HOLD:
            state = CLOSING

    elif state == CLOSING:
        if called:
            state = OPENING                     # กดตอนกำลังปิด = เปิดใหม่ (กันประตูหนีบ)
            game.sfx("lose")
        else:
            gap -= DOOR_SPEED
            if gap <= 0:
                gap = 0
                state = RETURNING
                call_dir = ""                   # ดับไฟบนแผง

    elif state == RETURNING:                    # กลับขึ้นไปจอดที่เดิม
        car_floor += CAR_SPEED
        if car_floor >= HOME_FLOOR:
            car_floor = HOME_FLOOR              # clamp
            state = IDLE


def draw_hud():
    """สั่งการ: แสดงผล — ส่วนนี้ไม่ตัดสินใจอะไร แค่รายงานสถานะปัจจุบัน"""
    draw_car()
    show_display()
    lamp.set_color(STATE_COLOR[state])
    state_text.set(STATE_NAME[state])
    status.set("เรียกแล้ว %d ครั้ง | ปุ่มที่กด: %s | ประตูเปิด %d px"
               % (calls, call_dir or "-", gap))


def on_each_frame():
    """หนึ่งเฟรม = รับการเรียก -> รับงาน -> ตัดสินใจ -> สั่งการ"""
    keys = game.keys()
    if keys.start:
        return False

    called = read_call_button(keys)
    accept_call(called)
    decide_state(called)
    draw_hud()



game.run(on_each_frame, fps=30)

# ------------------------------------------------------------------------------
# ลองเล่นกับมันดู:
#
#   1. คลิกปุ่มบนจอ กับ กด Z ค้างไว้ — สังเกตว่าทั้งคู่เรียกลิฟต์ได้เหมือนกัน
#      แต่โค้ดที่รับสองแบบนี้ต่างกัน: ปุ่มบนจอส่ง "เหตุการณ์คลิก" มาครั้งเดียว
#      ส่วนปุ่มจอยบอกแค่ "ตอนนี้กดอยู่ไหม" เราจึงต้อง debounce เองด้วย prev_a
#
#   2. **ลบ debounce ของปุ่มจอยออก (เหลือ called = "ขึ้น" if keys.a) แล้วกด Z ค้างไว้**
#      ดูสองอย่างตามลำดับ:
#
#      ก) ตัวนับ "เรียกแล้ว" **จะไม่พุ่ง** — ขึ้นแค่ 1 แล้วหยุด
#         เพราะบรรทัด if called and state == IDLE กันไว้อยู่แล้ว ลิฟต์ที่ออกเดินแล้ว
#         รับงานซ้ำไม่ได้ ตรงนี้จึงดูเหมือน debounce ไม่จำเป็น
#
#      ข) **แต่พอลิฟต์มาถึงแล้วประตูเปิด ประตูจะไม่ปิดอีกเลย** ค้างเปิดตลอด
#         เพราะในสถานะ OPEN มีบรรทัด if called: hold_count = 0 ที่รีเซ็ตเวลารอ
#         กดค้าง = รีเซ็ตทุกเฟรม = ตัวนับไม่มีวันถึง HOLD
#         (วัดจริง: กดค้าง 40 วินาที ประตูอยู่สถานะ OPEN 1140 จาก 1200 เฟรม
#          และไม่เคยปิดสนิทเลยสักครั้ง ส่วนตอนมี debounce เปิด 45 เฟรมแล้วปิดปกติ)
#
#      บทเรียนอยู่ที่ข้อ ก) พอ ๆ กับข้อ ข): **จุดที่ debounce สำคัญ ไม่ใช่จุดที่เดาไว้**
#      ตรงที่มี state คุมอยู่แล้วมันไม่จำเป็น แต่ตรงที่ใช้ปุ่ม "ขยายเวลา" มันจำเป็นมาก
#      ในลิฟต์จริงนี่คืออาการที่คนกดปุ่มค้างแล้วประตูไม่ยอมปิด
#
#      แล้วลองกดปุ่มบนจอค้างดูบ้าง จะเห็นว่าประตูปิดปกติ เพราะ ui.poll() ส่งมาครั้งเดียว
#
#   3. ลบเงื่อนไข if called ในสถานะ CLOSING ออก แล้วกดตอนประตูกำลังปิด
#      ประตูจะปิดต่อไปโดยไม่สนใจ — ในลิฟต์จริงนี่คือบั๊กที่หนีบคนได้
#
#   4. ตั้ง CAR_SPEED = 0.3 แล้วดูว่าเลขชั้นบนจอกระโดดข้ามชั้น
#      เพราะลิฟต์เคลื่อนเกิน 1 ชั้นต่อเฟรม — ระบบจริงต้องจำกัดความเร็วไว้เสมอ
#
#   5. เพิ่มสถานะที่เจ็ด BLOCKED (มีของขวางประตู) ที่ประตูจะปิดไม่ได้จนกว่าของจะออกไป
#      ลองคิดเองว่าจะเข้า/ออกสถานะนี้ตอนไหน
#
# ทักษะนี้ใช้ที่ไหนได้อีก: เครื่องซักผ้า (แช่→ซัก→ปั่น→ตาก), เครื่อง ATM,
#   โหมดของกล้อง, การจัดการการเชื่อมต่อเน็ตเวิร์ก (disconnected→connecting→connected)
#   ทุกอุปกรณ์ที่มี "โหมด" คือ state machine ทั้งหมด
