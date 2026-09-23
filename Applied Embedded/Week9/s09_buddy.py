#☐ เกมเขาวงกตลูกแก้ว — เปลี่ยนกล่องเป็นลูกแก้ว เติม &quot;หลุม&quot; หลายจุดที่ห้ามตก — เก็บตำแหน่งหลุมยังไง แล้วเช็กว่าลูกแก้วทับหลุมไหนในแต่ละเฟรม

import bentogame as game
import sensors
import time

game.start()
sensors.init()

BALL = 20
START_X, START_Y = 40, game.HEIGHT // 2


ball = game.Box(START_X, START_Y, BALL, BALL, color=game.CYAN)

label = game.Text("เอียงบอร์ดเพื่อขยับลูกแก้ว", 20, 20)
count_text = game.Text("Falls: 0", 20, 40) 

W, H = game.WIDTH, game.HEIGHT
holes = [
    (W * 0.12, H * 0.35, 16),
    (W * 0.42, H * 0.15, 20),
    (W * 0.78, H * 0.28, 15),
    (W * 0.22, H * 0.68, 18),
    (W * 0.60, H * 0.55, 22),
    (W * 0.88, H * 0.72, 17),
    (W * 0.35, H * 0.88, 19)
]
hole_shapes = [game.Box(hx, hy, hr * 2, hr * 2, color=game.GB_LIGHTEST) for hx, hy, hr in holes]

DEADZONE = 0.10
SPEED = 120.0
count = 0

def fall_check(ball_obj, hole_list):
    for h in hole_list:
        if game.hit(ball_obj, h):
            return True
    return False


while True:
    keys = game.keys()
    if keys.back:
        game.clear()
        break

    ax, ay, az = sensors.bmi270.acceleration()
    ax, ay, az = ax / 9.81, ay / 9.81, az / 9.81

    if abs(ax) < DEADZONE:
        ax = 0.0
    if abs(ay) < DEADZONE:
        ay = 0.0

    ball.move(ax * SPEED, -ay * SPEED)

    if fall_check(ball, hole_shapes):
        count += 1
        count_text.set("Falls: %d" % count) 
        ball.x, ball.y = START_X, START_Y

    time.sleep_ms(30)