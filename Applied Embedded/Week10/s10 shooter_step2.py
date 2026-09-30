# โครงเว้นช่อง — เติมช่องที่เป็นงานของน้อง ๆ ให้ครบ แล้วเกมจะเล่นได้จริง
# เฉลย: solution_codes/shooter_step2.py · ใบ้: ใบงานคาบ 10 + สไลด์ "step 2 — งานของน้อง ๆ"
# ------------------------------------------------------------------------------
# shooter_step2.py — Shooter #1 (คาบ 10) step 2: บังคับยานซ้าย/ขวา (เร่ง + ไถล)
# ------------------------------------------------------------------------------
# เรื่องของ step นี้: ทำให้ยาน "ขับได้และมีน้ำหนัก" เหมือนเข็นรถเข็นในห้าง กดค้างไว้
# จะค่อย ๆ เร็วขึ้น (เร่ง/ACCEL) พอปล่อยปุ่มก็ไถลต่อแล้วช้าลงเอง (FRICTION)
# ชนขอบจอแล้วหยุด ไม่หลุดออก (clamp = บีบค่าให้อยู่ในช่วง)
# คำสั่งที่เอนจินมีให้ (70%) ที่เพิ่งได้ใช้: game.keys() (อ่านปุ่ม/จอย) · ship.move_to()
# ท่าเดียวกับไม้ตี Pong คาบ 6 (pong_step2.py) แค่เปลี่ยนจากแนวตั้งเป็นแนวนอน
# ปุ่ม -> ความเร็ว (ship_speed) -> ตำแหน่ง (ship_x) -> จอ (ship.move_to)
# เกมเต็ม: full_games/shooter_full.py:18 (ค่าฟิสิกส์) และ :178-193 (ขับยาน 2 แกน)
# ------------------------------------------------------------------------------
import bentogame as game

ACCEL, MAX_SPEED, FRICTION = 1.4, 13.0, 0.80  # ค่าเดียวกับเกมเต็ม (shooter_full.py:18)

game.title("SHOOTER")                          # หน้าเริ่ม: Start=เล่น Back=ออก (ทำ start ให้ในตัว)

ship_x, ship_speed = 365.0, 0.0               # ตำแหน่ง x + ความเร็วของยาน
ship_y = 352

ship = game.Box(ship_x, ship_y, 50, 20, color=game.GREEN)
score, lives = 0, 3
hud = game.Text("Score: %d   Lives: %d" % (score, lives) ,20 ,20)

def on_frame():
    global ship_x, ship_speed
    keys = game.keys()
    # ปุ่มระบบ เอนจินจัดการเอง: Back = ออก · Start = พักเกม (Pause)

    # ----- เติมส่วนนี้เอง (งานของน้อง ๆ): 5 ขั้นของยานที่มีน้ำหนัก -----
    # ใช้ keys ที่อ่านมาแล้วด้านบน (game.keys() -> keys.left / keys.right)
    # ทำตามขั้นตอน:
    #   ① เร่ง: ถ้ากดซ้ายให้ "เร่งไปทางซ้าย" ถ้ากดขวาให้ "เร่งไปทางขวา"
    #      โดยปรับ ship_speed ด้วยค่า ACCEL (ทิศซ้าย/ขวาใช้คนละเครื่องหมาย ลองคิดดูนะ)
    if keys.left and not keys.right:
        ship_speed -= ACCEL
    elif keys.right and not keys.left:
        ship_speed += ACCEL
    #   ② ไถล: ถ้าไม่กดปุ่มใดเลย ให้ ship_speed ค่อย ๆ ลดลงด้วยตัวคูณ FRICTION (เหลือ 80%)
    else:
        ship_speed *= FRICTION
    #   ③ เพดาน: บีบ (clamp) ship_speed ให้อยู่ในช่วง -MAX_SPEED .. MAX_SPEED — ใช้ max()/min()
    ship_speed = max(-MAX_SPEED,min(ship_speed,MAX_SPEED))
    #   ④ ขยับ + ขอบจอ: บวก ship_speed เข้า ship_x แล้วบีบให้อยู่ในช่วง 0 .. (game.WIDTH - ship.w)
    ship_x += ship_speed
    ship_x = max(0, min(ship_x,game.WIDTH - ship.w))
    #   ⑤ วาด: ship.move_to(...) — ส่ง ship_x และ y เดิมของยาน
    ship.move_to(ship_x, ship_y)
    # ถ้าติดตรงไหน เปิดเฉลยเต็มดูได้ที่ solution_codes/shooter_step2.py
       # <- ลบ pass ออกเมื่อเริ่มเขียน
    # -----------------------------------------------------------------------

game.run(on_frame, fps=30)