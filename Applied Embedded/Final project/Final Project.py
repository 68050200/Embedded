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
import bento_assets as A

FPS = 30
#-------------------------GAME-----------------------------------------


screen_w = game.WIDTH
screen_h = game.HEIGHT


stage_mon = {0: (1, 0.50),
             1: (1, 0.50),
             2: (2, 0.40),
             3: (4, 0.30),
             4: (12, 0.15)}   #ระดับความยาก : จำนวนมอนสเตอร์ key drop rate
MAX_STAGE = 4
level = 0 

stage_clear = False

#---------------------------------------------------------------------



#-------------------------PLAYER-----------------------------------------------
PLAYER_SIZE = 20        
PLAYER_SPEED = 1

Heart = 3
PLAYER_DMG = 1
FRICTION = 0.8
MAX_V = 20
NORMAL_MAX_V = 20
CARRY_MAX_V = 10


SWING_REACH = 50       # ความกว้างการตี
cd_duration = 15        # คูลดาวน์การตี  s = cd_duration ÷ FPS = 15 ÷ 30 = 0.5 วินาที

getkey = False
key_wait = -100
door_frame = 0  
key_on_floor = False
kills_no_key = 0
KEY_PITY = 10


player_x = game.WIDTH // 2
player_y = game.HEIGHT // 2
player_vx = 0
player_vy = 0
cd = 0

score = 0
invicible = False
invicible_tset = 60
invicible_t = 0

# ---- อนิเมชั่นผู้เล่น / ดาบ (นับเฟรม ไม่ใช้ sleep) ----
RUN_EVERY = 4           # สลับเฟรมวิ่งทุก 4 เฟรมเกม
BLINK_EVERY = 4         # กะพริบตอน invicible ทุก 4 เฟรมเกม
FLASH_FRAME = 3         # เฟรมที่ 4 ของ glwindarkai (นับจาก 0) ใช้กะพริบตอนโดนตี
SLASH_FRAMES = 6        # ดาบฟันค้างกี่เฟรม (ภาพ slash มี 3 เฟรม เฟรมละ 2)
slash_t = 0
run_t = 0
player_frame = 0
#--------------------------------------------------------------------------------------------




#monsters

MON_W, MON_H = 30, 30
MAX_MONSTERS = 12
MONSTER_SPEED = 5
SPAWN_EVERY = FPS * 1   # เกิดใหม่ทุก

HIT_FRAMES = 8          # โดนตีแล้วหยุดเดินและเล่นอนิเมชั่นกี่เฟรม
POOF_FRAMES = 8         # ควัน poof ค้างกี่เฟรม (ภาพมี 4 เฟรม เฟรมละ 2)
poof_t = 0


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
game.background(0x14121F)
# พื้นที่ตี: ไม่มีภาพ (ไม่เสียวิดเจ็ต) ใช้แค่ x y w h ให้ aabb_parts ตรวจชน

door_x = screen_w - 32 - 50
door_y = 0
door = A.Sprite("rt_door", x=door_x, y=door_y)




class Rect:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
    def move_to(self, x, y):
        self.x, self.y = x, y

SWING_SIZE = PLAYER_SIZE + 2 * SWING_REACH
swing_area = Rect(player_x - SWING_REACH, player_y - SWING_REACH, SWING_SIZE, SWING_SIZE)

# ภาพดาบฟัน: สร้างก่อนตัวละคร = อยู่หลังตัวละคร ตัวละครจึงไม่หาย
s02p16_slash = A.Sprite("s02p16_slash", mons_wait, mons_wait).hide()



player = A.Sprite("glwindarkai", player_x, player_y)






princess = A.Sprite("glwindark_princess", x=princess_sx, y=princess_sy)



key = A.Sprite("glwindark_rt_key", x=key_wait, y=key_wait).hide()



# มอนสเตอร์: ภาพนิ่งเฟรม 0 จนกว่าจะโดนตีค่อยเล่นอนิเมชั่น
monsters = [A.Sprite("glwindark_monster", mons_wait, mons_wait).hide() for _ in range(MAX_MONSTERS)]




glwindark_monster = monsters[0]      # ชื่อเดิม ชี้ตัวแรกของชุด
mon_t = [0] * MAX_MONSTERS                 # >0 = กำลังเล่นอนิเมชั่นโดนตี












# ควัน poof ตอนตีโดนมอน 
s02p16_poof = A.Sprite("s02p16_poof", mons_wait, mons_wait).hide()




# ---- HUD (สร้างหลังสุด = อยู่ชั้นบนสุด) ----
HUD_STEP = 16           # ระยะห่างตัวอักษร/ตัวเลข (ปรับให้เท่าความกว้างภาพ hud_font / hud_digits)
HEART_STEP = 24         # ระยะห่างหัวใจ




score_label = [A.Sprite("hud_font", 10 + i * HUD_STEP, 18) for i in range(5)]      
score_digits = [A.Sprite("hud_digits", 58 + (2 + i) * HUD_STEP + 8, 10) for i in range(3)]  # 000-999






stage_label = [A.Sprite("hud_font", 160 + i * HUD_STEP, 18) for i in range(5)]       
stage_digits = [A.Sprite("hud_digits", 208 + (2 + i) * HUD_STEP + 8, 10) for i in range(1)]  # 0-4




hud_font = score_label[0]          # ชื่อเดิม ชี้ตัวแรก
hud_digits = score_digits[0]       # ชื่อเดิม ชี้ตัวแรก




heart_x = screen_w // 2 - (Heart * HEART_STEP) // 2
hud_hearts = [A.Sprite("hud_heart", heart_x + i * HEART_STEP, screen_h - 32) for i in range(Heart)]
hud_heart = hud_hearts[0]          # ชื่อเดิม ชี้ดวงแรก (ภาพนิ่ง เฟรม 0)
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


# ---- HUD ด้วยภาพ: ตัวอักษร A-Z = เฟรม 0-25 ของ hud_font · ตัวเลข 0-9 = เฟรม 0-9 ของ hud_digits ----
def set_letters(sprites, text):
    for i in range(len(sprites)):
        sprites[i].frame(ord(text[i]) - 65)

def set_number(sprites, n):
    n = max(0, min(n, 10 ** len(sprites) - 1))
    for i in range(len(sprites) - 1, -1, -1):      # เขียนจากหลักหน่วยย้อนไป
        sprites[i].frame(n % 10)
        n //= 10

set_letters(score_label, "SCORE")
set_letters(stage_label, "STAGE")
ui_shown = {"score": -1, "stage": -1, "heart": -1}


def pickup_key():
    global getkey, key_on_floor
    if key_on_floor and all(aabb_parts(player, key)):
        getkey = True
        door.frame(0)   
        key_on_floor = False
        key.hide()
        key.move(key_wait, key_wait)





def kill_monster(i):
    monsters[i].hide()
    monsters[i].move(mons_wait, mons_wait)
    monsters[i].frame(0)
    mon_t[i] = 0
  


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

    player.move(int(player_x), int(player_y))      # A.Sprite ใช้ .move() (Box ใช้ .move_to())

    # จุดศูนย์กลางพื้นที่ตี = จุดศูนย์กลางผู้เล่น
    cx = player_x + PLAYER_SIZE / 2
    cy = player_y + PLAYER_SIZE / 2
    swing_area.move_to(cx - SWING_SIZE / 2, cy - SWING_SIZE / 2)


def update_player_anim():

    global run_t, player_frame
    moving = abs(player_vx) > 0.5 or abs(player_vy) > 0.5
    run_t = run_t + 1 if moving else 0
    f = (run_t // RUN_EVERY) % 3


    if invicible and (invicible_t // BLINK_EVERY) % 2 == 0:
        f = FLASH_FRAME
    if f != player_frame:
        player.frame(f)
        player_frame = f


def update_slash():
    # ภาพดาบฟันรอบตัว: ตามตัวผู้เล่น เล่นเฟรม 0,0,1,1,2,2 แล้วซ่อน
    global slash_t
    if slash_t <= 0:
        return
    cx = player_x + PLAYER_SIZE / 2
    cy = player_y + PLAYER_SIZE / 2

    s02p16_slash.frame(min(2, (SLASH_FRAMES - slash_t) // 2))

    s02p16_slash.move(int(cx - s02p16_slash.w / 2), int(cy - s02p16_slash.h / 2))

    if slash_t == SLASH_FRAMES:
        s02p16_slash.show()
    slash_t -= 1
    if slash_t == 0:
        s02p16_slash.hide()


def update_poof():
    global poof_t
    if poof_t <= 0:
        return
    poof_t -= 1
    s02p16_poof.frame(min(3, (POOF_FRAMES - poof_t) // 2))
    if poof_t == 0:
        s02p16_poof.hide()


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
        princess.move(int(player_x - ( PLAYER_SIZE / 2)) , int(player_y - ( PLAYER_SIZE / 2)) )
    else:
        MAX_V = NORMAL_MAX_V



def attack(k):
    global cd, score, slash_t, poof_t
    pressed_a = game.pressed_once("a", k)
    if cd <= 0 and pressed_a:

        slash_t = SLASH_FRAMES                      # เริ่มภาพดาบฟัน

        for i in range(len(monsters)):
            m = monsters[i]
            if is_free(m) or mon_t[i] > 0:          # ว่าง หรือกำลังเล่นอนิเมชั่นโดนตีอยู่ = ข้าม (โดนได้ครั้งเดียวต่อครั้ง)
                continue
            if all(aabb_parts(swing_area, m)): #เป็นจริงเมื่อ 4 ค่าเป็นจริง
                mon_t[i] = HIT_FRAMES               # หยุดเดิน แล้วเริ่มเล่นอนิเมชั่น
                score += 1
                s02p16_poof.move(int(m.x + m.w / 2 - s02p16_poof.w / 2), int(m.y + m.h / 2 - s02p16_poof.h / 2))
                s02p16_poof.frame(0)
                s02p16_poof.show()
                poof_t = POOF_FRAMES
        cd = cd_duration

def drop_key(x, y):
    # เรียกตอนฟันมอนสเตอร์ตาย: สุ่มดรอปกุญแจตรงที่มันตาย
    global key_on_floor, kills_no_key
    if getkey or key_on_floor:
        return
    kills_no_key += 1
    key_droprate = stage_mon[level][1]            # อัตราดรอปของด่านนี้
    if random.random() < key_droprate or kills_no_key >= KEY_PITY:
        key.move(int(clamp(x, 0, screen_w - key.w)), int(clamp(y, 0, screen_h - key.h)))
        key.show()
        key_on_floor = True
        kills_no_key = 0

def spawn_monsters(monsters, screen_w, screen_h):

    mon_alive = 0
    for m in monsters:
        if not is_free(m):
            mon_alive += 1 
    if mon_alive >= stage_mon[level][0]:
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

    mon_t[i] = 0
    monsters[i].frame(0)                 
    monsters[i].move(spawn_x, spawn_y)
    monsters[i].show()




def to_target(m_pos, target_pos, speed, band): #ตำแหน่งมอน เป้าหมาย ความเร็ว dead_zone

    if target_pos - m_pos > band:
        return m_pos + speed
    if target_pos - m_pos < -band:
        return m_pos - speed
    return m_pos




def update_monsters(monsters, player, monsters_speed):

    for i in range(len(monsters)): #ตำแหน่งมอน
        m = monsters[i]
        if is_free(m): # ตัวที่ว่าง
            continue

        if mon_t[i] > 0:                     # โดนตี: หยุดเดิน เล่นอนิเมชั่น 4 เฟรม
            mon_t[i] -= 1
            m.frame(min(3, (HIT_FRAMES - mon_t[i]) * 4 // HIT_FRAMES))
            if mon_t[i] == 0:
                if mon_t[i] == 0:
                    mx, my = m.x, m.y
                    kill_monster(i)          # อนิเมชั่นจบ = หายไปเลย
                    drop_key(mx, my)
            continue

        new_x = to_target(m.x, player.x, monsters_speed, BAND)
        new_y = to_target(m.y, player.y, monsters_speed, BAND)
        m.move(new_x, new_y)

def check_player_hit():
    global invicible, invicible_t
    
    for i in range(len(monsters)):
        m = monsters[i]
        if not is_free(m) and mon_t[i] == 0: #ตัวที่อยู่ในจอ ไม่ว่าง และไม่ได้กำลังตาย
            if all(aabb_parts(player, m))and not invicible:
                kill_monster(i)
                invicible = True
                invicible_t = 0
                return True
    
    return False


def stage_cleared():
    global stage_clear
    if all(aabb_parts(princess, door)) and getkey and not carrying:
        stage_clear = True
        for i in range(len(monsters)):
            if not is_free(monsters[i]):
                kill_monster(i)
    return


def stage():
    global level, stage_clear, carrying, getkey, key_on_floor, kills_no_key

    #-------------------------------stage------------------------------------------------

    if not stage_clear:                    
        return

    
    getkey = False  
    
    kills_no_key = 0
    key.hide()
    key.move(key_wait, key_wait)
    stage_clear = False
    carrying = False         

    if level < MAX_STAGE:                  
        level += 1
    princess.move(int(princess_sx), int(princess_sy)) 
    door.move(door.x, random.randint(50, screen_h - 50))  

    #---------------------------------------------------------------------------------------------------

    princess.move(int(princess_sx), int(princess_sy))                                 # เจ้าหญิงกลับจุดเริ่ม
    door.move(door.x, random.randint(50, screen_h - 50))
    return 

def update_door():
    # ประตูตามสถานะกุญแจ: มีกุญแจ = เปิด (เฟรม 1) · ไม่มี = ปิด (เฟรม 0) ส่งคำสั่งเฉพาะตอนเปลี่ยน
    global door_frame
    f = 1 if getkey else 0
    if f != door_frame:
        door.frame(f)
        door_frame = f



def ui_update():
    # HUD เขียนเฉพาะตอนค่าเปลี่ยน
    if score != ui_shown["score"]:
        set_number(score_digits, score)
        ui_shown["score"] = score
    if level != ui_shown["stage"]:
        set_number(stage_digits, level)
        ui_shown["stage"] = level
    if Heart != ui_shown["heart"]:                 # หัวใจ = ภาพนิ่ง โชว์ตามจำนวนเลือด
        for i in range(len(hud_hearts)):
            if i < Heart:
                hud_hearts[i].show()
            else:
                hud_hearts[i].hide()
        ui_shown["heart"] = Heart

def on_frame():

    global spawn_timer, cd, Heart, invicible, invicible_t

    k = game.keys()
    update_player(k)
    cd = max(0, cd - 1)
    attack(k)
    carry(k)
    update_slash()

    update_monsters(monsters, player, MONSTER_SPEED)

    spawn_timer += 1
    if spawn_timer >= SPAWN_EVERY:
        spawn_timer = 0
        spawn_monsters(monsters, screen_w, screen_h)

    if check_player_hit():
        Heart -= 1


    if invicible:
        invicible_t += 1
        if invicible_t >= invicible_tset:
            invicible = False

    update_poof()
    update_player_anim()
    pickup_key()
    stage_cleared()
    stage()
    update_door()
    ui_update()



    if Heart <= 0: #ตาย
        return False




    return True


game.run(on_frame, fps=FPS)