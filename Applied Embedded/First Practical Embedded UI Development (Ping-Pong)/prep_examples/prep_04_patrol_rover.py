# prep_04_patrol_rover.py — เตรียมสอบกลางภาค ตัวอย่างที่ 4
#
# ทักษะที่ทบทวน: AABB collision (คาบ 4, 6) + state machine (คาบ 2, 7)
#                 integrate + reflect          (คาบ 5)
#
# เรื่องราว: โกดังสินค้าใช้หุ่นยนต์ลาดตระเวน (AGV) วิ่งตรวจพื้นที่เองตลอดเวลา
#   ชนผนังก็สะท้อนไปเรื่อย ๆ แต่มี **โซนอันตราย** ที่หุ่นห้ามเข้า
#   ถ้าเข้าไปแล้วอยู่นานเกินกำหนด ระบบต้องสั่งหยุดฉุกเฉิน
#
# วิธีเล่น: **ดูมันทำงานเอง** · Z/Space = ปลดล็อกหลังหยุดฉุกเฉิน
#           ลูกศรซ้าย/ขวา = ย้ายโซนอันตรายไปขวางทางหุ่น (ลองแกล้งมันดู)
#
# ================== หัวใจที่ต้องจำให้ได้ ==================
#
#   1. AABB = กล่องสองใบชนกันเมื่อ "ทับกันทั้งแกน X และแกน Y" พร้อมกันเท่านั้น
#   2. "อยู่ในโซนตอนนี้" กับ "อยู่ในโซนติดต่อกันมานานแค่ไหน" เป็นคนละคำถาม
#      อันหลังต้องมีตัวนับ และตัวนับต้อง **รีเซ็ตเมื่อออกจากโซน**
#   3. state เป็นแค่ตัวเลข มันไม่ได้หยุดการเคลื่อนที่เอง — ต้องสั่งความเร็วเป็น 0 ด้วย
#   4. ทุกปุ่มต้องมีสัญญาณตอบกลับ ไม่งั้นผู้ใช้แยกไม่ออกว่าปุ่มเสียหรือกดแล้วไม่มีอะไรต้องทำ

import bentogame as game

ROVER_W, ROVER_H = 44, 28
ALERT_LIMIT = 50                   # อยู่ในโซนติดต่อกันครบกี่เฟรมแล้วหยุดฉุกเฉิน

ZONE_W, ZONE_H = 150, 130
ZONE_Y = 150
ZONE_SPEED = 6                     # ผู้เล่นย้ายโซนได้เร็วแค่ไหน

WALL_TOP, WALL_BOTTOM = 124, 344   # กรอบพื้นที่ลาดตระเวน (ใต้แถบข้อความ)

PATROL, ALERT, STOPPED = 0, 1, 2
STATE_NAME = ["ลาดตระเวน", "เตือน", "หยุดฉุกเฉิน"]
STATE_COLOR = [game.GREEN, game.YELLOW, game.RED]

game.title("PATROL ROVER")

# --- ฉากโกดัง: พื้น + ชั้นวางของสองแถว ให้ดูเป็นโกดัง ไม่ใช่จอดำเปล่า ---
floor = game.Box(0, WALL_BOTTOM, game.WIDTH, 4, game.GB_DARK)
ceiling = game.Box(0, WALL_TOP - 4, game.WIDTH, 4, game.GB_DARK)
for sx in (40, 700):
    game.Box(sx, WALL_TOP + 10, 42, 60, game.GB_DARK, border=game.GB_DARK, border_w=0)
    game.Box(sx, WALL_TOP + 80, 42, 60, game.GB_DARK, border=game.GB_DARK, border_w=0)

zone = game.Box(360, ZONE_Y, ZONE_W, ZONE_H, game.BLACK, border=game.RED, border_w=3)
zone_label = game.Text("โซนอันตราย", 372, ZONE_Y - 26, game.RED)

# หุ่นลาดตระเวน: ตัวรถ + ไฟสัญญาณบนหลัง (ให้ดูเป็นยานพาหนะ ไม่ใช่กล่องลอย)
rover = game.Box(80, 200, ROVER_W, ROVER_H, game.GREEN,
                 border=game.GREEN, border_w=0)
beacon = game.Box(80 + ROVER_W // 2 - 5, 200 - 9, 10, 10, game.GREEN,
                  border=game.GREEN, border_w=0)

status = game.Text("", 24, 10, game.WHITE)
lamp = game.Box(24, 38, 26, 26, game.GREEN)
state_text = game.Text("", 60, 40, game.WHITE)
counter = game.Text("", 24, 72, game.GB_LIGHT)
game.Text("ลูกศร = ย้ายโซน | Z/Space = ปลดล็อก | Enter = ออก", 24, 100, game.CYAN)

# --- สถานะทั้งหมด ---
rover_x, rover_y = 80.0, 200.0
rover_vx, rover_vy = 4.2, 3.1
zone_x = 360.0
state = PATROL
alert_count = 0
resets = 0
prev_a = True


# ============================================================================
# แยกเป็นฟังก์ชันย่อยตามลำดับของระบบสมองกลฝังตัว: รับรู้ -> ตัดสินใจ -> สั่งการ
# ทุกไฟล์ในชุดเตรียมสอบใช้โครงเดียวกันนี้ อ่านไฟล์หนึ่งเป็น อ่านที่เหลือออกหมด
# ============================================================================


def restart_patrol():
    """กลับไปลาดตระเวน — ใช้ทั้งตอนกดปุ่มและตอนออกจากโซนทัน"""
    global state, alert_count, rover_vx, rover_vy
    state = PATROL
    alert_count = 0
    if rover_vx == 0 and rover_vy == 0:      # เคยหยุดสนิท ต้องปล่อยให้วิ่งใหม่
        rover_vx, rover_vy = 4.2, 3.1


def handle_unlock_button(keys):
    """ปุ่มปลดล็อก — กดหนึ่งครั้งนับหนึ่งครั้ง (debounce)"""
    global resets, prev_a

    if keys.a and not prev_a:
        resets += 1
        restart_patrol()
        game.sfx("paddle")
    prev_a = keys.a


def move_zone(keys):
    """ผู้เล่นย้ายโซนอันตรายไปขวางทางหุ่นได้ (ทำให้ทดลองง่าย)"""
    global zone_x

    if keys.left:
        zone_x -= ZONE_SPEED
    if keys.right:
        zone_x += ZONE_SPEED
    zone_x = max(100, min(game.WIDTH - ZONE_W - 100, zone_x))     # clamp
    zone.move_to(zone_x, ZONE_Y)


def patrol_move():
    """หุ่นวิ่งเองแล้วสะท้อนผนัง (integrate + reflect เหมือนลูก Pong)"""
    global rover_x, rover_y, rover_vx, rover_vy

    rover_x += rover_vx
    rover_y += rover_vy
    if rover_x < 0:
        rover_x = 0                              # ดันกลับเข้าขอบก่อน
        rover_vx = -rover_vx                     # แล้วค่อยกลับทิศ
    elif rover_x > game.WIDTH - ROVER_W:
        rover_x = game.WIDTH - ROVER_W
        rover_vx = -rover_vx
    if rover_y < WALL_TOP:
        rover_y = WALL_TOP
        rover_vy = -rover_vy
    elif rover_y > WALL_BOTTOM - ROVER_H:
        rover_y = WALL_BOTTOM - ROVER_H
        rover_vy = -rover_vy
    rover.move_to(rover_x, rover_y)
    beacon.move_to(rover_x + ROVER_W // 2 - 5, rover_y - 9)


def sense_zone():
    """รับรู้: ตอนนี้หุ่นทับโซนอันตรายอยู่ไหม (ต้องเรียกหลัง move_to)"""
    return game.hit(rover, zone)


def decide_state(in_zone):
    """ตัดสินใจ: state machine 3 สถานะ + ตัวนับที่ต้องรีเซ็ตให้ถูกที่"""
    global state, alert_count, rover_vx, rover_vy

    if state == STOPPED:
        pass                                    # หยุดสนิท รอปุ่มปลดล็อกอย่างเดียว
    elif in_zone:
        state = ALERT
        alert_count += 1
        if alert_count >= ALERT_LIMIT:
            state = STOPPED
            rover_vx, rover_vy = 0.0, 0.0       # state เดียวไม่หยุด ต้องสั่งความเร็วด้วย
            game.sfx("lose")
    else:
        if state == ALERT:
            game.sfx("wall")                    # ออกจากโซนได้ทันก่อนครบลิมิต
        state = PATROL
        alert_count = 0                         # รีเซ็ตตัวนับ — จุดที่คนพลาดบ่อยที่สุด


def draw_hud():
    """สั่งการ: แสดงผล — ส่วนนี้ไม่ตัดสินใจอะไร แค่รายงานสถานะปัจจุบัน"""
    rover.set_color(STATE_COLOR[state])
    beacon.set_color(STATE_COLOR[state])
    lamp.set_color(STATE_COLOR[state])
    state_text.set(STATE_NAME[state])
    zone_label.set("โซนอันตราย")
    if state == STOPPED:
        status.set("หยุดฉุกเฉิน — กด Z/Space เพื่อปลดล็อก")
    else:
        status.set("ตำแหน่ง (%d, %d)" % (rover_x, rover_y))
    counter.set("อยู่ในโซน %d/%d เฟรม | ปลดล็อก %d ครั้ง"
                % (alert_count, ALERT_LIMIT, resets))


def on_each_frame():
    """หนึ่งเฟรม = อ่านปุ่ม -> ขยับของ -> รับรู้ -> ตัดสินใจ -> สั่งการ"""
    keys = game.keys()
    if keys.start:
        return False

    handle_unlock_button(keys)
    move_zone(keys)
    patrol_move()
    in_zone = sense_zone()
    decide_state(in_zone)
    draw_hud()


game.run(on_each_frame, fps=30)

# ------------------------------------------------------------------------------
# ลองเล่นกับมันดู:
#
#   1. ใช้ลูกศรย้ายโซนไปขวางทางหุ่น แล้วดูว่ามันเปลี่ยนเป็นเหลืองทันทีที่ทับกัน
#      ถ้าหุ่นวิ่งผ่านเร็วพอ ตัวนับจะรีเซ็ตแล้วกลับเขียว — ยังไม่ถึงขั้นหยุด
#
#   2. ย้ายโซนไปดักให้หุ่นติดอยู่ในโซนนาน ๆ จนตัวนับครบ 50 แล้วดูมันหยุดสนิท
#      แล้วกด Z ปลดล็อก — สังเกตว่าหุ่นวิ่งต่อได้ ไม่ค้างอยู่กับที่
#
#   3. **ลบบรรทัด alert_count = 0 ในสาขา else ออก** แล้วดู:
#      หุ่นจะค่อย ๆ สะสมตัวนับข้ามรอบจนหยุดเอง ทั้งที่แค่วิ่งผ่านโซนสั้น ๆ หลายครั้ง
#      อาการเหมือนหุ่นสุ่มหยุดเอง — นี่คือบั๊กที่หายากที่สุดของโจทย์แนวนี้
#
#   4. **ลบ rover_vx, rover_vy = 0.0, 0.0 ตอนเข้า STOPPED ออก** แล้วดู:
#      ป้ายขึ้นว่า "หยุดฉุกเฉิน" แต่หุ่นยังวิ่งต่อ — เพราะ state เป็นแค่ตัวเลข
#      มันไม่ได้หยุดอะไรเอง โค้ด integrate ยังทำงานทุกเฟรมอยู่
#
#   5. **ลบ debounce ของปุ่ม (เหลือ if keys.a) แล้วกดค้าง** ดูตัวนับ "ปลดล็อก"
#      พุ่งขึ้นทุกเฟรม ทั้งที่กดครั้งเดียว
#
#   6. กด Z ตอนหุ่นยังลาดตระเวนปกติ — ไม่มีอะไรเปลี่ยนบนจอ **ยกเว้นตัวนับ "ปลดล็อก"**
#      ถ้าไม่มีตัวนับนั้น ผู้ใช้จะแยกไม่ออกว่าปุ่มเสียหรือกดแล้วไม่มีอะไรต้องทำ
#      ทุกปุ่มต้องมีสัญญาณตอบกลับ นี่เป็นกฎของงานออกแบบอุปกรณ์ ไม่ใช่แค่เรื่องสวยงาม
#
# ทักษะนี้ใช้ที่ไหนได้อีก: รั้วเสมือน (geofence) ของโดรน, ระบบกันชนรถยนต์,
#   หุ่นดูดฝุ่นที่ห้ามเข้าบางห้อง, สายพานที่หยุดเมื่อมีมือเข้าเขตใบมีด
#   — ทั้งหมดคือ AABB + ตัวนับที่รีเซ็ตถูกที่ + state machine
