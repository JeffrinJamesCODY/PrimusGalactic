
import turtle
import random

# Config
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 25
BULLET_SPEED = 25
ENEMY_SPEED_Z = 0.7
ENEMY_BULLET_SPEED = 18
SPAWN_RATE = 60

# Global leaderboard
highest_score = 0

# Main Game Function

def start_game():
    global highest_score

    wn = turtle.Screen()
    wn.setup(SCREEN_WIDTH, SCREEN_HEIGHT)
    wn.bgcolor("black")
    wn.title("Primus Galactic")
    wn.tracer(0)

    # Player
    player = turtle.Turtle()
    player.penup()
    player.color("cyan")
    player.shape("triangle")
    player.shapesize(2, 2)
    player.setheading(90)
    player.goto(0, -230)

    player_health = 100
    invincible = False
    inv_timer = 0

    # Bullets
    bullets = []
    enemy_bullets = []
    enemies = []

    # UI
    score = 0
    score_t = turtle.Turtle()
    score_t.hideturtle()
    score_t.penup()
    score_t.color("white")
    score_t.goto(-380, 260)

    health_t = turtle.Turtle()
    health_t.hideturtle()
    health_t.penup()
    health_t.color("white")
    health_t.goto(-380, 230)

    leaderboard_t = turtle.Turtle()
    leaderboard_t.hideturtle()
    leaderboard_t.penup()
    leaderboard_t.color("gold")
    leaderboard_t.goto(200, 260)

    def update_UI():
        score_t.clear()
        health_t.clear()
        leaderboard_t.clear()

        score_t.write(f"Score: {score}", font=("Arial", 16, "bold"))
        health_t.write(f"Health: {player_health}%", font=("Arial", 16, "bold"))
        leaderboard_t.write(f"Best: {highest_score}", font=("Arial", 16, "bold"))

    update_UI()

    # Enemy Object
    class Enemy:
        def __init__(self):
            self.t = turtle.Turtle()
            self.t.penup()
            self.t.color("red")
            self.t.shape("triangle")
            self.t.setheading(270)
            self.t.shapesize(3)

            self.x = random.randint(-280, 280)
            self.y = random.randint(80, 260)
            self.z = random.randint(300, 450)
            self.cool = random.randint(40, 110)

        def update(self):
            self.z -= ENEMY_SPEED_Z
            scale = max(0.3, 600 / (self.z + 1))
            self.t.shapesize(scale)
            self.t.goto(self.x * (scale * 0.1), self.y * (scale * 0.1))

            self.cool -= 1
            if self.cool <= 0:
                self.shoot()
                self.cool = random.randint(40, 110)

            return self.z > 20

        def shoot(self):
            eb = turtle.Turtle()
            eb.penup()
            eb.color("orange")
            eb.shape("circle")
            eb.shapesize(0.5)
            eb.goto(self.t.xcor(), self.t.ycor())
            enemy_bullets.append(eb)

    def collided(t1, t2, d=25):
        return t1.distance(t2) < d

    # Controls
    def move_left(): player.setx(player.xcor() - PLAYER_SPEED)
    def move_right(): player.setx(player.xcor() + PLAYER_SPEED)

    def fire_bullet():
        b = turtle.Turtle()
        b.penup()
        b.color("yellow")
        b.shape("circle")
        b.shapesize(0.4)
        b.goto(player.xcor(), player.ycor() + 15)
        bullets.append(b)

    wn.listen()
    wn.onkeypress(move_left, "Left")
    wn.onkeypress(move_right, "Right")
    wn.onkeypress(fire_bullet, "space")

    # Game Loop
    running = True
    frame = 0

    while running:
        wn.update()
        frame += 1

        # Spawn enemies
        if frame % SPAWN_RATE == 0:
            enemies.append(Enemy())

        # Update enemies
        new_enemies = []
        for e in enemies:
            if e.update():
                new_enemies.append(e)
            else:
                e.t.hideturtle()
        enemies = new_enemies

        # Player bullets
        new_bullets = []
        for b in bullets:
            b.sety(b.ycor() + BULLET_SPEED)
            hit = False
            for e in enemies:
                if collided(b, e.t, 30):
                    e.t.hideturtle()
                    e.z = 0
                    hit = True
                    score += 10
                    update_UI()
                    break

            if not hit and b.ycor() < 300:
                new_bullets.append(b)
            else:
                b.hideturtle()
        bullets = new_bullets

        # Enemy bullets
        new_enemy_bullets = []
        for eb in enemy_bullets:
            eb.sety(eb.ycor() - ENEMY_BULLET_SPEED)

            if not invincible and collided(eb, player, 25):
                eb.hideturtle()
                player_health -= 10
                invincible = True
                inv_timer = 40
                update_UI()
            elif eb.ycor() > -320:
                new_enemy_bullets.append(eb)
            else:
                eb.hideturtle()
        enemy_bullets = new_enemy_bullets

        # Invincibility
        if invincible:
            inv_timer -= 1
            if inv_timer % 6 < 3:
                player.hideturtle()
            else:
                player.showturtle()
            if inv_timer <= 0:
                invincible = False
                player.showturtle()

        # Restart condition
        if player_health <= 0:
            running = False
            if score > highest_score:
                highest_score = score

    # Restart the game
    wn.clearscreen()
    start_game()

# Start endless mode
turtle.clearscreen()
start_game()

turtle.mainloop()
