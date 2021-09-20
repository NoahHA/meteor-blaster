import pygame as pg
import random
from time import sleep
from math import tan, radians

import player
import sprites
from settings import screen
import settings as s


class boss(pg.sprite.Sprite):
    """Methods and data for the Boss sprite"""

    def __init__(self, ship1, ship2):
        super().__init__()

        self.ship1 = ship1
        self.ship2 = ship2
        self.health = 100
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

        interval = 0.04  # time between loops
        num_frames = 150
        drift = 1  # amount boss drifts each frame

        # boss' death animation
        for i in range(num_frames):
            sleep(interval)
            self.rect.centery += drift
            self.screen.blit(s.background, (0, 0))

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
            self.screen.blit(s.background, (0, 0))
            self.screen.blit(
                pg.transform.scale(self.image, (int(boss_width), int(boss_height))),
                self.rect,
            )
            pg.display.flip()

    def shoot(self, y_current, ship1, ship2, attack_choice):
        """Boss randomly selects from a range of attack choices"""
        angles = [40, 30, 20, 10, -10, -20, -30, -40]
        enemy_bullet_group = pg.sprite.Group()

        if attack_choice == "spread_shot":
            enemy_bullet_group.empty()
            laser_size = (2, 9)

            # creates a group of lasers
            while len(enemy_bullet_group) < len(angles):
                enemy_bullet_group.add(
                    laser(self.rect.centerx, 0, "images/beams1.png", laser_size)
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
                    laser(x_value, y_value, "images/beams3.png", laser_size)
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
                    laser(x_value, 0, "images/beams4.png", laser_size)
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
                    laser(x_value, 0, "images/beams2.png", laser_size)
                )
                x_value += x_offset

            # moves the bullets down the screen
            for bullet in enemy_bullet_group:
                bullet.rect.centery += y_current

        collision_list1 = pg.sprite.spritecollide(ship1, enemy_bullet_group, False)
        if ship2 != 0:
            collision_list2 = pg.sprite.spritecollide(ship2, enemy_bullet_group, False)

        # if player 1 gets shot
        if len(collision_list1) > 0:
            ship1.die()
            s.boss_bullet_pos = 101

        # if player 2 gets shot
        if ship2 != 0 and len(collision_list2) > 0:
            ship2.die()
            s.boss_bullet_pos = 101

        # boss's health bar
        height = self.health * 4
        border_rect = (7, 60, 15, 400)
        hitbox_rect = (7, 460 - height, 15, height)

        # if boss is damaged, show health bar
        if self.health < 100:
            screen.fill((138, 7, 7), border_rect)
            screen.fill((7, 136, 70), hitbox_rect)

        enemy_bullet_group.draw(self.screen)
        self.screen.blit(self.image, self.rect)
        pg.display.update()


class laser(pg.sprite.Sprite):
    """sprite for the lasers the bosses shoot out"""

    def __init__(self, center_x, center_y, image, size):
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


def boss_fight(ship1, ship2):
    """contains code for the boss fight at the end of each level"""

    clock = pg.time.Clock()
    # puts both players in the center of the screen
    ship1.rect.center = screen.get_rect().center
    if ship2 != 0:
        ship2.rect.center = screen.get_rect().center
    ship1.shield = False

    sleep(1)
    center_left, center_right = 250, 350

    # chooses appropriate attack based on player location
    if ship1.rect.centerx < center_right and ship1.rect.centerx > center_left:
        attack_choice = random.choice(["inside_shot", "wave_shot"])
    else:
        attack_choice = random.choice(["straight_shot", "spread_shot"])

    enemy_boss = boss(ship1, ship2)
    boss_group = pg.sprite.GroupSingle()
    boss_group.add(enemy_boss)
    s.boss_bullet_pos = 101
    exit_clicked = False

    # while player is still alive
    while ship1.lives > 0 and not exit_clicked:
        clock.tick(50)  # Set FPS to 50

        # if boss is killed
        if enemy_boss.health <= 0:
            sleep(1)
            enemy_boss.die()
            # gives player an extra life as bosses death animation kills the player
            ship1.lives += 1
            return True

        # if bosses attacks has reached the end of the screen
        if ((attack_choice != "wave_shot") and s.boss_bullet_pos > 530) or (
            attack_choice == "wave_shot" and s.boss_bullet_pos > 1800
        ):
            # reset bullet position
            s.boss_bullet_pos = 101

            # chooses appropriate attack based on player location
            if ship1.rect.centerx < center_right and ship1.rect.centerx > center_left:
                attack_choice = random.choice(
                    ["straight_shot", "inside_shot", "inside_shot", "wave_shot"]
                )
            else:
                attack_choice = random.choice(
                    ["straight_shot", "spread_shot", "spread_shot", "wave_shot"]
                )

        # if bullets are still on-screen, move them down
        elif attack_choice == "spread_shot":
            s.boss_bullet_pos += 4
        elif attack_choice == "wave_shot":
            s.boss_bullet_pos += 6
        elif attack_choice == "straight_shot":
            s.boss_bullet_pos += 6
        elif attack_choice == "inside_shot":
            s.boss_bullet_pos += 6

        # show players on screen
        screen.blit(s.background, (0, 0))
        screen.blit(ship1.ship, ship1.rect)
        if ship2 != 0:
            screen.blit(ship2.ship, ship2.rect)
        # check for player input (moving, shooting etc...)
        player.check_events(ship1, ship2, s.bullet_group)

        bullet_collision_list = pg.sprite.groupcollide(
            s.bullet_group, boss_group, True, False
        )

        # reduce boss health every time it gets shot
        for bullet in bullet_collision_list:
            enemy_boss.health -= 1

        # updates position of every bullet
        for sprite in s.bullet_group:
            sprite.update()

        sprites.sprite_collision(ship1, ship2, boss_group)
        enemy_boss.shoot(s.boss_bullet_pos, ship1, ship2, attack_choice)

        pg.display.update()
