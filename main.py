import pygame
import sys
from utils.config import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, FPS
from screens.start_screen import StartScreen
from screens.game_screen import GameScreen
from screens.level_up_screen import LevelUpScreen
from screens.ai_select_screen import AISelectScreen
from utils.data_loader import load_all_questions
from utils.save_manager import SaveManager

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_screen = None
        
        # AI mode (online or local)
        self.ai_mode = "online"  # Default to online AI
        
        # Loading screen
        self.show_loading_screen()
        
        # Load questions and save manager
        self.questions = load_all_questions()
        self.save_manager = SaveManager()
        
        # Initialize screens
        self.start_screen = StartScreen(self)
        self.ai_select_screen = AISelectScreen(self)
        self.game_screen = None
        self.level_up_screen = None
        self.complete_screen = None
        
        # Set initial screen
        self.current_screen = self.start_screen
    
    def show_loading_screen(self):
        # Display a loading animation while resources are being loaded
        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont('Arial', 36)
        
        loading_text = ["Loading", "Loading.", "Loading..", "Loading..."]
        for i in range(20):  # Simple animation loop
            self.screen.fill((0, 0, 0))
            text = font.render(loading_text[i % 4], True, (255, 255, 255))
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(text, text_rect)
            pygame.display.flip()
            pygame.time.delay(100)
            
    def set_ai_mode(self, mode):
        # Set the AI mode (online or local)
        self.ai_mode = mode
    
    def show_ai_selection(self):
        # Show AI selection screen
        self.current_screen = self.ai_select_screen
    
    def start_new_game(self):
        # Start a new game with current AI mode
        self.game_screen = GameScreen(self, 1, 0, [], self.ai_mode)
        self.current_screen = self.game_screen
    
    def load_game(self):
        # Load a saved game
        save_data = self.save_manager.load_game()
        if save_data:
            level, correct_answers, completed_questions, ai_mode = save_data
            self.ai_mode = ai_mode
            self.game_screen = GameScreen(self, level, correct_answers, completed_questions, ai_mode)
            self.current_screen = self.game_screen
        else:
            # If no save exists, show AI selection screen
            self.show_ai_selection()
    
    def show_level_up(self, level):
        # Show level up screen when player completes a level
        self.level_up_screen = LevelUpScreen(self, level)
        self.current_screen = self.level_up_screen
    
    def run(self):
        # Main game loop
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.current_screen.handle_event(event)
            
            self.current_screen.update()
            self.current_screen.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()