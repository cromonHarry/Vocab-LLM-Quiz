import pygame
import os
from utils.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT, 
    BUTTON_PADDING, WHITE, BLACK, GRAY, LIGHT_GRAY, START_BG_IMAGE
)

class Button:
    def __init__(self, x, y, width, height, text, font_size=32):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.SysFont('Arial', font_size)
        self.is_hovered = False
    
    def draw(self, surface):
        # Change color based on hover state
        color = LIGHT_GRAY if self.is_hovered else GRAY
        
        # Draw button
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)  # Border
        
        # Draw text
        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class StartScreen:
    def __init__(self, game):
        self.game = game
        
        # Load background image
        if os.path.exists(START_BG_IMAGE):
            self.bg_image = pygame.image.load(START_BG_IMAGE)
            self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.bg_image = None
        
        # Create buttons
        self.setup_buttons()
        
        # Title font
        self.title_font = pygame.font.SysFont('Arial', 64)
        
    def setup_buttons(self):
        center_x = SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2
        start_y = SCREEN_HEIGHT // 2 - BUTTON_HEIGHT // 2 + 150
        
        self.new_game_btn = Button(
            center_x, 
            start_y - BUTTON_HEIGHT - BUTTON_PADDING,
            BUTTON_WIDTH, BUTTON_HEIGHT,
            "New Game"
        )
        
        self.load_game_btn = Button(
            center_x, 
            start_y,
            BUTTON_WIDTH, BUTTON_HEIGHT,
            "Load Game"
        )
        
        self.quit_btn = Button(
            center_x, 
            start_y + BUTTON_HEIGHT + BUTTON_PADDING,
            BUTTON_WIDTH, BUTTON_HEIGHT,
            "Quit Game"
        )
    
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        
        # Check button hover states
        self.new_game_btn.check_hover(mouse_pos)
        self.load_game_btn.check_hover(mouse_pos)
        self.quit_btn.check_hover(mouse_pos)
        
        # Handle button clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.new_game_btn.is_clicked(mouse_pos, event):
                self.game.show_ai_selection()
            elif self.load_game_btn.is_clicked(mouse_pos, event):
                self.game.load_game()
            elif self.quit_btn.is_clicked(mouse_pos, event):
                self.game.running = False
    
    def update(self):
        # No continuous updates needed for start screen
        pass
    
    def draw(self, surface):
        # Draw background
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill(WHITE)
        
        # Draw buttons
        self.new_game_btn.draw(surface)
        self.load_game_btn.draw(surface)
        self.quit_btn.draw(surface)
