import pygame
import os
from utils.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT, 
    BUTTON_PADDING, WHITE, BLACK, GRAY, LIGHT_GRAY, START_BG_IMAGE
)

class AISelectScreen:
    def __init__(self, game):
        self.game = game
        
        # Load background image (reuse the start screen background)
        if os.path.exists(START_BG_IMAGE):
            self.bg_image = pygame.image.load(START_BG_IMAGE)
            self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.bg_image = None
        
        # Create buttons
        self.setup_buttons()
        
        # Title font
        self.title_font = pygame.font.SysFont('Arial', 48)
        self.description_font = pygame.font.SysFont('Arial', 24)
        
        # Button descriptions
        self.online_description = "Use Grok-3 for hints (requires internet)"
        self.local_description = "Use local model for hints (no internet needed)"
        self.current_description = None
        
    def setup_buttons(self):
        center_x = SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2
        start_y = SCREEN_HEIGHT // 2 - BUTTON_HEIGHT // 2 + 100
        
        self.online_ai_btn = Button(
            center_x, 
            start_y - BUTTON_HEIGHT - BUTTON_PADDING - 30,
            BUTTON_WIDTH, BUTTON_HEIGHT,
            "Online AI"
        )
        
        self.local_ai_btn = Button(
            center_x, 
            start_y,
            BUTTON_WIDTH, BUTTON_HEIGHT,
            "Local AI"
        )
        
        self.back_btn = Button(
            center_x, 
            start_y + BUTTON_HEIGHT + BUTTON_PADDING + 50,
            BUTTON_WIDTH, BUTTON_HEIGHT,
            "Back"
        )
    
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        
        # Check button hover states and update description
        self.current_description = None
        
        if self.online_ai_btn.check_hover(mouse_pos):
            self.current_description = self.online_description
        elif self.local_ai_btn.check_hover(mouse_pos):
            self.current_description = self.local_description
        else:
            self.back_btn.check_hover(mouse_pos)
        
        # Handle button clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.online_ai_btn.is_clicked(mouse_pos, event):
                self.game.set_ai_mode("online")
            elif self.local_ai_btn.is_clicked(mouse_pos, event):
                self.game.set_ai_mode("local")
            elif self.back_btn.is_clicked(mouse_pos, event):
                self.game.current_screen = self.game.start_screen
    
    def update(self):
        # No continuous updates needed for selection screen
        pass
    
    def draw(self, surface):
        # Draw background
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill(WHITE)
        
        # Draw title
        title_surf = self.title_font.render("Select AI Assistant", True, WHITE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4))
        surface.blit(title_surf, title_rect)
        
        # Draw buttons
        self.online_ai_btn.draw(surface)
        self.local_ai_btn.draw(surface)
        self.back_btn.draw(surface)
        
        # Draw description text if a button is hovered
        if self.current_description:
            # Determine which button is hovered to position the text below it
            if self.online_ai_btn.is_hovered:
                y_pos = self.online_ai_btn.rect.bottom + 10
            elif self.local_ai_btn.is_hovered:
                y_pos = self.local_ai_btn.rect.bottom + 10
            else:
                y_pos = SCREEN_HEIGHT//2 + 120  # Fallback position
                
            desc_surf = self.description_font.render(self.current_description, True, WHITE)
            desc_rect = desc_surf.get_rect(center=(SCREEN_WIDTH//2, y_pos))
            surface.blit(desc_surf, desc_rect)


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