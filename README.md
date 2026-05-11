
*This project has been created as part of the 42 curriculum by Nbarbosa and Nbilyj.*
## Description

This project is a modern, object-oriented recreation of the classic 1980 arcade game Pac-Man, written in Python. The goal of the project is to build a robust, modular game engine featuring autonomous ghost AI, level progression, and dynamic maze generation. It emphasizes clean software architecture, and strict error management without crashing.

## Instructions
The game requires Python 3.10 or later. A `Makefile` is provided to automate common tasks.

* **Install dependencies:** `make install`
* **Run the game:** `make run`
* **Run in debug mode:** `make debug`
* **Check code quality (Linter):** `make lint`
* **Clean cache files:** `make clean`

To launch the game manually, you must provide a valid configuration file:
`python3 pac-man.py config.json`

## Resources
* Pygame Official Documentation: To handle sprite rendering, surface manipulation, and event loops.
* **AI Usage:** Artificial Intelligence (Gemini) was used , Specifically, it helped resolve complex Mypy static typing errors (handling `Optional` types).

## Configuration
The game relies on a `config.json` file to define parameters. The custom JSON parser ignores comments starting with `#` to allow documentation directly inside the configuration file.

* `highscore_filename`: Path to the file where scores are saved.
* `lives`: Initial number of lives for the player.
* `points_per_pacgum`: Score awarded for regular dots.
* `points_per_super_pacgum`: Score awarded for power pellets.
* `points_per_ghost`: Score awarded for eating an edible ghost.
* `levels`: An array containing objects defining the `width` and `height` of each specific level.

If an invalid or missing value is detected, the engine clamps the parameter to a safe default value and logs a warning without interrupting the execution.

## Highscore System
The highscore system persists player scores across sessions. 

It is implemented using a separate JSON file. I chose this implementation because it allows for easy serialization and deserialization of native Python objects while remaining human-readable. The `HighscoreManager` class safely attempts to load the file on startup. If the file is missing or corrupted, it creates a fresh list. At the end of a game, players are prompted to input their names (up to 10 alphanumeric characters), and the top 10 scores are sorted and written back to the disk.

## Maze Generation
This project integrates an external maze generator package called `A-Maze-ing` (provided by another team). 

The game does not use a custom generation algorithm. Instead, a wrapper interfaces with the external package. The generator is called with the `PERFECT = False` parameter to ensure loops and corridors suitable for Pac-Man gameplay. The first level uses a fixed seed for evaluation consistency, while subsequent levels generate random layouts. If the external generator fails, a safe fallback map is provided to prevent the game from crashing.

## Implementation
The game loop runs at a fixed 60 FPS using `pygame.time.Clock()`. 

To ensure consistent movement speeds regardless of frame drops or fullscreen scaling, actors (Player and Ghosts) utilize Delta Time for their positional updates. A significant performance optimization was implemented in the `AssetManager`: instead of calculating alpha transparency dynamically at every frame for the background maze, the alpha layer is "baked" onto a solid black surface once during the loading phase. This reduces pixel recalculations and prevents performance drops in high resolutions.

## General Software Architecture
The project follows a modular, MVC-inspired architectural pattern:

* **`pac-man.py`:** Contains the core game loop, handles keyboard events, and manages the overall `GameState` transitions (Menu, Playing, Pause, Game Over).
* **`game_engine.py` (Engine):** The core logic center. It handles collision detection, score calculation, timers, and level progression. It holds instances of the Level, Player, and Ghosts.
* **`player.py` & `ghost.py`:** Actor classes defining movement logic, direction handling, and specific state machines (e.g., CHASE, FRIGHTENED, DEAD for ghosts).
* **`renderer.py` & `base_renderer.py`:** The presentation layer. Separated into sub-renderers (Maze, Actors, UI) to isolate drawing logic from game mechanics.
* **`asset_manager.py`:** A centralized singleton-like class responsible for pre-loading, scaling, and caching all sprites and fonts to optimize memory usage.

## Project Management
The development cycle was driven by a structured Agile approach to track features, mitigate technical risks, and manage task distribution. 

All evidence of project tracking, including Gantt charts, risk analysis, acceptance testing plans, and daily progress logs, can be found in the dedicated directory:
[Link to the Project Management Directory](./project_management/)