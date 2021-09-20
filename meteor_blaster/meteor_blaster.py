import pygame as pg
from time import sleep, time
from operator import itemgetter
import threading
import json
import sys

import helpers
import boss
import player
import sprites
from settings import screen
import settings as s

pg.init()
pg.font.init()


def background_tasks():
    clock = pg.time.Clock()
    explosion = pg.image.load("images/explosion.png")

    while True:
        clock.tick(5)

        # doesn't allow any more shots for a short period after shooting
        if s.shots_fired:
            s.bullet_cooldown_on = True
            sleep(s.bullet_cooldown)
            s.bullet_cooldown_on = False
            s.shots_fired = False

        if s.meteor_position is not None:
            for i in range(1000):
                screen.blit(explosion, s.meteor_position)
                pg.display.update(s.meteor_position)
            s.meteor_position = None

        for event in pg.event.get():
            # if player closes the window
            if event.type == pg.QUIT:
                pg.display.quit()
                pg.quit()
                sys.exit()


def start_menu():
    """contains the code for the start menu interface"""
    score = 0

    while True:
        pg.display.set_caption("'METEOR BLASTER - 'The Dark Souls of Arcade Games'")
        pg.key.set_repeat(1, 1)

        bg_image = pg.image.load("images/meteor shower load game.png").convert()
        bg_image = pg.transform.scale(bg_image, screen.get_size())
        screen.blit((bg_image), (0, 0))

        # defines all the buttons on the screen
        play_button = sprites.button(
            s.play_pos, (200, 50), "images/play_button.png", "images/hl_play_button.png"
        )
        one_player_button = sprites.button(
            s.one_player_pos,
            (130, 50),
            "images/one_player_button.png",
            "images/hl_op_button.png",
        )
        two_player_button = sprites.button(
            s.two_player_pos,
            (130, 50),
            "images/two_player_button.png",
            "images/hl_tp_button.png",
        )
        load_game_button = sprites.button(
            s.load_game_pos,
            (130, 50),
            "images/load_game_button.png",
            "images/hl_lg_button.png",
        )

        # group to hold all the buttons
        button_group = pg.sprite.Group()
        button_group.add(
            play_button, one_player_button, two_player_button, load_game_button
        )

        pg.display.update()
        end = False
        game_loaded = False

        # loops until a mode is selected
        while not (end):

            # highlights buttons when the mouse hovers over them
            for button in button_group:
                button.highlight()

            for event in pg.event.get():

                # if player clicks
                if event.type == pg.MOUSEBUTTONDOWN:
                    x, y = pg.mouse.get_pos()

                    # if one player mode is clicked
                    if one_player_button.rect.collidepoint(x, y):
                        s.two_player = False
                        one_player_button.highlight()
                        end = True

                    # if two player mode is clicked
                    if two_player_button.rect.collidepoint(x, y):
                        s.two_player = True
                        two_player_button.highlight()
                        end = True

                    # if load game button is clicked
                    if load_game_button.rect.collidepoint(x, y):
                        helpers.enter_name()
                        score = helpers.load_game()
                        end = True
                        game_loaded = True

            pg.display.update()

        # loops until play button is clicked and the game begins
        while end:
            if game_loaded:
                end = False
            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN:
                    x, y = pg.mouse.get_pos()
                    if play_button.rect.collidepoint(x, y):
                        end = False

        return score


def shop(ship1, ship2):
    """contains the interface for the inventory shop"""
    shop_menu = pg.image.load("images/shop_menu.png").convert()
    screen.blit(shop_menu, (0, 0))

    # prices for the different upgrades
    gun_upgrade_price, speed_boost_price = 1000, 1000
    nuke_price, shield_price, double_points_price = 500, 500, 500
    extra_lives_price = 250
    exit_clicked = False

    while not exit_clicked:
        # shows available money at top of screen
        helpers.display_text(
            (str(ship1.money)),
            "centerx",
            "centery",
            screen.get_rect().centerx,
            screen.get_rect().centery,
        )

        # shows out of stock sign if player can't buy a given item
        if ship1.lives == 3:
            screen.blit(pg.image.load("images/stock.jpg"), (s.extra_lives_pos))
        if ship1.shield or ship1.shield_available:
            screen.blit(pg.image.load("images/stock.jpg"), (s.shield_pos))
        if s.double_p:
            screen.blit(pg.image.load("images/stock.jpg"), (s.double_points_pos))
        if ship1.money < gun_upgrade_price:
            screen.blit(pg.image.load("images/stock.jpg"), (s.gun_upgrade_pos))
            screen.blit(pg.image.load("images/stock.jpg"), (s.speed_boost_pos))
            pg.display.update()
            if ship1.money < nuke_price:
                screen.blit(pg.image.load("images/stock.jpg"), (s.nuke_pos))
                screen.blit(pg.image.load("images/stock.jpg"), (s.shield_pos))
                screen.blit(pg.image.load("images/stock.jpg"), (s.double_points_pos))
                pg.display.update()
                if ship1.money < extra_lives_price:
                    screen.blit(pg.image.load("images/stock.jpg"), (s.extra_lives_pos))
                    pg.display.update()

        for event in pg.event.get():
            # if player clicks
            if event.type == pg.MOUSEBUTTONDOWN:
                x, y = pg.mouse.get_pos()
                screen.blit(shop_menu.convert(), (0, 0))
                # if player clicks on exit button
                if s.exit_pos.collidepoint(x, y):
                    exit_clicked = True

                # if player buys a nuke
                if s.nuke_pos.collidepoint(x, y) and ship1.money >= nuke_price:
                    ship1.money -= nuke_price
                    ship1.nuke = True

                # if player buys extra lives
                if (
                    s.extra_lives_pos.collidepoint(x, y)
                    and ship1.money >= extra_lives_price
                    and ship1.lives < 3
                ):
                    ship1.money -= extra_lives_price
                    ship1.lives += 1

                # if player buys a gun upgrade
                if (
                    s.gun_upgrade_pos.collidepoint(x, y)
                    and ship1.money >= gun_upgrade_price
                ):
                    ship1.money -= gun_upgrade_price
                    ship1.bullet_image = "images/bullet_upgrade.png"
                    if ship2 != 0:
                        ship2.bullet_image = "images/bullet_upgrade.png"
                    s.bullet_cooldown -= 0.1

                # if palyer buys a shield
                if (
                    s.shield_pos.collidepoint(x, y)
                    and ship1.money >= shield_price
                    and not ship1.shield_available
                ):
                    ship1.money -= shield_price
                    ship1.shield_available = True

                # if player buys double points
                if (
                    s.double_points_pos.collidepoint(x, y)
                    and ship1.money >= double_points_price
                    and not (s.double_p)
                ):
                    ship1.money -= double_points_price
                    s.double_p = True

                # if player buys a speed boost
                if (
                    s.speed_boost_pos.collidepoint(x, y)
                    and ship1.money >= speed_boost_price
                ):
                    ship1.money -= speed_boost_price
                    ship1.speed += 1
                    if s.two_player:
                        ship2.speed += 1

                pg.display.update()


def game_over(score, ship1, ship2, timer):
    """code that runs if player runs out of lives and the game ends"""
    ship1.lives = 0
    letters = []
    r = screen.get_rect()
    # if username has not been entered yet
    if s.username == "":
        while True:
            enter_pressed = helpers.get_name(letters)  # get username from player
            # show a game over screen
            game_over_image = pg.image.load("images/game over.jpg").convert()
            game_over_image = pg.transform.scale(game_over_image, screen.get_size())
            screen.blit(game_over_image, (0, 0))
            # display username as player types it
            helpers.display_text(
                s.username, "centerx", "centery", r.centerx, r.centery + 150
            )
            helpers.display_text(
                "Enter Name:", "centerx", "centery", r.centerx, r.centery + 100
            )
            # show player's final score on screen
            helpers.display_text(
                ("Score {0}".format(str(int(timer ** 2) + score))),
                "centerx",
                "centery",
                r.centerx,
                r.centery,
            )
            pg.display.update()

            # once player submits username, save their score to a file
            if enter_pressed:
                helpers.save_score(s.username, int(timer ** 2 + score))
                break

    else:
        helpers.save_score(s.username, int(timer ** 2 + score))

    # get all saved scores / usernames from the file
    f = open("names.txt", "r")
    data = json.load(f)
    f.close

    # leaderboard stores a sorted list of (username, score) tuples from all previous players
    leaderboard = []
    for key, value in data.items():
        leaderboard.append((key, value))
    leaderboard = sorted(leaderboard, key=itemgetter(1), reverse=True)

    screen.blit(pg.image.load("images/lb_bg.png"), (0, 0))
    n = 120
    y_offset = 33

    # goes through top 10 entries in the leaderboard and shows them on screen
    for i, user in enumerate(leaderboard):
        if i != 9:
            message = "  " + str(i + 1) + ": " + str(user[0])
        else:
            message = str(i + 1) + ": " + str(user[0])
        message = (
            message.strip()
            .replace("'", "")
            .replace(")", "")
            .replace("(", "")
            .replace(",", " :")
        )
        helpers.display_text(
            "LEADERBOARD", "centerx", "centery", r.centerx, r.centery - 200
        )
        helpers.display_text(message, "left", "top", 30, r.centery - n)

        n -= y_offset
        pg.display.update()
        if i == 9:
            break

    while True:
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                main()


def main():
    """contains the code for the actual game"""
    y1, y2 = 0, -s.screen_height
    clock = pg.time.Clock()
    time1 = time()  # records time that game starts
    FPS = 50
    level = 1  # game starts on first level

    # first run the start menu
    score = start_menu()

    # creates the players' sprites
    ship1 = player.spaceship(s.p1_image, False)

    if s.two_player:
        ship2 = player.spaceship(s.p2_image, False)
    else:
        ship2 = 0

    # while player is still alive
    while ship1.lives > 0:
        clock.tick(FPS)  # set the games FPS
        helpers.refresh_hearts(ship1.lives)

        # calculates total time played, excluding time spent paused
        timer = time() - time1 - s.time_paused
        # meteor falling speed gradually increases as time goes on
        speed_increase_factor = 100
        speed_increase = timer / speed_increase_factor
        # checks for collisions between meteors and players
        sprites.sprite_collision(ship1, ship2, s.meteor_group)
        # checks for colliisions between power ups and players
        powerup_collision = pg.sprite.spritecollide(ship1, s.powerup_group, True)
        # if collision has occured, player earns money
        powerup_reward = 500
        for sprite in powerup_collision:
            ship1.money += powerup_reward

        if ship2 != 0:
            powerup_collision2 = pg.sprite.spritecollide(ship2, s.powerup_group, True)
            for sprite in powerup_collision2:
                ship1.money += powerup_reward

        # updates all the sprites
        helpers.update_screen(ship1, ship2, y1, y2, score, level)
        _, score = sprites.update_sprites(s.meteor_group, speed_increase, score)
        _, score = sprites.update_sprites(s.powerup_group, speed_increase, score)

        # moves every bullet up the screen, disappearing if it goes over the top
        for bullet in s.bullet_group:
            bullet.update()

        # list of meteors hit by a bullet
        rocks_shot = pg.sprite.groupcollide(s.meteor_group, s.bullet_group, False, True)

        for rock in rocks_shot:
            # destroys the meteor and randomly spawns a coin in its place
            rock.get_shot()
            # score gain for hitting a meteor
            score_increase = 200 if s.double_p else 100
            score += score_increase

        # despawns coins if they haven't been collected after a given time
        if time() >= s.coin_despawn_time:
            s.coin_group.empty()

        s.coin_group.draw(screen)
        coin_bonus = 50  # money gained from picking up a coin
        coins_collected = pg.sprite.spritecollide(ship1, s.coin_group, True)
        if ship2 != 0:
            coins_collected += pg.sprite.spritecollide(ship2, s.coin_group, True)

        # player gains money for every coin picked up
        for sprite in coins_collected:
            ship1.money += coin_bonus

        # if all meteors are destroyed, initiate the boss fight
        if len(s.meteor_group) == 0:
            boss.boss_fight(ship1, ship2, level)
            # player advances to the next level
            level += 1
            s.num_meteors += 10
            s.double_p = False
            # shows level on the screen
            helpers.display_text(
                ("Level " + str(level)),
                "centerx",
                "centery",
                screen.get_rect().centerx,
                screen.get_rect().centery,
            )
            pg.display.update()
            sleep(1)
            # once boss is defeated, enter the shop to buy upgrades
            shop(ship1, ship2)

        # draw all sprites
        sprites.add_sprites(s.meteor_group, s.powerup_group)
        s.meteor_group.draw(screen)
        s.bullet_group.draw(screen)
        s.powerup_group.draw(screen)

        # makes the screen constantly scroll, giving the illusion of movement
        scroll_speed = 0.5 + timer * 0.001
        y1 += scroll_speed
        y2 += scroll_speed
        if y1 > s.screen_height:
            y1 = -s.screen_height
        if y2 > s.screen_height:
            y2 = -s.screen_height

        # show score and number of lives in the corner of the screen
        helpers.display_text((str(int(timer ** 2) + int(score))), "left", "top", 10, 10)
        s.heart_group.draw(screen)
        pg.display.update()

    # if player runs out of lives, game ends
    clock.tick(30)  # Sets FPS to 30
    game_over(score, ship1, ship2, timer)


# runs background tasks in a separate thread so things in game can happen simultaneously
background_tasks = threading.Thread(name="background_tasks", target=background_tasks)
background_tasks.start()


if __name__ == "__main__":
    main()


# add speech bubble when you defeat boss that's like "you've defeated me!"
# make it so there's only one place you can hit the boss and it's based on where the user spent the least time using q1 - q4
# make a shield version of ship 2
# new bosses: giant meteor that splits into smaller meteors a bunch of times until its just like 32 normal meteors and you destroy those, quasar that spins and sucks you in and then shoots a beam out of either end. settings screen on the main menu that allows you to change things like controls, ship image and bullet colour. also have a main database storing the averages of all the players, this has to include playercount so that you can update the average, store average accuracy, average rocks hit, percentage of game spent in each quadrant, average game length etc...
