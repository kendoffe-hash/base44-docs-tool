#!/bin/bash
# Boxing Game Launcher Script

echo "🥊 Starting Boxing Game..."
echo ""
echo "Controls:"
echo "  Arrow Keys - Move"
echo "  A - Jab | S - Hook | D - Uppercut"
echo "  SPACE - Block"
echo "  ESC - Pause/Menu"
echo ""
echo "Note: This game requires a graphical display."
echo "If running in a headless environment, you'll need X11 forwarding or a virtual display."
echo ""

python3 boxing_game.py
