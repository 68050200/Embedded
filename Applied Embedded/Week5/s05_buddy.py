import bentogame as game

BALL_SIZE = 30
NUM_BALLS = 5

game.title("PONG")
game.Text("Pong - 5 Balls Bouncing", 16, 12, game.WHITE)

# --- สร้างลูกบอลและกำหนดสถานะเริ่มต้น (ตำแหน่ง, ความเร็ว) ---
# โครงสร้างข้อมูลแต่ละลูก: {"box": วัตถุวาด, "x": พิกัด X, "y": พิกัด Y, "vx": ความเร็ว X, "vy": ความเร็ว Y}
balls = []
speeds = [(4.0, 4.0), (-3.0, 5.0), (5.0, -3.5), (-4.5, -4.0), (3.5, -5.0)]

for i in range(NUM_BALLS):
    box = game.Box(game.WIDTH // 2, game.HEIGHT // 2, BALL_SIZE, BALL_SIZE, game.GB_LIGHTEST)
    vx, vy = speeds[i % len(speeds)]
    balls.append({
        "box": box,
        "x": float(game.WIDTH // 2),
        "y": float(game.HEIGHT // 2),
        "vx": vx,
        "vy": vy
    })

def on_each_frame():
    # วนลูปอัปเดตและเช็กการชนของลูกบอลแต่ละลูก
    for b in balls:
        # 1. ขยับตำแหน่ง
        b["x"] += b["vx"]
        b["y"] += b["vy"]
        
        # 2. เช็กชนขอบบน / ขอบล่าง
        if b["y"] <= 0 or b["y"] >= game.HEIGHT - BALL_SIZE:
            game.sfx("wall")
            b["vy"] = -b["vy"]
            
        # 3. เช็กชนขอบซ้าย / ขอบขวา
        if b["x"] <= 0 or b["x"] >= game.WIDTH - BALL_SIZE:
            game.sfx("wall")
            b["vx"] = -b["vx"]
            
        # 4. วาดลูกบอลในตำแหน่งใหม่
        b["box"].move_to(b["x"], b["y"])

game.run(on_each_frame, fps=60)