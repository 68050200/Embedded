# โครงเว้นบางส่วน — ช่องที่คุณต้องเติมเอง / เฉลย: solution_codes/shooter_step5.py / ใบ้: สไลด์คาบ 12 (ขั้นต่อ) + ใบงาน
# ------------------------------------------------------------------------------
# shooter_step5.py — Shooter #3 ขั้นต่อ (คาบ 12, ทีมที่เสร็จเร็ว): ระดับความยาก + ปล่อยศัตรูเป็นจังหวะ
# ------------------------------------------------------------------------------
# ต่อจาก step4. สิ่งที่เพิ่ม 3 อย่าง:
#   1) ศัตรูเป็น "ชุดหมุนเวียน" ตัวจริง แบบเดียวกับกระสุนคาบ 11 (5 ขั้นเดิม):
#        (1) สร้างชุดครั้งเดียว: enemies + enemy_active (ธง True = ใช้อยู่, False = ว่าง)
#        (2) หาตัวว่าง: if not enemy_active[index]     (3) ยืม: spawn_enemy()
#        (4) อัปเดตทุกเฟรม: ในลูปศัตรู                   (5) คืน: park_enemy(index)
#   2) spawn_timer นับถอยหลังทีละเฟรม ถึง 0 แล้วปล่อยศัตรู 1 ตัว (ทุก SPAWN_DELAY + 1 เฟรม)
#   3) ตารางโหมด MODES (FREE / EASY / DIFFICULT) — ค่าความยากทั้งหมดอยู่ในตารางเดียว
#
# เลือกโหมดด้วยตัวแปร MODE (0/1/2). เกมเต็ม full_games/shooter_full.py เลือกผ่านเมนูบนจอ
#   (game.menu) และมีระเบิด ภาพสไปรต์ กับโมเมนตัมกระสุนเพิ่ม — step5 ไม่มีส่วนนั้น
# ลองเปลี่ยน MODE เป็น 0/1/2 แล้วดูความต่าง: จังหวะปล่อยศัตรู ความเร็วตก และกติกาเสียชีวิต
#
# ส่วนที่คุณจะเขียนเองใน step นี้ (ต่อจาก step4):
#   1) ตารางโหมด: เพิ่มแถว EASY / DIFFICULT
#   2) spawn_enemy(): หาตัวว่าง -> ยืม (ขั้น 2 + 3 ของชุดหมุนเวียน)
#   3) ยานชนศัตรู -> เสียชีวิต (ยกเว้นโหมด FREE) ด้วย boxes_overlap()
# engine ที่ใช้ (เดิมทั้งหมด): game.title / Box / Text / keys / sfx / run
# กล่องชนหด: กระสุน 4x10, ศัตรู 26x16 (เล็กกว่ากล่องที่เห็น)
# เกมเต็มสำหรับเทียบ: full_games/shooter_full.py (MODES :36-40, ปล่อยศัตรู :123-135, ลูปศัตรู :216-259)
#
# ------------------------------------------------------------------------------
import bentogame as game
import random

ACCEL, MAX_SPEED, FRICTION = 1.4, 13.0, 0.80
MAX_BULLETS, MAX_ENEMIES = 6, 8                 # ชุดกระสุน 6 นัด, ชุดศัตรู 8 ตัว
ENEMY_COLORS = [game.RED, game.ORANGE, game.PINK]

# กล่องชน "หด" ให้เล็กกว่ากล่องที่เห็น (ต้องเข้าเนื้อจริงถึงนับ): กระสุน 4x10,
# ศัตรู 26x16 (เท่ากับ full_games/shooter_full.py:237) — ยานใช้ขนาดเต็ม 62x24
BULLET_HITBOX = (4, 10)
ENEMY_HITBOX  = (26, 16)

def boxes_overlap(a_x, a_y, a_width, a_height, b_x, b_y, b_width, b_height):
    """ชนแบบกล่อง (AABB) ด้วยขนาดที่กำหนดเอง — ใช้ทำกล่องชนหด
    a_* = กล่องแรก, b_* = กล่องที่สอง: โดนเมื่อทับกันจริง (ขอบชนกันพอดีไม่นับ)"""
    return (a_x < b_x + b_width and a_x + a_width > b_x and
            a_y < b_y + b_height and a_y + a_height > b_y)

# ----- เติมส่วนนี้เอง (งานของคุณ) (1): สร้างตารางโหมด 3 ระดับ -----
#   ตาราง MODES = list ของ tuple 6 ช่อง:
#   (ชื่อ, spawn_delay, speed_mul, lives, lose_when_pass, lose_when_hit)
# TODO ทำตามขั้น:
#   1) เก็บแถว FREE ตัวอย่างไว้ (รันได้แล้ว) — มันคือโหมดฝึกมือ ไม่มีอะไรลงโทษ
#   2) เพิ่มแถว EASY: spawn ห่างขึ้น (ปล่อยช้าลง), speed_mul < 1 (ช้าลง), ชีวิตน้อยลง,
#      lose_when_pass=False แต่ lose_when_hit=True (ชนยานเสีย แต่หลุดล่างไม่เสีย)
#   3) เพิ่มแถว DIFFICULT: spawn ถี่ที่สุด, speed_mul สูงสุด, ชีวิตน้อยสุด,
#      lose_when_pass=True และ lose_when_hit=True (โหดทั้งสองทาง)
#   ค่าตัวเลขปรับเอาเองให้รู้สึก "ยากขึ้นเป็นชั้น" (ดู solution_codes/shooter_step5.py ถ้าอยากเทียบค่า)
MODES = [
    ("FREE SHOOTER", 16, 0.85, 99, False, False),  # ตัวอย่างไว้ 1 แถวให้รันได้ก่อน เดี๋ยวคุณเพิ่ม EASY/DIFFICULT เอง
    ("EASY", 25, 0.55, 66, False, True),
    ("DIFFICULT", 5, 0.99, 10, True, True)
]
MODE = 1                                        # เลือกโหมด (0/1/2) — เกมเต็มเลือกผ่านเมนูบนจอ
MODE_NAME, SPAWN_DELAY, SPEED_MUL, START_LIVES, LOSE_WHEN_PASS, LOSE_WHEN_HIT = MODES[MODE]

game.title("SHOOTER")                          # หน้าเริ่ม: Start=เล่น Back=ออก (ทำ start ให้ในตัว)

ship = game.Box(365, 352, 62, 24, game.GREEN)
ship_x, ship_speed = 365.0, 0.0
score, lives, fire_cooldown = 0, START_LIVES, 0
spawn_timer = 8                                  # นับถอยหลังก่อนปล่อยศัตรูตัวถัดไป
hud = game.Text("%s   Score: 0   Lives: %d" % (MODE_NAME, lives), 10, 8, game.WHITE)

bullets = [game.Box(0, -50, 6, 14, game.CYAN) for _ in range(MAX_BULLETS)]
for bullet in bullets:
    bullet.hide()

# (1) สร้างชุดศัตรูครั้งเดียว: ทุกตัวเริ่ม "ว่าง" ซ่อนเหนือจอ / enemy_active[i] = True แปลว่าใช้อยู่
enemies = [game.Box(0, -50, 30, 24, ENEMY_COLORS[0]) for _ in range(MAX_ENEMIES)]
for enemy in enemies:
    enemy.hide()
enemy_active = [False] * MAX_ENEMIES
enemy_speed = [0.0] * MAX_ENEMIES

def find_free_bullet():
    for bullet in bullets:
        if bullet.y < -20:
            return bullet
    return None

def spawn_enemy():
    # ----- เติมส่วนนี้เอง (งานของคุณ) (2): ปล่อยศัตรู 1 ตัว = (2) หาตัวว่าง + (3) ยืม -----
    # ทำตามขั้น:
    #   1) หาตัวว่าง: วน index ใน range(MAX_ENEMIES) หาตัวแรกที่ enemy_active[index] เป็น False
    #   2) ยืม: ตั้ง enemy_active[index] = True (จองตัวนั้นว่า "ใช้อยู่")
    #   3) สุ่มสีปล่อยมัน: ใช้ .set_color(...) กับ random.choice(ENEMY_COLORS)
    #   4) วางมันไว้บนสุดนอกจอ: ใช้ .move_to(...) — x สุ่ม (random.randint) ให้อยู่ในจอ, y ติดลบ (ยังไม่โผล่)
    #   5) เรียก .show() ให้มองเห็น
    #   6) ตั้ง enemy_speed[index] = ความเร็วสุ่ม (random.uniform) คูณ SPEED_MUL ของโหมด
    #   7) return ออกทันที (ปล่อยแค่ตัวเดียวต่อการเรียก 1 ครั้ง)
    # (ช่วงตัวเลขความเร็ว/ขอบ x ปรับเอง — ดู solution_codes/shooter_step5.py ถ้าติด)
    # <- ลบ pass ออกเมื่อเริ่มเขียน
    for index in range(MAX_ENEMIES):
        if not enemy_active[index]:
            enemy_active[index] = True 
            enemies[index].set_color(random.choice(ENEMY_COLORS))
            enemies[index].move_to(random.randint(0, game.WIDTH - 30), -random.randint(100, 500))
            enemies[index].show()
            enemy_speed[index] = (random.uniform(2,5))*SPEED_MUL
            return
    
def park_enemy(index):                             # (5) คืน: กลับเป็นว่าง
    enemy_active[index] = False
    enemies[index].hide()
    enemies[index].move_to(0, -50)

# ปล่อยศัตรู 3 ตัวแรกทันที (เหมือนเกมเต็ม full_games/shooter_full.py:265-266)
spawn_enemy(); spawn_enemy(); spawn_enemy()

def on_frame():
    global ship_x, ship_speed, score, lives, fire_cooldown, spawn_timer
    keys = game.keys()
    # (Back = ออก / Start = พักเกม — game.run() จัดการให้ bentogame.py:970-974)

    # spawn_timer: นับลงทีละเฟรม ถึง 0 แล้วปล่อย 1 ตัว แล้วตั้งใหม่ = SPAWN_DELAY
    if spawn_timer > 0:
        spawn_timer -= 1
    else:
        spawn_enemy()
        spawn_timer = SPAWN_DELAY

    # ยาน
    if keys.left:    ship_speed -= ACCEL
    elif keys.right: ship_speed += ACCEL
    else:            ship_speed *= FRICTION
    ship_speed = max(-MAX_SPEED, min(MAX_SPEED, ship_speed))
    ship_x = max(0, min(game.WIDTH - ship.w, ship_x + ship_speed))
    ship.move_to(ship_x, 352)

    # ยิง
    fire_cooldown = max(0, fire_cooldown - 1)
    if (keys.a or keys.up) and fire_cooldown == 0:
        bullet = find_free_bullet()
        if bullet:
            bullet.show(); bullet.move_to(ship_x + ship.w // 2 - 3, 340); game.sfx("fire"); fire_cooldown = 8
    for bullet in bullets:
        if bullet.y >= -20:
            bullet.move_to(bullet.x, bullet.y - 9)
            if bullet.y < -20: bullet.hide()

    # (4) อัปเดตศัตรูที่ใช้อยู่ทุกเฟรม + ชน + คะแนน + ชีวิต
    for index in range(MAX_ENEMIES):
        if not enemy_active[index]:
            continue
        enemy = enemies[index]
        enemy.move_to(enemy.x, enemy.y + enemy_speed[index])
        if enemy.y > game.HEIGHT:               # หลุดล่าง
            park_enemy(index)
            if LOSE_WHEN_PASS:                  # เฉพาะ DIFFICULT ที่หลุดล่างแล้วเสียชีวิต
                lives -= 1
                hud.set("%s   Score: %d   Lives: %d" % (MODE_NAME, score, lives))
                if lives <= 0:
                    game.sfx("gameover")
                    game.Text("GAME OVER", 320, 180, game.RED)
                    return False
            continue

        # กระสุน x ศัตรู (ใช้กล่องชนหด)
        enemy_box = (enemy.x, enemy.y, ENEMY_HITBOX[0], ENEMY_HITBOX[1])
        was_hit = False
        for bullet in bullets:
            if bullet.y >= -20 and boxes_overlap(bullet.x, bullet.y, BULLET_HITBOX[0], BULLET_HITBOX[1], *enemy_box):
                score += 1
                game.sfx("hit")
                hud.set("%s   Score: %d   Lives: %d" % (MODE_NAME, score, lives))
                bullet.move_to(0, -50); bullet.hide()
                park_enemy(index)
                was_hit = True
                break
        if was_hit:
            continue

        # ----- เติมส่วนนี้เอง (งานของคุณ) (3): ยานชนศัตรู แล้วเสียชีวิต (ยกเว้นโหมด FREE) -----
        # ทำตามขั้น (เทียบ enemy_box ที่เตรียมไว้ด้านบน):
        #   1) เช็คยานชนศัตรูด้วย boxes_overlap(...) — กล่องยานคือ ship_x, ตำแหน่ง y ของยาน,
        #      ขนาด ship.w/ship.h, แล้วกาง *enemy_box เป็นกล่องที่สอง
        #   2) ถ้าชน: เรียก park_enemy(index) คืนศัตรูกลับชุด (กลับเป็นว่าง)
        #   3) ถ้าโหมดนี้ลงโทษ (LOSE_WHEN_HIT): ลด lives ลง 1 แล้วอัปเดต hud ด้วย hud.set(...)
        #   4) ถ้า lives หมด (<= 0): เล่น game.sfx("gameover"), โชว์ game.Text("GAME OVER", ...) แล้ว return False
        #   5) ถ้ายังไม่หมดชีวิต: เล่นเสียงระเบิด game.sfx("explode")
        # (FREE ไม่ลงโทษ เพราะ LOSE_WHEN_HIT=False — ปล่อยให้ if ข้ามไปเอง)
           # <- ลบ pass ออกเมื่อเริ่มเขียน
        if boxes_overlap(ship_x, ship.y, ship.w, ship.h, *enemy_box):
            park_enemy(index)                   
            if LOSE_WHEN_HIT:                    
                lives -= 1
                hud.set("%s   Score: %d   Lives: %d" % (MODE_NAME, score, lives))
                if lives <= 0:                 
                    game.sfx("gameover")
                    game.Text("GAME OVER", 320, 180, game.RED)
                    return False
                game.sfx("explode")             

game.run(on_frame, fps=30)