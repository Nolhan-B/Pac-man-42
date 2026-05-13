PROJECT MANAGEMENT REPORT - PAC-MAN
1. General Idea & Architecture
Engine: This is the "brain" of the game. It handles logic, collisions, and scores.
Renderer: This handles all the Pygame drawing. I made sub-renderers for the UI, the maze, and
the actors to keep it organized.
Asset Manager: A central place to load images and fonts so I don't reload them every frame.
2. Risks & Problems I Fixed
What went wrong? How did I fix it?
Lag in Fullscreen
mode.
The transparency of the background was too heavy for the CPU. I
"baked" the maze onto a black surface at the start. Huge FPS boost.
Game crashing with
bad JSON.
Added try/except blocks in the config loader. If the file is broken, the
game uses default values instead of crashing.
Ghost behavior
bugs.
Used a simple State Machine (Chase, Frightened, Dead) to make sure
they don't do weird stuff during transitions.
Step 1: The Basics
Step 2: Graphics and Menus
• 
• 
• 
By: nbarbosa , nbilyj / 42 
Student
This document explains how we organized the work for the Pac-Man project and the technical 
choices we made during development.
We wanted a clean code that is easy to debug. We split the game into different parts so they don't 
depend too much on each other:
3. My Progress
(How we built it)
We started with a simple grid and made Pac-Man move. We spent a lot of time on the collision 
system to make sure he doesn't get stuck in walls.
We integrated the AssetManager to load sprites. Then we built the Menu system and the Pause 
screen. We used a State machine for the global GameState

Step 3: AI and Polishing
4. Testing
I tested the game by playing it a lot and trying to break it:
Checked if ghosts respawn correctly after being eaten.
Verified that levels change automatically when the maze is empty.
Tested the invincibility cheat to see if collisions still count for eating dots.
Final Note: The main challenge was the performance optimization. Using 
convert_alpha() and pre-rendering the background made the game much smoother. 
• 
• 
• 
Added the ghosts with their different modes. Finally, Nbilyj added the Highscore system (JSON 
storage) and the Cheat mode for debuggi