import pygame as pg
from time import time
import sys

import helpers
from settings import screen
import settings as s


def pause_game(ship1, score, level):
    """displays a paused game screen showing information to the player"""
    t1 = time()

    # if game is still going, give option to save game
    if len(s.meteor_group) > 0:
        save = pg.image.load("images/save_game_button.png")
        save_rect = save.get_rect()
        save_rect.center = (523, 23)
        screen.blit(save, save_rect)

    # show pause screen
    paused = pg.image.load("images/paused.jpg")
    paused_rect = paused.get_rect()
    paused_rect.center = screen.get_rect().center
    screen.blit(paused, paused_rect)

    # display meteors remaining, money and lives left to user
    # -1 meteor is to make the boss fight start properly
    helpers.display_text(
        ("Meteors: " + str(len(s.meteor_group) - 1)), "left", "top", 20, 20
    )
    helpers.display_text(("Money: " + str(ship1.money)), "left", "top", 20, 50)
    helpers.display_text(("Lives: " + str(ship1.lives)), "left", "top", 20, 80)

    pg.display.update()
    end = False

    while not (end):
        pg.event.clear()
        event = pg.event.wait()

        if event.type == pg.MOUSEBUTTONDOWN:
            x, y = pg.mouse.get_pos()

            # if user clicks on save game button
            if save_rect.collidepoint(x, y) and len(s.meteor_group) > 0:
                helpers.save_game(score, ship1, level)

        # unpauses
        if event.type == pg.KEYDOWN:
            if event.unicode == "p":
                s.time_paused += time() - t1
                end = True


class bullet(pg.sprite.Sprite):
    """players' bullet sprites"""

    def __init__(self, ship, player_two=False):
        super().__init__()

        self.screen = screen
        self.ship = ship
        self.speed = 5
        self.size = (3, 12)
        self.gun_num = 0
        self.cooldown = 0.4  # cooldown between shots, in seconds
        self.cooldown_on = False

        # player 1 and 2 have different guns
        if not player_two:
            self.bullet_image = "images/bullet2.png"
        else:
            self.bullet_image = "images/bullet3.png"

        # modifies the bullet image and places it in middle of ship
        self.image = pg.image.load(self.bullet_image).convert()
        pg.transform.scale(self.image, self.size)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        y_offset = 10  # makes bullet spawn from the centre of the ship
        self.rect.centery = self.ship.rect.centery - y_offset

        x_offset = 1 if ship.ship_image == "images/spaceship.bmp" else 10
        self.rect.centerx = self.ship.rect.centerx + x_offset

    def update(self):
        """Moves the bullet up the screen each frame"""
        self.rect.y -= self.speed
        screen.blit(self.image, self.rect)

        # if bullet goes above the screen, destroy it
        if self.rect.y < 0:
            self.kill()


class spaceship(pg.sprite.Sprite):
    """Player's spaceship sprite"""

    def __init__(self, ship_image, start_pos=False):
        super().__init__()

        self.speed = 0.4
        self.size = (35, 35)
        self.lives = 3
        self.money = 10000
        self.screen = screen
        self.ship_image = ship_image
        self.username = ""
        self.shield = False  # true if shield is active
        self.shield_available = False  # true if shield is bought
        self.nuke = False  # true if nuke is bought

        self.image = pg.image.load(ship_image).convert()
        self.ship = pg.transform.scale(self.image, self.size).convert()
        self.ship.set_colorkey((255, 0, 0))

        self.rect = self.ship.get_rect()
        self.screen_rect = screen.get_rect()

        # if no starting position specified, spawn in bottom centre of screen
        if not (start_pos):
            self.rect.centerx = self.screen_rect.centerx
            self.rect.centery = self.screen_rect.centery
            self.rect.bottom = self.screen_rect.bottom
        else:
            self.rect = start_pos

        self.centerx = float(self.rect.centerx)
        self.centery = float(self.rect.centery)

        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False

    def move(self):
        """
        Allows the player to move around the screen,
        the player cannot go beyond the upper and lower bounds of the screen
        and will loop to the other side if they pass the left or right bounds
        """
        padding = 20  # so they don't start right at the edge of the screen

        if self.moving_right:
            self.centerx += self.speed

        # loop from far right to the left side of the screen
        if self.rect.right > self.screen_rect.right:
            self.centerx = padding

        # stop moving if you've reached the bottom of the screen
        if self.moving_down and self.rect.bottom <= self.screen_rect.bottom:
            self.centery += self.speed

        if self.moving_left:
            self.centerx -= self.speed

        # loop from far left to the right side of the screen
        if self.rect.left < 0:
            self.centerx = self.screen_rect.right - padding

        if self.moving_up and self.rect.top >= 0:
            self.centery -= self.speed

        self.rect.centerx = self.centerx
        self.rect.centery = self.centery

    def die(self):
        """player death, triggered by hitting a meteor or being shot"""

        if not self.shield:
            # turns player invisible
            self.lives -= 1

            # fades player in and out 3 times to signify death has occured
            for i in range(3):
                for i in range(0, 255, 5):
                    self.ship.set_alpha(i)
                    # update_screen(ship1, ship2, y1, y2, s.bullet_group, timer) TODO
                    # shows image of a grave on screen
                    grave = pg.image.load("images/grave.jpeg")
                    grave = pg.transform.scale(grave, (200, 200))
                    grave.set_colorkey((255, 255, 255))
                    screen.blit(grave, (200, 140))
                    pg.display.update()

        self.shield = False

        # fades the player back in
        for i in range(255):
            self.ship.set_alpha(i)
            screen.blit(self.ship, self.rect)
            pg.display.update()

        helpers.refresh_hearts(self.lives)  # change the number of hearts on screen


def check_movement(event, ship1, ship2):
    """checks for player movement"""

    if event.type == pg.KEYDOWN:
        # if player 1 moves
        if event.key == pg.K_UP:
            ship1.moving_up = True
        if event.key == pg.K_DOWN:
            ship1.moving_down = True
        if event.key == pg.K_LEFT:
            ship1.moving_left = True
        if event.key == pg.K_RIGHT:
            ship1.moving_right = True

        # if player 2 moves
        if ship2 != 0:
            if event.key == pg.K_w:
                ship2.moving_up = True
            if event.key == pg.K_s:
                ship2.moving_down = True
            if event.key == pg.K_a:
                ship2.moving_left = True
            if event.key == pg.K_d:
                ship2.moving_right = True

    # if player 1 stops moving
    if event.type == pg.KEYUP:
        if event.key == pg.K_UP:
            ship1.moving_up = False
        if event.key == pg.K_DOWN:
            ship1.moving_down = False
        if event.key == pg.K_LEFT:
            ship1.moving_left = False
        if event.key == pg.K_RIGHT:
            ship1.moving_right = False

        # if player 2 stops moving
        if ship2 != 0:
            if event.key == pg.K_w:
                ship2.moving_up = False
            if event.key == pg.K_s:
                ship2.moving_down = False
            if event.key == pg.K_a:
                ship2.moving_left = False
            if event.key == pg.K_d:
                ship2.moving_right = False


def check_events(ship1, ship2, score, level):
    """checks for and responds to user input"""
    for event in pg.event.get():

        # if player closes the window
        if event.type == pg.QUIT:
            pg.display.quit()
            pg.quit()
            sys.exit()

        # check if either player has moved
        check_movement(event, ship1, ship2)

        # if button press is detected
        if event.type == pg.KEYDOWN:

            # if user pauses
            if event.key == pg.K_p:
                # makes it so holding p only generates one event
                pg.key.set_repeat()
                pause_game(ship1, score, level)
                pg.key.set_repeat(1, 1)

            # if player 1 shoots
            if event.key == pg.K_SPACE and not (s.bullet_cooldown_on or s.shots_fired):
                s.shots_fired = True
                s.bullet_group.add(bullet(ship1))

                # if player 2 shoots
                if event.key == pg.K_q:
                    pg.key.set_repeat()
                    s.bullet_group.add(bullet(ship2, True))
                    pg.key.set_repeat(1, 1)

            # if player activates nuke power up
            if event.key == pg.K_2 and ship1.nuke:
                # TODO: have this run in a separate thread so game doesn't stall why the nuke is going off
                helpers.use_nuke(ship1)

            # if player activates shield power up
            if event.key == pg.K_1 and ship1.shield_available:
                ship1.shield = True
                if ship2 != 0:
                    ship2.shield = True

                # removes the power up so they can't use it again
                ship1.shield_available = False
                # puts a shield image around the player
                ship1.ship_image = "images/shield_ship1.jpg"
                if ship2 != 0:
                    # TODO: make a shield_ship2 image
                    ship2.ship_image = "images/shield_ship1.jpg"

        ship1.move()
        if ship2 != 0:
            ship2.move()
