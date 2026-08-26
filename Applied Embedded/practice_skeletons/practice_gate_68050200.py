# practice_gate_skeleton.py — (Parking Barrier Gate)


import bentogame as game

SID = 68050200                      # <<< เปลี่ยนเป็นรหัสนิสิตของคุณ
P1 = SID % 6

# --- ค่าที่ผูกกับรหัสนิสิต ---
SENSOR_W = 100 + P1 * 12
HOLD = 60 + P1 * 10

GATE_SPEED = 3
CAR_W, CAR_H = 76, 44
CAR_SPEED = 5

# --- สถานะของไม้กั้น ---
DOWN, RAISING, UP, LOWERING = 0, 1, 2, 3
STATE_NAME = ["DOWN", "RAISING", "UP", "LOWERING"]
STATE_COLOR = [game.RED, game.YELLOW, game.GREEN, game.ORANGE]

game.title("PARKING GATE")

# ---------------------------------------------------------------- ผังหน้าจอ
# จอกว้าง 792 สูง 398 · วางถนนไว้ครึ่งล่าง เว้นครึ่งบนให้ข้อความสถานะ
# และเว้นขอบล่าง ~50 px ไว้ เพราะหน้า Playground มีแถบข้อความของตัวเองอยู่ตรงนั้น
ROAD_TOP = 244
ROAD_H = 72
ROAD_BOTTOM = ROAD_TOP + ROAD_H                  # 316

CAR_Y = ROAD_TOP + (ROAD_H - CAR_H) // 2         # รถอยู่กลางถนน

POST_X, POST_W = 560, 14                         # เสาไม้กั้น
POST_TOP = 172                                   # ไม้ยกสุดต้องต่ำกว่าแถบข้อความ (จบ ~152)

# ไม้กั้นกว้างเท่าโซนเซนเซอร์พอดี และอยู่ตรงกันเป๊ะ — จงใจให้เป็นแบบนี้
# ถ้าไม้ยาวเกินเซนเซอร์ จะมีช่องที่ "รถอยู่ใต้ไม้ แต่เซนเซอร์ไม่เห็น" = ไม้ฟาดรถได้
GATE_W, GATE_H = SENSOR_W, 14
GATE_X = POST_X - GATE_W                         # ไม้ยื่นไป "ซ้าย" คือฝั่งที่รถวิ่งมา
GATE_DOWN_Y = CAR_Y + 6                          # ปิด = อยู่ในระดับตัวรถ (ขวางทางจริง)
GATE_UP_Y = POST_TOP + 10                        # เปิด = ยกขึ้นไปชิดยอดเสา

# ถนน (ฉากหลัง วาดก่อนของอื่นเพื่อให้อยู่ชั้นล่างสุด)
road = game.Box(0, ROAD_TOP, game.WIDTH, ROAD_H, game.GB_DARKEST)

# โซนเซนเซอร์ — อยู่ใต้ไม้กั้นพอดี กว้างเท่ากัน เริ่มที่เดียวกัน
SENSOR_X = GATE_X
sensor = game.Box(SENSOR_X, ROAD_TOP, SENSOR_W, ROAD_H, game.BLACK,
                  border=game.CYAN, border_w=2)
game.Text("SENSOR", SENSOR_X + 6, ROAD_TOP - 26, game.CYAN)

post = game.Box(POST_X, POST_TOP, POST_W, ROAD_BOTTOM - POST_TOP, game.GB_DARK)
gate = game.Box(GATE_X, GATE_DOWN_Y, GATE_W, GATE_H, game.RED)

car = game.Box(40, CAR_Y, CAR_W, CAR_H, game.BLUE)

# ข้อความเริ่มต้นบอกว่าแต่ละบรรทัดเป็นของใคร — เขียน draw_hud() แล้วจะถูกแทนที่เอง
game.Text("PARKING GATE", 24, 14, game.WHITE)
lamp = game.Box(24, 52, 24, 24, game.RED)
state_text = game.Text("(state_text: ชื่อสถานะ + คำเตือน)", 56, 54, game.WHITE)
counter = game.Text("(counter: รถผ่าน + ตัวนับค้าง + P1)", 24, 92, game.GB_LIGHT)
game.Text("ลูกศร = ขับรถ | Z/Space = แตะบัตร | Enter = ออก", 24, 128, game.CYAN)

# --- สถานะทั้งหมด ---
car_x = 40.0
gate_y = float(GATE_DOWN_Y)
state = DOWN
hold_count = 0
car_count = 0
was_in_sensor = False               # จำเฟรมก่อน — ใช้นับตอน "ออก" จากโซน
prev_a = True


# ============================================================================
# ตั้งแต่บรรทัดนี้ลงไปคือส่วนที่คุณต้องเขียนเอง
#
# แยกเป็นฟังก์ชันย่อยตามลำดับ รับรู้ -> ตัดสินใจ -> สั่งการ
# เหมือนตัวอย่างเตรียมสอบทุกไฟล์ จะเขียนและดีบักง่ายกว่ามาก
# ============================================================================


def read_card(keys):
    """แตะบัตรหนึ่งครั้ง = นับหนึ่งครั้ง — คืนค่าว่าเฟรมนี้แตะไหม"""
    global prev_a
    tapped = keys.a and not prev_a
    prev_a = keys.a
    return tapped


def drive_car(keys):
    #"""[แจกให้ทั้งฟังก์ชัน] ขับรถ + clamp ขอบจอ + ไม้ที่ปิดอยู่ขวางรถ"""
    global car_x

    if keys.left:
        car_x -= CAR_SPEED
    if keys.right:
        car_x += CAR_SPEED
    car_x = max(0, min(game.WIDTH - CAR_W, car_x))

    # ไม้ที่ยังไม่ยกพ้นระดับรถ ต้องบังรถได้จริง — ให้ไว้เลยเพราะโจทย์ไม่ได้ให้คะแนน
    # ส่วนนี้ แต่ถ้าไม่มี ไม้กั้นจะไม่มีความหมาย
    gate_blocks = (gate_y + GATE_H > CAR_Y) and (gate_y < CAR_Y + CAR_H)
    if gate_blocks and car_x + CAR_W > GATE_X:
        car_x = GATE_X - CAR_W                  # จอดชิดไม้ ไปต่อไม่ได้จนกว่าไม้จะยก
    car.move_to(car_x, CAR_Y)


def sense_car():
    #"""รับรู้: รถอยู่ในโซนเซนเซอร์ไหม + นับรถตอน 'ออก' จากโซน"""
    global car_count, was_in_sensor
    in_zone = game.hit(car, sensor)
    if was_in_sensor and not in_zone:
        car_count += 1
    was_in_sensor = in_zone
    return in_zone


def decide_state(tapped, in_sensor):
    #"""ตัดสินใจ: state machine 4 สถานะ — กฎความปลอดภัยอยู่ในสถานะ LOWERING"""
    global gate_y, state, hold_count

    if state == DOWN:
        if tapped:
            state = RAISING
    elif state == RAISING:
        gate_y -= GATE_SPEED
        if gate_y <= GATE_UP_Y:
            gate_y = GATE_UP_Y
            state = UP
            hold_count = 0
    elif state == UP:
        hold_count += 1
        if tapped:
            hold_count = 0
        if hold_count >= HOLD:
            state = LOWERING
    elif state == LOWERING:
        if in_sensor:
            state = RAISING
        else:
            gate_y += GATE_SPEED
            if gate_y >= GATE_DOWN_Y:
                gate_y = GATE_DOWN_Y
                state = DOWN
        


def draw_hud(in_sensor):
    
    gate.move_to(GATE_X, gate_y)
    
    lamp.set_color(STATE_COLOR[state])
    
    if in_sensor:
        state_text.set("สถานะ %s - เตือน มีรถใต้ไม้" % STATE_NAME[state])
    else:
        state_text.set("สถานะ %s" % STATE_NAME[state])
    
    counter.set("รถผ่าน: %d HOLD: %d/%d  รถในโซน: %s P1=%d" % (car_count, hold_count, HOLD, in_sensor, P1))
    pass


def on_each_frame():
    #"""หนึ่งเฟรม = อ่านปุ่ม -> ขยับของ -> รับรู้ -> ตัดสินใจ -> สั่งการ"""
    keys = game.keys()
    if keys.start:
        return False

    tapped = read_card(keys)
    drive_car(keys)
    in_sensor = sense_car()
    decide_state(tapped, in_sensor)
    draw_hud(in_sensor)


game.run(on_each_frame, fps=30)
