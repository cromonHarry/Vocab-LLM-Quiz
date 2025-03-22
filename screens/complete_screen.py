import pygame
import os
import time
from utils.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GRAY, LIGHT_GRAY,
    BUTTON_WIDTH, BUTTON_HEIGHT, COMPLETE_IMAGE
)

class GameCompleteScreen:
    def __init__(self, game):
        self.game = game
        self.display_time = 5.0  # Show for 5 seconds before showing button
        self.start_time = time.time()
        
        # Load completion image
        if os.path.exists(COMPLETE_IMAGE):
            self.bg_image = pygame.image.load(COMPLETE_IMAGE)
            self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.bg_image = None
        
        # Setup button
        self.return_btn = Button(
            SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
            SCREEN_HEIGHT - 100,
            BUTTON_WIDTH, BUTTON_HEIGHT,
            "Return to Menu"
        )
        
        # Button visibility
        self.show_button = False
        
    def handle_event(self, event):
        # Only process button clicks after display time
        if self.show_button:
            mouse_pos = pygame.mouse.get_pos()
            self.return_btn.check_hover(mouse_pos)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.return_btn.is_clicked(mouse_pos, event):
                    # Delete save file and return to start screen
                    self.game.save_manager.delete_save()
                    self.game.current_screen = self.game.start_screen
    
    def update(self):
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        # Show button after display time
        if elapsed >= self.display_time:
            self.show_button = True
    
    def draw(self, surface):
        # Draw background
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill(WHITE)
        
        # Draw return button after display time
        if self.show_button:
            self.return_btn.draw(surface)


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