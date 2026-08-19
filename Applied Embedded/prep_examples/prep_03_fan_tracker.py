# prep_03_fan_tracker.py — เตรียมสอบกลางภาค ตัวอย่างที่ 3
#
# ทักษะที่ทบทวน: sense → decide → act + deadzone (คาบ 7)
#                 accel / friction / clamp        (คาบ 6)
#
# เรื่องราว: พัดลมตั้งโต๊ะที่ "หันหัวตามคน" ฐานอยู่กับที่ หัวหมุนซ้าย-ขวา
#   เซนเซอร์บอกว่าคนอยู่ตรงไหน มอเตอร์หมุนหัวพัดลมให้เป่าไปทางนั้น
#
#   ปัญหาจริงของอุปกรณ์แบบนี้คือ "หมุนเลยเป้าแล้วหมุนกลับ วนไปมาไม่หยุด"
#   (เรียกว่า hunting) มอเตอร์ร้อน เสียงดัง พังเร็ว
#
#   วิศวกรแก้ด้วยสองอย่างที่คุณเรียนมาแล้วทั้งคู่:
#     - deadzone: ใกล้พอแล้วก็ "ไม่ต้องหมุน" (มาจากไม้ AI ของ Pong)
#     - ความเฉื่อย: เร่ง/หน่วงแทนการกระโดดไปมุมเป้าทันที (มาจากไม้ผู้เล่นของ Pong)
#
# วิธีเล่น: X = เปิด/ปิด deadzone · ดูหัวพัดลมหมุนตามคนที่เดินไปมา
#
# ================== หัวใจที่ต้องจำให้ได้ ==================
#
#   1. วงจรควบคุมทุกตัวคือ 3 ขั้นซ้ำ ๆ:  sense (อ่าน) → decide (ตัดสิน) → act (สั่ง)
#   2. deadzone = "ช่วงที่ถือว่าถึงแล้ว ไม่ต้องแก้" — ขาดตัวนี้ ระบบจะสั่นตลอดเวลา
#   3. clamp 2 ชั้นเสมอ: clamp ความเร็ว (ไม่ให้แรงเกิน) และ clamp ช่วง (ไม่ให้หมุนหลุด)
#   4. friction คือสิ่งที่ทำให้ "ปล่อยแล้วค่อย ๆ หยุด" ไม่ใช่ "ปล่อยแล้วหยุดทันที"
#
# ================== พัดลม "หัน" ไม่ใช่ "เลื่อน" ==================
#
# ฐานพัดลมอยู่กับที่ตลอด สิ่งที่เปลี่ยนคือ *มุมของหัว*
# game.Box วาดได้แต่สี่เหลี่ยมตรง ๆ หมุนไม่ได้ — หัวพัดลมจึงวาดด้วย ui.Line
# ซึ่งลากเส้นที่มุมใดก็ได้ (ui เป็นโมดูลเดียวกับที่ bentogame ใช้อยู่ข้างใน)
#
# ตัวควบคุมยังคุม "ตัวเลขตัวเดียว" เหมือนเดิม คือตำแหน่งที่หัวเล็งอยู่
# แล้วค่อยแปลงเป็นมุมตอนวาด — โจทย์ดูซับซ้อนขึ้น แต่ตรรกะควบคุมไม่เปลี่ยนเลย

import bentogame as game
import ui

# --- พารามิเตอร์ของตัวควบคุม (ของจริงคือค่าที่วิศวกรต้องจูน) ---
FAN_ACCEL = 0.5           # เร่งได้แรงแค่ไหนต่อเฟรม
FAN_MAX = 7.0             # ความเร็วหมุนสูงสุดของหัวพัดลม
FAN_FRICTION = 0.85       # ปล่อยแล้วเหลือความเร็วกี่ % ต่อเฟรม
DEADZONE = 10             # ห่างไม่เกินกี่ px ถือว่า "ตรงแล้ว"

PERSON_SPEED = 2.2        # คนเดินเร็วแค่ไหน
WALK_Y = 150              # คนเดินอยู่ระดับนี้
PERSON_W, PERSON_H = 22, 34

FAN_CX = game.WIDTH // 2  # ฐานพัดลมอยู่กลางจอ ไม่ขยับ
FAN_CY = 316              # จุดหมุนของหัวพัดลม
FAN_HALF = 34             # ครึ่งความกว้างของหัวพัดลม
FAN_THICK = 15            # ความหนาของหัว
FLOOR_Y = 352

game.title("AUTO FAN")

# --- ฉาก ---
floor = game.Box(0, FLOOR_Y, game.WIDTH, 4, game.GB_DARK)
stand = game.Box(FAN_CX - 5, FAN_CY, 10, FLOOR_Y - FAN_CY, game.GB_DARK,
                 border=game.GB_DARK, border_w=0)
base = game.Box(FAN_CX - 30, FLOOR_Y - 8, 60, 10, game.GB_DARK,
                border=game.GB_DARK, border_w=0)
hub = game.Box(FAN_CX - 7, FAN_CY - 7, 14, 14, game.GB_LIGHT,
               border=game.GB_LIGHT, border_w=0)

# คนเดิน — หัวกับตัว เพื่อให้ดูออกว่าเป็นคน ไม่ใช่กล่องลอย
person_body = game.Box(0, WALK_Y, PERSON_W, PERSON_H, game.YELLOW,
                       border=game.YELLOW, border_w=0)
person_head = game.Box(0, WALK_Y - 16, 14, 14, game.YELLOW,
                       border=game.YELLOW, border_w=0)

status = game.Text("", 24, 10, game.WHITE)
mode_lamp = game.Box(24, 38, 26, 26, game.GREEN)
state_text = game.Text("", 60, 40, game.WHITE)
counter = game.Text("", 24, 72, game.GB_LIGHT)
game.Text("X = เปิด/ปิด deadzone | Enter = ออก", 24, 100, game.CYAN)

# --- สถานะ ---
person_x = float(game.WIDTH // 2)
person_vx = PERSON_SPEED           # คนเดินไปมา — integrate + reflect เหมือน prep_01
aim_x = float(game.WIDTH // 2)     # หัวพัดลมเล็งไปที่ตำแหน่งไหน (นี่คือตัวที่เราคุม)
fan_speed = 0.0                    # ความเร็วหมุนสะสม
aligned_frames = 0
use_deadzone = True
prev_b = True
head = None

WALK_LEFT = 60
WALK_RIGHT = game.WIDTH - 60 - PERSON_W
AIM_LEFT, AIM_RIGHT = 40, game.WIDTH - 40      # ช่วงที่หัวหมุนได้


def unit_toward(tx, ty):
    """ทิศจากจุดหมุนไปยัง (tx, ty) ยาว 1 หน่วย — ไม่ใช้รากที่สอง

    ปกติต้องใช้ sqrt(dx*dx + dy*dy) ซึ่ง MCU ที่ไม่มีหน่วยประมวลผลทศนิยมทำช้ามาก
    งานฝังตัวจึงใช้สูตรประมาณ "alpha max plus beta min":
        ความยาว ~= max(|dx|,|dy|) + 0.4 * min(|dx|,|dy|)
    คลาดไม่เกิน 8% ซึ่งตาแยกไม่ออกเมื่อใช้กับความยาวหัวพัดลม
    """
    dx, dy = tx - FAN_CX, ty - FAN_CY
    approx = max(abs(dx), abs(dy)) + 0.4 * min(abs(dx), abs(dy))
    if approx < 1:
        return 0.0, -1.0
    return dx / approx, dy / approx


def draw_head():
    """วาดหัวพัดลมให้ตั้งฉากกับทิศที่เล็ง = หน้าพัดลมหันไปทางนั้นพอดี

    หน้าพัดลมเป็นแผ่นกลม มองจากด้านข้างจึงเป็นเส้นตรงหนา ๆ
    ถ้าทิศเล็งคือ (ux, uy) หัวต้องวางตามแนวตั้งฉาก คือ (-uy, ux)
    """
    global head
    if head is not None:
        head.delete()

    ux, uy = unit_toward(aim_x, WALK_Y + PERSON_H / 2)
    px, py = -uy, ux                                  # หมุน 90 องศา
    x1, y1 = FAN_CX + px * FAN_HALF, FAN_CY + py * FAN_HALF
    x2, y2 = FAN_CX - px * FAN_HALF, FAN_CY - py * FAN_HALF
    left, top = int(min(x1, x2)) - 4, int(min(y1, y2)) - 4
    head = ui.Line(x=left, y=top, w=int(abs(x1 - x2)) + 10,
                   h=int(abs(y1 - y2)) + 10,
                   color=game.GB_LIGHTEST, value=FAN_THICK)
    head.add_point(int(x1 - left), int(y1 - top))
    head.add_point(int(x2 - left), int(y2 - top))


draw_head()

# ============================================================================
# แยกเป็นฟังก์ชันย่อยตามลำดับของระบบสมองกลฝังตัว: รับรู้ -> ตัดสินใจ -> สั่งการ
# ทุกไฟล์ในชุดนี้ใช้โครงเดียวกัน อ่านไฟล์หนึ่งเป็น อ่านที่เหลือออกหมด
# ============================================================================


def handle_mode_button(keys):
    """ปุ่ม B สลับโหมด deadzone เปิด/ปิด (debounce แบบเดียวกับ prep_02)"""
    global use_deadzone, aligned_frames, fan_speed, prev_b

    if keys.b and not prev_b:
        use_deadzone = not use_deadzone
        aligned_frames = 0
        fan_speed = 0.0
    prev_b = keys.b


def move_person():
    """คนเดินไปมาเอง (integrate + reflect — ทักษะจาก prep_01)"""
    global person_x, person_vx

    person_x += person_vx
    if person_x < WALK_LEFT:
        person_x = WALK_LEFT                      # ดันกลับเข้าขอบก่อน
        person_vx = -person_vx                    # แล้วค่อยกลับทิศ
    elif person_x > WALK_RIGHT:
        person_x = WALK_RIGHT
        person_vx = -person_vx
    person_body.move_to(person_x, WALK_Y)
    person_head.move_to(person_x + PERSON_W // 2 - 7, WALK_Y - 16)


def sense_error():
    """รับรู้: คนอยู่ตรงไหน เทียบกับที่หัวพัดลมเล็งอยู่"""
    person_center = person_x + PERSON_W / 2
    return person_center - aim_x


def decide_turn(error):
    """ตัดสินใจ: จะหมุนไปทางไหน (หรือไม่หมุนเลย) — คืนค่าว่าหันตรงแล้วหรือยัง"""
    global fan_speed

    zone = DEADZONE if use_deadzone else 0
    if error > zone:
        fan_speed += FAN_ACCEL                    # คนอยู่ขวา -> หมุนไปขวา
        aligned = False
    elif error < -zone:
        fan_speed -= FAN_ACCEL                    # คนอยู่ซ้าย -> หมุนไปซ้าย
        aligned = False
    else:
        # อยู่ใน deadzone แล้ว = "ตรงพอแล้ว" ไม่เร่งเพิ่ม
        # ปล่อยให้ friction ค่อย ๆ หน่วงจนหยุดเอง — ตรงนี้แหละที่กัน hunting
        fan_speed *= FAN_FRICTION
        aligned = True
    return aligned


def act_turn_head():
    """สั่งการ: clamp 2 ชั้น แล้วหมุนหัวพัดลมจริง"""
    global aim_x, fan_speed

    fan_speed = max(-FAN_MAX, min(FAN_MAX, fan_speed))     # ชั้น 1: ความเร็วมอเตอร์
    aim_x += fan_speed
    aim_x = max(AIM_LEFT, min(AIM_RIGHT, aim_x))           # ชั้น 2: ช่วงที่หมุนได้
    draw_head()


def draw_hud(error, aligned):
    """แสดงผล — ส่วนนี้ไม่ตัดสินใจอะไร แค่รายงานสถานะปัจจุบัน"""
    hub.set_color(game.GREEN if aligned else game.GB_LIGHT)
    status.set("%s   err=%+.1f   v=%+.2f"
               % ("ตรงแล้ว " if aligned else "กำลังหมุน", error, fan_speed))
    if use_deadzone:
        mode_lamp.set_color(game.GREEN)
        state_text.set("มี deadzone %d (หัวหยุดนิ่งได้)" % DEADZONE)
    else:
        mode_lamp.set_color(game.RED)
        state_text.set("ไม่มี deadzone (หัวสั่นรอบเป้า)")
    counter.set("หันตรงแล้ว %d เฟรม (ยิ่งมาก = คุมนิ่งกว่า)" % aligned_frames)


def on_each_frame():
    """หนึ่งเฟรม = อ่านปุ่ม -> คนเดิน -> รับรู้ -> ตัดสินใจ -> สั่งการ"""
    global aligned_frames

    keys = game.keys()
    if keys.start:
        return False

    handle_mode_button(keys)
    move_person()
    error = sense_error()
    aligned = decide_turn(error)
    act_turn_head()
    if aligned:
        aligned_frames += 1
    draw_hud(error, aligned)



game.run(on_each_frame, fps=30)

# ------------------------------------------------------------------------------
# ลองเล่นกับมันดู — ตัวอย่างนี้ออกแบบมาให้ "เห็นความต่างด้วยตา":
#
#   1. กด X เพื่อปิด deadzone แล้วดูหัวพัดลม จะเห็นมันสั่นซ้าย-ขวารอบคนไม่หยุด
#      แม้คนจะเดินช้า ๆ — นี่คือ hunting ตัวจริง และเป็นเหตุผลทั้งหมดที่ deadzone มีอยู่
#      ดูค่า "หันตรงแล้ว" ประกอบ จะเห็นว่าโหมดไม่มี deadzone แทบไม่เคยนิ่งเลย
#
#   2. ตั้ง FAN_FRICTION = 1.0 (ไม่มีแรงเสียดทาน) แล้วรัน หัวพัดลมจะไม่มีวันหยุด
#      เพราะไม่มีอะไรลดความเร็วที่สะสมไว้ — friction ไม่ใช่ของประดับ
#      **deadzone อย่างเดียวไม่พอ ต้องมีทั้งคู่**
#
#   3. ตั้ง FAN_ACCEL = 3.0 (เร่งแรงมาก) แล้วดูว่าหัวหมุนเลยเป้าไปไกลแค่ไหนก่อนจะกลับมา
#
#   4. ลองทำ "เล็งล่วงหน้า": เปลี่ยน person_center เป็น
#          person_center + person_vx * 10
#      คือเล็งไปที่ตำแหน่งที่คนจะไปอยู่ในอีก 10 เฟรม แล้วเทียบ "หันตรงแล้ว" ดูว่าดีขึ้นไหม
#
#   5. **ลบ clamp ชั้นที่สอง (บรรทัด aim_x = max(AIM_LEFT, ...)) ออก** แล้วดูสองขั้น:
#
#      ก) ด้วยค่าเริ่มต้น **จะไม่เห็นอะไรเปลี่ยนเลย** หัวยังหมุนอยู่ในช่วงเดิมเป๊ะ
#         เพราะคนเดินอยู่ในช่วง 73–719 ซึ่งแคบกว่าลิมิตของหัว (40–752) อยู่แล้ว
#         และคนเดินช้าพอที่หัวจะไม่เหวี่ยงเลยเป้าไปไกล — clamp จึงไม่เคยได้ทำงาน
#
#      ข) ทีนี้เปลี่ยน PERSON_SPEED เป็น 9.0 และ FAN_MAX เป็น 12.0 แล้วรันใหม่
#         **หัวจะเหวี่ยงเลยขอบจอออกไปจนหายไปเลย** (วัดได้ไกลสุดถึง x=811
#         ทั้งที่ลิมิตคือ 752) เพราะความเฉื่อยที่สะสมไว้พาเลยเป้าไปไกลกว่าเดิมมาก
#
#      บทเรียนอยู่ที่ข้อ ก): **clamp ที่ไม่เคยทำงานตอนทดสอบ ไม่ใช่ clamp ที่ไม่จำเป็น**
#      มันคือ clamp ที่รอเงื่อนไขหน้างานอยู่ ระบบจริงเจอของเร็วกว่าที่เราทดสอบเสมอ
#      กลไกจริงหมุนได้จำกัดมุมเสมอ — ระบบที่ไม่ clamp จะพังที่ปลายทาง
#
# ทักษะนี้ใช้ที่ไหนได้อีก: กล้องวงจรปิดที่หมุนตามวัตถุ, จานดาวเทียมตามสัญญาณ,
#   แขนกลจับชิ้นงาน, เทอร์โมสตัทแอร์ (ไม่ปรับทุก 0.1 องศา ไม่งั้นคอมเพรสเซอร์พัง)
#   — ทุกตัวคือ sense → decide → act + deadzone + clamp
