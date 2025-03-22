import pickle
import os
from utils.config import SAVE_FILE

class SaveManager:
    def __init__(self):
        self.save_file = SAVE_FILE
        
        # Make sure the data directory exists
        os.makedirs(os.path.dirname(self.save_file), exist_ok=True)
    
    def save_game(self, game_state):
        # Save the current game state
        try:
            with open(self.save_file, 'wb') as f:
                pickle.dump(game_state, f)
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def load_game(self):
        # Load a saved game if one exists
        if not os.path.exists(self.save_file):
            return None
        
        try:
            with open(self.save_file, 'rb') as f:
                game_state = pickle.load(f)
            return game_state
        except Exception as e:
            print(f"Error loading game: {e}")
            return None
    
    def delete_save(self):
        # Delete saved game
        if os.path.exists(self.save_file):
            try:
                os.remove(self.save_file)
                return True
            except Exception as e:
                print(f"Error deleting save: {e}")
                return False
        return True  # Nothing to delete
