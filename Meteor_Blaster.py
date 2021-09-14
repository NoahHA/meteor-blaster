import pygame as pg
from random import randrange, randint, choice
from time import sleep, time
from operator import itemgetter
from math import tan, radians
import threading
import sqlite3
import json

pg.init()
pg.font.init()


class settings:
    def __init__(self):
        self.p1_image = "images/spaceship.bmp"
        self.p2_image = "images/spaceship2.png"
        self.u_name = ""
        self.b_ground = pg.image.load("images/space.jpeg")
        self.width, self.height = self.b_ground.get_size()
        self.ship_size = (35, 35)
        self.total_meteors = 60
        self.FPS = 50
        self.ship_speed = 7
        self.lives = 3
        self.level = 1
        self.b_cooldown = 0.4
        self.score = 0
        self.money = 0
        self.time_paused = 0
        self.time_coin = 0
        self.gun_image = 0
        self.ship_pos = 0
        self.q1 = 0
        self.q2 = 0
        self.q3 = 0
        self.q4 = 0
        self.boss_bullet_pos = 0
        self.meteor_position = None
        self.no_sprite_hits = False
        self.two_player = False
        self.double_p = False
        self.shield_activate = False
        self.b_cooldown_on = False
        self.shots_fired = False
        self.nuke_activate = False
        self.nuke_ready = True
        self.heart_refresh = True
        self.meteor_group = pg.sprite.Group()
        self.heart_group = pg.sprite.Group()
        self.bullet_group = pg.sprite.Group()
        self.coin_group = pg.sprite.Group()
        self.powerup_group = pg.sprite.GroupSingle()
        self.font = pg.font.Font(None, 45)

        self.nuke_number = 1 if self.nuke_activate else 0
        if self.shield_activate:
            self.shield_number = 1
        if self.no_sprite_hits:
            self.shield_number = 2
        else:
            self.shield_number = 0

class boss(pg.sprite.Sprite):
    def __init__(self, screen, health, ship1, ship2):
        super().__init__()

        self.ship1 = ship1
        self.ship2 = ship2
        self.health = health
        self.screen = screen
        self.screen_rect = screen.get_rect()

        # configures boss image
        self.image = pg.image.load("images/flying saucer.png").convert()
        self.image = pg.transform.scale(self.image, (700, 200))
        self.image.set_colorkey((255, 255, 255))

        # places boss at top-centre of the screen
        self.rect = self.image.get_rect()
        self.rect.centerx = self.screen_rect.centerx
        self.rect.centery = 0

    def die(self):
        """Animation that gets played when boss is defeated"""
        pg.display.update()
        boss_width = self.rect.width
        boss_height = self.rect.height

        interval = 0.04 # time between loops
        num_frames = 150
        drift = 1 # amount boss drifts each frame

        # boss' death animation
        for i in range(num_frames):
            sleep(interval)
            self.rect.centery += drift
            self.screen.blit(s.b_ground, (0, 0))

            self.screen.blit(self.image, self.rect)
            pg.display.flip()

        sleep(2)

        interval = 0.01
        num_frames = 400

        for i in range(num_frames):
            sleep(interval)

            # slowly shrinks the boss image as it drifts off screen
            boss_width *= 0.99
            boss_height *= 0.99
            self.rect.centery += drift
            self.screen.blit(s.b_ground, (0, 0))
            self.screen.blit(
                pg.transform.scale(self.image, (int(boss_width), int(boss_height))),
                self.rect,
            )
            pg.display.flip()

    def shoot(self, y_current, enemy_boss_health, ship1, ship2, attack_choice):
        """Boss randomly selects from a range of attack choices"""
        angles = [40, 30, 20, 10, -10, -20, -30, -40]
        enemy_bullet_group = pg.sprite.Group()

        if attack_choice == "spread_shot":
            enemy_bullet_group.empty()
            laser_size = (2, 9)

            # creates a group of lasers
            while len(enemy_bullet_group) < len(angles):
                enemy_bullet_group.add(
                    laser(screen, self.rect.centerx, 0, "images/beams1.png", laser_size)
                )

            # rotates each of the lasers to a different angle
            for i, bullet in enumerate(enemy_bullet_group):
                bullet.image = pg.transform.rotate(bullet.image, angles[i])
                gradient = tan(radians(angles[i]))
                bullet.rect.centery += y_current
                bullet.rect.centerx += gradient * y_current

        elif attack_choice == "wave_shot":
            enemy_bullet_group.empty()
            x_value, y_value = 20, 0
            num_bullets = 10
            # offset between each bullet in the group
            x_offset, y_offset = 60, 150
            laser_size = (1, 4)

            # creates a group of bullets offset from eachother
            while len(enemy_bullet_group) < num_bullets:
                enemy_bullet_group.add(
                    laser(screen, x_value, y_value, "images/beams3.png", laser_size)
                )
                x_value += x_offset
                y_value -= y_offset

            # moves the bullets down the screen
            for bullet in enemy_bullet_group:
                bullet.rect.centery += y_current

        elif attack_choice == "straight_shot":
            enemy_bullet_group.empty()
            x_value = 10
            num_bullets = 8
            laser_size = (2, 9)
            x_offset = 80

            # creates a group of bullets in a line
            while len(enemy_bullet_group) < num_bullets:
                enemy_bullet_group.add(
                    laser(screen, x_value, 0, "images/beams4.png", laser_size)
                )
                x_value += x_offset

            # moves the bullets down the screen
            for bullet in enemy_bullet_group:
                bullet.rect.centery += y_current

        elif attack_choice == "inside_shot":
            enemy_bullet_group.empty()
            x_value = 180
            laser_size = (2, 9)
            num_bullets = 10
            x_offset = 30

            # creates a group of bullets in the middle of the screen
            while len(enemy_bullet_group) < num_bullets:
                enemy_bullet_group.add(
                    laser(screen, x_value, 0, "images/beams2.png", laser_size)
                )
                x_value += x_offset

            # moves the bullets down the screen
            for bullet in enemy_bullet_group:
                bullet.rect.centery += y_current

        collision_list1 = pg.sprite.spritecollide(ship1, enemy_bullet_group, False)
        if ship2 != 0:
            collision_list2 = pg.sprite.spritecollide(ship2, enemy_bullet_group, False)

        # if a player gets shot
        if (ship2 != 0 and (len(collision_list1) + len(collision_list2) > 0)) or (
            ship2 == 0 and len(collision_list1) > 0
        ):
            pg.display.update()
            s.lives -= 1

            # reinitialises players' ships
            ship1.__init__(
                ship1.speed,
                s.ship_size,
                ship1.lives,
                ship1.screen,
                ship1.ship_image,
                ship1.rect,
            )
            if ship2 != 0:
                ship2.__init__(
                    ship2.speed, ship2.size, ship2.lives, ship2.screen, ship2.ship_image
                )

            # fades the ships back in
            for i in range(255):
                ship1.ship.set_alpha(i)
                if ship2 != 0:
                    ship2.ship.set_alpha(i)
                screen.blit(ship1.ship, ship1.rect)
                if ship2 != 0:
                    screen.blit(ship2.ship, ship2.rect)
                pg.display.update()

            s.boss_bullet_pos = 101

        height = enemy_boss_health * 4
        border_rect = (7, 60, 15, 400)
        hitbox_rect = (7, 460 - height, 15, height)

        if enemy_boss_health < 100:
            screen.fill((138, 7, 7), border_rect)
            screen.fill((7, 136, 70), hitbox_rect)

        enemy_bullet_group.draw(self.screen)
        self.screen.blit(self.image, self.rect)
        pg.display.update()



class laser(pg.sprite.Sprite):
    def __init__(self, screen, center_x, center_y, image, size):
        super().__init__()
        self.image = image
        self.center_x = center_x
        self.center_y = center_y
        self.screen = screen
        self.speed = 5
        self.size = size

        self.image = pg.image.load(self.image).convert()
        pg.transform.scale(self.image, self.size)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.centery = center_y
        self.rect.centerx = center_x


class boost(pg.sprite.Sprite):
    def __init__(self, choice=0):
        super().__init__()
        if choice == 2:
            powerup_image = "images/heart.png"
        else:
            powerup_image = "images/coin.png"
        self.image = pg.image.load(powerup_image).convert()
        self.image.set_colorkey((255, 255, 255))
        self.image = pg.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect()


class meteor(pg.sprite.Sprite):
    def __init__(self, screen, size, speed, image, health):
        super().__init__()

        self.health = health
        self.screen = screen
        self.size = size
        self.speed = speed
        self.image = image

        self.image = pg.image.load(image)
        self.image = pg.transform.scale(self.image, self.size).convert()
        self.image.set_colorkey((0, 0, 0))
        self.image.set_colorkey((255, 255, 255))
        self.surface = pg.Surface(self.image.get_size())
        self.rect = self.image.get_rect()
        self.width = self.image.get_width()
        self.height = self.image.get_height()


class gun(pg.sprite.Sprite):
    def __init__(self, screen, ship, player_two=False):
        super().__init__()

        bullet_images = [
            "images/bullet2.png",
            "images/bullet3.png",
            "images/bullet_upgrade.png",
        ]
        self.screen = screen
        self.ship = ship
        self.speed = 5
        self.size = (3, 12)
        if not player_two:
            self.bullet_image = bullet_images[s.gun_image]
        else:
            self.bullet_image = bullet_images[s.gun_image + 1]

        self.image = pg.image.load(self.bullet_image).convert()
        pg.transform.scale(self.image, self.size)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.centery = self.ship.rect.centery - 10

        if ship.ship_image == "images/spaceship.bmp":
            self.rect.centerx = self.ship.rect.centerx + 1
        else:
            self.rect.centerx = self.ship.rect.centerx + 10

    def update(self):
        self.rect.y -= 5
        screen.blit(self.image, self.rect)


class spaceship(pg.sprite.Sprite):
    def __init__(self, speed, size, lives, screen, ship_image, start=False):
        super().__init__()

        self.speed = speed
        self.size = size
        self.lives = lives
        self.screen = screen
        self.ship_image = ship_image

        self.image = pg.image.load(ship_image).convert()
        self.ship = pg.transform.scale(self.image, self.size).convert()
        self.ship.set_colorkey((255, 0, 0))
        self.rect = self.ship.get_rect()
        self.screen_rect = screen.get_rect()

        if not (start):
            self.rect.centerx = self.screen_rect.centerx
            self.rect.centery = self.screen_rect.centery
            self.rect.bottom = self.screen_rect.bottom
        else:
            self.rect = start

        self.centerx = float(self.rect.centerx)
        self.centery = float(self.rect.centery)

        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False

    def move(self):
        if self.moving_right:
            self.centerx += self.speed
        if self.rect.right > 600:
            self.centerx = 20
        if self.moving_down and self.rect.bottom <= 475:
            self.centery += self.speed

        if self.moving_left:
            self.centerx -= self.speed
        if self.rect.left < 0:
            self.centerx = 580
        if self.moving_up and self.rect.top >= 0:
            self.centery -= self.speed

        self.rect.centerx = self.centerx
        self.rect.centery = self.centery


def get_name(letters):
    pg.key.set_repeat()
    event = pg.event.wait()
    enter_pressed = False
    if event.type == pg.KEYDOWN:
        if event.key == pg.K_RETURN:
            enter_pressed = True
        elif event.key == pg.K_BACKSPACE and len(letters) > 0:
            letters.pop()
        elif event.key != pg.K_BACKSPACE:
            letters.append((event.unicode).upper())
    yield enter_pressed
    yield "".join(letters)


def check_events(ship1, ship2, screen, bullet_group, timer):

    for event in pg.event.get():
        if event.type == pg.KEYDOWN:

            if event.key == pg.K_p:
                pg.key.set_repeat()
                t1 = time()

                if len(s.meteor_group) > 0:
                    save = pg.image.load("images/save_game_button.png")
                    save_rect = save.get_rect()
                    save_rect.center = (523, 23)
                    screen.blit(save, save_rect)

                paused = pg.image.load("images/paused.jpg")
                paused_rect = paused.get_rect()
                paused_rect.center = screen.get_rect().center
                screen.blit(paused, paused_rect)

                display_text(
                    ("Meteors: " + str(len(s.meteor_group))), "left", "top", 20, 20
                )
                display_text(("Money: " + str(s.money)), "left", "top", 20, 50)
                display_text(("Lives: " + str(s.lives)), "left", "top", 20, 80)
                pg.display.update()
                end = False

                while not (end):
                    pg.event.clear()
                    event = pg.event.wait()

                    if event.type == pg.MOUSEBUTTONDOWN:
                        x, y = pg.mouse.get_pos()

                        if (
                            save_rect.collidepoint(x, y) and len(s.meteor_group) > 0
                        ):  # save game
                            connection = sqlite3.connect("User_Data.sqlite")
                            cursor = connection.cursor()
                            screen.blit(pg.image.load("images/enter_name.jpg"), (0, 0))
                            pg.display.update()
                            letters = []

                            if s.u_name == "":
                                while True:
                                    enter_pressed, s.u_name = get_name(letters)

                                    display_text(
                                        s.u_name, "centerx", "centery", 300, 390
                                    )
                                    pg.display.update()
                                    screen.blit(
                                        pg.image.load("images/enter_name.jpg"), (0, 0)
                                    )
                                    if enter_pressed:
                                        break

                            cursor.execute(
                                "SELECT Name FROM Saved_Games WHERE Name=?",
                                (s.u_name.upper(),),
                            )
                            data = cursor.fetchone()

                            if data is None:
                                cursor.execute(
                                    """INSERT INTO Saved_Games(Name, Rocks, Speed, Shield, Money, Points, Nuke, Lives, Level) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                    (
                                        s.u_name.upper(),
                                        len(s.meteor_group),
                                        ship1.speed,
                                        s.shield_number,
                                        s.money,
                                        s.score,
                                        s.nuke_number,
                                        s.lives,
                                        s.level,
                                    ),
                                )

                                connection.commit()
                                connection.close()
                                screen.blit(
                                    pg.image.load("images/game_saved.jpg"), (0, 0)
                                )
                                pg.display.update()
                                sleep(2)
                                exit()

                            else:
                                print("username already exists in database")

                    if event.type == pg.KEYDOWN:
                        if event.unicode == "p":
                            s.time_paused += time() - t1
                            pg.key.set_repeat(1, 1)
                            end = True

            if event.key == pg.K_SPACE and not (s.b_cooldown_on):
                s.shots_fired = True
                s.bullet_group.add(gun(screen, ship1))
                sleep(0.05)

            if event.key == pg.K_UP:
                ship1.moving_up = True
            if event.key == pg.K_DOWN:
                ship1.moving_down = True
            if event.key == pg.K_LEFT:
                ship1.moving_left = True
            if event.key == pg.K_RIGHT:
                ship1.moving_right = True
            if event.key == pg.K_2 and s.nuke_ready:
                s.nuke_activate = True
                s.nuke_ready = False
            if event.key == pg.K_1 and s.shield_activate:
                s.no_sprite_hits = True
                s.shield_activate = False
                ship1.__init__(
                    ship1.speed,
                    (50, 50),
                    ship1.lives,
                    ship1.screen,
                    "images/shield_ship1.jpg",
                    ship1.rect,
                )

            if ship2 != 0:
                if event.key == pg.K_w:
                    ship2.moving_up = True
                if event.key == pg.K_s:
                    ship2.moving_down = True
                if event.key == pg.K_a:
                    ship2.moving_left = True
                if event.key == pg.K_d:
                    ship2.moving_right = True
                if event.key == pg.K_q:
                    pg.key.set_repeat()
                    s.bullet_group.add(gun(screen, ship2, True))
                    pg.key.set_repeat(1, 1)

        if event.type == pg.KEYUP:
            if event.key == pg.K_UP:
                ship1.moving_up = False
            if event.key == pg.K_DOWN:
                ship1.moving_down = False
            if event.key == pg.K_LEFT:
                ship1.moving_left = False
            if event.key == pg.K_RIGHT:
                ship1.moving_right = False

        if ship2 != 0:
            if event.type == pg.KEYUP:
                if event.key == pg.K_w:
                    ship2.moving_up = False
                if event.key == pg.K_s:
                    ship2.moving_down = False
                if event.key == pg.K_a:
                    ship2.moving_left = False
                if event.key == pg.K_d:
                    ship2.moving_right = False

        ship1.move()
        if ship2 != 0:
            ship2.move()


def update_screen(ship1, ship2, screen, y1, y2, bullet_group, timer):
    screen.blit(s.b_ground, (0, y1))
    screen.blit(s.b_ground, (0, y2))
    screen.blit(ship1.ship, ship1.rect)
    if ship2 != 0:
        screen.blit(ship2.ship, ship2.rect)
    check_events(ship1, ship2, screen, s.bullet_group, timer)


def add_sprites(rock_list, screen, powerup_list):
    if len(s.meteor_group) == 0:
        for i in range(int(round(s.total_meteors * (5 / 6)))):  # 50
            x, y = randrange(15, 35), randrange(15, 35)
            area = x * y
            health = 1
            rock_speed = 4.675
            for i in range(area):
                rock_speed -= 0.003
            rock = meteor(screen, (x, y), rock_speed, "images/meteor.png", health)
            rock.rect.x = randrange(10, 590)
            rock.rect.y = randrange(-15000, -250)
            rock.image.set_colorkey((0, 0, 0))
            s.meteor_group.add(rock)

        for i in range(int(round(s.total_meteors * 1 / 6))):  # 10
            x, y = randrange(40, 70), randrange(40, 70)
            health = 2
            rock_speed = 1.5
            rock = meteor(screen, (x, y), rock_speed, "images/meteor.png", health)
            rock.rect.x = randrange(screen.get_width())
            rock.rect.y = randrange(-15000, -250)
            rock.image.set_colorkey((0, 0, 0))
            s.meteor_group.add(rock)

    while len(s.powerup_group) != 1:
        powerup = boost()
        powerup.rect.x = randrange(screen.get_width())
        powerup.rect.y = randrange(-10000, -1000)
        s.powerup_group.add(powerup)

    pg.sprite.groupcollide(s.powerup_group, s.meteor_group, True, True)


def highlight_button(rect, size, image):
    highlighted_button = pg.image.load(image)
    highlighted_button = pg.transform.scale(highlighted_button, size)
    screen.blit(highlighted_button, rect)
    pg.display.update()


def update_sprites(sprite_list, screen, speed_increase):
    for sprite in sprite_list:
        if len(sprite_list) > 1:
            sprite.rect.y += sprite.speed + speed_increase
        else:
            sprite.rect.y += 2.5 + speed_increase
        if sprite.rect.y > screen.get_height():
            sprite.kill()
            s.score -= 200

    return sprite_list


def sprite_collision(ship1, ship2, group, screen, kill):
    collision_list1 = pg.sprite.spritecollide(ship1, group, False)
    if ship2 != 0:
        collision_list2 = pg.sprite.spritecollide(ship2, group, False)

    for sprite in collision_list1:
        if kill:
            sprite.kill()
        if not (s.no_sprite_hits):
            ship1.ship.set_alpha(0)
            pg.display.update()
            screen.blit(ship1.ship, ship1.rect)
            s.lives -= 1

        s.no_sprite_hits = False
        ship1.__init__(
            ship1.speed, s.ship_size, ship1.lives, ship1.screen, s.p1_image, ship1.rect
        )

    if ship2 != 0:
        for sprite in collision_list2:
            if kill:
                sprite.kill()
            if not (s.no_sprite_hits):
                ship2.ship.set_alpha(0)
                pg.display.update()
                screen.blit(ship2.ship, ship2.rect)
                s.lives -= 1

            ship2.__init__(
                ship2.speed, ship2.size, ship2.lives, ship2.screen, ship2.ship_image
            )
            s.no_sprite_hits = False

    return s.lives


while True:
    s = settings()
    screen = pg.display.set_mode((600, 480))
    pg.display.set_caption("'METEOR BLASTER - 'The Dark Souls of Arcade Games'")
    pg.key.set_repeat(1, 1)

    screen.blit(
        pg.transform.scale(
            pg.image.load("images/meteor shower load game.png").convert(),
            (screen.get_size()),
        ),
        (0, 0),
    )
    play_button, one_player_button, two_player_button, load_game_button = (
        pg.Rect(200, 375, 200, 50),
        pg.Rect(85, 265, 130, 50),
        pg.Rect(385, 265, 130, 50),
        pg.Rect(235, 267, 130, 50),
    )
    pg.display.update()
    end = False
    game_loaded = False

    while not (end):
        x, y = pg.mouse.get_pos()

        if one_player_button.collidepoint(x, y):
            highlight_button(
                one_player_button, (130, 50), "images/highlighted_op_button.png"
            )

        elif two_player_button.collidepoint(x, y):
            highlight_button(
                two_player_button, (130, 50), "images/highlighted_tp_button.png"
            )

        elif load_game_button.collidepoint(x, y):
            highlight_button(
                load_game_button, (130, 50), "images/highlighted_lg_button.png"
            )

        elif play_button.collidepoint(x, y):
            highlight_button(
                play_button, (200, 50), "images/highlighted_play_button.png"
            )

        else:
            screen.blit(
                pg.transform.scale(
                    pg.image.load("images/meteor shower load game.png").convert(),
                    (screen.get_size()),
                ),
                (0, 0),
            )

        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                x, y = pg.mouse.get_pos()

                if one_player_button.collidepoint(x, y):
                    s.two_player = False
                    highlight_button(
                        one_player_button, (130, 50), "images/clicked_op_button.png"
                    )
                    end = True

                if two_player_button.collidepoint(x, y):
                    s.two_player = True
                    highlight_button(
                        two_player_button, (130, 50), "images/clicked_tp_button.png"
                    )
                    end = True

                if load_game_button.collidepoint(x, y):
                    connection = sqlite3.connect("User_Data.sqlite")
                    cursor = connection.cursor()
                    letters = []

                    while True:
                        enter_pressed, s.u_name = get_name(letters)
                        display_text(s.u_name, "centerx", "centery", 300, 390)
                        pg.display.update()
                        screen.blit(pg.image.load("images/enter_name.jpg"), (0, 0))
                        if enter_pressed:
                            cursor.execute(
                                "SELECT * FROM Saved_Games WHERE Name=?",
                                (s.u_name.upper(),),
                            )
                            if cursor.fetchone() is not None:
                                (
                                    a,
                                    s.total_meteors,
                                    s.ship_speed,
                                    d,
                                    s.money,
                                    s.score,
                                    g,
                                    s.lives,
                                    s.level,
                                ) = cursor.fetchone()
                                cursor.execute(
                                    "DELETE FROM Saved_Games WHERE Name=?",
                                    (s.u_name.upper(),),
                                )
                                connection.commit()
                                connection.close()
                                pg.key.set_repeat(1, 1)
                                game_loaded = True
                                end = True
                                break
                            else:
                                print("ERROR: USERNAME NOT FOUND")

        pg.display.update()

    while end:
        if game_loaded:
            end = False
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                x, y = pg.mouse.get_pos()
                if play_button.collidepoint(x, y):
                    end = False

    ship2 = 0
    ship1 = spaceship(s.ship_speed, s.ship_size, s.lives, screen, s.p1_image, False)

    break


def display_text(text, rect_x, rect_y, x, y):

    message = s.font.render(text, True, (255, 255, 255))
    message_rect = message.get_rect()
    setattr(message_rect, rect_x, x)
    setattr(message_rect, rect_y, y)
    screen.blit(message, (message_rect))


def main(ship1, ship2):
    if s.two_player:
        ship2 = spaceship(s.ship_speed, s.ship_size, s.lives, screen, s.p2_image, False)
    y1, y2 = 0, -s.height
    clock = pg.time.Clock()
    time1 = time()
    s.level = 1
    coin_position = None

    while s.lives > 0:  # main loop
        position = 560
        clock.tick(s.FPS)
        timer = time() - time1 - s.time_paused
        speed_increase = timer / 100

        previous_lives = s.lives
        s.lives = sprite_collision(ship1, ship2, s.meteor_group, screen, True)

        powerup_collision = pg.sprite.spritecollide(ship1, s.powerup_group, True)
        for sprite in powerup_collision:
            s.money += 500

        if ship2 != 0:
            powerup_collision2 = pg.sprite.spritecollide(ship2, s.powerup_group, True)
            for sprite in powerup_collision2:
                s.money += 500

        update_screen(ship1, ship2, screen, y1, y2, s.bullet_group, timer)
        update_sprites(s.meteor_group, screen, speed_increase)
        update_sprites(s.powerup_group, screen, speed_increase)

        for bullet in s.bullet_group:
            bullet.update()
            if bullet.rect.y < 0:
                bullet.kill()

        bullet_hit_list = pg.sprite.groupcollide(
            s.meteor_group, s.bullet_group, False, True
        )

        for rock in bullet_hit_list:
            if not (s.double_p):
                s.score += 100
            else:
                s.score += 200
            coin_position = rock.rect
            s.meteor_position = rock.rect
            rock.health -= 1
            rock.image = pg.image.load("images/cracked.png")
            rock.image.set_colorkey((0, 0, 0))
            rock.image = pg.transform.scale(rock.image, rock.size)
            if rock.health == 0:
                rock.kill()

        s.ship_pos = ship1.rect.centerx
        drop = randint(1, 5)
        coin = boost()
        if drop == 1 and len(s.coin_group) == 0 and coin_position != None:
            s.coin_group.add(coin)
            s.time_coin = time() + 5
            coin.rect = coin_position
        else:
            coin_position = None

        if time() >= s.time_coin:
            s.coin_group.empty()
        s.coin_group.draw(screen)
        coin_collect_list = pg.sprite.spritecollide(ship1, s.coin_group, True)
        for sprite in coin_collect_list:
            s.money += 50

        if ship2 != 0:
            coin_collect_list2 = pg.sprite.spritecollide(ship2, s.coin_group, True)
            for sprite in coin_collect_list2:
                s.money += 50
                coin_positions = []

        if (int((timer ** 2) + s.score)) < 0:
            break

        if len(s.meteor_group) == 0 and timer > 10:  # boss loop
            ship1.__init__(
                ship1.speed,
                s.ship_size,
                ship1.lives,
                ship1.screen,
                s.p1_image,
                ship1.rect,
            )
            if s.two_player:
                ship2.__init__(
                    ship2.speed,
                    s.ship_size,
                    ship2.lives,
                    ship2.screen,
                    s.p2_image,
                    ship2.rect,
                )
            s.no_sprite_hits = False

            if ship1.rect.centerx < 350 and ship1.rect.centerx > 250:
                attack_choice = choice(["inside_shot", "wave_shot"])
            else:
                attack_choice = choice(["straight_shot", "spread_shot"])

            enemy_boss = boss(screen, 100, ship1, ship2)
            boss_group = pg.sprite.GroupSingle()
            boss_group.add(enemy_boss)
            s.boss_bullet_pos = 101
            stop = False

            while s.lives > 0 and not (stop):
                timer = time() - time1
                clock.tick(50)
                if enemy_boss.health <= 0:
                    sleep(1)
                    enemy_boss.die()
                    s.lives += 1
                    s.heart_refresh = True
                    s.level += 1
                    s.total_meteors += 10
                    s.double_p = False
                    display_text(
                        ("Level" + str(s.level)),
                        "centerx",
                        "centery",
                        screen.get_rect().centerx,
                        screen.get_rect().centery,
                    )
                    pg.display.update()
                    sleep(1)
                    screen.blit(pg.image.load("images/shop_menu.png").convert(), (0, 0))
                    nb, elb, sbb, gub, sb, dpb, eb = (
                        pg.Rect(44, 129, 192, 59),
                        pg.Rect(44, 256, 192, 59),
                        pg.Rect(44, 379, 192, 59),
                        pg.Rect(362, 129, 192, 59),
                        pg.Rect(362, 257, 192, 59),
                        pg.Rect(362, 377, 192, 59),
                        pg.Rect(535, 0, 65, 35),
                    )

                    while not (stop):
                        display_text(
                            (str(s.money)),
                            "centerx",
                            "centery",
                            screen.get_rect().centerx,
                            screen.get_rect().centery,
                        )

                        if s.lives == 3:
                            screen.blit(pg.image.load("images/stock.jpg"), (elb))
                        if s.shield_activate:
                            screen.blit(pg.image.load("images/stock.jpg"), (sb))
                        if s.double_p:
                            screen.blit(pg.image.load("images/stock.jpg"), (dpb))
                        if s.money < 1000:
                            screen.blit(pg.image.load("images/stock.jpg"), (gub))
                            screen.blit(pg.image.load("images/stock.jpg"), (sbb))
                            pg.display.update()
                            if s.money < 500:
                                screen.blit(pg.image.load("images/stock.jpg"), (nb))
                                screen.blit(pg.image.load("images/stock.jpg"), (sb))
                                screen.blit(pg.image.load("images/stock.jpg"), (dpb))
                                pg.display.update()
                                if s.money < 250:
                                    screen.blit(
                                        pg.image.load("images/stock.jpg"), (elb)
                                    )
                                    pg.display.update()

                        for event in pg.event.get():
                            if event.type == pg.MOUSEBUTTONDOWN:
                                x, y = pg.mouse.get_pos()
                                screen.blit(
                                    pg.image.load("images/shop_menu.png").convert(),
                                    (0, 0),
                                )
                                if eb.collidepoint(x, y):
                                    stop = True
                                if nb.collidepoint(x, y) and s.money >= 500:
                                    s.money -= 500
                                    s.nuke_ready = True
                                if (
                                    elb.collidepoint(x, y)
                                    and s.money >= 250
                                    and s.lives < 3
                                ):
                                    s.money -= 250
                                    s.lives += 1
                                if gub.collidepoint(x, y) and s.money >= 1000:
                                    s.money -= 1000
                                    s.gun_image += 2
                                    s.b_cooldown -= 0.1
                                if (
                                    sb.collidepoint(x, y)
                                    and s.money >= 500
                                    and not (s.shield_activate)
                                ):
                                    s.money -= 500
                                    s.shield_activate = True
                                if (
                                    dpb.collidepoint(x, y)
                                    and s.money >= 500
                                    and not (s.double_p)
                                ):
                                    s.money -= 500
                                    s.double_p = True
                                if sbb.collidepoint(x, y) and s.money >= 1000:
                                    s.money -= 1000
                                    ship1.speed += 1
                                    if s.two_player:
                                        ship2.speed += 1
                                pg.display.update()

                previous_lives = s.lives

                if (
                    (
                        attack_choice == "spread_shot"
                        or attack_choice == "straight_shot"
                        or attack_choice == "inside_shot"
                    )
                    and int(s.boss_bullet_pos) > 530
                ) or (attack_choice == "wave_shot" and int(s.boss_bullet_pos) > 1800):
                    s.boss_bullet_pos = 101
                    if ship1.rect.centerx < 400 and ship1.rect.centerx > 200:
                        attack_choice = choice(
                            ["inside_shot", "inside_shot", "wave_shot", "straight_shot"]
                        )
                    else:
                        attack_choice = choice(
                            ["straight_shot", "spread_shot", "spread_shot", "wave_shot"]
                        )

                elif attack_choice == "spread_shot":
                    s.boss_bullet_pos += 4
                elif attack_choice == "wave_shot":
                    s.boss_bullet_pos += 6
                elif attack_choice == "straight_shot":
                    s.boss_bullet_pos += 6
                elif attack_choice == "inside_shot":
                    s.boss_bullet_pos += 6

                update_screen(ship1, ship2, screen, y1, y2, s.bullet_group, timer)
                bullet_collision_list = pg.sprite.groupcollide(
                    s.bullet_group, boss_group, True, False
                )
                for i in bullet_collision_list:
                    enemy_boss.health -= 1

                for sprite in s.bullet_group:
                    sprite.update()
                    if sprite.rect.y < 0:
                        sprite.kill()

                s.lives = sprite_collision(ship1, ship2, boss_group, screen, False)
                enemy_boss.shoot(
                    s.boss_bullet_pos, enemy_boss.health, ship1, ship2, attack_choice
                )

                y1 += 0.2
                y2 += 0.2
                if y1 > s.height:
                    y1 = -s.height
                if y2 > s.height:
                    y2 = -s.height
                pg.display.update()

        add_sprites(s.meteor_group, screen, s.powerup_group)
        s.meteor_group.draw(screen)
        s.bullet_group.draw(screen)
        s.powerup_group.draw(screen)

        y1 += 0.5
        y2 += 0.5
        if y1 > s.height:
            y1 = -s.height
        if y2 > s.height:
            y2 = -s.height

        if previous_lives > s.lives:
            for i in range(3):
                for i in range(0, 255, 5):
                    ship1.ship.set_alpha(i)
                    if ship2 != 0:
                        ship2.ship.set_alpha(i)
                    update_screen(ship1, ship2, screen, y1, y2, s.bullet_group, timer)
                    grave = pg.image.load("images/grave.jpeg")
                    grave = pg.transform.scale(grave, (200, 200))
                    grave.set_colorkey((255, 255, 255))
                    screen.blit(grave, (200, 140))
                    pg.display.update()

        if previous_lives != s.lives or s.heart_refresh:
            s.heart_refresh = False
            for i in range(s.lives):
                heart = boost(2)
                heart.rect.x = position
                position -= 30
                heart.rect.y = 10
                s.heart_group.add(heart)
            for sprite in s.heart_group:
                if sprite.rect.x < (590 - (s.lives * 30)):
                    sprite.kill()

        display_text((str(int(timer ** 2) + s.score)), "left", "top", 10, 10)
        s.heart_group.draw(screen)
        pg.display.update()

    s.lives = 0
    letters = []
    r = screen.get_rect()

    if s.u_name == "":
        while True:
            clock.tick(30)
            enter_pressed, s.u_name = get_name(letters)

            image = pg.image.load("images/game over.jpg").convert()
            image = pg.transform.scale(image, screen.get_size())
            screen.blit(image, (0, 0))
            display_text(s.u_name, "centerx", "centery", r.centerx, r.centery + 150)
            display_text(
                "Enter Name:", "centerx", "centery", r.centerx, r.centery + 100
            )
            display_text(
                ("Score {0}".format(str(int(timer ** 2) + s.score))),
                "centerx",
                "centery",
                r.centerx,
                r.centery,
            )
            pg.display.update()

            if enter_pressed:
                save(s.u_name, int(timer ** 2 + s.score))
                break

    else:
        save(s.u_name, int(timer ** 2 + s.score))

    f = open("names.txt", "r")
    data = json.load(f)
    f.close

    lb_tuple = []
    for key, value in data.items():
        lb_tuple.append((key, value))
    lb_tuple = sorted(lb_tuple, key=itemgetter(1), reverse=True)

    screen.blit(pg.image.load("images/lb_bg.png"), (0, 0))
    n = 120

    for i in range(len(lb_tuple)):
        if i != 9:
            message = "  " + str(i + 1) + ": " + str(lb_tuple[i])
        else:
            message = str(i + 1) + ": " + str(lb_tuple[i][0])
        message = (
            message.strip()
            .replace("'", "")
            .replace(")", "")
            .replace("(", "")
            .replace(",", " :")
        )
        display_text("LEADERBOARD", "centerx", "centery", r.centerx, r.centery - 200)
        display_text(message, "left", "top", 30, r.centery - n)
        n -= 33
        pg.display.update()
        if i == 10:
            break

    while True:
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                exit()


def save(name, score):
    f = open("names.txt", "r")
    data = json.load(f)
    data[name] = score
    f.close

    f = open("names.txt", "w")
    json.dump(data, f)
    f.close


def background_tasks():
    clock = pg.time.Clock()
    explosion = pg.image.load("images/explosion.png")

    while True:
        clock.tick(20)

        if s.shots_fired:
            s.b_cooldown_on = True
            sleep(s.b_cooldown)
            s.b_cooldown_on = False
            s.shots_fired = False

        if s.meteor_position != None:
            for i in range(1000):
                screen.blit(explosion, s.meteor_position)
                pg.display.update(s.meteor_position)
            s.meteor_position = None

        if s.nuke_activate:
            s.nuke_activate = False
            for rock in s.meteor_group:
                if rock.rect.centery < 480 and rock.rect.centery > 0:
                    rock_rect = rock.rect
                    rock.kill()
                    for i in range(1500):
                        screen.blit(explosion, rock_rect)
                        pg.display.update(rock_rect)


def position_checker():
    while True:
        if s.ship_pos >= 0 and s.ship_pos < 150:
            s.q1 += 1
        elif s.ship_pos >= 150 and s.ship_pos < 300:
            s.q2 += 1
        elif s.ship_pos >= 300 and s.ship_pos < 450:
            s.q3 += 1
        elif s.ship_pos >= 450 and s.ship_pos <= 600:
            s.q4 += 1
        sleep(1)


main = threading.Thread(name="main", target=main, args=(ship1, ship2))
background_tasks = threading.Thread(name="background_tasks", target=background_tasks)
# position_checker = threading.Thread(name='position_checker', target=position_checker)

main.start()
background_tasks.start()
# position_checker.start()

# make it so there's only one place you can hit the boss and it's based on where the user spent the least time using q1 - q4
# make a shield version of ship 2
# new bosses: giant meteor that splits into smaller meteors a bunch of times until its just like 32 normal meteors and you destroy those, quasar that spins and sucks you in and then shoots a beam out of either end. settings screen on the main menu that allows you to change things like controls, ship image and bullet colour. also have a main database storing the averages of all the players, this has to include playercount so that you can update the average, store average accuracy, average rocks hit, percentage of game spent in each quadrant, average game length etc...
