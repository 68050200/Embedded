#☐ AI ที่ทำนายล่วงหน้า — ไม่ไล่ ball_y ปัจจุบัน แต่เดาว่าลูกจะถึงขอบขวาที่ตำแหน่งไหนแล้วรอรับไว้ก่อน (โจทย์เดียวกับระบบนำวิถี / รถอัตโนมัติ ที่เล็งจุดในอนาคต)


#สมการเส้นตรงด้วยความเร็วคงที่ y = y0 + vy*t
#คำนวณเฉพาะตอนลูกเด้งเข้าหา



import bentogame as game

PADDLE_W, PADDLE_H, BALL_SIZE = 14, 90, 14
PADDLE_START_Y = game.HEIGHT // 2 - PADDLE_H // 2

ACCEL, MAX_SPEED, FRICTION = 1.5, 12.0, 0.78
SPEEDUP, BALL_CAP, SPIN = 0.5, 14.0, 0.28
SERVE_SPEED = 6.2

# --- ตารางโหมด (mirror ของ s_pong_modes[] ใน C :50-54) ---
# (1name, 2ai_speed = ความเร็วไล่ตามของ AI, 3ball_mul = ตัวคูณความเร็วลูก, 4win_score)
MODES = [
    ("EASY",   2.2, 0.85, 7),
    ("NORMAL", 3.2, 1.00, 10),
    ("HARD",   6, 1.5, 10),
]

game.title("PONG")                          # หน้าเริ่ม: Start=เล่น Back=ออก (ทำ start ให้ในตัว)

player_paddle = game.Box(20, PADDLE_START_Y, PADDLE_W, PADDLE_H, game.GB_LIGHT)
ai_paddle = game.Box(game.WIDTH - 20 - PADDLE_W, PADDLE_START_Y, PADDLE_W, PADDLE_H, game.GB_LIGHT)
ball = game.Box(game.WIDTH // 2, game.HEIGHT // 2, BALL_SIZE, BALL_SIZE, game.GB_LIGHTEST)
score_text = game.Text("Player: 0   AI: 0", 16, 12, game.WHITE)
hint = game.Text("UP/DOWN choose mode, A start", game.WIDTH // 2 - 130,
                 game.HEIGHT // 2 + 40, game.CYAN)

selected_mode = 1         # default = NORMAL
choosing_mode = True
ai_speed, ball_mul, win_score = MODES[selected_mode][1], MODES[selected_mode][2], MODES[selected_mode][3]

ball_x, ball_y = float(game.WIDTH // 2), float(game.HEIGHT // 2)
ball_vx, ball_vy = -SERVE_SPEED, 3.4
player_y, player_speed = float(PADDLE_START_Y), 0.0
ai_y = float(PADDLE_START_Y)
player_score, ai_score = 0, 0
game_over = False
# จำสถานะปุ่มเฟรมก่อนหน้า เพื่อตรวจ "เพิ่งกด" (กันปุ่มค้างลั่นเมนูรัว ๆ)
prev_a = prev_up = prev_down = True   # mask ปุ่มแรกที่เข้าหน้าจอ

def show_menu():
    score_text.set("SELECT MODE:  < %s >" % MODES[selected_mode][0])

def serve(direction):
    global ball_x, ball_y, ball_vx, ball_vy
    ball_x, ball_y = game.WIDTH / 2, game.HEIGHT / 2
    ball_vx, ball_vy = SERVE_SPEED * ball_mul * direction, 3.4

def start_match():
    global choosing_mode, ai_speed, ball_mul, win_score
    global player_score, ai_score, player_y, ai_y, player_speed
    ai_speed, ball_mul, win_score = MODES[selected_mode][1], MODES[selected_mode][2], MODES[selected_mode][3]
    player_score, ai_score = 0, 0
    player_y, ai_y, player_speed = float(PADDLE_START_Y), float(PADDLE_START_Y), 0.0
    choosing_mode = False
    score_text.set("Player: 0   AI: 0  (%s)" % MODES[selected_mode][0])
    hint.set("UP/DOWN move, START menu")
    serve(1)

show_menu()

BALL_BOUNCE_H = game.HEIGHT - BALL_SIZE #ขอบเขตที่ลูกเคลื่อนที่ได้

def predict_ball_y():
    if ball_vx <= 0: #คำนวณเฉพาะตอนลูกเด้งเข้าหาลูกวิ่งออกจาก ai
        return None
        
    time_reach = (ai_paddle.x - ball_x) / ball_vx #เวลาที่ลูกบอลจะวิ่งมาถึงแกน X ของไม้ AI
    
    if time_reach < 0: # กันลูกไปไกลกว่าไม้ ซึ่งจะทำให้เวลาติดลบ
        return None
        
    direct_y = ball_y + ball_vy * time_reach #คาดการณ์ระยะทาง ตอนลูกมาถึง x เดียวกับไม้ สมการเส้นตรงด้วยความเร็วคงที่ y = y0 + vy*t
    
    period = 2 * BALL_BOUNCE_H #ระยะทางเด้งลงขึ้น ชนขอบบน ตำแหน่งจะเป็น y = 0
    
    m = direct_y % period  #ตัดระยะที่เด้งครบรอบ(ลงขึ้น)ทิ้ง ที่กลับไป y = 0 หาระยะทางที่เหลือ (เพื่อนำไปเช็กว่าเป็นเด้งขึ้นหรือเด้งลง)
    
    if m <= BALL_BOUNCE_H: #ระยะทางที่เหลือยังไม่เกินขอบ
        predicted_y = m # ตำแหน่งที่ลูกจะไปโดน y = m
        
    else: #ถ้าระยะทางที่เหลือเกินขอบไปแล้ว ให้กลับทิศ
        predicted_y = period - m # y = ขอบล่าง - (m ระยะทางที่เหลือที่มากกว่าขอบล่าง - ขอบล่าง) 
                                    #= ขอบล่าง - m + ขอบล่าง 
                                    #= (2 * ขอบล่าง) - m 
                                    #= period - m
        
    return predicted_y #ส่งค่าตำแหน่ง y เป้าหมาย

def on_each_frame():
    global ball_x, ball_y, ball_vx, ball_vy, player_y, player_speed, ai_y
    global player_score, ai_score, game_over
    global selected_mode, choosing_mode, prev_a, prev_up, prev_down
    keys = game.keys()
    if game_over:
        return False

    # --- หน้าจอเลือกโหมด ---
    if choosing_mode:
        if keys.up and not prev_up:
            selected_mode = (selected_mode + 2) % 3
            show_menu()
        elif keys.down and not prev_down:
            selected_mode = (selected_mode + 1) % 3
            show_menu()
        if (keys.a and not prev_a) or keys.start:
            start_match()
        prev_a, prev_up, prev_down = keys.a, keys.up, keys.down
        return

    if keys.start:                             # กลับไปหน้าเลือกโหมด
        choosing_mode = True
        prev_a = prev_up = prev_down = True
        show_menu()
        hint.set("UP/DOWN choose mode, A start")
        return

    # ไม้ผู้เล่น (ซ้าย) — เร่ง/เสียดทาน
    if keys.up and not keys.down:
        player_speed -= ACCEL
    elif keys.down and not keys.up:
        player_speed += ACCEL
    else:
        player_speed *= FRICTION

    
    player_speed = max(-MAX_SPEED, min(MAX_SPEED, player_speed))
    player_y = max(0, min(game.HEIGHT - PADDLE_H, player_y + player_speed))
    player_paddle.move_to(20, player_y)

    # --- AI tracker (ไม้ขวา) — กฎ AI ที่ง่ายที่สุด ---

    predicted = predict_ball_y()
    if predicted is not None: #พิกัดล่วงหน้า มาหักลบครึ่งหนึ่งของความสูงไม้ เพื่อให้ "กึ่งกลางไม้
        target_y = predicted - PADDLE_H / 2
    else:
        target_y = (game.HEIGHT / 2) - (PADDLE_H / 2) #กรณีที่ลูกบอลไม่ได้พุ่งมาหา AI
    # -6 +6 เป็น deadzone
    if   ai_y < target_y - 6:
        #ai_paddle.set_color(game.RED)
        ai_y += ai_speed  
        
    elif ai_y > target_y + 6:
        #ai_paddle.set_color(game.RED)
        ai_y -= ai_speed  

   # else:
        #ai_paddle.set_color(game.GB_LIGHTEST)
    ai_y = max(0, min(game.HEIGHT - PADDLE_H, ai_y))   # ไม่ให้หลุดจอ
    ai_paddle.move_to(ai_paddle.x, ai_y)
    
    ai_y = max(0, min(game.HEIGHT - PADDLE_H, ai_y))
    ai_paddle.move_to(ai_paddle.x, ai_y)

    # ลูกบอล + เด้งบน/ล่าง
    ball_x += ball_vx
    ball_y += ball_vy
    if ball_y <= 0 or ball_y >= game.HEIGHT - BALL_SIZE:
        ball_vy = -ball_vy
        game.sfx("wall")
    ball.move_to(ball_x, ball_y)

    # ตีไม้ซ้าย + ไม้ขวา(AI)
    if ball_vx < 0 and game.hit(ball, player_paddle):
        hit_offset = ((ball_y + BALL_SIZE / 2) - (player_y + PADDLE_H / 2)) / (PADDLE_H / 2)
        ball_vx = min(-ball_vx + SPEEDUP, BALL_CAP)
        ball_vy += hit_offset * 2.0 + player_speed * SPIN
        game.sfx("paddle")
    elif ball_vx > 0 and game.hit(ball, ai_paddle):
        hit_offset = ((ball_y + BALL_SIZE / 2) - (ai_y + PADDLE_H / 2)) / (PADDLE_H / 2)
        ball_vx = -min(ball_vx + SPEEDUP, BALL_CAP)
        ball_vy += hit_offset * 2.0
        game.sfx("paddle")

    # คะแนน + เสิร์ฟใหม่ + จบเกม

    #คะแนน
    if ball_x < 0:
        ai_score += 1
        score_text.set("Player: %d   AI: %d" % (player_score, ai_score))
        serve(1)
    elif ball_x > game.WIDTH:
        player_score += 1
        score_text.set("Player: %d   AI: %d" % (player_score, ai_score))
        serve(-1)

    if player_score >= win_score or ai_score >= win_score:
        player_won = player_score > ai_score
        game.sfx("win" if player_won else "lose")
        game.Text("YOU WIN!" if player_won else "AI WINS",
                  game.WIDTH // 2 - 70, game.HEIGHT // 2,
                  game.GREEN if player_won else game.RED)
        game_over = True
        return False

game.run(on_each_frame, fps=60)
