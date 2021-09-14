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
