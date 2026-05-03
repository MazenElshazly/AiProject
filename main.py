import sys

if __name__ == "__main__":
    print("Welcome to Hnefatafl!")
    print("1. Play with GUI (Pygame)")
    print("2. Play in Console")
    choice = input("Select an option (1/2): ").strip()
    
    if choice == '1':
        try:
            import pygame
        except ImportError:
            print("Pygame is not installed. Please run: pip install pygame")
            sys.exit(1)
        from gui import run_gui
        run_gui()
    else:
        from game_controller import run_game
        run_game()