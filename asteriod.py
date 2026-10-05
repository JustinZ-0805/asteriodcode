import pygame
import random
import math

pygame.init()

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids")

clock = pygame.time.Clock()


ship_position = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
ship_velocity = pygame.Vector2(0, 0)
ship_acceleration = pygame.Vector2(0, 0)

ship_angle = 90

ROTATION_SPEED = 3
THRUST = 0.15
DRAG = 0.99
MAX_SPEED = 7

MISSILE_SPEED = 8
ENEMY_MISSILE_SPEED = 2.5
ENEMY_FIRE_DELAY = 120
ENEMY_PATROL_SPEED = 1.4
MAX_HEALTH = 3
RESPAWN_TIME = 600


asteroids = []
missiles = []
enemy_missiles = []

enemy_position = pygame.Vector2(WIDTH * 0.25, HEIGHT / 2)
enemy_velocity = pygame.Vector2(ENEMY_PATROL_SPEED, 0.8)
enemy_angle = 0
enemy_fire_timer = 0
enemy_alive = True
enemy_respawn_timer = 0
player_health = MAX_HEALTH
player_invulnerable_timer = 0
font = pygame.font.SysFont(None, 32)
game_over = False


def take_damage():
    global player_health, player_invulnerable_timer, game_over

    if player_invulnerable_timer > 0 or game_over:
        return

    player_health -= 1
    player_invulnerable_timer = 90

    if player_health <= 0:
        game_over = True


for i in range(6):

    x = random.randint(50, WIDTH - 50)
    y = random.randint(50, HEIGHT - 50)

    radius = random.randint(20, 40)

    vx = random.randint(-3, 3)
    vy = random.randint(-3, 3)

    if vx == 0:
        vx = 1

    if vy == 0:
        vy = 1

    asteroids.append([
        pygame.Vector2(x, y),
        pygame.Vector2(vx, vy),
        radius
    ])


running = True

while running:

    if game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill("black")
        game_over_text = font.render("GAME OVER", True, "red")
        screen.blit(game_over_text, (WIDTH / 2 - 70, HEIGHT / 2 - 20))
        health_text = font.render(f"Health: {player_health}", True, "white")
        screen.blit(health_text, (WIDTH / 2 - 60, HEIGHT / 2 + 20))
        pygame.display.flip()
        clock.tick(60)
        continue

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:

                radians = math.radians(ship_angle)

                forward = pygame.Vector2(
                    math.cos(radians),
                    -math.sin(radians)
                )

                missile_position = pygame.Vector2(ship_position)

                missile_velocity = forward * MISSILE_SPEED

                missiles.append([
                    missile_position,
                    missile_velocity
                ])


    keys = pygame.key.get_pressed()


    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        ship_angle += ROTATION_SPEED

    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        ship_angle -= ROTATION_SPEED


    radians = math.radians(ship_angle)

    forward = pygame.Vector2(
        math.cos(radians),
        -math.sin(radians)
    )


    ship_acceleration = pygame.Vector2(0, 0)


    if keys[pygame.K_UP] or keys[pygame.K_w]:

        ship_acceleration = forward * THRUST


    ship_velocity += ship_acceleration


    ship_velocity *= DRAG


    if ship_velocity.length() > MAX_SPEED:

        ship_velocity.scale_to_length(MAX_SPEED)


    ship_position += ship_velocity
    player_invulnerable_timer = max(0, player_invulnerable_timer - 1)


    if ship_position.x > WIDTH:
        ship_position.x = 0

    if ship_position.x < 0:
        ship_position.x = WIDTH

    if ship_position.y > HEIGHT:
        ship_position.y = 0

    if ship_position.y < 0:
        ship_position.y = HEIGHT


    if not enemy_alive:
        enemy_respawn_timer -= 1
        if enemy_respawn_timer <= 0:
            enemy_alive = True
            enemy_position = pygame.Vector2(WIDTH * 0.25, HEIGHT / 2)
            enemy_velocity = pygame.Vector2(ENEMY_PATROL_SPEED, 0.8)
            enemy_fire_timer = 0
    else:
        enemy_fire_timer -= 1

        enemy_position += enemy_velocity

        if enemy_position.x < 60 or enemy_position.x > WIDTH - 60:
            enemy_velocity.x *= -1

        if enemy_position.y < 60 or enemy_position.y > HEIGHT - 60:
            enemy_velocity.y *= -1

        to_player = ship_position - enemy_position
        if to_player.length() > 0:
            enemy_angle = math.degrees(math.atan2(-to_player.y, to_player.x))

        if enemy_fire_timer <= 0:
            if to_player.length() > 0:
                enemy_direction = to_player.normalize()
                enemy_missiles.append([
                    pygame.Vector2(enemy_position),
                    enemy_direction * ENEMY_MISSILE_SPEED
                ])
            enemy_fire_timer = ENEMY_FIRE_DELAY

    for asteroid in asteroids:

        asteroid[0] += asteroid[1]


        if asteroid[0].x > WIDTH:
            asteroid[0].x = 0

        if asteroid[0].x < 0:
            asteroid[0].x = WIDTH

        if asteroid[0].y > HEIGHT:
            asteroid[0].y = 0

        if asteroid[0].y < 0:
            asteroid[0].y = HEIGHT


    for missile in missiles:

        missile[0] += missile[1]

    for enemy_missile in enemy_missiles:

        enemy_missile[0] += enemy_missile[1]


    for missile in missiles[:]:

        if (
            missile[0].x < 0
            or missile[0].x > WIDTH
            or missile[0].y < 0
            or missile[0].y > HEIGHT
        ):

            missiles.remove(missile)


    for i in range(len(asteroids)):

        for j in range(i + 1, len(asteroids)):

            a = asteroids[i]
            b = asteroids[j]

            distance = a[0].distance_to(b[0])

            if distance < a[2] + b[2]:

                normal = a[0] - b[0]

                if normal.length() != 0:

                    normal = normal.normalize()

                    speed1 = a[1].dot(normal)
                    speed2 = b[1].dot(normal)

                    mass1 = a[2]
                    mass2 = b[2]

                    new_speed1 = (
                        speed1 * (mass1 - mass2)
                        + 2 * mass2 * speed2
                    ) / (mass1 + mass2)

                    new_speed2 = (
                        speed2 * (mass2 - mass1)
                        + 2 * mass1 * speed1
                    ) / (mass1 + mass2)

                    a[1] += (new_speed1 - speed1) * normal
                    b[1] += (new_speed2 - speed2) * normal


    for missile in missiles[:]:

        for asteroid in asteroids[:]:

            distance = missile[0].distance_to(asteroid[0])

            if distance < asteroid[2] + 4:

                if asteroid in asteroids:
                    asteroids.remove(asteroid)

                if missile in missiles:
                    missiles.remove(missile)

                break

    if enemy_alive:
        for missile in missiles[:]:
            if missile[0].distance_to(enemy_position) < 18:
                enemy_alive = False
                enemy_respawn_timer = RESPAWN_TIME
                missiles.remove(missile)
                break

    for enemy_missile in enemy_missiles[:]:

        if enemy_missile[0].distance_to(ship_position) < 14:
            if player_invulnerable_timer <= 0:
                take_damage()
            enemy_missiles.remove(enemy_missile)
            continue

        if (
            enemy_missile[0].x < 0
            or enemy_missile[0].x > WIDTH
            or enemy_missile[0].y < 0
            or enemy_missile[0].y > HEIGHT
        ):
            enemy_missiles.remove(enemy_missile)

    for asteroid in asteroids[:]:
        if ship_position.distance_to(asteroid[0]) < asteroid[2] + 12:
            take_damage()
            asteroids.remove(asteroid)
            break


    screen.fill("black")


    left = forward.rotate(140)
    right = forward.rotate(-140)

    p1 = ship_position + forward * 22
    p2 = ship_position + left * 16
    p3 = ship_position + right * 16


    pygame.draw.polygon(
        screen,
        "white",
        [p1, p2, p3],
        2
    )


    if keys[pygame.K_UP] or keys[pygame.K_w]:

        back = ship_position - forward * 18

        pygame.draw.circle(
            screen,
            "yellow",
            back,
            5
        )


    if enemy_alive:
        enemy_forward = pygame.Vector2(
            math.cos(math.radians(enemy_angle)),
            -math.sin(math.radians(enemy_angle))
        )

        enemy_left = enemy_forward.rotate(140)
        enemy_right = enemy_forward.rotate(-140)

        enemy_p1 = enemy_position + enemy_forward * 22
        enemy_p2 = enemy_position + enemy_left * 16
        enemy_p3 = enemy_position + enemy_right * 16

        pygame.draw.polygon(
            screen,
            "red",
            [enemy_p1, enemy_p2, enemy_p3],
            2
        )

    health_text = font.render(f"Health: {player_health}", True, "white")
    screen.blit(health_text, (20, 20))

    for asteroid in asteroids:

        pygame.draw.circle(
            screen,
            "white",
            asteroid[0],
            asteroid[2],
            2
        )


    for missile in missiles:

        pygame.draw.circle(
            screen,
            "white",
            missile[0],
            4
        )

    for enemy_missile in enemy_missiles:

        pygame.draw.circle(
            screen,
            "red",
            enemy_missile[0],
            4
        )


    pygame.display.flip()

    clock.tick(60)


pygame.quit()