# Boxing Game 🥊

A fun 2D boxing game built with Python and Pygame featuring player vs AI combat with multiple punch types, blocking mechanics, and smooth animations.

## Features

- **Player vs AI Combat**: Fight against an AI opponent with intelligent behavior
- **Multiple Punch Types**:
  - **Jab (A key)**: Fast punch with low damage
  - **Hook (S key)**: Medium speed with medium damage
  - **Uppercut (D key)**: Slow but powerful punch
- **Defensive Mechanics**: Block incoming attacks with SPACE key
- **Health System**: Visual health bars with damage tracking
- **Scoring System**: Points awarded for successful hits
- **Round Timer**: 3-minute rounds with time-based decisions
- **Visual Effects**: Particle effects for hits, smooth animations
- **Game States**: Menu, gameplay, pause, and game over screens

## Installation

1. Make sure Python 3 is installed on your system
2. Install pygame:
   ```bash
   pip install pygame==2.5.2
   ```
   Or install all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Play

### Starting the Game
```bash
python3 boxing_game.py
```

### Controls

**Movement:**
- `←` Left Arrow - Move left
- `→` Right Arrow - Move right

**Attacks:**
- `A` - Jab (fast, 5 damage)
- `S` - Hook (medium, 10 damage)
- `D` - Uppercut (slow, 15 damage)

**Defense:**
- `SPACE` - Block (reduces damage by 66%)

**Menu:**
- `ENTER` - Start game / Play again
- `ESC` - Pause game / Return to menu / Quit

## Gameplay Mechanics

### Combat System
- Each punch type has different speed, damage, and range
- Punches have cooldown periods to prevent spamming
- Blocking reduces incoming damage significantly
- Getting hit causes brief stun period

### AI Opponent
- Intelligent AI that moves, attacks, and blocks
- Adapts distance based on combat situation
- Uses all three punch types strategically
- Random decision-making for unpredictability

### Winning Conditions
1. **Knockout**: Reduce opponent's health to 0
2. **Points Decision**: Higher score when time runs out
3. **Draw**: Equal scores at end of round

### Scoring
- Points awarded based on damage dealt
- Blocked attacks give reduced points
- Combo attacks increase score multiplier

## Game Features

### Visual Elements
- Animated boxer sprites with bobbing motion
- Particle effects on successful hits
- Health bars with smooth updates
- Boxing ring with ropes and canvas
- Hit stun visual feedback

### UI Elements
- Real-time health bars for both fighters
- Round timer (3 minutes)
- Score tracking
- Control hints
- Pause menu
- Game over screen with results

## Tips for Playing

1. **Mix Up Your Attacks**: Don't rely on one punch type
2. **Use Jabs**: Quick jabs can interrupt opponent's attacks
3. **Block Strategically**: Don't hold block constantly, time it right
4. **Manage Distance**: Move in for attacks, back away to recover
5. **Watch the Timer**: Play aggressively when ahead, defensively when behind
6. **Uppercuts for Knockouts**: Save powerful uppercuts for finishing moves

## Technical Details

- **Resolution**: 1000x700 pixels
- **Frame Rate**: 60 FPS
- **Round Duration**: 180 seconds (3 minutes)
- **Health**: 100 HP for each fighter
- **Punch Cooldown**: 30 frames (~0.5 seconds)

## Code Structure

- `BoxingGame`: Main game class managing game loop and states
- `Boxer`: Base class for fighters with combat mechanics
- `Player`: Player-controlled boxer
- `Opponent`: AI-controlled boxer with decision-making
- `Punch`: Active punch objects with hitboxes
- `Particle`: Visual effect particles for hits
- `GameState`: Enum for game states (Menu, Playing, Paused, Game Over)
- `PunchType`: Enum for punch types (Jab, Hook, Uppercut)

## Troubleshooting

### Game won't start
- Ensure pygame is installed: `pip install pygame`
- Check Python version: Python 3.7+ required

### Display issues
- Make sure your display supports 1000x700 resolution
- Try running in windowed mode (default)

### Performance issues
- Close other applications
- Update graphics drivers
- Reduce particle effects (modify code if needed)

## Future Enhancements

Potential features for future versions:
- Multiple difficulty levels
- Character selection
- Power-ups and special moves
- Multiplayer mode (local)
- Tournament mode
- Statistics tracking
- Sound effects and music
- More advanced AI patterns
- Training mode

## License

This boxing game is part of the base44-docs-tool project and follows the same MIT License.

## Credits

Created as a demonstration of Python game development with Pygame.

---

**Enjoy the fight! 🥊**
