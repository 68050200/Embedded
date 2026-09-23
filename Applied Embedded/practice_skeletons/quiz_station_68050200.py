# quiz_station_skeleton.py — โครงเริ่มต้นของ Quiz ชุด B (Fire Station Door)
#
# *** ไฟล์นี้แจกให้ทุกคน (กลุ่มชุด B) ใช้เป็นจุดตั้งต้นได้เลย ***
#
# ================== วิธีใช้ ==================
#
#   1. เปลี่ยน SID ข้างล่างเป็นรหัสนิสิตของคุณ
#   2. รันดูก่อน — จะเห็นถนน วงกบ บานประตู และรถดับเพลิงที่ขับซ้าย-ขวาได้
#      แต่ประตูยังไม่ทำงาน และรถขับทะลุประตูที่ปิดอยู่ได้ (ผิด — คุณต้องแก้)
#   3. เขียนส่วนที่เป็น TODO ให้ครบ แล้วเปลี่ยนชื่อไฟล์เป็น quiz_station.py
#
# ================== สิ่งที่แจกให้ (ไม่ต้องเขียนเอง) ==================
#
#   ฉากทั้งหมด: ถนน โซนเซนเซอร์ วงกบ บานประตู รถดับเพลิง และแถบข้อความ
#   การขับรถซ้าย-ขวา + clamp ขอบจอ (ยังไม่รวมการกันรถล้ำช่องประตู)
#
# ================== สิ่งที่คุณต้องเขียนเอง ==================
#
#   - read_alarm()    กดสัญญาณหนึ่งครั้ง = หนึ่งครั้ง (debounce)
#   - กันรถล้ำช่องประตูเมื่อบานยังไม่พ้นระดับรถ (ใน drive_truck)
#   - sense_truck()   รถอยู่ในโซนไหม + นับรถตอน "ออก" จากโซน (edge detection)
#   - decide_state()  state machine 4 สถานะ + กฎความปลอดภัย
#   - draw_hud()      ไฟสี ชื่อสถานะ และตัวนับ
#
# ทุก TODO มีโครงของ pattern แปะไว้ให้ในคอมเมนต์ — หน้าที่ของคุณคือแปลงมัน
# เข้าบริบทประตูสถานีให้ถูก จุดที่ต้องคิดเองจริง ๆ (ไม่มีเฉลยในคอมเมนต์) คือ
# กฎความปลอดภัย การกลับด้านเงื่อนไขตอนนับ และเงื่อนไขต่อเวลาเปิด

import bentogame as game

SID = 68050200                      # <<< เปลี่ยนเป็นรหัสนิสิตของคุณ
Q = SID % 5

# --- ค่าที่ผูกกับรหัสนิสิต ---
DOOR_W = 120 + Q * 10               # ความกว้างช่องประตู/โซนเซนเซอร์
HOLD_UP = 50 + Q * 8                # เวลาค้างเปิด (เฟรม)

DOOR_SPEED = 3
TRUCK_W, TRUCK_H = 80, 34
TRUCK_SPEED = 5

# --- สถานะของประตู ---
CLOSED, OPENING, OPEN, CLOSING = 0, 1, 2, 3
STATE_NAME = ["CLOSED", "OPENING", "OPEN", "CLOSING"]
STATE_COLOR = [game.RED, game.YELLOW, game.GREEN, game.ORANGE]

game.title("FIRE STATION")

# ---------------------------------------------------------------- ผังหน้าจอ
# จอกว้าง 792 สูง 398 · แถบข้อความครึ่งบน (จบ ~152) · เว้นขอบล่าง ~50 px
# ช่องประตูอยู่ค่อนซ้าย รถเริ่มฝั่งขวา (ในสถานี) ขับออกไปทางซ้าย
ROAD_TOP = 244
ROAD_H = 86
ROAD_BOTTOM = ROAD_TOP + ROAD_H                 # 330

TRUCK_Y = ROAD_TOP + 18                         # รถวิ่งบนพื้นถนน

DOOR_X = game.WIDTH - 340 - DOOR_W              # ขอบซ้ายของช่องประตู
DOOR_T = 12                                     # ความหนาบานประตู
DOOR_DOWN_Y = TRUCK_Y - 8                       # ปิด = บานอยู่ระดับหัวรถ (ขวางจริง)
DOOR_UP_Y = 168                                 # เปิดสุด — ต่ำกว่าแถบข้อความ

# พื้นถนน (ฉากหลัง วาดก่อนของอื่นเพื่อให้อยู่ชั้นล่างสุด)
road = game.Box(0, ROAD_TOP, game.WIDTH, ROAD_H, game.GB_DARKEST)

# โซนเซนเซอร์ = พื้นใต้ช่องประตูพอดี — กว้างเท่าบาน เริ่มที่เดียวกัน
zone = game.Box(DOOR_X, ROAD_TOP, DOOR_W, ROAD_H, game.BLACK,
                border=game.CYAN, border_w=2)
game.Text("SENSOR", DOOR_X + 6, ROAD_TOP - 26, game.CYAN)

# วงกบสองข้างของช่องประตู
post_l = game.Box(DOOR_X - 16, DOOR_UP_Y - 10, 16,
                  ROAD_BOTTOM - (DOOR_UP_Y - 10), game.GB_DARK)
post_r = game.Box(DOOR_X + DOOR_W, DOOR_UP_Y - 10, 16,
                  ROAD_BOTTOM - (DOOR_UP_Y - 10), game.GB_DARK)

door = game.Box(DOOR_X, DOOR_DOWN_Y, DOOR_W, DOOR_T, game.RED)

# รถดับเพลิง: ตัวรถ + หัวเก๋ง (เก๋งเป็นแค่ภาพ ตามตัวรถ — hit ใช้ตัวรถอย่างเดียว)
truck = game.Box(672, TRUCK_Y, TRUCK_W, TRUCK_H, game.RED)
cab = game.Box(672 + 10, TRUCK_Y - 14, 24, 14, game.GB_LIGHT,
               border=game.GB_LIGHT, border_w=0)

# ข้อความเริ่มต้นบอกว่าแต่ละบรรทัดเป็นของใคร — เขียน draw_hud() แล้วจะถูกแทนที่เอง
game.Text("FIRE STATION", 24, 14, game.WHITE)
lamp = game.Box(24, 52, 24, 24, game.RED)
state_text = game.Text("(state_text: ชื่อสถานะ + คำเตือน)", 56, 54, game.WHITE)
counter = game.Text("(counter: รถออกเหตุ + ตัวนับค้าง + Q)", 24, 92, game.GB_LIGHT)
game.Text("ซ้าย/ขวา = ขับรถ | Z = แจ้งเหตุ | Enter = ออก", 24, 128, game.CYAN)

# --- สถานะทั้งหมด ---
truck_x = 672.0
door_y = float(DOOR_DOWN_Y)
state = CLOSED
hold_count = 0
truck_count = 0
was_in_zone = False                 # จำเฟรมก่อน — ใช้นับตอน "ออก" จากโซน
prev_a = True


# ============================================================================
# ตั้งแต่บรรทัดนี้ลงไปคือส่วนที่คุณต้องเขียนเอง
#
# แยกเป็นฟังก์ชันย่อยตามลำดับ รับรู้ -> ตัดสินใจ -> สั่งการ
# เหมือนตัวอย่างเตรียมสอบทุกไฟล์ จะเขียนและดีบักง่ายกว่ามาก
# ============================================================================


def read_alarm(keys):
    """กดสัญญาณแจ้งเหตุหนึ่งครั้ง = ขอเปิดหนึ่งครั้ง — คืนค่าว่าเฟรมนี้กดไหม"""
    global prev_a

    # TODO: debounce — โครงเดียวกับปุ่มลิฟต์ใน prep_02 เป๊ะ:
    #     pressed = keys.a and not prev_a
    #     prev_a = keys.a
    #     return pressed
    # อธิบายให้ตัวเองได้ด้วยว่าทำไมสองบรรทัดแรกสลับกันไม่ได้ —
    # เป็นคำถามยอดฮิตของแบบทดสอบในห้อง
    pressed = keys.a and not prev_a
    prev_a = keys.a
    return pressed


def drive_truck(keys):
    """ขับรถ + clamp ขอบจอ [แจกให้] + กันรถล้ำช่องประตู [คุณเขียน]"""
    global truck_x

    if keys.left:
        truck_x -= TRUCK_SPEED
    if keys.right:
        truck_x += TRUCK_SPEED
    truck_x = max(0, min(game.WIDTH - TRUCK_W, truck_x))

    # TODO: ถ้าบานยังไม่พ้นระดับรถ รถต้องล้ำเข้าช่องประตูไม่ได้ —
    #       และต้องกันทั้งสองฝั่ง เพราะรถขับถอยกลับได้
    #       โครงที่ควรได้ (เติมส่วน <...> เอง):
    #     door_blocks = door_y + DOOR_T > TRUCK_Y
    #     if door_blocks:
    #         if truck_x + TRUCK_W / 2 < <กึ่งกลางช่องประตู>:
    #             truck_x = min(truck_x, <ตำแหน่งจอดชิดฝั่งซ้าย>)
    #         else:
    #             truck_x = max(truck_x, <ตำแหน่งจอดชิดฝั่งขวา>)
    door_blocks = door_y + DOOR_T > TRUCK_Y
    if door_blocks:
        if truck_x + TRUCK_W / 2 < DOOR_X + DOOR_W / 2 :
            truck_x = min(truck_x, DOOR_X - TRUCK_W - DOOR_T)
        else:
            truck_x = max(truck_x, DOOR_X + DOOR_W + DOOR_T)

    truck.move_to(truck_x, TRUCK_Y)
    cab.move_to(truck_x + 10, TRUCK_Y - 14)


def sense_truck():
    """รับรู้: รถอยู่ในโซนใต้ประตูไหม + นับรถตอน 'ออก' จากโซน"""
    global truck_count, was_in_zone
    
    # TODO: in_zone = game.hit(truck, zone)  (ต้องเช็คหลัง move_to)
    #       นับรถด้วย edge detection ตอน "ออก" จากโซน — เข้าออก 3 ครั้งต้องนับได้ 3
    #       pattern จาก prep_04 นับตอน "เข้า" หน้าตาแบบนี้:
    #     if in_zone and not was_in_zone:
    #         count += 1
    #       ข้อนี้นับตอน "ออก" — สลับเงื่อนไขเอง (นี่คือจุดที่ต้องคิด อย่าลอกตรง ๆ)
    #       และอย่าลืมอัปเดต was_in_zone ทุกเฟรมก่อน return

    in_zone = game.hit(truck, zone)
    if was_in_zone and not in_zone:
        truck_count += 1

    was_in_zone = in_zone

    return in_zone


def decide_state(pressed, in_zone):
    """ตัดสินใจ: state machine 4 สถานะ — กฎความปลอดภัยอยู่ในสถานะ CLOSING"""
    global door_y, state, hold_count

    # TODO ทีละสถานะ:
    #   CLOSED   — รอสัญญาณแจ้งเหตุอย่างเดียว กดแล้วไป OPENING
    #   OPENING  — บานเปิดขึ้นทีละ DOOR_SPEED จนสุดแล้วไป OPEN (อย่าลืม clamp)
    #   OPEN     — นับ hold_count ครบ HOLD_UP แล้วไป CLOSING
    #              กดสัญญาณซ้ำระหว่างนี้ = รีเซ็ตตัวนับ (ขยายเวลาเปิด)
    #   CLOSING  — *** กฎความปลอดภัย: ถ้ามีรถในโซน ห้ามปิดต่อ
    #              ต้องกลับ OPENING ทันที และต้องเช็คทุกเฟรม ***
    #              ไม่มีรถค่อยปิดทีละ DOOR_SPEED จนสุดแล้วกลับ CLOSED (clamp)
    #
    # โครงที่ควรได้ — สาขาละสถานะ แบบเดียวกับประตูลิฟต์ใน prep_02
    # (เนื้อในแต่ละสาขาเติมเองตาม spec ข้างบน — โดยเฉพาะ CLOSING ที่ต้องตัดสินใจ
    #  ว่าเช็คอะไร "ก่อน" ขยับบาน):
    #     if state == CLOSED:
    #         ...
    #     elif state == OPENING:
    #         door_y -= DOOR_SPEED
    #         ...ถึงสุดแล้ว clamp + เปลี่ยนสถานะ...
    #     elif state == OPEN:
    #         ...
    #     elif state == CLOSING:
    #         ...
    if state == CLOSED:
        if pressed:
            state = OPENING

    elif state == OPENING:
        door_y -= DOOR_SPEED
        if door_y <= DOOR_UP_Y:
            door_y = DOOR_UP_Y
            state = OPEN

    elif state == OPEN:
        hold_count += 1
        if pressed:
            hold_count = 0
        if hold_count >= HOLD_UP:
            state = CLOSING
            hold_count = 0
    elif state == CLOSING:
        if in_zone:
            state = OPENING
        else:
            door_y += DOOR_SPEED
            if door_y >= DOOR_DOWN_Y:
                            door_y = DOOR_DOWN_Y
                            state = CLOSED
    


def draw_hud(in_zone):
    """แสดงผล — ส่วนนี้ไม่ตัดสินใจอะไร แค่รายงานสถานะปัจจุบัน"""
    # TODO: door       -> move_to ตาม door_y + สีตาม STATE_COLOR[state]
    #       lamp       -> สีตาม STATE_COLOR[state]
    #       state_text -> ชื่อสถานะ + คำเตือนเมื่อมีรถใต้ประตู
    #       counter    -> รถออกเหตุกี่คัน, hold_count/HOLD_UP, มีรถในโซนไหม, Q ของคุณ
    #
    # ตัวอย่างสองบรรทัดแรกให้เลย (ที่เหลือรูปแบบเดียวกัน):
    #     door.move_to(DOOR_X, door_y)
    #     lamp.set_color(STATE_COLOR[state])
    # ส่วนข้อความใช้ .set() กับ % แบบเดียวกับทุกไฟล์ prep เช่น
    #     state_text.set("%s" % STATE_NAME[state])
    #
    # ระวัง: ข้อความยาวเกิน 126 ไบต์จะถูกตัดทิ้งเงียบ ๆ (ภาษาไทย = 3 ไบต์/ตัว)
    door.move_to(DOOR_X, door_y)
    lamp.set_color(STATE_COLOR[state])
    if in_zone:
        state_text.set("สถานะ %s - เตือน มีรถใต้ประตู" % STATE_NAME[state])
    else:
        state_text.set("สถานะ %s" % STATE_NAME[state])

    counter.set("รถออกไป : %d คัน HOLD: %d/%d  รถในโซน: %s Q =%d" % (truck_count, hold_count, HOLD_UP, in_zone, Q))
    


def on_each_frame():
    """หนึ่งเฟรม = อ่านปุ่ม -> ขยับของ -> รับรู้ -> ตัดสินใจ -> สั่งการ"""
    keys = game.keys()
    if keys.start:
        return False

    pressed = read_alarm(keys)
    drive_truck(keys)
    in_zone = sense_truck()
    decide_state(pressed, in_zone)
    draw_hud(in_zone)


game.run(on_each_frame, fps=30)
