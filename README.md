<h1 style="text-align: center;">User manual - Capture the flag</h1>

### Introduction
This is an arcade-style tank shooter game, where the goal is to 
grab the flag and bring it back to your base. At your disposal is
your trusty tank cannon, which can fire both regular bullets which
follow a straight path, and guided bullets, which follow your command.
Your opponents will be other tanks which are controlled by the computer,
or you can select two-player mode and a friend can join the match.
<center>
<video loop muted autoplay>
	<source src="example-videos/generic_gameplay.mp4">
</video>
</center>

### Contents
* [Setup](#setup)
  + [Installation](#installation)
  + [Controls](#controls)
* [Gameplay and features](#gameplay-and-features)
* [Explanation of modules](#explanation-of-modules)
  + [ai.py](#aipy)
  + [ctf.py](#ctfpy)
  + [gameobjects.py](#gameobjectspy)
  + [gamestate.py](#gamestatepy)
  + [handle_events.py](#handle-eventspy)
  + [maps.py](#mapspy)
  + [menus.py](#menuspy)
  + [objectcreation.py](#objectcreationpy)
  + [resources.py](#resourcespy)


## Setup

### Installation
Ensure both the modules pymunk and pygame are installed on your machine.

This can easily done with pip:
`pip install pymunk`
`pip install pygame`

After cloning the git repository, you can start the game simply by running the
python file `ctf.py`.
`python3 ctf.py`


## Gameplay and features

### Menu
The menu is composed of a home screen and a settings menu. From the home screen
you can either start a new game, exit the game, or go into the settings menu.
In the settings menu, you can change the current map and the number of players.

### Controls
The keyboard controls for **player 1** are:

|key      |action                        |
|---------|------------------------------|
|up       |accelerate tank forward       |
|down     |accelerate tank backward      |
|left     |rotate tank counter-clockwise |
|right    |rotate tank clockwise         |
|spacebar |fire a (guided) bullet        |

To exit the game, either press **ESC** or simply close the pygame window with
the x button.

If couch multiplayer is enabled, the following keyboard controls are for
**player 2:**

|key|action                         |
|---|-------------------------------|
|w  | accelerate tank forward       |
|a  | accelerate tank backward      |
|s  | rotate tank counter-clockwise |
|d  | rotate tank clockwise         |
|b  | fire a (guided) bullet        |

### Guided Bullets
By keeping the "shoot" button held down, players may shoot a guided bullet,
which is controller with the movement keys. Keep in mind that the tank cannot
be controlled while steering the bullet. Also, the tank can accidentally shoot
itself.

### Score display
At all times during the game, the current score of each tank is displayed on
the top left of their starting base. When a tank scores, all scores are shown
on a larger overlay, and the game is restarted.

### Visual enhancements
Whenever a bullet hits something or a thing is destroyed, an explosion effect
is automatically played. Additionally, damage is shown through cracks in
objects.

### Audio
The game has a background soundtrack and plays sounds for things like
explosions and collisions.

### A* Search
When the AI searches for a path, it first investigates paths which go through
as few metalboxes as possible, as to not slow down too much.

### Unfair AI
The AI moves significantly faster than the player. Additionally, the bullets
shot by AI tanks are 1.3 times faster than player bullets.

### Health and respawn protection.
Each tank has 3HP and 5 seconds of invulnerability after death. Wooden boxes
have 2HP and do not respawn. Health indication is visualized through cracks
on the objects.

### Custom maps
Custom maps can be loaded from txt or json files. To do this, run the game with
the flag `--map` followed by the map file. Keep in mind that this disables the
map selection in the settings. For example maps, see the `cmaps` directory in
this repository.

### Optional flags
The game also provides some optional flags to alter its behaviour:
* `--mp` allows for multiplayer mode.
* `--noclock` turns off the clock, significantly speeding up the game.
* `--nosound` turns off all sound effects.


## Explanation of modules

### ai.py
Contains declaration of the AI class, which contains methods and fields that
enable it to make decisions in the game.

### ctf.py
This is the main file, which imports in some way or another from every other
module found in the repository.

It mostly handles meta- or program aspects of the game, such as defining window
size and handling resizing, but of course alls calls every other necessary
function, such as displaying the current game state, or menus.

This module also keeps track of score.

### gameobjects.py
This module contains declarations for every 'object' in the game. There is one
superclass from which every object inherits, GameObject, which only keeps track
of the object's sprite. There also exists two superclasses which inherit from
GameObject: GamePhysicsObject and GameVisibleObject.

Tanks, boxes and bullets are GamePhysicsObject:s, which means they have
collision, and basically "exist" in the game space.

Flags, explosions and bases are GameVisibleObject:s, which means they only are
displayed in the game, but don't obstruct physics objects.

### gamestate.py
This module contains definition for the GameState class, which we instance in
the main module to keep track of everything happening in the game. Some of the
attributes contained in a GameState: settings, current_map, objects, ais.

### handle_events.py
Contains functions for handling keyboard input and displaying things to screen.

### maps.py
Contains definition of the Map class, and the three default maps: map0, map1 and
map2.

### menus.py
Contains functions for displaying the homescreen and the settings screen.

### objectcreation.py
Small module with a definition for generating every game object from scratch,
i.e. start a new game.

### resources.py
Handles loading external images to use as sprites ingame. Also contains the
definition of the Constants class, which is what the 'settings' object in every
GameState is an instance of.
