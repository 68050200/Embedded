
import bentogame as game

BALL_SIZE = 30                                 # ลูกบอลกว้าง/สูงกี่พิกเซล

game.title("PONG")                          # หน้าเริ่ม: Start=เล่น Back=ออก (ทำ start ให้ในตัว)

ball = game.Box(game.WIDTH // 2, game.HEIGHT // 2, BALL_SIZE, BALL_SIZE, game.GB_LIGHTEST)
game.Text("Pong - ball bounces the walls", 16, 12, game.WHITE)

# --- สถานะลูกบอล (ตำแหน่ง + ความเร็วต่อเฟรม) ---
# ============ ----- เติมส่วนนี้เอง (งานของคุณ): ตั้งค่าเริ่มต้นของลูกบอล ----- ============
# TODO: 1) ตั้ง ball_x, ball_y ให้ลูกเริ่มกลางจอ (อ่านค่าจาก game.WIDTH, game.HEIGHT)
#       2) ตั้งความเร็วต่อเฟรม ball_vx, ball_vy เป็นเลขทศนิยม
#          (บวก=ไปขวา/ลง, ลบ=ไปซ้าย/ขึ้น — เลือกค่าเล็กๆ ลองปรับเอง / ดู starter ถ้าติด)
ball_x, ball_y = game.WIDTH // 2, game.HEIGHT // 2       # <- แก้ค่าให้เริ่มกลางจอเมื่อเริ่มเขียน
ball_vx, ball_vy = 5.0, 5.0     # <- ใส่ความเร็วต่อเฟรมเมื่อเริ่มเขียน

def on_each_frame():
    global ball_x, ball_y, ball_vx, ball_vy
    keys = game.keys()
    # (Back=ออก / Start=เริ่มใหม่ — game.run() จัดการให้)

    # --- ขยับลูกหนึ่งก้าว แล้วเด้งกำแพงบน/ล่าง ---
    # ============ ----- เติมส่วนนี้เอง (งานของคุณ): ขยับลูก + เด้งกำแพงบน/ล่าง ----- ============
    # TODO: 1) "ขยับ" หนึ่งก้าว: บวกความเร็วแต่ละแกนเข้ากับตำแหน่งแกนนั้น (integrate)
    #       2) เช็กว่าลูกชนขอบบนหรือขอบล่างหรือยัง — ขอบบนคือ y ต่ำสุด,
    #          ขอบล่างคือ y ที่ขอบลูกแตะก้นจอ (คิดจาก game.HEIGHT กับ BALL_SIZE)
    #       3) ถ้าชน ให้กลับทิศความเร็วแนวตั้ง (สลับเครื่องหมาย ball_vy) แล้วเรียก game.sfx("wall")
    #       4) ยังไม่มีไม้ตี: ถ้าชนขอบซ้าย/ขวา ให้กลับทิศ ball_vx ด้วย กันลูกหลุดจอ
    ball_x += ball_vx   
    ball_y += ball_vy 
    if ball_y <= 0 or ball_y >= game.HEIGHT-BALL_SIZE:
        game.sfx("wall")
        ball_vy = -ball_vy


    if ball_x <= 0 or ball_x >= game.WIDTH - BALL_SIZE:
        game.sfx("wall")
        ball_vx = -ball_vx

    ball.move_to(ball_x, ball_y)               # core: วาดลูกที่ตำแหน่งใหม่

game.run(on_each_frame, fps=60)                # core: เรียก on_each_frame() 60 ครั้ง/วินาที
