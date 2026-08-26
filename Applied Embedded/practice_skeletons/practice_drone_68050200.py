# practice_drone_skeleton.py — โครงเริ่มต้นของข้อสอบซ้อม ข้อ 2 (Drone Altitude Hold)
#
# *** ไฟล์นี้แจกให้ทุกคน ใช้เป็นจุดตั้งต้นได้เลย ***
#
# ================== ทำไมถึงมีไฟล์นี้ ==================
#
# ข้อสอบจริงข้อ 2 จะแจกไฟล์โครงแบบนี้ให้เหมือนกัน (`midterm_tracker_skeleton.py`)
# ไฟล์นี้จึงมีไว้ให้คุณ **คุ้นกับวิธีทำงานแบบนั้นก่อนวันสอบ** — เปิดโครงที่มีคนวางฉาก
# ไว้ให้แล้ว อ่านให้เข้าใจว่าเขาให้อะไรมาบ้าง แล้วเขียนเฉพาะส่วนที่เป็นตัวควบคุม
#
# ส่วนข้อซ้อม 1 (ไม้กั้น) มีโครงตัวช่วยให้เหมือนกัน (`practice_gate_skeleton.py`)
# **แต่ข้อสอบจริงข้อ 1 ไม่มีโครงให้** — อ่านหมายเหตุหัวไฟล์นั้นก่อนใช้:
# ลองจากไฟล์เปล่าก่อนอย่างน้อย 1 ชั่วโมง แล้วค่อยเปิดโครงถ้าติดจริง
#
# ================== วิธีใช้ ==================
#
#   1. เปลี่ยน SID ข้างล่างเป็นรหัสนิสิตของคุณ
#   2. รันดูก่อน — จะเห็นฉาก โดรน และเส้นเป้าหมาย แต่ยังไม่มีอะไรขยับ
#   3. เขียนส่วนที่เป็น TODO ให้ครบ แล้วเปลี่ยนชื่อไฟล์เป็น practice_drone.py
#
# ================== สิ่งที่แจกให้ (ไม่ต้องเขียนเอง) ==================
#
#   alt_to_y(a)  แปลงความสูงจากพื้น -> พิกัด y ของตัวโดรน
#   ฉากพื้น ลานจอด เสา โดรน ใบพัด เส้นเป้าหมาย และแถบข้อความทั้งหมด
#
# ================== สิ่งที่คุณต้องเขียนเอง ==================
#
#   - เส้นเป้าหมายเลื่อนขึ้น-ลงแล้วสะท้อน
#   - ลมกระโชกจากผู้เล่น (ลูกศรขึ้น/ลง)
#   - ตัวควบคุมมอเตอร์ sense -> decide -> act พร้อม deadzone
#   - แรงโน้มถ่วงที่ดึงลงทุกเฟรม และ clamp 2 ชั้น
#   - ปุ่มสลับโหมด SMOOTH / BANG-BANG (debounce)
#   - ตัวชี้วัดและข้อความบนจอ
#
# ================== กับดักหลักของข้อนี้ ==================
#
# บนจอ ค่า y น้อย = อยู่สูง แต่ "ความสูงของโดรน" คิดเป็น "สูงจากพื้น" ซึ่งกลับทางกัน
# โครงนี้จึงเก็บ alt เป็นความสูงจริง แล้วแปลงเป็น y ตอนวาดด้วย alt_to_y()
# ถ้าคุณเผลอเก็บเป็น y ตรง ๆ เครื่องหมายของ error และแรงยกจะกลับหมด
# **โค้ดจะรันได้ ไม่ error แต่โดรนจะบินหนีเป้าแทนที่จะเข้าหา** — บั๊กแบบนี้หายากที่สุด

import bentogame as game
import ui

SID = 68050200                      # <<< เปลี่ยนเป็นรหัสนิสิตของคุณ
P2 = (SID // 100) % 4

# --- ค่าที่ผูกกับรหัสนิสิต ---
TARGET_SPEED = 0.8 + P2 * 0.3
DEADZONE = 6 + P2 * 4

THRUST_ACCEL = 0.35                 # มอเตอร์เร่งแรงยกได้เร็วแค่ไหนต่อเฟรม
THRUST_MAX = 4.5
THRUST_FRICTION = 0.88
GRAVITY = 0.5                       # ดึงลงทุกเฟรม — โดรนไม่มีวันลอยนิ่งเองโดยไม่ใช้มอเตอร์
GUST = 1.6                          # ลมกระโชกที่ผู้เล่นยิงใส่

# --- เรขาคณิตของฉาก ---
# แถบข้อความกินพื้นที่ y=0..104 -> วัตถุทุกอย่างต้องเริ่มที่ y >= 120
GROUND_Y = game.HEIGHT - 46         # ระดับพื้นดิน (พิกัด y)
SKY_TOP = 130                       # เพดานบินสูงสุด (พิกัด y)
DRONE_W, DRONE_H = 54, 14
MAX_ALT = GROUND_Y - SKY_TOP - DRONE_H      # ความสูงสูงสุดที่บินได้

TARGET_TOP = SKY_TOP + 10
TARGET_BOTTOM = GROUND_Y - 60

game.title("DRONE ALTITUDE")

# --- ฉาก: พื้น ลานจอด และเสาสูงให้เทียบระดับ ---
ground = game.Box(0, GROUND_Y, game.WIDTH, 4, game.GB_DARK)
pad = game.Box(330, GROUND_Y - 6, 130, 6, game.GB_LIGHT,
               border=game.GB_LIGHT, border_w=0)
for tx in (120, 660):
    game.Box(tx, GROUND_Y - 90, 16, 90, game.GB_DARK,
             border=game.GB_DARK, border_w=0)

# [แจกให้] เส้นเป้าหมายแบบเส้นประ: ให้ดูเป็น "เส้นอ้างอิงที่ต้องเล็ง" ไม่ใช่ของแข็ง
# สร้างขีดทั้งหมดครั้งเดียวไว้แล้ว คุณแค่ .pos() เลื่อนแต่ละขีดใน move_target()
TARGET_X0, TARGET_X1 = 60, game.WIDTH - 60
DASH_LEN, GAP_LEN = 20, 14
DASH_PERIOD = DASH_LEN + GAP_LEN
N_DASHES = (TARGET_X1 - TARGET_X0) // DASH_PERIOD

target_dashes = []
for _i in range(N_DASHES):
    _seg = ui.Line(x=TARGET_X0 + _i * DASH_PERIOD, y=TARGET_TOP,
                   w=DASH_LEN + 4, h=6, color=game.YELLOW, value=4)
    _seg.add_point(2, 3)
    _seg.add_point(DASH_LEN + 2, 3)
    target_dashes.append(_seg)

# โดรน: ตัวเครื่อง + ใบพัดสองข้าง (ให้ดูเป็นอากาศยาน ไม่ใช่กล่องลอย)
drone = game.Box(370, 260, DRONE_W, DRONE_H, game.CYAN,
                 border=game.CYAN, border_w=0)
rotor_l = game.Box(360, 254, 22, 4, game.GB_LIGHTEST,
                   border=game.GB_LIGHTEST, border_w=0)
rotor_r = game.Box(412, 254, 22, 4, game.GB_LIGHTEST,
                   border=game.GB_LIGHTEST, border_w=0)

# ข้อความเริ่มต้นบอกว่าแต่ละบรรทัดเป็นของใคร — เขียน draw_hud() แล้วจะถูกแทนที่เอง
status = game.Text("(status: ระดับได้/กำลังปรับ + err)", 24, 10, game.WHITE)

# --- แถบบอกโหมด: ไฟสี + ชื่อโหมดเป็นบรรทัดของตัวเอง ---
# จุดประสงค์ทั้งหมดของตัวอย่างนี้คือ "เปรียบเทียบสองโหมด" ถ้าดูไม่ออกว่าอยู่โหมดไหน
# ตัวอย่างก็ไม่ได้สอนอะไรเลย จึงต้องเห็นชัดจากระยะไกล
mode_lamp = game.Box(24, 38, 26, 26, game.GREEN)
state_text = game.Text("(state_text: โหมดที่ใช้อยู่)", 60, 40, game.WHITE)

counter = game.Text("(counter: นิ่งได้กี่เฟรม + P2)", 24, 72, game.GB_LIGHT)
game.Text("ขึ้น/ลง = ยิงลม | X = สลับโหมด | Enter = ออก", 24, 100, game.CYAN)

# --- สถานะทั้งหมด ---
target_y = float(game.HEIGHT // 2)  # ระดับเป้าหมาย เก็บเป็นพิกัด y
target_vy = TARGET_SPEED
alt = 100.0                         # ความสูงของโดรนจากพื้น (ไม่ใช่ y!)
thrust = 0.0                        # แรงยกสะสมจากมอเตอร์ (บวก = ดันขึ้น)
in_range_frames = 0
gusts = 0                           # ผู้เล่นยิงลมไปกี่เฟรม
smooth_mode = True
prev_b = True


def alt_to_y(a):
    """[แจกให้] แปลงความสูงจากพื้น -> พิกัด y ของตัวโดรน"""
    return GROUND_Y - DRONE_H - a


# ============================================================================
# ตั้งแต่บรรทัดนี้ลงไปคือส่วนที่คุณต้องเขียนเอง
#
# แนะนำให้แยกเป็นฟังก์ชันย่อยตามลำดับ รับรู้ -> ตัดสินใจ -> สั่งการ
# เหมือนที่เห็นในตัวอย่างเตรียมสอบทุกไฟล์ จะเขียนและดีบักง่ายกว่ามาก
# ============================================================================


def handle_mode_button(keys):
    #"""ปุ่ม B (คีย์ X) สลับ SMOOTH/BANG-BANG — กดหนึ่งครั้งสลับหนึ่งครั้ง"""
    global smooth_mode, in_range_frames, thrust, prev_b

    if keys.b and not prev_b:
        smooth_mode = not smooth_mode
        in_range_frames = 0
        thrust = 0.0
    prev_b = keys.b


def move_target():
    """ระดับเป้าหมายเลื่อนขึ้น-ลงเอง"""
    global target_y, target_vy

    target_y += target_vy
    if target_y < TARGET_TOP:
        target_y = TARGET_TOP          
        target_vy = -target_vy         
    elif target_y > TARGET_BOTTOM:
        target_y = TARGET_BOTTOM
        target_vy = -target_vy
        
    for i, seg in enumerate(target_dashes):
        seg.pos(TARGET_X0 + i * DASH_PERIOD, int(target_y))


def player_gust(keys):
    #"""ลมกระโชกที่ผู้เล่นยิงใส่ — คืนค่าแรงที่บวกเข้ากับความสูงในเฟรมนี้"""
    global gusts

    # TODO: ลูกศรขึ้น = ดันขึ้น (+GUST) · ลูกศรลง = กดลง (-GUST)
    #       นับจำนวนเฟรมที่ยิงลมไว้ใน gusts เพื่อแสดงบนจอ
    #       นี่ไม่ใช่การบังคับโดรน — ตัวควบคุมยังทำงานของมันเต็มที่
    push = 0.0
    if keys.up:
        push = GUST
        gusts += 1
    elif keys.down:
        push = -GUST
        gusts += 1
    return push


def sense_error():
    #"""รับรู้: โดรนอยู่ต่ำหรือสูงกว่าเป้าหมายเท่าไร"""
    # TODO: แปลง target_y (พิกัดจอ) เป็น "ความสูงที่ต้องการ" ก่อน
    #       แล้วค่อยลบด้วย alt — ต้องเทียบในหน่วยเดียวกันเสมอ
    #       คืนค่า error โดยให้ค่าบวก = โดรนต่ำไป ต้องยกขึ้น
    target_alt = GROUND_Y - DRONE_H - target_y
    error = target_alt - alt
    return error


def decide_thrust(error):
    """ตัดสินใจ: จะสั่งมอเตอร์เท่าไร — คืนค่าว่าเข้าระดับแล้วหรือยัง"""
    global thrust

    in_range = False
 
    if smooth_mode:
        if error > DEADZONE:
            thrust += THRUST_ACCEL
        elif error < -DEADZONE:
            thrust -= THRUST_ACCEL  
        else:
            thrust *= THRUST_FRICTION
            in_range = True
        thrust = max(-THRUST_MAX, min(THRUST_MAX, thrust))
    

    else:
        thrust = THRUST_MAX if error > 0 else -THRUST_MAX
        in_range = abs(error) <= DEADZONE
    return in_range


def act_fly(push):
    #"""สั่งการ: มอเตอร์ยกขึ้น แรงโน้มถ่วงดึงลง บวกลมจากผู้เล่น"""
    global alt
    
    alt += thrust
    alt -= GRAVITY
    alt += push
    alt = max(0.0, min(MAX_ALT, alt))

    y = alt_to_y(alt)
    drone.move_to(370, y)
    rotor_l.move_to(360, y - 6)
    rotor_r.move_to(412, y - 6)



def draw_hud(error, in_range):
    #"""แสดงผล — ส่วนนี้ไม่ตัดสินใจอะไร แค่รายงานสถานะปัจจุบัน"""
    # TODO: drone      -> เขียวเมื่อเข้าระดับ, ฟ้าเมื่อกำลังปรับ
    #       status     -> ระดับได้/กำลังปรับ + error + แรงมอเตอร์
    #       mode_lamp  -> เขียวเมื่อ SMOOTH, แดงเมื่อ BANG-BANG
    #       state_text -> บอกว่าโหมดไหน และโหมดนั้นต่างกันยังไง
    #       counter    -> in_range_frames, ความสูง, ลมที่ยิง, และ P2 ของคุณ
    #
    # ตัวอย่างสองบรรทัดแรกให้เลย (ที่เหลือรูปแบบเดียวกัน):
    #     drone.set_color(game.GREEN if in_range else game.CYAN)
    #     mode_lamp.set_color(game.GREEN if smooth_mode else game.RED)
    # ส่วนข้อความใช้ .set() กับ % เช่น
    #     counter.set("นิ่งได้ %d เฟรม" % in_range_frames)
    #
    # ระวัง: ข้อความยาวเกิน 126 ไบต์จะถูกตัดทิ้งเงียบ ๆ (ภาษาไทย = 3 ไบต์/ตัว)
    drone.set_color(game.GREEN if in_range else game.CYAN)
    status.set("ระดับ:%s error:%d thrust:%.1f" % ("OK" if in_range else "กำลังปรับ", error, thrust))
    mode_lamp.set_color(game.GREEN if smooth_mode else game.RED)
    state_text.set("SMOOTH" if smooth_mode else "BANG-BANG")
    counter.set("นิ่งได้:%d เฟรม ความสูง:%d ลม:%d P2:%d" % (in_range_frames, alt, gusts, P2))


def on_each_frame():
    #"""หนึ่งเฟรม = อ่านปุ่ม -> ขยับเป้า -> รับรู้ -> ตัดสินใจ -> สั่งการ"""
    global in_range_frames

    keys = game.keys()
    if keys.start:
        return False

    handle_mode_button(keys)
    move_target()
    push = player_gust(keys)
    error = sense_error()
    in_range = decide_thrust(error)
    act_fly(push)
    if in_range:
        in_range_frames += 1
    draw_hud(error, in_range)


game.run(on_each_frame, fps=30)
