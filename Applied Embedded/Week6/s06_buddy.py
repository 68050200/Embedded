#ปุ่มพิเศษให้ไม้ตีแล้วลูกพุ่งเร็วขึ้น
#เกจชาร์จกดค้าง จะแรงขึ้นตามเวลา
import bentogame as game

PADDLE_W, PADDLE_H, BALL_SIZE = 14, 90, 14
PADDLE_START_Y = game.HEIGHT // 2 - PADDLE_H // 2   # วางไม้กลางจอตอนเริ่ม

ACCEL    = 0.5      # เร่งต่อเฟรมเมื่อกดค้าง
MAX_SPEED = 12.0    # ความเร็วสูงสุดของไม้
FRICTION = 0.78     # หน่วงเมื่อปล่อยปุ่ม (คูณความเร็วให้ค่อย ๆ เหลือศูนย์)

charge_max   = 60    # เฟรม ชาร์จเต็ม
hit_range   = 20    # เฟรมหลังโดนไม้ ที่ยังนับว่า ปล่อยทัน
boost_mult = 1.5  # ความเร่งลูกตอนชาร์จเต็ม

charge = 0.0
hit_timer = 0
prev_a = False

game.title("PONG")                          # หน้าเริ่ม: Start=เล่น Back=ออก (ทำ start ให้ในตัว)

player_paddle = game.Box(20, PADDLE_START_Y, PADDLE_W, PADDLE_H, game.GB_LIGHT)
ball = game.Box(game.WIDTH // 2, game.HEIGHT // 2, BALL_SIZE, BALL_SIZE, game.GB_LIGHTEST)
game.Text("Move your paddle: UP / DOWN", 16, 12, game.WHITE)

charge_bar_x, charge_bar_y = 16, 40   # ตำแหน่งหลอด 
charge_bar_w, charge_bar_h = 120, 10  # ขนาดเต็มของหลอด

charge_bg = game.Box(charge_bar_x, charge_bar_y, charge_bar_w, charge_bar_h, game.GB_DARK)
charge_fill = game.Box(charge_bar_x, charge_bar_y, 0, charge_bar_h, game.GB_LIGHTEST)

ball_x, ball_y = float(game.WIDTH // 2), float(game.HEIGHT // 2)
ball_vx, ball_vy = 6.2, 3.4
player_y, player_speed = float(PADDLE_START_Y), 0.0   # ตำแหน่ง + ความเร็วไม้ของเรา

def on_each_frame():
    global ball_x, ball_y, ball_vx, ball_vy, player_y, player_speed ,charge, hit_timer, prev_a
    keys = game.keys()

    #ไม้ตี
    if   keys.up   and not keys.down:
        player_speed -= ACCEL
    elif keys.down and not keys.up:
        player_speed += ACCEL
    else:
        player_speed *= FRICTION

    player_speed = max(-MAX_SPEED, min(MAX_SPEED, player_speed))
    player_y = max(0, min(game.HEIGHT - PADDLE_H, player_y + player_speed))
    player_paddle.move_to(20, player_y)

    #ชนไม้
    if ball_vx < 0 and game.hit(ball, player_paddle):
        ball_vx = -ball_vx
        hit_timer = hit_range
        game.sfx("paddle")

    if hit_timer > 0: #ถ้าโดนไม้ hit_timer = hit_range (20) และจะลดลงเรื่อยๆทุกเฟรม
        hit_timer -= 1

    #ชาร์จ + ปล่อยตรงจังหวะ = เร่งลูก
    if keys.a:
        charge = min(charge_max, charge + 1)
    else:
        if prev_a and hit_timer > 0:  #ถ้ายังกดอยู่ และ เวลาโดนไม้ไม่เกินที่หน่วงไว้
            mult = 1 + (charge / charge_max) * boost_mult
            ball_vx *= mult
            ball_vy *= mult
        charge = 0 #รีเซ็ต charge กลับเป็น 0 ทุกครั้งที่ ไม่ได้กด a
    prev_a = keys.a

    
    ball_x += ball_vx
    ball_y += ball_vy
    if ball_y <= 0 or ball_y >= game.HEIGHT - BALL_SIZE:
        ball_vy = -ball_vy
        game.sfx("wall")
    if ball_x <= 0 or ball_x >= game.WIDTH - BALL_SIZE:
        ball_vx = -ball_vx
    ball.move_to(ball_x, ball_y)

    #หลอดชาร์จ
    fill_w = max(1, int(charge_bar_w * (charge / charge_max)))
    charge_fill.resize(fill_w, charge_bar_h)

game.run(on_each_frame, fps=60)