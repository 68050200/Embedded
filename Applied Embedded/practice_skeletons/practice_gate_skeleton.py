# practice_gate_skeleton.py — โครงตัวช่วยของข้อซ้อม 1 (Parking Barrier Gate)
#
# *** อ่านตรงนี้ก่อนใช้ ***
#
# ข้อสอบจริงข้อ 1 **ไม่มีโครงให้** — ต้องเขียนเองตั้งแต่บรรทัดแรก
# ไฟล์นี้จึงเป็น "บันได" สำหรับตอนซ้อม ไม่ใช่ของที่จะมีให้ในวันสอบ:
#
#   1. **ลองเริ่มจากไฟล์เปล่าก่อนอย่างน้อย 1 ชั่วโมง** — การได้เจอไฟล์เปล่า
#      ตอนซ้อมคือการเตรียมวันสอบที่ตรงที่สุด อย่าพรากมันไปจากตัวเอง
#   2. ติดจริง ๆ ค่อยเปิดไฟล์นี้ — ฉากทั้งหมดวางให้แล้ว เหลือส่วนที่เป็นทักษะ
#      ที่ข้อสอบวัดให้เขียนเอง
#   3. ทำเสร็จด้วยโครงนี้แล้ว **กลับไปลองไฟล์เปล่าอีกรอบ** ถ้าเขียนเองได้หมด
#      แปลว่าพร้อมจริง
#
# ================== วิธีใช้ ==================
#
#   1. เปลี่ยน SID ข้างล่างเป็นรหัสนิสิตของคุณ
#   2. รันดูก่อน — จะเห็นถนน เซนเซอร์ เสา ไม้กั้น และรถที่ขับได้ (ไม้กั้นขวางรถ
#      ให้แล้ว) แต่ไม้กั้นยังไม่ทำงาน
#   3. เขียนส่วนที่เป็น TODO ให้ครบ แล้วเปลี่ยนชื่อไฟล์เป็น
#      practice_gate_<รหัสนิสิต>.py
#
# ================== สิ่งที่แจกให้ (ไม่ต้องเขียนเอง) ==================
#
#   ฉากทั้งหมด: ถนน โซนเซนเซอร์ เสา ไม้กั้น รถ และแถบข้อความ
#   การขับรถ + clamp ขอบจอ + ไม้กั้นที่ปิดอยู่ขวางรถ (ส่วนนี้โจทย์ไม่ได้ให้คะแนน)
#
# ================== สิ่งที่คุณต้องเขียนเอง (คือสิ่งที่โจทย์ให้คะแนน) ==================
#
#   - read_card()     แตะบัตรหนึ่งครั้ง = หนึ่งครั้ง (debounce)
#   - sense_car()     รถอยู่ในโซนไหม + นับรถตอน "ออก" จากโซน (edge detection)
#   - decide_state()  state machine 4 สถานะ + กฎความปลอดภัย
#   - draw_hud()      ไฟสี ชื่อสถานะ และตัวนับ
#
# ทุก TODO มีโครงของ pattern แปะไว้ให้ในคอมเมนต์ — จุดที่ต้องคิดเองจริง ๆ
# (ไม่มีเฉลยในคอมเมนต์) คือ กฎความปลอดภัย การกลับด้านเงื่อนไขตอนนับ
# และเงื่อนไขขยายเวลาเปิด

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

    # TODO: debounce — โครงเดียวกับปุ่มลิฟต์ใน prep_02 เป๊ะ:
    #     tapped = keys.a and not prev_a
    #     prev_a = keys.a
    #     return tapped
    # อธิบายให้ตัวเองได้ด้วยว่าทำไมสองบรรทัดแรกสลับกันไม่ได้ —
    # เป็นคำถามยอดฮิตของแบบทดสอบในห้อง
    return False


def drive_car(keys):
    """[แจกให้ทั้งฟังก์ชัน] ขับรถ + clamp ขอบจอ + ไม้ที่ปิดอยู่ขวางรถ"""
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
    """รับรู้: รถอยู่ในโซนเซนเซอร์ไหม + นับรถตอน 'ออก' จากโซน"""
    global car_count, was_in_sensor

    # TODO: in_sensor = game.hit(car, sensor)  (ต้องเช็คหลัง move_to)
    #       นับรถด้วย edge detection ตอน "ออก" จากโซน — เข้าออก 3 คันต้องนับได้ 3
    #       pattern จาก prep_04 นับตอน "เข้า" หน้าตาแบบนี้:
    #     if in_zone and not was_in_zone:
    #         count += 1
    #       ข้อนี้นับตอน "ออก" — สลับเงื่อนไขเอง (นี่คือจุดที่ต้องคิด อย่าลอกตรง ๆ)
    #       และอย่าลืมอัปเดต was_in_sensor ทุกเฟรมก่อน return
    return False


def decide_state(tapped, in_sensor):
    """ตัดสินใจ: state machine 4 สถานะ — กฎความปลอดภัยอยู่ในสถานะ LOWERING"""
    global gate_y, state, hold_count

    # TODO ทีละสถานะ:
    #   DOWN     — รอบัตรอย่างเดียว แตะแล้วไป RAISING
    #   RAISING  — ไม้ยกขึ้นทีละ GATE_SPEED จนสุดแล้วไป UP (อย่าลืม clamp)
    #   UP       — นับ hold_count ครบ HOLD แล้วไป LOWERING
    #              แตะบัตรซ้ำระหว่างนี้ = รีเซ็ตตัวนับ (ขยายเวลาเปิด)
    #   LOWERING — *** กฎความปลอดภัย: ถ้ามีรถในโซน ห้ามลงต่อ
    #              ต้องกลับ RAISING ทันที และต้องเช็คทุกเฟรม ***
    #              ไม่มีรถค่อยลงทีละ GATE_SPEED จนสุดแล้วกลับ DOWN (clamp)
    #
    # โครงที่ควรได้ — สาขาละสถานะ แบบเดียวกับประตูลิฟต์ใน prep_02
    # (เนื้อในแต่ละสาขาเติมเองตาม spec ข้างบน — โดยเฉพาะ LOWERING ที่ต้องตัดสินใจ
    #  ว่าเช็คอะไร "ก่อน" ขยับไม้):
    #     if state == DOWN:
    #         ...
    #     elif state == RAISING:
    #         gate_y -= GATE_SPEED
    #         ...ถึงสุดแล้ว clamp + เปลี่ยนสถานะ...
    #     elif state == UP:
    #         ...
    #     elif state == LOWERING:
    #         ...
    pass


def draw_hud(in_sensor):
    """แสดงผล — ส่วนนี้ไม่ตัดสินใจอะไร แค่รายงานสถานะปัจจุบัน"""
    # TODO: gate       -> move_to ตาม gate_y + สีตาม STATE_COLOR[state]
    #       lamp       -> สีตาม STATE_COLOR[state]
    #       state_text -> ชื่อสถานะ + คำเตือนเมื่อมีรถใต้ไม้
    #       counter    -> รถผ่านกี่คัน, hold_count/HOLD, มีรถในโซนไหม, P1 ของคุณ
    #
    # ตัวอย่างสองบรรทัดแรกให้เลย (ที่เหลือรูปแบบเดียวกัน):
    #     gate.move_to(GATE_X, gate_y)
    #     lamp.set_color(STATE_COLOR[state])
    # ส่วนข้อความใช้ .set() กับ % แบบเดียวกับทุกไฟล์ prep เช่น
    #     state_text.set("%s" % STATE_NAME[state])
    #
    # ระวัง: ข้อความยาวเกิน 126 ไบต์จะถูกตัดทิ้งเงียบ ๆ (ภาษาไทย = 3 ไบต์/ตัว)
    pass


def on_each_frame():
    """หนึ่งเฟรม = อ่านปุ่ม -> ขยับของ -> รับรู้ -> ตัดสินใจ -> สั่งการ"""
    keys = game.keys()
    if keys.start:
        return False

    tapped = read_card(keys)
    drive_car(keys)
    in_sensor = sense_car()
    decide_state(tapped, in_sensor)
    draw_hud(in_sensor)


game.run(on_each_frame, fps=30)
