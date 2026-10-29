#Final Project "Glow In The Dark" by Chisanupong Wicheankul 68050200
#Glow in the Dark ให้ผู้เล่นสวมบทบาทเป็นนักผจญภัย ใช้ดาบต่อสู้กับมอนสเตอร์และเอาชีวิตรอด เพื่อช่วยเหลือผู้คนก่อนที่พลังชีวิตจะหมดลง

import bentogame as game
import random
import math
import bento_assets as A
import ui

FPS = 30
#-------------------------GAME-----------------------------------------


screen_w = game.WIDTH
screen_h = game.HEIGHT


# ด่าน : (มอนพร้อมกัน, key drop rate, เลือดมอน, ความเร็วมอน, เวลาด่าน วินาที, โอกาสฟื้นหัวใจตอนฆ่ามอน, เฟรมห่างระหว่างเกิดแต่ละตัว)
# ความเร็วมอนไม่ควรเกิน CARRY_MAX_V (3)   เฟรมห่าง 30 = 1 วินาที
stage_mon = {0: (1, 0.50, 1, 2, 60, 0.05, 36),
             1: (1, 0.50, 1, 2, 57, 0.05, 34),
             2: (2, 0.40, 1, 2, 54, 0.05, 32),
             3: (4, 0.30, 2, 2, 51, 0.08, 30),
             4: (5, 0.25, 2, 2, 48, 0.08, 28),
             5: (6, 0.20, 2, 2, 45, 0.08, 26),
             6: (7, 0.18, 3, 3, 42, 0.10, 24),
             7: (8, 0.15, 3, 3, 39, 0.10, 22),
             8: (8, 0.12, 3, 3, 36, 0.10, 20),
             9: (8, 0.10, 4, 3, 33, 0.10, 18)}
MAX_STAGE = 9
level = 0

stage_clear = False
time_up = False

#---------------------------------------------------------------------



#-------------------------PLAYER-----------------------------------------------
PLAYER_SIZE = 20
PLAYER_SPEED = 0.8

Heart = 3
MAX_HEART = 3           # ฟื้นได้ไม่เกินจำนวนนี้ (ตรงกับจำนวนเฟรมถุงเลือด)
PLAYER_DMG = 1
FRICTION = 0.8
MAX_V = 6
NORMAL_MAX_V = 6
CARRY_MAX_V = 3         # ตอนอุ้มเจ้าหญิง = ครึ่งหนึ่งของปกติ


SWING_REACH = 50        # ความกว้างการตี
cd_duration = 10        # คูลดาวน์การตี 10 ÷ 30 = 0.33 วินาที 

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

#เฟรม
RUN_EVERY = 4
BLINK_EVERY = 4
FLASH_FRAME = 3
SLASH_FRAMES = 6
slash_t = 0
run_t = 0
player_frame = 0
#--------------------------------------------------------------------------------------------




#monsters

MON_W, MON_H = 30, 30
MAX_MONSTERS = 8


HIT_FRAMES = 8
POOF_FRAMES = 8
poof_t = 0

#knockback
KB_SPEED = 16
STUN_FRAMES = 20
MON_BLINK = 3                 # ฟันแต่ไม่ตาย
MON_FLASH_FRAME = 3


BAND = 4
mons_wait = -100
spawn_timer = 0



#---------------------------------------------------------------------------------------------------





#------------------------------------PRINCESS---------------------------------------

princess_sx = 20
princess_sy = random.randint(50, screen_h - 50)
carrying = False





##---------------------------------------------------------------------------------------------------


#------------------------------------LIGHT (วงแสง)---------------------------------------
# เวลาของด่านอยู่ใน stage_mon วงแสงหดจาก LIGHT_R_MAX เหลือ LIGHT_R_MIN ตอนหมดเวลา
# มอนสเตอร์นอกวงจะถูกซ่อน (ยังเดินและชนผู้เล่นได้)
LIGHT_R_MAX = 190
LIGHT_R_MIN = 60

light_t = 0             # เฟรมที่เหลือ
light_total = 1         # เฟรมทั้งหมดของด่านนี้
light_r = LIGHT_R_MAX
light_cx = 0
light_cy = 0
WARN_SECS = 5           
warn_sec = -1           


RING_PTS = 15
RING_W = 4
RING_COLOR = game.YELLOW
RING_STEP = 6          
ring_unit = [(math.cos(2 * math.pi * i / RING_PTS), math.sin(2 * math.pi * i / RING_PTS))
             for i in range(RING_PTS + 1)]
light_ring = None
ring_r = 0
#------------------------------------------------------------------------------------------------------



#------------------------------------Bgm---------------------------------------
BGM_MUTE_FRAMES = 8     
BGM_WAVE = ui.WAVE_SINE  
BGM_VEL = 125           
BGM_SHIFT = 0              
BGM_FAST_SECS = 10         
BGM_FAST_UP = 2             


BGM_TUNE = (
    
    (69, 2), (69, 1), (71, 1), (72, 2), (71, 2),
    (69, 2), (76, 2), (74, 2), (72, 1), (71, 1),
    (69, 1), (64, 1), (69, 1), (71, 1), (72, 1), (71, 1), (69, 1), (67, 1),

    
    (69, 2), (69, 1), (71, 1), (72, 2), (74, 2),
    (76, 3), (77, 1), (76, 2), (74, 2),
    (72, 1), (69, 1), (72, 1), (74, 1), (76, 1), (74, 1), (72, 1), (71, 1),

    
    (69, 2), (70, 2), (69, 2), (67, 2),
    (65, 2), (69, 2), (67, 2), (65, 2),
    (64, 1), (65, 1), (67, 1), (65, 1), (64, 1), (62, 1), (60, 1), (59, 1),

    
    (57, 1), (60, 1), (64, 1), (69, 1), (67, 2), (65, 2),
    (64, 1), (67, 1), (71, 1), (76, 1), (74, 2), (71, 2),
    (72, 2), (71, 2), (69, 2), (64, 2)
)

def bgm_build(shift, fpe):
    
    return tuple((n + shift if n else 0, e * fpe * 25, e * fpe) for n, e in BGM_TUNE)

BGM_STEPS = bgm_build(BGM_SHIFT, 5)                          
BGM_STEPS_FAST = bgm_build(BGM_SHIFT + BGM_FAST_UP, 3)        
bgm = {"steps": (), "i": 0, "wait": 0}
bgm_mute = 0
#------------------------------------------------------------------------------------------------------


#----------------------------------------Interface---------------------------------------------------------


class Rect:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
    def move_to(self, x, y):
        self.x, self.y = x, y

SWING_SIZE = PLAYER_SIZE + 2 * SWING_REACH

HUD_STEP = 16
#------------------------------------------------------------------------------------------------------





#----------------------------------------สมอง (คิดล้วน ๆ ไม่แตะจอ)---------------------------------------
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


def monster_speed(lv):
    return stage_mon[lv][3]

def monster_hp(lv):
    return stage_mon[lv][2]

def spawn_gap(lv):
    return stage_mon[lv][6]

def to_int(v):
    return int(v + 0.5) if v >= 0 else -int(-v + 0.5)

def knock_dir(mx, my, px, py):
    
    dx = mx - px
    dy = my - py
    d = math.sqrt(dx * dx + dy * dy)
    if d == 0:
        return 1.0, 0.0
    return dx / d, dy / d

def light_time(lv):
    return stage_mon[lv][4] * FPS

def light_radius(left, total):
    return LIGHT_R_MIN + (LIGHT_R_MAX - LIGHT_R_MIN) * left // total

def in_light(obj):
    dx = obj.x + obj.w // 2 - light_cx
    dy = obj.y + obj.h // 2 - light_cy
    return dx * dx + dy * dy <= light_r * light_r
#------------------------------------------------------------------------------------------------------


#----------------------------------------bgm---------------------------------------
def make_player():
    return {"steps": (), "i": 0, "wait": 0}

def play(pl, steps):
    pl["steps"], pl["i"], pl["wait"] = steps, 0, 0

def player_step(pl):
    if pl["i"] >= len(pl["steps"]):
        return None
    if pl["wait"] > 0:
        pl["wait"] -= 1
        return None
    note, ms, frames = pl["steps"][pl["i"]]
    if note:
        ui.tone(note, BGM_WAVE, BGM_VEL, ms)       
    pl["i"] += 1
    pl["wait"] = frames - 1
    return note


def play_sfx(name):
    global bgm_mute
    game.sfx(name)
    bgm_mute = BGM_MUTE_FRAMES


def update_bgm():
    global bgm_mute
    if bgm_mute > 0:
        bgm_mute -= 1
        return
    if bgm["i"] >= len(bgm["steps"]):        
        if bgm["wait"] > 0:
            bgm["wait"] -= 1
            return
        play(bgm, BGM_STEPS_FAST if 0 < light_t <= BGM_FAST_SECS * FPS else BGM_STEPS)   # เวลาใกล้หมด = เร่ง
    player_step(bgm)
#------------------------------------------------------------------------------------------------------


def set_letters(sprites, text):
    for i in range(len(sprites)):
        sprites[i].frame(ord(text[i]) - 65)

def set_number(sprites, n):
    n = max(0, min(n, 10 ** len(sprites) - 1))
    for i in range(len(sprites) - 1, -1, -1):
        sprites[i].frame(n % 10)
        n //= 10


def heal():
    # ฟื้นหัวใจ 1 ดวง 
    global Heart
    if 0 < Heart < MAX_HEART:
        Heart += 1
        return True
    return False


def pickup_key():
    global getkey, key_on_floor
    if key_on_floor and all(aabb_parts(player, key)):
        getkey = True
        key_on_floor = False
        key.hide()
        key.move(key_wait, key_wait)
        play_sfx("point")





def kill_monster(i):
    monsters[i].hide()
    monsters[i].move(mons_wait, mons_wait)
    monsters[i].frame(0)
    mon_t[i] = 0
    mon_stun[i] = 0
    mon_vis[i] = False
    kb_vx[i] = 0.0
    kb_vy[i] = 0.0



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


    player_vx = clamp(player_vx, -MAX_V, MAX_V)
    player_vy = clamp(player_vy, -MAX_V, MAX_V)


    player_x = clamp(player_x + player_vx, 0, screen_w - player.w)
    player_y = clamp(player_y + player_vy, 0, screen_h - player.h)

    player.move(int(player_x), int(player_y))


    cx = player_x + player.w / 2
    cy = player_y + player.h / 2
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
    global slash_t
    if slash_t <= 0:
        return
    cx = player_x + player.w / 2
    cy = player_y + player.h / 2

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
    global carrying, MAX_V
    pressed_b = game.pressed_once("b", k)

    if pressed_b:
        if carrying:
            carrying = False
            play_sfx("back")
        elif all(aabb_parts(princess, swing_area)):
            carrying = True
            play_sfx("select")

    if carrying:
        MAX_V = CARRY_MAX_V
        princess.move(int(player_x - ( PLAYER_SIZE / 2)) , int(player_y - ( PLAYER_SIZE / 2)) )
    else:
        MAX_V = NORMAL_MAX_V


def knock_monster(i):
    m = monsters[i]
    dx, dy = knock_dir(m.x + m.w / 2, m.y + m.h / 2,
                       player_x + player.w / 2, player_y + player.h / 2)
    kb_vx[i] = dx * KB_SPEED
    kb_vy[i] = dy * KB_SPEED
    mon_stun[i] = STUN_FRAMES
    m.frame(MON_FLASH_FRAME)


def attack(k):
    global cd, score, slash_t, poof_t
    pressed_a = game.pressed_once("a", k)
    if cd <= 0 and pressed_a:

        slash_t = SLASH_FRAMES
        killed = False
        hurt = False
        healed = False

        for i in range(len(monsters)):
            m = monsters[i]
            if is_free(m) or mon_t[i] > 0:
                continue
            if all(aabb_parts(swing_area, m)):
                mon_hp[i] -= PLAYER_DMG
                if mon_hp[i] <= 0:
                    mon_t[i] = HIT_FRAMES
                    score += 1
                    s02p16_poof.move(int(m.x + m.w / 2 - s02p16_poof.w / 2), int(m.y + m.h / 2 - s02p16_poof.h / 2))
                    s02p16_poof.frame(0)
                    s02p16_poof.show()
                    poof_t = POOF_FRAMES
                    killed = True
                    if random.random() < stage_mon[level][5] and heal():
                        healed = True
                else:
                    knock_monster(i)
                    hurt = True

        # หนึ่งการฟัน หนึ่งเสียง (tone ไม่ต่อคิว)
        if healed:
            play_sfx("point")
        elif killed:
            play_sfx("explode")
        elif hurt:
            play_sfx("hit")
        else:
            play_sfx("fire")
        cd = cd_duration

def drop_key(x, y):

    global key_on_floor, kills_no_key
    if getkey or key_on_floor:
        return
    kills_no_key += 1
    key_droprate = stage_mon[level][1]
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
    if i is None:
        return

    edge = random.choice([1, 2, 3, 4]) # บน ล่าง ซ้าย ขวา

    if edge == 1:
        spawn_x = random.randint(0, screen_w)
        spawn_y = 0
    elif edge == 2:
        spawn_x = random.randint(0, screen_w)
        spawn_y = screen_h
    elif edge == 3:
        spawn_x = 0
        spawn_y = random.randint(0, screen_h)
    else:
        spawn_x = screen_w
        spawn_y = random.randint(0, screen_h)

    mon_t[i] = 0
    mon_stun[i] = 0
    mon_hp[i] = monster_hp(level)
    monsters[i].frame(0)
    monsters[i].move(spawn_x, spawn_y)
    monsters[i].show()
    mon_vis[i] = True             




def to_target(m_pos, target_pos, speed, band):

    if target_pos - m_pos > band:
        return m_pos + speed
    if target_pos - m_pos < -band:
        return m_pos - speed
    return m_pos




def update_monsters(monsters, player, monsters_speed):

    for i in range(len(monsters)):
        m = monsters[i]
        if is_free(m):
            continue

        if mon_t[i] > 0:
            mon_t[i] -= 1
            m.frame(min(3, (HIT_FRAMES - mon_t[i]) * 4 // HIT_FRAMES))
            if mon_t[i] == 0:
                mx, my = m.x, m.y
                kill_monster(i)
                drop_key(mx, my)
            continue

        if mon_stun[i] > 0:
            mon_stun[i] -= 1
            if mon_stun[i] % MON_BLINK == 0:      
                m.frame(MON_FLASH_FRAME if (mon_stun[i] // MON_BLINK) % 2 == 1 else 0)
            nx = clamp(m.x + to_int(kb_vx[i]), 0, screen_w - MON_W)  
            ny = clamp(m.y + to_int(kb_vy[i]), 0, screen_h - MON_H)
            m.move(nx, ny)
            kb_vx[i] *= FRICTION
            kb_vy[i] *= FRICTION
            continue

        new_x = to_target(m.x, player.x, monsters_speed, BAND)
        new_y = to_target(m.y, player.y, monsters_speed, BAND)
        m.move(new_x, new_y)


def update_mon_vis():
    # มอนนอกวงแสงซ่อน ในวงโชว์
    for i in range(len(monsters)):
        m = monsters[i]
        if is_free(m):
            continue
        vis = in_light(m)
        if vis != mon_vis[i]:
            if vis:
                m.show()
            else:
                m.hide()
            mon_vis[i] = vis


def check_player_hit():
    global invicible, invicible_t

    for i in range(len(monsters)):
        m = monsters[i]
        if not is_free(m) and mon_t[i] == 0:
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
        heal()                          # ผ่านด่าน ฟื้น 1 ดวง
        play_sfx("win")
        for i in range(len(monsters)):
            if not is_free(monsters[i]):
                kill_monster(i)
    return


def start_light():
    global light_t, light_total, light_r, warn_sec
    warn_sec = -1                    
    light_total = light_time(level)
    light_t = light_total
    light_r = LIGHT_R_MAX


def update_light():
  
    global light_t, light_r, light_cx, light_cy
    if light_t > 0:
        light_t -= 1
    light_r = light_radius(light_t, light_total)
    light_cx = int(player_x) + player.w // 2
    light_cy = int(player_y) + player.h // 2
    return light_t <= 0


def draw_light():

    global light_ring, ring_r
    pad = RING_W + 1
    if light_ring is None or abs(light_r - ring_r) >= RING_STEP:
        if light_ring is not None:
            light_ring.delete()
        size = 2 * light_r + 2 * pad
        light_ring = ui.Line(x=light_cx - light_r - pad, y=light_cy - light_r - pad,
                             w=size, h=size, color=RING_COLOR, value=RING_W)
        for ux, uy in ring_unit:
            light_ring.add_point(int(light_r + pad + ux * light_r),
                                 int(light_r + pad + uy * light_r))
        ring_r = light_r
    else:
        light_ring.pos(light_cx - ring_r - pad, light_cy - ring_r - pad)


def stage():
    global level, stage_clear, carrying, getkey, kills_no_key

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

    start_light()
    princess.move(int(princess_sx), int(princess_sy))
    door.move(door.x, random.randint(50, screen_h - 50))

def update_door():

    global door_frame
    if getkey:
        f = 1
    else:
        f = 0
    if f != door_frame:
        door.frame(f)
        door_frame = f



def ui_update():

    if score != ui_shown["score"]:
        set_number(score_digits, score)
        ui_shown["score"] = score
    if level != ui_shown["stage"]:
        set_number(stage_digits, level)
        ui_shown["stage"] = level
    if Heart != ui_shown["heart"]:
        hud_bag.frame(Heart)        # เฟรม 3 = เต็ม 0 = หมด
        ui_shown["heart"] = Heart

def on_frame():

    global spawn_timer, cd, Heart, invicible, invicible_t, time_up, warn_sec

    k = game.keys()
    update_player(k)
    cd = max(0, cd - 1)
    attack(k)
    carry(k)
    update_slash()

    update_monsters(monsters, player, monster_speed(level))

    spawn_timer += 1
    if spawn_timer >= spawn_gap(level):
        spawn_timer = 0
        spawn_monsters(monsters, screen_w, screen_h)

    if check_player_hit():
        Heart -= 1
        play_sfx("gameover" if Heart <= 0 else "lose_life")


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

    time_over = update_light()        
    update_mon_vis()                 

    secs = (light_t + FPS - 1) // FPS            
    if 0 < secs <= WARN_SECS and secs != warn_sec:
        warn_sec = secs
        play_sfx("move")
    draw_light()
    update_bgm()
    ui_update()

    if time_over:
        time_up = True
        play_sfx("gameover")
        return False

    if Heart <= 0:
        return False

    return True

def new_game():
    global Heart, score, level, getkey, key_on_floor, kills_no_key
    global player_x, player_y, player_vx, player_vy, cd, MAX_V
    global invicible, invicible_t, carrying, stage_clear, spawn_timer
    global slash_t, poof_t, run_t, player_frame, door_frame
    global princess_sy, swing_area, mon_t, mon_hp, mon_stun, mon_vis, kb_vx, kb_vy
    global door, s02p16_slash, player, princess, key, monsters
    global s02p16_poof
    global score_digits, stage_digits
    global hud_bag, ui_shown
    global time_up, bgm, bgm_mute, light_ring, ring_r

    Heart = 3
    score = 0
    level = 0
    getkey = False
    key_on_floor = False
    kills_no_key = 0
    player_x = game.WIDTH // 2
    player_y = game.HEIGHT // 2
    player_vx = 0
    player_vy = 0
    cd = 0
    MAX_V = NORMAL_MAX_V
    invicible = False
    invicible_t = 0
    carrying = False
    stage_clear = False; spawn_timer = 0
    slash_t = 0
    poof_t = 0
    run_t = 0
    player_frame = 0;
    door_frame = 0

    time_up = False
    light_ring = None
    ring_r = 0
    bgm_mute = 0
    bgm = make_player()
    play(bgm, BGM_STEPS)
    start_light()

    princess_sy = random.randint(50, screen_h - 50)


    game.ui.background("/assets/glwindark_bg.jpg")

    door = A.Sprite("rt_door", x=screen_w - 32 - 50, y=0)
    swing_area = Rect(player_x - SWING_REACH, player_y - SWING_REACH,
                      SWING_SIZE, SWING_SIZE)

    s02p16_slash = A.Sprite("s02p16_slash", mons_wait, mons_wait).hide()

    player = A.Sprite("glwindarkai", player_x, player_y)

    princess = A.Sprite("glwindark_princess", x=princess_sx, y=princess_sy)

    key = A.Sprite("glwindark_rt_key", x=key_wait, y=key_wait).hide()

    monsters = [A.Sprite("glwindark_monster", mons_wait, mons_wait).hide()
                for _ in range(MAX_MONSTERS)]
    mon_t = [0] * MAX_MONSTERS                
    mon_hp = [1] * MAX_MONSTERS
    mon_stun = [0] * MAX_MONSTERS            
    mon_vis = [False] * MAX_MONSTERS         
    kb_vx = [0.0] * MAX_MONSTERS
    kb_vy = [0.0] * MAX_MONSTERS

    s02p16_poof = A.Sprite("s02p16_poof", mons_wait, mons_wait).hide()


    score_label = [A.Sprite("hud_font", 10 + i * HUD_STEP, 18) for i in range(2)]
    score_digits = [A.Sprite("hud_digits", 10 + (2 + i) * HUD_STEP + 8, 10) for i in range(3)]  
    stage_label = [A.Sprite("hud_font", 160 + i * HUD_STEP, 18) for i in range(2)]
    stage_digits = [A.Sprite("hud_digits", 160 + (2 + i) * HUD_STEP + 8, 10) for i in range(1)]

    # หลอดเลือดชิ้นเดียว 96x24 4 เฟรม เปลี่ยนเฟรมตามเลือดที่เหลือ (เฟรม 0 = หมด ... เฟรม 3 = เต็ม)
    hud_bag = A.Sprite("glwidark_blood", x=screen_w // 2 - 64, y=screen_h - 40)

    set_letters(score_label, "PT")
    set_letters(stage_label, "LV")
    ui_shown = {"score": -1, "stage": -1, "heart": -1}

    how = "A ATTACK   B CARRY"
    game.Text(how, 510, 370, game.GB_LIGHTEST)

game.title("Glow In The Dark")

while True:
    new_game()
    if not game.run(on_frame, fps=FPS):
        game.save_best(score, "glow")       # กด Back
        break
    if not game.game_over(score, name="glow",
                          msg=("TIME UP" if time_up else "GAME OVER") + "  LV %d" % level):
        break