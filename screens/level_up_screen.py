import pygame
import os
import time
from utils.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, LEVEL_UP_IMAGE
)

class LevelUpScreen:
    def __init__(self, game, level):
        self.game = game
        self.level = level
        self.display_time = 3.0  # Show for 3 seconds
        self.start_time = time.time()
        
        # Load level up image
        if os.path.exists(LEVEL_UP_IMAGE):
            self.bg_image = pygame.image.load(LEVEL_UP_IMAGE)
            self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.bg_image = None
    
    def handle_event(self, event):
        # Skip to next level on mouse click
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.proceed_to_next_level()
    
    def update(self):
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        # Automatically proceed after display time
        if elapsed >= self.display_time:
            self.proceed_to_next_level()
    
    def proceed_to_next_level(self):
        # Proceed to the next level gameplay
        # Preserve the AI mode from the previous screen
        ai_mode = self.game.game_screen.logic.ai_mode
        
        # Create new game screen with the same AI mode
        self.game.game_screen = self.game.game_screen.__class__(
            self.game, self.level, 0, [], ai_mode
        )
        self.game.current_screen = self.game.game_screen
        
        # Save the game state immediately after level up
        self.game.save_manager.save_game(self.game.game_screen.logic.get_game_state())
    
    def draw(self, surface):
        # Draw only the background image
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill(WHITE)