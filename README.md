# Meteor Blaster

Meteor Blaster is a 2D space shooter that I created to teach myself pygame and the basics of game development. The game is inspired by old arcade shooters and the idea of the game is that you control a spaceship that's flying through a meteor shower. The object of the game is to destroy the meteors before they reach the bottom of the screen and to avoid being hit by them. Players also have the option to save and load games using a SQL database and at the end of the game are prompted to enter their name so it can be displayed in a leaderboard.

The game is written in Python using the Pygame module, it uses MySQL to access the SQL database, NumPy for calculations, and the threading module to run some aspects of the game in parallel with the main loop so that animations could play without them interupting the rest of the game.

The game controls are:

<table class="tg">
<thead>
  <tr>
    <th class="tg-baqh"></th>
    <th class="tg-baqh">Movement</th>
    <th class="tg-baqh">Shoot</th>
    <th class="tg-baqh">Activate Shield</th>
    <th class="tg-baqh">Activate Nuke</th>
    <th class="tg-baqh">Pause</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td class="tg-baqh">Player 1</td>
    <td class="tg-baqh">Arrow Keys</td>
    <td class="tg-baqh">Space Bar</td>
    <td class="tg-baqh">1</td>
    <td class="tg-baqh">2</td>
    <td class="tg-baqh">P</td>
  </tr>
  <tr>
    <td class="tg-baqh">Player 2</td>
    <td class="tg-baqh">WASD</td>
    <td class="tg-baqh">Q</td>
    <td class="tg-baqh">1</td>
    <td class="tg-baqh">2</td>
    <td class="tg-baqh">P</td>
  </tr>
</tbody>
</table>

## Features:

Start menu with options for one player or two player mode. It also gives players the option to load a previous game and continue from where they left off.

![Meteor Blaster: Main Menu](https://github.com/NoahHA/meteor-blaster/blob/main/meteor_blaster/images/demonstration%20images/main%20menu.png?raw=true)

Bulk of the game is meteors/gems falling from the sky which the player has to shoot/collect:

Insert GIF of gameplay

Pause Menu with game info and option to save game, accessed by pressing 'p'.

![Meteor Blaster: Pause Menu](https://github.com/NoahHA/meteor-blaster/blob/main/meteor_blaster/images/demonstration%20images/pause%20screen.png?raw=true)

At the end of each level there is a boss fight where you fight a giant spaceship that has 4 different attack methods that effect different areas of the screen, the boss constantly attacks, picking the attack method based on player position. The bosses health is indicated by a health bar on the side of the screen, when this reaches 0 the boss fight ends and a death animation is triggered.

![Meteor Blaster: Boss Fight](https://github.com/NoahHA/meteor-blaster/blob/main/meteor_blaster/images/demonstration%20images/boss%20fight%202.png?raw=true)

Insert GIF of killing the boss

Once the boss is defeated, the player enters a shop menu where they can purchase a variety of power ups based on how many gems they have collected over the course of the game. Once they exit the shop they enter the next level and have to go through everything again but with increased difficulty, this continues until they die.

![Meteor Blaster: Shop Menu](https://github.com/NoahHA/meteor-blaster/blob/main/meteor_blaster/images/demonstration%20images/shop%20menu.png?raw=true)

When the game ends the player is sent to a game over screen where they are prompted to enter their name and then shown a leaderboard of the top ten scores of all time.

![Meteor Blaster: Game Over](https://github.com/NoahHA/meteor-blaster/blob/main/meteor_blaster/images/demonstration%20images/game%20over%20screen.png?raw=true)
