#!/usr/bin/env python3
"""
Comprehensive test suite for boxing_game.py
Tests all components without requiring a display
"""

import sys

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import pygame
        import boxing_game
        print("  ✓ All imports successful")
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False

def test_enums():
    """Test enum definitions"""
    print("\nTesting enums...")
    try:
        import boxing_game
        
        # Test GameState
        states = [s.name for s in boxing_game.GameState]
        assert 'MENU' in states
        assert 'PLAYING' in states
        assert 'GAME_OVER' in states
        assert 'PAUSED' in states
        print(f"  ✓ GameState enum: {len(states)} states")
        
        # Test PunchType
        punches = [p.name for p in boxing_game.PunchType]
        assert 'JAB' in punches
        assert 'HOOK' in punches
        assert 'UPPERCUT' in punches
        print(f"  ✓ PunchType enum: {len(punches)} types")
        
        return True
    except Exception as e:
        print(f"  ✗ Enum test failed: {e}")
        return False

def test_classes():
    """Test class definitions and basic instantiation"""
    print("\nTesting classes...")
    try:
        import boxing_game
        
        # Test Particle
        particle = boxing_game.Particle(100, 100, boxing_game.RED)
        assert particle.x == 100
        assert particle.y == 100
        assert particle.life == 30
        print("  ✓ Particle class")
        
        # Test Punch
        punch = boxing_game.Punch(200, 200, boxing_game.PunchType.JAB, 1)
        assert punch.x == 200
        assert punch.y == 200
        assert punch.damage == 5
        print("  ✓ Punch class")
        
        # Check class methods
        boxer_methods = [m for m in dir(boxing_game.Boxer) if not m.startswith('_')]
        assert len(boxer_methods) >= 7
        print(f"  ✓ Boxer class: {len(boxer_methods)} methods")
        
        game_methods = [m for m in dir(boxing_game.BoxingGame) if not m.startswith('_')]
        assert len(game_methods) >= 11
        print(f"  ✓ BoxingGame class: {len(game_methods)} methods")
        
        return True
    except Exception as e:
        print(f"  ✗ Class test failed: {e}")
        return False

def test_constants():
    """Test game constants"""
    print("\nTesting constants...")
    try:
        import boxing_game
        
        assert boxing_game.SCREEN_WIDTH == 1000
        assert boxing_game.SCREEN_HEIGHT == 700
        assert boxing_game.FPS == 60
        print(f"  ✓ Screen: {boxing_game.SCREEN_WIDTH}x{boxing_game.SCREEN_HEIGHT}")
        print(f"  ✓ FPS: {boxing_game.FPS}")
        
        # Test colors
        assert len(boxing_game.RED) == 3
        assert len(boxing_game.BLUE) == 3
        print("  ✓ Colors defined")
        
        return True
    except Exception as e:
        print(f"  ✗ Constants test failed: {e}")
        return False

def test_punch_mechanics():
    """Test punch type properties"""
    print("\nTesting punch mechanics...")
    try:
        import boxing_game
        
        # Test Jab
        jab = boxing_game.Punch(0, 0, boxing_game.PunchType.JAB, 1)
        assert jab.damage == 5
        assert jab.speed == 15
        assert jab.range == 60
        print("  ✓ Jab: 5 damage, 15 speed, 60 range")
        
        # Test Hook
        hook = boxing_game.Punch(0, 0, boxing_game.PunchType.HOOK, 1)
        assert hook.damage == 10
        assert hook.speed == 10
        assert hook.range == 50
        print("  ✓ Hook: 10 damage, 10 speed, 50 range")
        
        # Test Uppercut
        uppercut = boxing_game.Punch(0, 0, boxing_game.PunchType.UPPERCUT, 1)
        assert uppercut.damage == 15
        assert uppercut.speed == 8
        assert uppercut.range == 45
        print("  ✓ Uppercut: 15 damage, 8 speed, 45 range")
        
        return True
    except Exception as e:
        print(f"  ✗ Punch mechanics test failed: {e}")
        return False

def test_particle_system():
    """Test particle behavior"""
    print("\nTesting particle system...")
    try:
        import boxing_game
        
        particle = boxing_game.Particle(100, 100, boxing_game.RED)
        initial_life = particle.life
        initial_y = particle.y
        
        # Update particle
        particle.update()
        
        assert particle.life < initial_life
        assert particle.y != initial_y  # Should move due to velocity
        print("  ✓ Particle updates correctly")
        print(f"  ✓ Particle lifetime: {initial_life} frames")
        
        return True
    except Exception as e:
        print(f"  ✗ Particle test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Boxing Game - Comprehensive Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_enums,
        test_classes,
        test_constants,
        test_punch_mechanics,
        test_particle_system,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    print("Test Results")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ All tests passed! Game is ready to play.")
        print("\nRun the game with: python3 boxing_game.py")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
