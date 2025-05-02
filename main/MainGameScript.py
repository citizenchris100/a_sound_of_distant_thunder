"""
A Sound of Distant Thunder
Main game script that initializes and starts the game.
"""
import os
import sys
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("game.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("Main")

def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="A Sound of Distant Thunder")
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Enable debug mode"
    )
    parser.add_argument(
        "--data", 
        default="./data/", 
        help="Path to game data directory"
    )
    parser.add_argument(
        "--assets", 
        default="./assets/", 
        help="Path to game assets directory"
    )
    parser.add_argument(
        "--load", 
        help="Load saved game at startup"
    )
    
    return parser.parse_args()

def ensure_directories(data_path, asset_path):
    """
    Ensure required directories exist.
    
    Args:
        data_path (str): Path to game data directory
        asset_path (str): Path to game assets directory
    """
    # Create main directories
    os.makedirs(data_path, exist_ok=True)
    os.makedirs(asset_path, exist_ok=True)
    
    # Create subdirectories
    for subdir in ["npcs", "locations", "items", "dialogs", "events", "saves", "schemas"]:
        os.makedirs(os.path.join(data_path, subdir), exist_ok=True)
    
    for subdir in ["ui", "locations", "npcs", "items", "fonts", "sounds", "music"]:
        os.makedirs(os.path.join(asset_path, subdir), exist_ok=True)

def main():
    """Main function that starts the game"""
    # Parse command line arguments
    args = parse_args()
    
    # Ensure required directories exist
    ensure_directories(args.data, args.assets)
    
    # Initialize pygame
    try:
        import pygame
        pygame.init()
        
        # Set window properties
        pygame.display.set_caption("A Sound of Distant Thunder")
        pygame.display.set_icon(pygame.Surface((32, 32)))  # Placeholder icon
        
        logger.info("Pygame initialized")
    except ImportError:
        logger.error("Pygame not installed. Please install pygame: pip install pygame")
        return
    except Exception as e:
        logger.error(f"Error initializing pygame: {e}")
        return
    
    # Import game modules
    try:
        from game_engine import GameEngine
    except ImportError as e:
        logger.error(f"Error importing game modules: {e}")
        logger.error("Make sure all required files are in the correct location.")
        return
    
    # Create game engine
    try:
        game_engine = GameEngine(
            data_path=args.data,
            asset_path=args.assets,
            debug_mode=args.debug
        )
        
        # Initialize game
        game_engine.initialize()
        
        # Load saved game if specified
        if args.load:
            game_engine.load_game(args.load)
        else:
            # Start new game
            game_engine.handle_event("game_start")
        
        # Run game
        game_engine.run()
    except Exception as e:
        logger.exception(f"Error running game: {e}")
    finally:
        # Clean up
        pygame.quit()
        logger.info("Game terminated")

if __name__ == "__main__":
    main()