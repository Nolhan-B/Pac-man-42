# Task Tracking

## Done
- [x] Config parser with comment handling
- [x] Highscore system (persistent JSON)
- [x] Maze generator integration
- [x] Player movement with wall collision detection
- [x] Ghost AI (chase / frightened / dead states)
- [x] Smooth interpolated movement (player & ghosts)
- [x] Pacgum & super-pacgum logic
- [x] Collision detection (visual pixel-based)
- [x] Cheat mode (invincibility, speed, ghost freeze)
- [x] HUD (score, lives, level, time)
- [x] Main menu, pause menu, game over screen
- [x] Death animation & respawn countdown
- [x] Fullscreen support
- [x] Multi-level progression with random seeds
- [x] flake8 + mypy strict compliance

## Bugs fixed
- Ghost direction `None` on spawn causing type errors
- Player position uninitialized causing arithmetic on `None`
- Intra-wall collisions fixed using prev/current cell check
- Asset loading crash on malformed PNG headers
- Display glitches in fullscreen mode