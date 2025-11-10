# Boxing Game - Quick Start Guide 🥊

## Installation & Running

### Quick Start (3 steps)
```bash
# 1. Install pygame
pip install pygame

# 2. Run the game
python3 boxing_game.py

# Or use the launcher script
./play_boxing.sh
```

## Game Controls

### Essential Controls
| Key | Action |
|-----|--------|
| `←` `→` | Move left/right |
| `A` | Jab (fast, 5 damage) |
| `S` | Hook (medium, 10 damage) |
| `D` | Uppercut (slow, 15 damage) |
| `SPACE` | Block (reduces damage) |
| `ESC` | Pause / Menu |
| `ENTER` | Start / Restart |

## Quick Tips

1. **Mix your punches** - Don't spam one attack
2. **Use jabs** to interrupt opponent attacks
3. **Block strategically** - Time it, don't hold it
4. **Watch your health** - Retreat when low
5. **Uppercuts for KO** - Save them for finishing

## Game Modes

- **Knockout**: Reduce opponent health to 0
- **Points Decision**: Higher score after 3 minutes
- **Draw**: Equal scores at time limit

## Troubleshooting

### "No module named pygame"
```bash
pip install pygame
```

### "Display not found" (headless environment)
The game requires a graphical display. Options:
- Run on a system with a display
- Use X11 forwarding: `ssh -X user@host`
- Use virtual display: `xvfb-run python3 boxing_game.py`

### Game runs slow
- Close other applications
- Update graphics drivers
- Check system requirements

## System Requirements

- **Python**: 3.7 or higher
- **Pygame**: 2.5.2 or higher
- **Display**: 1000x700 minimum resolution
- **RAM**: 512 MB minimum
- **CPU**: Any modern processor

## File Structure

```
boxing_game.py              # Main game file (run this)
BOXING_GAME_README.md       # Full documentation
BOXING_GAME_QUICKSTART.md   # This file
play_boxing.sh              # Launcher script
requirements.txt            # Dependencies (includes pygame)
```

## Features at a Glance

✅ Player vs AI combat  
✅ 3 punch types with different stats  
✅ Blocking mechanics  
✅ Health & scoring system  
✅ 3-minute rounds  
✅ Particle effects  
✅ Smooth animations  
✅ Pause functionality  
✅ Game over screen with results  

## Next Steps

1. **Read full docs**: See `BOXING_GAME_README.md` for detailed info
2. **Practice**: Learn the timing and combos
3. **Experiment**: Try different strategies
4. **Have fun**: It's a game! 🎮

---

**Ready to fight? Run `python3 boxing_game.py` and start boxing!** 🥊
