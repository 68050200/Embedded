#Final Project "Glow In The Dark" by Chisanupong Wicheankul 68050200
#Glow in the Dark ให้ผู้เล่นเป็นนักผจญภัย ฟันมอนส์เตอร์ด้วยดาบและเก็บสมบัติในด่านเดียว เพื่อเอาชีวิตรอดและทำคะแนนให้สูงที่สุดก่อนเลือดหมด


#ฟังกช๊น 
# เดินมีนำ้หนัก มี friction (clamp ตำแหน่ง + ความเร็ว)
# สำหรับผู้เล่น สภาวะ invicible สถานะโดนตีไม่ได้
# สำหรับมอนสเตอร์ - เดินเข้าหาตำแหน่งผู้เล่น + ระบบเลือด
# ระบบคะแนน สมบัติ drop จากมอนส์เตอร์
# ความยาก เพิ่มจำนวนมอนสเตอร์ เลือดมอนสเตอร์ เมื่อฆ่าถึงเกณฑ์ที่กำหนด

import bentogame as game
import random


FPS = 30
#-------------------------GAME-----------------------------------------


screen_w = game.WIDTH
screen_h = game.HEIGHT


stage_mon = {0: 1, 
         1: 1,
         2: 2,
         3: 4,
         4: 12 } #ระดับความยาก : จำนวนมอนสเตอร์
MAX_STAGE = 4
level = 0 

stage_clear = False

#---------------------------------------------------------------------



#-------------------------PLAYER-----------------------------------------------
PLAYER_SIZE = 20        # ผู้เล่นเป็นจัตุรัส (กว้าง = สูง)
PLAYER_SPEED = 1

Heart = 3
PLAYER_DMG = 1
FRICTION = 0.8
MAX_V = 20
NORMAL_MAX_V = 20
CARRY_MAX_V = 10


SWING_REACH = 50       # ความกว้างการตี
cd_duration = 15        # คูลดาวน์การตี  s = cd_duration ÷ FPS = 15 ÷ 30 = 0.5 วินาที



player_x = game.WIDTH // 2
player_y = game.HEIGHT // 2
player_vx = 0
player_vy = 0
cd = 0

score = 0
invicible = False
invicible_tset = 60
invicible_t = 0
#--------------------------------------------------------------------------------------------




#monsters

MON_W, MON_H = 30, 30
MAX_MONSTERS = 12
MONSTER_SPEED = 5
SPAWN_EVERY = FPS * 1   # เกิดใหม่ทุก


BAND = 4                         # ช่องว่างกันสั่น
mons_wait = -100                 # จุดนอกจอ
spawn_timer = 0



#---------------------------------------------------------------------------------------------------





#------------------------------------PRINCESS---------------------------------------

princess_sx = 20
princess_sy = random.randint(50, screen_h - 50)
carrying = False





##---------------------------------------------------------------------------------------------------


#----------------------------------------Interface---------------------------------------------------------
game.title("Glow In The Dark")

# พื้นที่ตี: กล่องเดียว จุดศูนย์กลางตรงกับกึ่งกลางผู้เล่น (สร้างก่อนผู้เล่นเพื่อให้อยู่ด้านหลัง)
SWING_SIZE = PLAYER_SIZE + 2 * SWING_REACH
swing_area = game.Box(player_x - SWING_REACH, player_y - SWING_REACH, SWING_SIZE, SWING_SIZE, game.YELLOW)

player = game.Box(player_x, player_y, PLAYER_SIZE, PLAYER_SIZE, game.CYAN)

princess = game.Box(princess_sx, princess_sy, 20, 30, 0xFF8FD0)

monsters = [game.Box(mons_wait, mons_wait, MON_W, MON_H, game.RED) for _ in range(MAX_MONSTERS)]

door_w = 40
door_x = screen_w - door_w - 50
door_y = 0
door = game.Box(door_x, door_y, door_w, 60, 0x7B4FD6)




score_text = game.Text("Score: 0", 10, 10, game.WHITE)
stage_text = game.Text("Stage : 0", 140, 10, game.WHITE)
#------------------------------------------------------------------------------------------------------

def clamp(value, low, high):
    return max(low, min(high, value))

def is_free(monster):
    return monster.x < 0

def find_free(monsters):
    for i in range(len(monsters)):
        if is_free(monsters[i]):
            return i
    return None

def aabb_parts(a, b):
    return (a.x < b.x + b.w, a.x + a.w > b.x, a.y < b.y + b.h, a.y + a.h > b.y)




def update_player(k):

    global player_x, player_y, player_vx, player_vy

    if k.left and not k.right:
        player_vx -= PLAYER_SPEED
    elif k.right and not k.left:
        player_vx += PLAYER_SPEED
    else:
        player_vx *= FRICTION

    if k.up and not k.down:
        player_vy -= PLAYER_SPEED
    elif k.down and not k.up:
        player_vy += PLAYER_SPEED
    else:
        player_vy *= FRICTION

    # จำกัดความเร็วสูงสุด
    player_vx = clamp(player_vx, -MAX_V, MAX_V)
    player_vy = clamp(player_vy, -MAX_V, MAX_V)

    # ไม่ให้หลุดขอบจอ
    player_x = clamp(player_x + player_vx, 0, screen_w - PLAYER_SIZE)
    player_y = clamp(player_y + player_vy, 0, screen_h - PLAYER_SIZE)

    player.move_to(player_x, player_y)

    # จุดศูนย์กลางพื้นที่ตี = จุดศูนย์กลางผู้เล่น
    cx = player_x + PLAYER_SIZE / 2
    cy = player_y + PLAYER_SIZE / 2
    swing_area.move_to(cx - SWING_SIZE / 2, cy - SWING_SIZE / 2)


def carry(k):
    global princess_x, princess_y, player_x, player_y ,carrying, MAX_V
    pressed_b = game.pressed_once("b", k)

    if pressed_b:
        if carrying:
            carrying = False
        elif all(aabb_parts(princess, swing_area)):
            carrying = True

    if carrying:
        MAX_V = CARRY_MAX_V
        princess.move_to(player_x - ( PLAYER_SIZE / 2) , player_y - ( PLAYER_SIZE / 2) )
    else:
        MAX_V = NORMAL_MAX_V



def attack(k):
    global cd, score
    pressed_a = game.pressed_once("a", k)
    if cd <= 0 and pressed_a:

        swing_area.set_color(game.WHITE)

        # พื้นที่ตี = จัตุรัสที่มีศูนย์กลางตรงกับผู้เล่น
        sx = swing_area.x
        sy = swing_area.y
        for m in monsters:
            if not is_free(m):
                if all(aabb_parts(swing_area, m)): #เป็นจริงเมื่อ 4 ค่าเป็นจริง
                    score += 1
                    score_text.set("Score: " + str(score))
                    m.move_to(mons_wait, mons_wait)  # วาร์ปออก (ตาย)
        cd = cd_duration
    elif cd <= 0:
        swing_area.set_color(game.YELLOW)



def spawn_monsters(monsters, screen_w, screen_h):

    mon_alive = 0
    for m in monsters:
        if not is_free(m):
            mon_alive += 1 
    if mon_alive >= stage_mon[level]:
        return


    i = find_free(monsters)
    if i is None: #ไม่มีเหลือเลย
        return

    #จุดเกิดมอนสเตอร์
    edge = random.choice([1, 2, 3, 4]) # ด้าน บน ล่าง ซ้าย ขวา

    if edge == 1: # ขอบบน
        spawn_x = random.randint(0, screen_w)
        spawn_y = 0
    elif edge == 2: # ขอบล่าง
        spawn_x = random.randint(0, screen_w)
        spawn_y = screen_h
    elif edge == 3: # ขอบซ้าย
        spawn_x = 0
        spawn_y = random.randint(0, screen_h)
    else: # ขอบขวา
        spawn_x = screen_w
        spawn_y = random.randint(0, screen_h)

    monsters[i].move_to(spawn_x, spawn_y)




def to_target(m_pos, target_pos, speed, band): #ตำแหน่งมอน เป้าหมาย ความเร็ว dead_zone

    if target_pos - m_pos > band:
        return m_pos + speed
    if target_pos - m_pos < -band:
        return m_pos - speed
    return m_pos




def update_monsters(monsters, player, monsters_speed):

    for m in monsters: #ตำแหน่งมอน
        if is_free(m): # ตัวที่ว่าง
            continue
        new_x = to_target(m.x, player.x, monsters_speed, BAND)
        new_y = to_target(m.y, player.y, monsters_speed, BAND)
        m.move_to(new_x, new_y)

def check_player_hit():
    global invicible, invicible_t
    
    for m in monsters:
        if not is_free(m): #ตัวที่อยู่ในจอ ไม่ว่าง
            if all(aabb_parts(player, m))and not invicible:
                m.move_to(mons_wait, mons_wait)
                invicible = True
                invicible_t = 0
                return True
    
    return False



def stage_cleared():
    global stage_clear
    if all(aabb_parts(princess, door)) and not carrying:
        stage_clear = True
        for m in monsters:
            m.move_to(mons_wait, mons_wait)
    return


def stage():
    global level, stage_clear, carrying

    #-------------------------------stage------------------------------------------------


    if not stage_clear:                    
        return
    #if state_clear
    stage_clear = False                    
    carrying = False         

    if level < MAX_STAGE:                  
        level += 1
    stage_text.set("Stage : " + str(level))       
    princess.move_to(princess_sx, princess_sy)     
    door.move_to(door.x, random.randint(50, screen_h - 50))  

    #---------------------------------------------------------------------------------------------------

    princess.move_to(princess_sx, princess_sy)                                  # เจ้าหญิงกลับจุดเริ่ม
    door.move_to(door.x, random.randint(50, screen_h - 50))
    return 

def on_frame():

    global spawn_timer, cd, Heart, invicible, invicible_t

    k = game.keys()
    update_player(k)
    cd = max(0, cd - 1)
    attack(k)
    carry(k)

    update_monsters(monsters, player, MONSTER_SPEED)

    spawn_timer += 1
    if spawn_timer >= SPAWN_EVERY:
        spawn_timer = 0
        spawn_monsters(monsters, screen_w, screen_h)

    if check_player_hit():
        Heart -= 1


    if invicible:
        invicible_t += 1
        player.set_color(game.WHITE)

        if invicible_t >= invicible_tset:
            player.set_color(game.CYAN)
            invicible = False

    stage_cleared()
    stage()



    if Heart <= 0: #ตาย
        return False




    return True


game.run(on_frame, fps=FPS)