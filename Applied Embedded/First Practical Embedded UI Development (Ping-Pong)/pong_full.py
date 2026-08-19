# pong_full.py — เกมเต็มของ Pong (ผู้เล่น vs AI)
# ตัวนี้เราตั้งใจลอก "หน้าตาและจังหวะ" มาจากเกม C บนเครื่อง (page_game_pong.c)
# ให้ครบที่สุด: โต๊ะสักหลาดเขียว + เส้นเน็ต, ไม้กับลูกเป็น sprite ชุดเดียวกับเกม C,
# เมนูเลือกความยาก, HUD Player/AI/Best, เสียงครบทุกจังหวะ และจบเกมแล้วกด Start
# เล่นต่อได้ทันทีไม่ต้องรีบูตเครื่อง
#
# ปุ่ม: UP/DOWN ขยับไม้   Y เริ่มตาใหม่   Start พักเกม   Back ออก
#
# งบ widget ของจอมี 32 ชิ้น เกมนี้ใช้:
#   พื้นโต๊ะ 1 + ขอบขาว 4 + เน็ต 14 + ไม้ 2 + ลูก 1 + HUD 1 + ป้ายโหมด 1 = 24
#   บวกป้ายคุมของ run() 1 (ป้ายพักยืมป้ายนี้ ไม่กินงบเพิ่ม)
#   + ป้ายจบเกมชั่วคราวอีก 4 = สูงสุด 29 ยังเหลือเผื่อ

import bentogame as game
import random

# ---- ค่าคงที่ชุดเดียวกับเกม C เป๊ะ (จูนมาให้มือดีแล้ว อยากลองแก้ก็ได้แต่จดค่าเดิมไว้ก่อน) ----
PADDLE_W, PADDLE_H = 14, 90
BALL_SIZE       = 14
BALL_SPEED0     = 6.2    # ความเร็วลูกตอนเสิร์ฟ (ก่อนคูณตามโหมด)
BALL_MAXV       = 14.0   # เพดานความเร็วรวม แรลลี่ยาวแค่ไหนก็ยังพอรับทัน
BALL_SPEEDUP    = 0.35   # ตีโดนหนึ่งครั้ง ลูกเร็วขึ้นเท่านี้
PADDLE_ACCEL    = 1.5    # กดค้างแล้วไม้เร่งความเร็วขึ้นเรื่อยๆ
PADDLE_MAXV     = 13.0
PADDLE_FRICTION = 0.78   # ปล่อยปุ่มแล้วไม้ค่อยๆ หน่วงจนหยุด
PADDLE_SPIN     = 0.28   # ไม้ที่กำลังวิ่งอยู่จะใส่สปินให้ลูก
PADDLE_X        = 14     # ระยะไม้ห่างจากขอบจอ
FELT  = 0x1C7A34         # สีโต๊ะปิงปอง (สักหลาดเขียว) สีเดียวกับเกม C
CHALK = 0xF0F8F0         # สีขอบโต๊ะและเส้นเน็ต

# โหมดความยาก (ชื่อ, ความเร็ว AI ต่อเฟรม, ตัวคูณความเร็วลูก, แต้มชนะ)
# ค่าตรงกับตาราง s_pong_modes ของเกม C: NORMAL คือจังหวะมาตรฐานดั้งเดิม
MODES = (("EASY", 2.2, 0.85, 7), ("NORMAL", 3.2, 1.0, 10), ("HARD", 4.6, 1.2, 10))


def serve(to_right):
    # วางลูกกลางโต๊ะ แล้วเสิร์ฟออกด้วยมุมสุ่มเล็กน้อย (เหมือน lv_rand ของเกม C)
    global ball_x, ball_y, ball_vx, ball_vy
    ball_x = game.WIDTH / 2 - BALL_SIZE / 2
    ball_y = game.HEIGHT / 2 - BALL_SIZE / 2
    speed = BALL_SPEED0 * ball_mul
    ball_vx = speed if to_right else -speed
    ball_vy = random.randint(-22, 22) / 10.0


def clamp_ball_speed():
    # จำกัดความเร็ว "รวม" ของลูก (ทั้งแกน x และ y) ไม่ให้ทะลุเพดาน
    global ball_vx, ball_vy
    speed = (ball_vx * ball_vx + ball_vy * ball_vy) ** 0.5
    if speed > BALL_MAXV:
        k = BALL_MAXV / speed
        ball_vx *= k
        ball_vy *= k


def update_hud():
    # Best นับจากฝั่งที่ทำแต้มสูงสุด (นับ AI ด้วย) แบบเดียวกับเกม C
    global session_best
    session_best = max(session_best, left_score, right_score)
    hud.set("Player: %d    AI: %d    Best: %d" % (left_score, right_score, session_best))


def new_round():
    # ปุ่ม Y ของเกม C: ล้างแต้มแล้วเริ่มแมตช์ใหม่ทันทีในโหมดเดิม
    global left_score, right_score, left_y, right_y, left_vy
    left_score = right_score = 0
    left_y = right_y = float(paddle_start_y)
    left_vy = 0.0
    update_hud()
    serve(True)


def update():
    global ball_x, ball_y, ball_vx, ball_vy
    global left_y, right_y, left_vy, left_score, right_score
    k = game.keys()

    if game.pressed_once("y", k):    # Y = เริ่มตาใหม่ (กดค้างไม่นับซ้ำ)
        new_round()

    # ไม้ผู้เล่น: กดค้างเร่งความเร็ว ปล่อยแล้วหน่วงด้วยแรงเสียดทาน (มือเดียวกับเกม C)
    if k.up and not k.down:
        left_vy -= PADDLE_ACCEL
    elif k.down and not k.up:
        left_vy += PADDLE_ACCEL
    else:
        left_vy *= PADDLE_FRICTION
    left_vy = max(-PADDLE_MAXV, min(PADDLE_MAXV, left_vy))
    left_y += left_vy
    if left_y <= 0 or left_y >= game.HEIGHT - PADDLE_H:
        left_y = max(0.0, min(float(game.HEIGHT - PADDLE_H), left_y))
        left_vy = 0.0                # ชนขอบแล้วหยุดนิ่ง ไม่มีเด้ง
    left_paddle.move_to(PADDLE_X, left_y)

    # ลูกวิ่ง + เด้งขอบบนล่าง
    ball_x += ball_vx
    ball_y += ball_vy
    if ball_y <= 0:
        ball_y = 0.0
        ball_vy = -ball_vy
        game.sfx("wall")
    elif ball_y >= game.HEIGHT - BALL_SIZE:
        ball_y = float(game.HEIGHT - BALL_SIZE)
        ball_vy = -ball_vy
        game.sfx("wall")

    # ตีโดนไม้: สะท้อนกลับ + เร่งขึ้น + มุมสะท้อนตามจุดที่โดนหน้าไม้ (โดนปลายไม้มุมยิ่งแรง)
    if ball_vx < 0 and game.hit(ball, left_paddle):
        norm = ((ball_y + BALL_SIZE / 2) - (left_y + PADDLE_H / 2)) / (PADDLE_H / 2)
        ball_x = float(PADDLE_X + PADDLE_W)
        ball_vx = abs(ball_vx) + BALL_SPEEDUP
        ball_vy += norm * 2.0
        ball_vy += left_vy * PADDLE_SPIN   # ไม้ที่กำลังวิ่งใส่สปินเพิ่มให้อีก
        clamp_ball_speed()
        game.sfx("paddle")
    elif ball_vx > 0 and game.hit(ball, right_paddle):
        norm = ((ball_y + BALL_SIZE / 2) - (right_y + PADDLE_H / 2)) / (PADDLE_H / 2)
        ball_x = float(game.WIDTH - PADDLE_X - PADDLE_W - BALL_SIZE)
        ball_vx = -(abs(ball_vx) + BALL_SPEEDUP)
        ball_vy += norm * 2.0
        clamp_ball_speed()
        game.sfx("paddle")
    # วาดลูก "หลัง" เคลียร์เรื่องชนไม้แล้วเท่านั้น (ลำดับเดียวกับเกม C) —
    # ไม่งั้นจะเห็นลูกจมอยู่ในไม้ 1 เฟรมทุกครั้งที่ตีโดน
    ball.move_to(ball_x, ball_y)

    # ได้แต้มเมื่อลูกเลยขอบจอไป 25px (ตามเกม C) แล้วเสิร์ฟใหม่ไปทางฝั่งที่เพิ่งได้แต้ม
    if ball_x < -25:
        right_score += 1
        update_hud()
        if right_score >= win_score:
            game.sfx("lose")
            return False
        game.sfx("pong_score")
        serve(True)
    elif ball_x > game.WIDTH + 25:
        left_score += 1
        update_hud()
        if left_score >= win_score:
            game.sfx("win")
            return False
        game.sfx("pong_score")
        serve(False)

    # ไม้ AI: ไล่ตามลูกด้วยความเร็วคงที่ตามโหมด (±5px คือระยะที่ AI พอใจแล้วหยุดขยับ)
    ball_c = ball_y + BALL_SIZE / 2
    paddle_c = right_y + PADDLE_H / 2
    if ball_c > paddle_c + 5:
        right_y += ai_speed
    elif ball_c < paddle_c - 5:
        right_y -= ai_speed
    right_y = max(0.0, min(float(game.HEIGHT - PADDLE_H), right_y))
    right_paddle.move_to(game.WIDTH - PADDLE_X - PADDLE_W, right_y)


game.title("PONG", melody=True)

session_best = game.best("pong")   # Best ค้างไว้จนกว่าจะปิดเครื่อง เหมือนเกม C
mode = 1                           # เปิดมาชี้ NORMAL ก่อน เหมือนเกม C

while True:
    # เลือกโหมดใหม่ได้ทุกแมตช์ (เกม C ก็กลับมาหน้าเลือกโหมดหลังจบเกมเช่นกัน)
    picked = game.menu("EASY", "NORMAL", "HARD", selected=mode)
    if picked is None:               # BACK จากหน้าเมนู = เลิกเล่น (เหมือนเกม C)
        break
    mode = picked
    mode_name, ai_speed, ball_mul, win_score = MODES[mode]

    # ---- จัดฉากโต๊ะปิงปอง (สร้างพื้นก่อนเสมอ ของที่สร้างทีหลังจะทับอยู่ข้างบน) ----
    game.background(FELT)
    game.Box(0, 0, game.WIDTH, 3, CHALK)                  # ขอบบน
    game.Box(0, game.HEIGHT - 3, game.WIDTH, 3, CHALK)    # ขอบล่าง
    game.Box(0, 0, 3, game.HEIGHT, CHALK)                 # ขอบซ้าย
    game.Box(game.WIDTH - 3, 0, 3, game.HEIGHT, CHALK)    # ขอบขวา
    game.net(CHALK)                                        # เส้นเน็ตประกลางโต๊ะ

    # ไม้กับลูกใช้ sprite ลายเดียวกับเกม C (ไม้ปิงปองจริง + ลูกมีไฮไลต์)
    paddle_start_y = game.HEIGHT // 2 - PADDLE_H // 2
    left_paddle = game.Sprite("paddle", PADDLE_X, paddle_start_y)
    right_paddle = game.Sprite("paddle", game.WIDTH - PADDLE_X - PADDLE_W, paddle_start_y)
    ball = game.Sprite("ball", game.WIDTH // 2, game.HEIGHT // 2)
    # sprite ไม่รู้ขนาดตัวเอง เลยบอกกว้างxสูงไว้ให้ game.hit() ใช้เช็คชน
    left_paddle.w = right_paddle.w = PADDLE_W
    left_paddle.h = right_paddle.h = PADDLE_H
    ball.w = ball.h = BALL_SIZE

    hud = game.Text("", 16, 4, game.WHITE)
    # ป้ายบอกวิธีเล่น: ประโยคและตำแหน่งเดียวกับเกม C (กลางจอชิดล่าง สีเข้มบนสักหลาด)
    # ขยับขึ้นหนึ่งบรรทัดหลบป้ายคุมของ run() ที่จองมุมล่างซ้ายไว้
    status = "%s  -  UP/DOWN move, Score %d, Y = new round" % (mode_name, win_score)
    game.Text(status, game.WIDTH // 2 - len(status) * 4, game.HEIGHT - 46, game.GB_DARKEST)

    left_y = right_y = float(paddle_start_y)
    left_vy = 0.0
    left_score = right_score = 0
    update_hud()
    serve(True)                      # เกม C เปิดแมตช์ด้วยการเสิร์ฟไปทางฝั่ง AI

    if not game.run(update, fps=60):     # Back = เลิกเล่น
        break
    # จบแมตช์: ฉากค้างไว้ ขึ้นป้ายผลพร้อมคะแนนกับ Best แล้วถามว่าไปต่อไหม
    msg = "Player wins!" if left_score > right_score else "AI wins"
    if not game.game_over(max(left_score, right_score), name="pong", msg=msg):
        break
