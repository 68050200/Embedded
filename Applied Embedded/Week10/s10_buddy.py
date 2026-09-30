
# ------------------------------------------------------------------------------
#s10_buddy.py
# ------------------------------------------------------------------------------

import bentogame as game

ACCEL, MAX_SPEED, FRICTION = 1.4, 13.0, 0.80  # ค่าเดียวกับเกมเต็ม (shooter_full.py:18)

game.title("SHOOTER")                          # หน้าเริ่ม: Start=เล่น Back=ออก (ทำ start ให้ในตัว)

ship_x, ship_speed = 365.0, 0.0               # ตำแหน่ง x + ความเร็วของยาน
ship_y = 352

score, lives = 0, 3
hud = game.Text("Score: %d   Lives: %d" % (score, lives) ,20 ,20)


def ship_create(x, color): #ตำแหน่ง สี ล
    return( {"ship" : game.Box(x, ship_y, 50, 20, color=color),
             "x" : float(x), 
             "speed": 0.0 }
        )


ships = [ship_create(200, game.GREEN),    # ผู้เล่น 1
         ship_create(550, game.GREEN)]      # ผู้เล่น 2

def controller(s, left, right): #ยานลำที่ ปุ่มซ้าย ปุ่มขวา
    if left and not right:
        s["speed"] -= ACCEL
        
    elif right and not left:
        s["speed"] += ACCEL
        
    else:
        s["speed"] *= FRICTION
        
    s["speed"] = max(-MAX_SPEED, min(s["speed"], MAX_SPEED)) #Clamp ความเร็ว
    
    s["x"] += s["speed"] #ตำแหน่ง+ความเร็ว
    
    s["x"] = max(0, min(s["x"], game.WIDTH - s["ship"].w)) #Clamp  ขอบ
    
    s["ship"].move_to(s["x"], ship_y) #ขยับยาน



def on_frame():
    keys = game.keys()
    controller(ships[0], keys.left, keys.right)   # ผู้เล่น 1 ปุ่ม ซ้ายขวา left right
    controller(ships[1], keys.x, keys.b) # ผู้เล่น 2 ปุ่ม ซ้ายขวา x b


game.run(on_frame, fps=30)