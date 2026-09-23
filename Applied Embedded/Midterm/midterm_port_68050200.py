# midterm_port_skeleton.py — โครงเริ่มต้นข้อสอบกลางภาค ชุด G2 (Container Terminal Crane Monitor)
#
# *** ไฟล์นี้แจกให้ทุกคนในกลุ่มชุด G2 ใช้เป็นจุดตั้งต้นได้เลย ***
#
# ================== วิธีใช้ ==================
#
#   1. เปลี่ยน SID ข้างล่างเป็นรหัสนิสิตของคุณ
#   2. รันดูก่อน — จะเห็นลานตู้คอนเทนเนอร์ เขตระวัง เขตอันตรายใต้เครน รถหัวลาก และแถบข้อความ
#      แต่ยังไม่มีอะไรขยับ ปุ่มยังไม่ทำงาน (คุณต้องเขียน)
#   3. เขียนส่วนที่เป็น TODO ให้ครบ แล้วเปลี่ยนชื่อไฟล์เป็น midterm_port_<รหัสนิสิต>.py
#
# ================== สิ่งที่แจกให้ (ไม่ต้องเขียนเอง) ==================
#
#   ค่าคงที่ทั้งหมด (รวมค่าที่คำนวณจาก S ของคุณ) · ฉากทั้งหมด · ตัวแปรสถานะ
#   draw_hud() ครบแล้ว · on_each_frame() เรียกฟังก์ชันตามลำดับที่ถูกต้องแล้ว
#
# ================== สิ่งที่คุณต้องเขียนเอง (5 ฟังก์ชัน) ==================
#
#   - handle_release_button() ปุ่มปลดล็อก กดหนึ่งครั้ง = หนึ่งครั้ง (debounce)
#   - move_hazard_zone()      เขตอันตรายเลื่อนขึ้น-ลงแล้วสะท้อน (integrate + reflect)
#   - drive_tractor()         รถหัวลากขับ 4 ทิศแบบมีน้ำหนัก (accel / friction / clamp 2 ชั้น)
#   - sense_zones()           รถทับเขตไหน + นับ "ครั้งที่เข้า" (game.hit + edge detection)
#   - decide_state()          state machine 4 สถานะ + กฎความปลอดภัย
#
# ห้ามเปลี่ยนชื่อตัวแปรที่แจกให้ — draw_hud() อ่านตัวแปรพวกนี้ไปแสดงบนจอ
# ห้ามพิมพ์ตัวเลขทับค่าที่คำนวณจาก S — ค่าต้องตรงกับรหัสของคุณ

import bentogame as game

SID = 68050200                     # <<< เปลี่ยนเป็นรหัสนิสิตของคุณ
S = SID % 7

# --- ค่าที่ผูกกับรหัสนิสิต ---
CAUTION_W = 140 + S * 12            # ความกว้างเขตระวัง
HAZARD_SPEED = 0.8 + S * 0.25       # เขตอันตรายเลื่อนเร็วแค่ไหนต่อเฟรม
HALT_AT = 2 + S % 3                 # เข้าเขตอันตรายครบกี่ครั้งถึงล็อก

# --- ผังหน้าจอ (จอกว้าง 792 สูง 398 · แถบข้อความ y < 130 · พื้น y = 352) ---
CAUTION_Y, CAUTION_H = 150, 170
CAUTION_X = game.WIDTH - 180 - CAUTION_W    # ขอบขวาของเขตระวังอยู่ที่ x = 612 เสมอ
HAZARD_X, HAZARD_W, HAZARD_H = 292, 150, 70
HAZARD_TOP, HAZARD_BOTTOM = 130, 320     # ช่วงที่เขตอันตรายเลื่อนได้ (ขอบบน/ขอบล่าง)
LABEL_Y = 326                            # ป้ายชื่อเขต ใต้ช่วงที่เขตเลื่อน

TRACTOR_W, TRACTOR_H = 46, 30
TRACTOR_START_X, TRACTOR_START_Y = 686, 300
TRACTOR_TOP, TRACTOR_BOTTOM = 130, 348   # รถขับได้ในช่วง y นี้ (ใต้แถบข้อความ เหนือพื้น)
TRACTOR_ACCEL, TRACTOR_MAX, TRACTOR_FRICTION = 0.9, 6.0, 0.86

CLEAR, CAUTION, HAZARD, HALT = 0, 1, 2, 3
STATE_NAME = ["CLEAR", "CAUTION", "HAZARD", "HALT"]
STATE_COLOR = [game.CYAN, game.YELLOW, game.RED, game.RED]

game.title("CRANE MONITOR")

# --- ฉากลานตู้คอนเทนเนอร์ ---
floor = game.Box(0, 352, game.WIDTH, 4, game.GB_DARK)
caution_zone = game.Box(CAUTION_X, CAUTION_Y, CAUTION_W, CAUTION_H, game.BLACK,
                        border=game.YELLOW, border_w=3)
hazard_zone = game.Box(HAZARD_X, HAZARD_TOP, HAZARD_W, HAZARD_H, game.BLACK,
                       border=game.RED, border_w=3)
game.Text("CAUTION", CAUTION_X + 6, LABEL_Y, game.YELLOW)
game.Text("HAZARD", HAZARD_X + 6, LABEL_Y, game.RED)

tractor = game.Box(TRACTOR_START_X, TRACTOR_START_Y, TRACTOR_W, TRACTOR_H, game.CYAN)

status = game.Text("", 24, 10, game.WHITE)
lamp = game.Box(24, 38, 26, 26, game.CYAN)
state_text = game.Text("", 60, 40, game.WHITE)
counter = game.Text("", 24, 72, game.GB_LIGHT)
game.Text("ลูกศร = ขับรถ | Z = ปลดล็อก | Backspace = ออก", 24, 100, game.CYAN)

# --- สถานะทั้งหมด ---
tractor_x, tractor_y = float(TRACTOR_START_X), float(TRACTOR_START_Y)
tractor_vx, tractor_vy = 0.0, 0.0
hazard_y = float(HAZARD_TOP)
hazard_vy = HAZARD_SPEED
state = CLEAR
caution_entries = 0
hazard_entries = 0
releases = 0                        # นับการกดปลดล็อก — ให้ปุ่มมีสัญญาณตอบกลับเสมอ
was_in_caution = False              # จำเฟรมก่อน เพื่อแยก "อยู่ในเขต" กับ "เพิ่งเข้า"
was_in_hazard = False
prev_a = True                       # True = กันปุ่มที่ค้างมาจากหน้าจอก่อน


# ============================================================================
# ตั้งแต่บรรทัดนี้ลงไปคือส่วนที่คุณต้องเขียนเอง
#
# แยกเป็นฟังก์ชันย่อยตามลำดับ อ่านปุ่ม -> ขยับของ -> รับรู้ -> ตัดสินใจ -> แสดงผล
# เหมือนตัวอย่างเตรียมสอบทุกไฟล์
# ============================================================================


def handle_release_button(keys):
    """ปุ่มปลดล็อก — กดหนึ่งครั้งนับหนึ่งครั้ง (debounce)"""
    global state, caution_entries, hazard_entries, releases, prev_a

    # TODO: กด A (คีย์ Z) หนึ่งครั้ง -> ทำครั้งเดียว กดค้างไว้ต้องไม่ทำซ้ำ
    #       pattern ปุ่มแบบนี้อยู่ใน prep_02 (read_call_button) และ prep_04
    #       เมื่อกดหนึ่งครั้ง:
    #         - releases เพิ่ม 1 (สัญญาณตอบกลับ ต้องเห็นทุกครั้งที่กด แม้ไม่ได้ล็อกอยู่)
    #         - ล้างตัวนับ caution_entries และ hazard_entries เป็น 0
    #         - ถ้าล็อกอยู่ (HALT) ให้กลับเป็น CLEAR
    #       อย่าลืมจำสถานะปุ่มของเฟรมนี้ไว้ใน prev_a ทุกเฟรม
    pressed = keys.a and not prev_a
    
    if pressed:
        releases += 1
        caution_entries = 0
        hazard_entries = 0
        state = CLEAR

    
    prev_a = keys.a
    return pressed


def move_hazard_zone():
    """เขตอันตรายเลื่อนขึ้น-ลงเอง (integrate + reflect เหมือนลูก Pong)"""
    global hazard_y, hazard_vy

    # TODO: hazard_y เดินทีละ hazard_vy ทุกเฟรม
    #       ถ้าหลุดขอบบน (HAZARD_TOP) หรือขอบล่าง (ขอบล่างของ "กล่อง" ต้องไม่เกิน HAZARD_BOTTOM)
    #       ให้สะท้อนกลับ — pattern เดียวกับลูก Pong และ prep_01
    #       คิดเองด้วยว่าต้องทำอะไรกับ hazard_y ก่อนกลับทิศ ถ้าไม่ทำจะเกิดอะไรขึ้น
    hazard_y += hazard_vy
    
    if hazard_y <= HAZARD_TOP:
        hazard_y = HAZARD_TOP
        hazard_vy = -hazard_vy
        
    if hazard_y >= HAZARD_BOTTOM-HAZARD_H:
        hazard_y = HAZARD_BOTTOM-HAZARD_H
        hazard_vy = -hazard_vy
        
    hazard_zone.move_to(HAZARD_X, hazard_y)


def drive_tractor(keys):
    """ขับรถหัวลากแบบมีน้ำหนัก: เร่ง -> แรงเสียดทาน -> จำกัด 2 ชั้น"""
    global tractor_x, tractor_y, tractor_vx, tractor_vy

    # TODO: 1. ถ้าล็อกอยู่ (HALT) รถต้องขับไม่ได้เลย
    #       2. ไม่ได้ล็อก: กดลูกศรทิศไหน = เร่งความเร็วแกนนั้นทีละ TRACTOR_ACCEL
    #          ไม่กดแกนนั้น (หรือกดสองทิศของแกนเดียวกันพร้อมกัน) = คูณความเร็วแกนนั้น
    #          ด้วย TRACTOR_FRICTION (ไถลต่อแล้วค่อย ๆ หยุด) — ขณะกดอยู่ไม่ต้องคูณ
    #          ทำแยกกันทั้งแกน x และแกน y — แบบเดียวกับไม้ Pong ของผู้เล่น (pong_step2)
    #       3. clamp ชั้นที่ 1: ความเร็วแต่ละแกนอยู่ในช่วง -TRACTOR_MAX..TRACTOR_MAX
    #       4. บวกความเร็วเข้าตำแหน่ง
    #       5. clamp ชั้นที่ 2: ตัวรถทั้งคันอยู่ในจอ
    #          x อยู่ในช่วง 0..game.WIDTH - TRACTOR_W · y อยู่ในช่วง TRACTOR_TOP..TRACTOR_BOTTOM - TRACTOR_H
    if state == HALT:
        pass
    else:
        tractor_x += tractor_vx
        tractor_y += tractor_vy
        
        if keys.left and not keys.right:                       
            tractor_vx -= TRACTOR_ACCEL
        if keys.right and not keys.left:
            tractor_vx += TRACTOR_ACCEL
            
        if keys.up and not keys.down:
            tractor_vy -= TRACTOR_ACCEL
        if keys.down and not keys.up:
            tractor_vy += TRACTOR_ACCEL
            
        else:
            tractor_vx *= TRACTOR_FRICTION
            tractor_vy *= TRACTOR_FRICTION

    tractor_vx = max(-TRACTOR_MAX,min(TRACTOR_MAX, tractor_vx))
    tractor_vy = max(-TRACTOR_MAX,min(TRACTOR_MAX, tractor_vy))

    tractor_x = max(0, min(game.WIDTH - TRACTOR_W,tractor_x + tractor_vx ))
    tractor_y = max(TRACTOR_TOP, min(TRACTOR_BOTTOM - TRACTOR_H,tractor_y + tractor_vy ))
    
    tractor.move_to(tractor_x, tractor_y)

    
                    
def sense_zones():
    """รับรู้: อยู่ในเขตไหน และ 'เพิ่งเข้า' เขตไหน — คืนค่าให้ส่วนตัดสินใจใช้ต่อ"""
    global caution_entries, hazard_entries, was_in_caution, was_in_hazard

    # TODO: ตรวจการทับด้วย game.hit() ทั้งสองเขต (ต้องเรียกหลังรถและเขต move_to แล้ว)
    #       นับ "ครั้งที่เข้า" แยกสองเขต ลงใน caution_entries / hazard_entries
    #       นับ 1 ทุกครั้งที่ "เริ่มทับ" (เฟรมก่อนไม่ทับ เฟรมนี้ทับ) — เข้าออก 3 ครั้งต้องได้ 3 ไม่ใช่ 300
    #       ใช้หลักเดียวกับปุ่ม debounce (keys.a and not prev_a ใน prep_02) แต่ใช้กับการทับเขต
    #       ด้วยตัวแปรจำเฟรมก่อน was_in_caution / was_in_hazard (ดู sense_car ใน practice_gate)
    #       ระวัง: alert_count ใน prep_04 นับ "เฟรมที่อยู่ในเขต" ไม่ใช่ "ครั้งที่เข้า"
    #       อย่าลืมอัปเดต was_in_caution / was_in_hazard ทุกเฟรมก่อน return
    #       ต้อง return ค่าสองตัว: (in_caution, in_hazard)
    in_caution = game.hit(tractor, caution_zone)
    in_hazard = game.hit(tractor, hazard_zone)
    
    if in_caution and not was_in_caution:
        caution_entries += 1
    
    if in_hazard and not was_in_hazard:
        hazard_entries += 1

    was_in_caution = in_caution
    was_in_hazard = in_hazard
    
    return in_caution, in_hazard

def decide_state(in_caution, in_hazard):
    """ตัดสินใจ: state machine 4 สถานะ — ลำดับการเช็คคือกติกาความปลอดภัย"""
    global state, tractor_vx, tractor_vy,hazard_entries

    # TODO: เลือก state ของเฟรมนี้
    #   HALT    — ถ้าล็อกอยู่แล้ว ให้ล็อกค้างไว้ (ปลดได้ด้วยปุ่มอย่างเดียว)
    #             hazard_entries ถึง HALT_AT เมื่อไร -> HALT ทันทีในเฟรมนั้น
    #   HAZARD  — รถทับเขตอันตราย -> HAZARD และสั่งหยุด = ตั้งความเร็วทั้งสองแกนเป็น 0
    #             (รถไถลต่อไม่ได้ แต่ยังกดลูกศรค่อย ๆ ขับออกจากเขตได้ — อย่าล็อกการขับ)
    #   CAUTION — รถทับเขตระวัง -> CAUTION
    #   CLEAR   — ไม่ทับเขตไหนเลย
    #
    #   *** รถทับทั้งสองเขตพร้อมกัน ต้องเป็น HAZARD ไม่ใช่ CAUTION ***
    #   ลำดับการเช็คของคุณคือสิ่งที่ตัดสินเรื่องนี้ — คิดเอง
    
    if state == HALT:
        pass
        
    elif in_hazard:
        state = HAZARD
        tractor_vx, tractor_vy = 0.0, 0.0
        if hazard_entries >= HALT_AT:
            state = HALT

    elif in_caution:
        state = CAUTION
    else:
        
        state = CLEAR
            
    
            

    


def draw_hud():
    """แสดงผล — [แจกให้] ส่วนนี้ไม่ตัดสินใจอะไรเลย แค่รายงานสถานะปัจจุบัน"""
    tractor.set_color(STATE_COLOR[state])
    lamp.set_color(STATE_COLOR[state])
    if state == HALT:
        state_text.set("HALT - กด Z เพื่อปลดล็อก")
    elif state == HAZARD:
        state_text.set("HAZARD - หยุดรถ!")
    elif state == CAUTION:
        state_text.set("CAUTION - ระวัง ใกล้รางเครน")
    else:
        state_text.set("CLEAR")
    status.set("v=(%+.1f, %+.1f)  release %d" % (tractor_vx, tractor_vy, releases))
    counter.set("CAUTION %d | HAZARD %d/%d | S=%d"
                % (caution_entries, hazard_entries, HALT_AT, S))


def on_each_frame():
    """[แจกให้] หนึ่งเฟรม = อ่านปุ่ม -> ขยับของ -> รับรู้ -> ตัดสินใจ -> แสดงผล"""
    keys = game.keys()
    handle_release_button(keys)
    move_hazard_zone()
    drive_tractor(keys)
    in_caution, in_hazard = sense_zones()
    decide_state(in_caution, in_hazard)
    draw_hud()


game.run(on_each_frame, fps=30)
