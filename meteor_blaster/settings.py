import pygame as pg

pg.font.init()

screen = pg.display.set_mode((600, 480))
background = pg.image.load("images/space.jpeg")
screen_width, screen_height = background.get_size()
p1_image = "images/spaceship.bmp"
p2_image = "images/spaceship2.png"
num_meteors = 60
bullet_cooldown = 0.4  # cooldown between when player can shoot, in seconds
bullet_cooldown_on = False
font = pg.font.Font(None, 45)
coin_despawn_time = 5
username = ''

play_pos = pg.Rect(200, 375, 200, 50)
one_player_pos = pg.Rect(85, 265, 130, 50)
two_player_pos = pg.Rect(385, 265, 130, 50)
load_game_pos = pg.Rect(235, 267, 130, 50)

nuke_pos = pg.Rect(44, 129, 192, 59)
extra_lives_pos = pg.Rect(44, 256, 192, 59)
speed_boost_pos = pg.Rect(44, 379, 192, 59)
gun_upgrade_pos = pg.Rect(362, 129, 192, 59)
shield_pos = pg.Rect(362, 257, 192, 59)
double_points_pos = pg.Rect(362, 377, 192, 59)
exit_pos = pg.Rect(535, 0, 65, 35)

# these variables need to be checked to see if they're necessary

time_paused = 0
boss_bullet_pos = 0
meteor_position = None
two_player = False
double_p = False
shots_fired = False
meteor_group = pg.sprite.Group()
heart_group = pg.sprite.Group()
bullet_group = pg.sprite.Group()
coin_group = pg.sprite.Group()
powerup_group = pg.sprite.GroupSingle()
