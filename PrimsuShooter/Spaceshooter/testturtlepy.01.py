import turtle
import random
import time
import winsound
import os
import pygame
import cv2

# Register
turtle.register_shape("Player_Ship.gif")
turtle.register_shape("Enemy_Ship.gif")
turtle.register_shape("Boss_Ship.gif") 
turtle.register_shape("Laser_Bullet.gif")

# ----------------- CONFIG -----------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 20
PLAYER_BULLET_SPEED = 12
PLAYER_FIRE_COOLDOWN = 6

ENEMY_SPEED_Z = 0.18
ENEMY_FIRE_COOLDOWN_MIN = 110
ENEMY_FIRE_COOLDOWN_MAX = 160
ENEMY_BULLET_SPEED = 6

MAX_ENEMIES = 2
RESPAWN_MIN = 1
RESPAWN_MAX = 2

BOSS_APPEAR_SCORE = 200
BOSS_SPEED = 0.08
BOSS_HEALTH = 30

highest_score = 0

# ----------------- WAV FILES -----------------
folder = os.path.dirname(os.path.abspath(__file__))
laser_path = os.path.join(folder, "laser.wav")
explosion_path = os.path.join(folder, "explosion.wav")

def play_laser():
    winsound.PlaySound(laser_path, winsound.SND_ASYNC)

def play_explosion():
    winsound.PlaySound(explosion_path, winsound.SND_ASYNC)

# ----------------- WELCOME + PLAYER CARD -----------------
def show_welcome_and_player_card():
    wn = turtle.Screen()
    wn.setup(SCREEN_WIDTH, SCREEN_HEIGHT)
    wn.bgcolor("black")
    wn.title("Primus Galactic")
    
    # Welcome title
    welcome = turtle.Turtle()
    welcome.hideturtle()
    welcome.penup()
    welcome.color("cyan")
    welcome.goto(0, 50)
    welcome.write("Welcome to Primus Galactic", align="center", font=("Scarbes", 32, "bold"))
    time.sleep(2)
    welcome.clear()
    
    # Ask for player name
    player_name = wn.textinput("Enter your name", "Commander, what is your name?")
    if not player_name:
        player_name = "Unknown"

    # Player card display
    card = turtle.Turtle()
    card.hideturtle()
    card.penup()
    card.color("white")
    card.goto(-SCREEN_WIDTH//2 + 20, -SCREEN_HEIGHT//2 + 50)  # right side
    
    card.write(f"--- Player Card ---\n"
               f"Title: Commander\n"
               f"Name: {player_name}\n"
               f"Faction: Saga Empire\n"
               f"Ruler: Emperor Primus",
               align="left", font=("Scarbes", 16, "bold"))
    
    time.sleep(3)
    wn.clearscreen()

# ----------------- EXPLOSION FUNCTION -----------------
def explosion(wn, x, y):
    exp = turtle.Turtle()
    exp.hideturtle()
    exp.penup()
    exp.goto(x, y)
    play_explosion()
    colors = ["yellow", "orange", "red"]
    for size in range(6,0,-1):
        exp.clear()
        exp.color(random.choice(colors))
        exp.dot(size*10)
        wn.update()
        time.sleep(0.01)
    exp.clear()
    exp.hideturtle()
    exp.clear()

# ----------------- MAIN GAME -----------------
def start_game():
    global highest_score

    wn = turtle.Screen()
    wn.setup(SCREEN_WIDTH, SCREEN_HEIGHT)
    wn.bgcolor("black")
    wn.title("Primus Game")
    wn.tracer(0)

    # Starfield
    stars = []
    for _ in range(50):
        s = turtle.Turtle()
        s.penup()
        s.hideturtle()
        s.color("white")
        s.shape("circle")
        s.shapesize(random.uniform(0.05,0.15))
        s.goto(random.randint(-400,400), random.randint(-300,300))
        s.showturtle()
        stars.append(s)

    def update_starfield():
        for s in stars:
            s.sety(s.ycor() - 2)
            if s.ycor() < -310:
                s.sety(310)
                s.setx(random.randint(-400,400))

    # Player
    turtle.register_shape("player_ship", ((0,15),(10,-10),(0,-5),(-10,-10)))
    player = turtle.Turtle()
    player.penup()
    player.shape("Player_Ship.gif")
    player.color("cyan")
    player.setheading(90)
    player.goto(0, -230)

    player_health = 100
    score = 0
    fire_ready = True
    fire_timer = 0
    invincible = False
    inv_timer = 0

    bullets = []
    enemies = []
    enemy_bullets = []
    bosses = []

    # UI
    score_t = turtle.Turtle()
    score_t.hideturtle()
    score_t.penup()
    score_t.color("white")
    score_t.goto(-380,260)

    health_t = turtle.Turtle()
    health_t.hideturtle()
    health_t.penup()
    health_t.color("white")
    health_t.goto(-380,230)

    best_t = turtle.Turtle()
    best_t.hideturtle()
    best_t.penup()
    best_t.color("gold")
    best_t.goto(200,260)

    def update_ui():
        score_t.clear()
        health_t.clear()
        best_t.clear()
        score_t.write(f"Score: {score}", font=("Scarbes",16,"bold"))
        health_t.write(f"Health: {player_health}%", font=("Scarbes",16,"bold"))
        best_t.write(f"Best: {highest_score}", font=("Scarbes",16,"bold"))

    update_ui()

    # ----------------- ENEMY -----------------
    class Enemy:
        def __init__(self):
            self.t = turtle.Turtle()
            self.t.penup()
            self.t.color("red")
            self.t.shape("Enemy_Ship.gif")
            self.t.setheading(270)
            self.t.shapesize(2)
            self.x = random.randint(-250,250)
            self.y = random.randint(80,250)
            self.z = random.randint(350,480)
            self.cool = random.randint(ENEMY_FIRE_COOLDOWN_MIN,ENEMY_FIRE_COOLDOWN_MAX)
            self.alive = True

        def update(self):
            if not self.alive:
                return False
            self.z -= ENEMY_SPEED_Z
            scale = max(0.4,600/(self.z+1))
            self.t.shapesize(scale)
            self.t.goto(self.x*(scale*0.1), self.y*(scale*0.1))
            self.cool -=1
            if self.cool<=0:
                self.shoot()
                self.cool = random.randint(ENEMY_FIRE_COOLDOWN_MIN,ENEMY_FIRE_COOLDOWN_MAX)
            return self.z>20

        def shoot(self):
            if not self.alive:  # ensure dead enemies do not shoot
                return
            eb = turtle.Turtle()
            eb.penup()
            eb.color("orange")
            eb.shape("circle")
            eb.shapesize(0.8)
            eb.goto(self.t.xcor(), self.t.ycor())
            enemy_bullets.append(eb)
            play_laser()

    # ----------------- BOSS -----------------
    class Boss:
        def __init__(self):
            self.t = turtle.Turtle()
            self.t.penup()
            self.t.shape("Boss_Ship.gif")
            self.t.shapesize(4,6)
            self.t.color("purple")
            self.t.goto(0,200)
            self.health = BOSS_HEALTH
            self.cool = 60
            self.alive = True

        def update(self):
            if not self.alive:
                return False
            self.t.sety(self.t.ycor() - BOSS_SPEED)
            self.cool -=1
            if self.cool<=0:
                for angle in [-30,0,30]:
                    eb = turtle.Turtle()
                    eb.penup()
                    eb.color("orange")
                    eb.shape("circle")
                    eb.shapesize(1)
                    eb.goto(self.t.xcor(),self.t.ycor())
                    eb.setheading(270+angle)
                    enemy_bullets.append(eb)
                self.cool=80
                play_laser()
            return self.t.ycor()>-150

    # ----------------- COLLISION -----------------
    def collided(t1,t2,d=30):
        return t1.distance(t2)<d

    # ----------------- CONTROLS -----------------
    def left(): player.setx(player.xcor()-PLAYER_SPEED)
    def right(): player.setx(player.xcor()+PLAYER_SPEED)

    def fire():
        nonlocal fire_ready, fire_timer
        if fire_ready:
            b = turtle.Turtle()
            b.penup()
            b.color("yellow")
            b.shape("Laser_Bullet.gif")
            b.shapesize(1.0)
            b.goto(player.xcor(),player.ycor()+20)
            bullets.append(b)
            fire_ready=False
            fire_timer=PLAYER_FIRE_COOLDOWN
            play_laser()

    wn.listen()
    wn.onkeypress(left,"Left")
    wn.onkeypress(right,"Right")
    wn.onkeypress(fire,"space")

    # Spawn initial enemies
    for _ in range(random.randint(1,2)):
        enemies.append(Enemy())

    running=True

    while running:
        wn.update()
        update_starfield()

        # Player fire cooldown
        if not fire_ready:
            fire_timer -=1
            if fire_timer<=0:
                fire_ready=True

        # Spawn enemies
        if len(enemies)<MAX_ENEMIES:
            for _ in range(random.randint(RESPAWN_MIN,RESPAWN_MAX)):
                if len(enemies)<MAX_ENEMIES:
                    enemies.append(Enemy())

        # Spawn boss
        if score>=BOSS_APPEAR_SCORE and len(bosses)==0:
            bosses.append(Boss())

        # Update enemies
        alive=[]
        for e in enemies:
            if e.update():
                alive.append(e)
            else:
                if e.alive:
                    e.alive=False
                    e.t.hideturtle()
                    explosion(wn,e.t.xcor(),e.t.ycor())
                    score+=10
                    update_ui()
        enemies=alive

        # Update bosses
        alive_bosses=[]
        for b in bosses:
            if b.update():
                alive_bosses.append(b)
            else:
                if b.alive:
                    b.alive=False
                    explosion(wn,b.t.xcor(),b.t.ycor())
                    score+=50
                    update_ui()
        bosses=alive_bosses

        # Player bullets
        new_bullets=[]
        for b in bullets:
            b.sety(b.ycor()+PLAYER_BULLET_SPEED)
            hit=False
            for e in enemies:
                if collided(b,e.t,40) and e.alive:
                    e.alive=False
                    e.t.hideturtle()
                    explosion(wn,e.t.xcor(),e.t.ycor())
                    score+=10
                    hit=True
                    update_ui()
                    break
            for bb in bosses:
                if collided(b,bb.t,50) and bb.alive:
                    bb.health-=1
                    explosion(wn,b.xcor(),b.ycor())
                    if bb.health<=0:
                        bb.alive=False
                        bb.t.hideturtle()
                        score+=50
                        update_ui()
                    hit=True
                    break
            if not hit and b.ycor()<310:
                new_bullets.append(b)
            else:
                b.hideturtle()
        bullets=new_bullets

        # Enemy bullets
        new_enemy_bullets=[]
        for eb in enemy_bullets:
            eb.sety(eb.ycor()-ENEMY_BULLET_SPEED)
    
            if eb.ycor() < -330:
                eb.hideturtle()
            elif not invincible and collided(eb,player,35):
                player_health -= 10
                invincible = True
                inv_timer = 30
                explosion(wn, player.xcor(), player.ycor())  # show explosion
                update_ui()
                eb.hideturtle()  # hide the bullet immediately
            else:
                new_enemy_bullets.append(eb)

        enemy_bullets = new_enemy_bullets

        # Invincibility
        if invincible:
            inv_timer-=1
            if inv_timer%4<2:
                player.hideturtle()
            else:
                player.showturtle()
            if inv_timer<=0:
                invincible=False
                player.showturtle()

        if player_health<=0:
            running=False
            if score>highest_score:
                highest_score=score

    wn.clearscreen()
    show_welcome_and_player_card()
    start_game()

# RUN 
show_welcome_and_player_card()
start_game()