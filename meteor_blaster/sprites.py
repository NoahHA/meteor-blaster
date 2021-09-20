import pygame as pg
import random
from time import time

from settings import screen
import settings as s


class boost(pg.sprite.Sprite):
    """sprite for player enhancing boosts"""

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
        self.speed = 2.5


class meteor(pg.sprite.Sprite):
    """sprite for meteors that fall randomly from above"""

    def __init__(self, size, speed, image, health):
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

    def get_shot(self):
        # TODO: make meteor explode in it's own thread and thus remove meteor_position
        s.meteor_position = self.rect
        self.health -= 1
        self.image = pg.image.load("images/cracked.png")
        self.image.set_colorkey((0, 0, 0))
        self.image = pg.transform.scale(self.image, self.size)
        if self.health == 0:
            self.kill()

        drop_rate = 0.2  # chance for a power up to drop from a meteor
        drop = random.random()
        coin = boost()

        # randomly generates coins when meteors are destroyed
        if drop < drop_rate and len(s.coin_group) == 0:
            s.coin_group.add(coin)
            s.coin_despawn_time = time() + 5
            coin.rect = self.rect


class button(pg.sprite.Sprite):
    def __init__(self, rect, size, normal_image, highlighted_image=""):
        super().__init__()

        self.rect = rect
        self.size = size
        self.normal_image = pg.image.load(normal_image)
        self.highlighted_image = pg.image.load(highlighted_image)
        self.normal_image = pg.transform.scale(self.normal_image, self.size)
        self.highlighted_image = pg.transform.scale(self.highlighted_image, self.size)
        self.image = self.normal_image

    def highlight(self):
        """highlights the button when mouse hovers over it"""
        x, y = pg.mouse.get_pos()

        if self.rect.collidepoint(x, y):
            self.image = self.highlighted_image

        else:
            self.image = self.normal_image

        screen.blit(self.image, self.rect)
        pg.display.update()


def add_sprites(rock_list, powerup_list):
    """creates meteors and powerups that fall throughout the game"""

    # if no meteors exist
    if len(s.meteor_group) == 0:
        # range of sizes that meteors can have
        max_size = 35
        min_size = 20
        # range of speeds that meteors can have
        max_speed = 4
        min_speed = 1
        # meteors are divided into normal and large
        percent_normal = 0.75
        num_normal = int(s.num_meteors * percent_normal)
        num_large = s.num_meteors - num_normal
        health = 1

        # generates normal meteors
        generate_meteors(num_normal, max_size, min_size, max_speed, min_speed, health)
        # generates slower, stronger meteors
        generate_meteors(
            num_large,
            max_size * 2,
            min_size * 2,
            max_speed / 2,
            min_speed / 2,
            health * 2,
        )

    # generate a power up if one doesn't already exist
    while len(s.powerup_group) != 1:
        # range of heights over which power ups can spawn
        max_height = -10_000
        min_height = -1_000

        powerup = boost()
        powerup.rect.x = random.randrange(screen.get_width())
        powerup.rect.y = random.randrange(max_height, min_height)
        s.powerup_group.add(powerup)

    pg.sprite.groupcollide(s.powerup_group, s.meteor_group, True, True)


def generate_meteors(n, max_size, min_size, max_speed, min_speed, health):
    """Generates meteor sprites to fall from above"""
    max_height = -15_000
    min_height = -250
    padding = 30  # area on sides of screen where meteors can't spawn
    screen_width = screen.get_width()

    for i in range(n):
        x, y = random.randrange(min_size, max_size), random.randrange(
            min_size, max_size
        )
        speed = random.randrange(int(min_speed), int(max_speed))
        rock = meteor((x, y), speed, "images/meteor.png", health)
        rock.rect.x = random.randrange(padding, screen_width - padding)
        rock.rect.y = random.randrange(max_height, min_height)
        rock.image.set_colorkey((0, 0, 0))
        s.meteor_group.add(rock)


def update_sprites(sprite_list, speed_increase, score):
    """updates position of every sprite given to it"""
    screen_height = screen.get_height()
    score_loss = 200 + score * 0.1  # point loss for missing a falling sprite
    for sprite in sprite_list:
        sprite.rect.y += sprite.speed + speed_increase

        # if sprite falls below the screen player loses points
        if sprite.rect.y > screen_height:
            sprite.kill()
            score -= score_loss

    return (sprite_list, score)


def sprite_collision(ship1, ship2, group):
    """checks for collisions between player and enemy sprites"""

    collision_list1 = pg.sprite.spritecollide(ship1, group, False)

    # if player 1 hits a sprite
    for sprite in collision_list1:
        # if sprite is a meteor
        if type(sprite).__name__ == "meteor":
            sprite.kill()

        ship1.die()

    # if player 2 hits a sprite
    if ship2 != 0:
        collision_list2 = pg.sprite.spritecollide(ship2, group, False)

        for sprite in collision_list2:
            # if sprite is a meteor
            if type(sprite).__name__ == "meteor":
                sprite.kill()

            ship2.die()
