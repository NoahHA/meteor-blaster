import pygame as pg
from time import sleep
import sqlite3
import json

import player
import sprites
from settings import screen
import settings as s


def update_screen(ship1, ship2, y1, y2, score, level):
    """
    creates the moving background effect, checks for
    player input and blits players to the screen
    """
    screen.blit(s.background, (0, y1))
    screen.blit(s.background, (0, y2))
    screen.blit(ship1.ship, ship1.rect)
    if ship2 != 0:
        screen.blit(ship2.ship, ship2.rect)
    player.check_events(ship1, ship2, score, level)


def get_name(letters):
    """returns the name typed by the user as a string"""
    pg.key.set_repeat()
    event = pg.event.wait()
    enter_pressed = False

    # if user presses a key
    if event.type == pg.KEYDOWN:
        # check if return key has been pressed
        if event.key == pg.K_RETURN:
            enter_pressed = True
        # remove a letter if backspace has been pressed
        elif event.key == pg.K_BACKSPACE:
            if len(letters) > 0:
                letters.pop()
        # if a letter has been pressed then add it to list of letters
        else:
            letters.append((event.unicode).upper())

    s.username = "".join(letters)

    return enter_pressed


def display_text(text, rect_x, rect_y, x, y):

    message = s.font.render(text, True, (255, 255, 255))
    message_rect = message.get_rect()
    setattr(message_rect, rect_x, x)
    setattr(message_rect, rect_y, y)
    screen.blit(message, (message_rect))


def load_game(ship1):
    """
    searches database for players username and loads their previous game if found
    """

    # connects to database
    with sqlite3.connect("User_Data.sqlite") as con:
        # searches database for user's name
        cursor = con.cursor()
        cursor.execute(
            "SELECT * FROM Saved_Games WHERE Name=?",
            (s.username.upper(),),
        )

        # if name is in database
        if cursor.fetchone() is not None:
            (
                name,
                s.num_meteors,
                speed,
                shield,
                money,
                score,
                nuke,
                lives,
                level,
            ) = cursor.fetchone()

            # delete loaded game from database
            cursor.execute(
                "DELETE FROM Saved_Games WHERE Name=?",
                (s.username.upper(),),
            )
            con.commit()

            pg.key.set_repeat(1, 1)
            return score

        else:
            print("ERROR: USERNAME NOT FOUND")
            return 0

    return (name, speed, shield, money, score, nuke, lives, level)


def refresh_hearts(lives):
    x_pos, y_pos = 560, 10  # coordinates of first heart
    offset = 30  # offset between heart positions

    # creates heart images in corner to show player how many lives they have
    for i in range(lives):
        heart = sprites.boost(2)
        heart.rect.x = x_pos
        x_pos -= offset
        heart.rect.y = y_pos
        s.heart_group.add(heart)

    # delete any out of bounds heart sprites
    for sprite in s.heart_group:
        if sprite.rect.x < ((x_pos + offset) - (lives * offset)):
            sprite.kill()


def enter_name():
    """user enters name to be displayed on the screen"""
    screen.blit(pg.image.load("images/enter_name.jpg"), (0, 0))
    pg.display.update()
    letters = []

    if s.username == "":
        while True:
            screen.blit(pg.image.load("images/enter_name.jpg"), (0, 0))

            # get letter from user input and write it to the screen
            enter_pressed = get_name(letters)
            display_text(s.username, "centerx", "centery", 300, 390)
            pg.display.update()

            # if user submits their name
            if enter_pressed:
                return True


def save_game(score, ship1, level):
    """
    Save current game state to a sql database so it can be reloaded in the future
    """
    enter_name()

    with sqlite3.connect("User_Data.sqlite") as con:
        cursor = con.cursor()
        cursor.execute(
            "SELECT Name FROM Saved_Games WHERE Name=?",
            (s.username.upper(),),
        )
        data = cursor.fetchone()

        # checks if username is taken, otherwise saves game state
        if data is None:

            cursor.execute(
                """INSERT INTO Saved_Games(
                                    Name,
                                    Rocks,
                                    Speed,
                                    Shield,
                                    Money,
                                    Points,
                                    Nuke,
                                    Lives,
                                    Level)
                                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    s.username.upper(),
                    len(s.meteor_group),
                    ship1.speed,
                    ship1.shield,
                    ship1.money,
                    score,
                    ship1.nuke,
                    ship1.lives,
                    level,
                ),
            )

            con.commit()

        else:
            print("username already exists in database")
            save_game(score, ship1)

        # signal to user that the game is saved
        screen.blit(pg.image.load("images/game_saved.jpg"), (0, 0))
        pg.display.update()
        sleep(2)
        # terminates the program
        exit()


def save_score(name, score):
    """saves user's score in a txt file"""
    f = open("names.txt", "r")
    data = json.load(f)
    data[name] = score
    f.close

    f = open("names.txt", "w")
    json.dump(data, f)
    f.close


def use_nuke(ship1):
    screen_top, screen_bottom = 480, 0
    ship1.nuke = False  # remove nuke from player inventory
    num_frames = 1500
    explosion = pg.image.load("images/explosion.png")

    for rock in s.meteor_group:
        # if meteor is on the screen
        if rock.rect.centery < screen_top and rock.rect.centery > screen_bottom:
            rock.kill()  # delete the meteor
            for i in range(num_frames):
                # explodes the meteors
                screen.blit(explosion, rock.rect)
                pg.display.update(rock.rect)
