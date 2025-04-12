import pygame
import os
import time
from game import GameLogic
from utils.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GRAY, LIGHT_GRAY, 
    BLUE, LIGHT_BLUE, GREEN, RED, BG_IMAGE, ASSISTANT_IMAGE, QUESTIONS_PER_LEVEL
)

class GameScreen:
    def __init__(self, game, level, correct_answers, completed_questions, ai_mode="online", teacher_mode="normal"):
        self.game = game
        
        # Init game logic
        self.logic = GameLogic(game.questions, ai_mode, teacher_mode)
        self.logic.set_state(level, correct_answers, completed_questions, ai_mode, teacher_mode)
        
        # Load background image
        if os.path.exists(BG_IMAGE):
            self.bg_image = pygame.image.load(BG_IMAGE)
            self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.bg_image = None
        
        # Load AI assistant image
        if os.path.exists(ASSISTANT_IMAGE):
            self.assistant_image = pygame.image.load(ASSISTANT_IMAGE)
            self.assistant_image = pygame.transform.scale(self.assistant_image, (100, 100))
            self.assistant_rect = self.assistant_image.get_rect(bottomleft=(20, SCREEN_HEIGHT - 20))
        else:
            self.assistant_image = None
            self.assistant_rect = pygame.Rect(20, SCREEN_HEIGHT - 120, 100, 100)
        
        # Set font
        self.question_font = pygame.font.SysFont('Arial', 20)
        self.option_font = pygame.font.SysFont('Arial', 24)
        self.info_font = pygame.font.SysFont('Arial', 20)
        self.hint_font = pygame.font.SysFont('Arial', 18)
        
        # Init game state
        self.current_question = self.logic.get_question()
        self.selected_option = None
        self.correct_option = None
        self.show_result = False
        self.result_time = 0
        
        # Init AI assistant
        self.show_hint = False
        self.hint_text = ""
        self.option_to_remove = None
        self.option_buttons = []
        
        # Create option buttons
        self.create_option_buttons()
        
        # Init animation
        self.animation_active = False
        self.animation_start_time = 0
        self.animation_duration = 1.0  # seconds
        self.animation_type = None
    
    def create_option_buttons(self):
        # Create buttons for each option in the question
        self.option_buttons = []
        
        # Calculate button dimensions and positions
        button_width = 200
        button_height = 40
        button_padding = 20
        start_y = SCREEN_HEIGHT // 2 - 25
        
        # Get all available options.
        available_options = list(self.current_question['Choices'].keys())
        
        # Create a button for each option
        for i, option in enumerate(available_options):
            # Skip option if it's been removed by the AI assistant
            if option == self.option_to_remove:
                continue
                
            if i % 2 == 0:  # Left column
                x = SCREEN_WIDTH // 4 - 40
            else:  # Right column
                x = 2 * SCREEN_WIDTH // 4
            
            y = start_y + (i // 2) * (button_height + button_padding)
            
            text = f"{option}: {self.current_question['Choices'][option]}"
            
            button = {
                "rect": pygame.Rect(x, y + 50, button_width, button_height),
                "text": text,
                "option": option,
                "hovered": False
            }
            self.option_buttons.append(button)
    
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        
        # Don't process events during animations
        if self.animation_active:
            return
        
        # Check if the AI assistant is clicked
        if event.type == pygame.MOUSEBUTTONDOWN and self.assistant_rect.collidepoint(mouse_pos):
            if not self.show_hint and not self.show_result:
                self.get_ai_hint()
        
        # Handle option button hover and clicks
        for button in self.option_buttons:
            button["hovered"] = button["rect"].collidepoint(mouse_pos)
            
            if event.type == pygame.MOUSEBUTTONDOWN and button["rect"].collidepoint(mouse_pos) and not self.show_result:
                self.selected_option = button["option"]
                self.show_result = True
                self.result_time = time.time()
                
                # Check if answer is correct
                is_correct = self.logic.check_answer(self.current_question, self.selected_option)
                self.correct_option = self.current_question["Answer"]
                
                # Start animation
                self.animation_active = True
                self.animation_start_time = time.time()
                self.animation_type = "correct" if is_correct else "incorrect"
                
                # Auto-save game after each answer
                self.game.save_manager.save_game(self.logic.get_game_state())
    
    def get_ai_hint(self):
        # Get hint from AI assistant
        self.show_hint = True
        
        # Get hint from the AI
        hint_response = self.logic.get_ai_hint(self.current_question)
        
        # Parse hint response
        lines = hint_response.strip().split('\n')
        self.hint_text = "No hint available"
        self.option_to_remove = None
        
        for line in lines:
            if line.startswith("Hint:"):
                hint_content = line[5:].strip()
                # Only update hint_text if we got actual content
                if hint_content:
                    self.hint_text = hint_content
                else:
                    self.hint_text = "Think about the context and usage of this word."
            elif line.startswith("Remove option:"):
                self.option_to_remove = line.split(':')[1].strip()
        
        # Recreate option buttons to remove the least correct option
        self.create_option_buttons()
    
    def update(self):
        current_time = time.time()
        
        # Update animation state
        if self.animation_active:
            elapsed = current_time - self.animation_start_time
            if elapsed >= self.animation_duration:
                self.animation_active = False
                self.check_level_progress()
        
        # Move to next question after showing result
        elif self.show_result and current_time - self.result_time > 2.0:
            self.show_result = False
            self.show_hint = False
            self.hint_text = ""
            self.option_to_remove = None
            self.selected_option = None
            self.correct_option = None
            
            # Get new question
            self.current_question = self.logic.get_question()
            self.create_option_buttons()
    
    def check_level_progress(self):
        # Check if player should level up
        level_up = self.logic.should_level_up()
        
        if level_up == "completed":
            # Game completed - show completion screen
            try:
                # Import here to avoid circular imports
                from screens.complete_screen import GameCompleteScreen
                if not hasattr(self.game, 'complete_screen') or self.game.complete_screen is None:
                    self.game.complete_screen = GameCompleteScreen(self.game)
                self.game.current_screen = self.game.complete_screen
            except Exception as e:
                print(f"Error showing completion screen: {e}")
                # Fallback to start screen if there's any error
                self.game.current_screen = self.game.start_screen
        elif level_up:
            # Level up
            self.game.show_level_up(self.logic.current_level)
    
    def draw(self, surface):
        # Draw background
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill(WHITE)
        
        # Draw game info
        level_text = f"Level: {self.logic.current_level}"
        progress_text = f"Progress: {self.logic.correct_answers}/{QUESTIONS_PER_LEVEL}"
        ai_text = f"AI: {'Grok-3' if self.logic.ai_mode == 'online' else 'Local Model'}"
        teacher_text = f"Teacher: {'Normal' if self.logic.teacher_mode == 'normal' else 'Sharpmouse'}"
        
        level_surf = self.info_font.render(level_text, True, BLACK)
        progress_surf = self.info_font.render(progress_text, True, BLACK)
        ai_surf = self.info_font.render(ai_text, True, BLACK)
        teacher_surf = self.info_font.render(teacher_text, True, BLACK)
        
        surface.blit(level_surf, (20, 20))
        surface.blit(progress_surf, (20, 50))
        surface.blit(ai_surf, (20, 80))
        surface.blit(teacher_surf, (20, 110))
        
        # Draw question
        self.draw_question(surface)
        
        # Draw option buttons
        self.draw_option_buttons(surface)
        
        # Draw AI assistant
        self.draw_assistant(surface)
        
        # Draw hint if showing
        if self.show_hint:
            self.draw_hint(surface)
        
        # Draw animation if active
        if self.animation_active:
            self.draw_animation(surface)
    
    def draw_question(self, surface):
        # Draw the question text
        question_text = self.current_question["Question"]
        
        # Split question into multiple lines if needed
        words = question_text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            # Check if current line is too long
            test_line = ' '.join(current_line)
            if self.question_font.size(test_line)[0] > SCREEN_WIDTH - 300:
                # Remove last word and add line
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
        
        # Add final line
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw each line
        y = SCREEN_HEIGHT//2
        for line in lines:
            text_surf = self.question_font.render(line, True, BLACK)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, y - 70))
            surface.blit(text_surf, text_rect)
            y += 40
            
    def draw_option_buttons(self, surface):
        # Draw option buttons
        for button in self.option_buttons:
            # Determine button color based on state
            if self.show_result:
                if button["option"] == self.correct_option:
                    color = GREEN  # Correct answer
                elif button["option"] == self.selected_option:
                    color = RED    # Wrong answer (if selected)
                else:
                    color = LIGHT_GRAY
            else:
                color = LIGHT_BLUE if button["hovered"] else BLUE
            
            # Draw button with rounded corners (border radius of 10)
            pygame.draw.rect(surface, color, button["rect"], border_radius=10)
            pygame.draw.rect(surface, BLACK, button["rect"], 2, border_radius=10)
            
            # Draw text - wrap if necessary with WHITE color
            self.draw_wrapped_text(surface, button["text"], button["rect"], self.option_font, WHITE)
    
    def draw_wrapped_text(self, surface, text, rect, font, color=BLACK):
        # Draw text that wraps within a given rectangle
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            # Check if current line is too long
            test_line = ' '.join(current_line)
            if font.size(test_line)[0] > rect.width - 20:
                # Remove last word and add line
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
        
        # Add final line
        if current_line:
            lines.append(' '.join(current_line))
        
        # Calculate total height of text
        total_height = len(lines) * font.get_height()
        start_y = rect.y + (rect.height - total_height) // 2
        
        # Draw each line
        for i, line in enumerate(lines):
            y = start_y + i * font.get_height()
            text_surf = font.render(line, True, color)
            text_rect = text_surf.get_rect(center=(rect.centerx, y + font.get_height() // 2))
            surface.blit(text_surf, text_rect)
    
    def draw_assistant(self, surface):
        # Draw the AI assistant
        if self.assistant_image:
            surface.blit(self.assistant_image, self.assistant_rect)
        else:
            # Draw a placeholder if image is not available
            pygame.draw.rect(surface, LIGHT_BLUE, self.assistant_rect)
            pygame.draw.rect(surface, BLACK, self.assistant_rect, 2)
            text = self.info_font.render("AI", True, BLACK)
            text_rect = text.get_rect(center=self.assistant_rect.center)
            surface.blit(text, text_rect)
    
    def draw_hint(self, surface):
        # Draw the hint bubble from the AI assistant
        # Draw speech bubble
        bubble_width = 300
        bubble_height = 100
        bubble_x = self.assistant_rect.right + 10
        bubble_y = self.assistant_rect.top - bubble_height // 2 + 50
        
        bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_width, bubble_height)
        
        # Make sure bubble stays on screen
        if bubble_rect.right > SCREEN_WIDTH:
            bubble_rect.right = SCREEN_WIDTH - 10
        if bubble_rect.top < 10:
            bubble_rect.top = 10
        
        # Draw bubble
        pygame.draw.rect(surface, WHITE, bubble_rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, bubble_rect, 2, border_radius=10)
        
        # Draw tail of bubble pointing to assistant
        points = [
            (self.assistant_rect.right, self.assistant_rect.centery),
            (bubble_rect.left + 5, bubble_rect.centery - 10),
            (bubble_rect.left + 5, bubble_rect.centery + 10)
        ]
        pygame.draw.polygon(surface, WHITE, points)
        pygame.draw.polygon(surface, BLACK, points, 2)
        
        # Draw hint text (keep BLACK color for hint text)
        self.draw_wrapped_text(surface, self.hint_text, bubble_rect, self.hint_font, BLACK)
    
    def draw_animation(self, surface):
        # Draw answer animation effects
        elapsed = time.time() - self.animation_start_time
        progress = min(elapsed / self.animation_duration, 1.0)
        
        if self.animation_type == "correct":
            # Green flash effect for correct answer
            alpha = int(255 * (1.0 - progress))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 255, 0, alpha))
            surface.blit(overlay, (0, 0))
            
            # Draw congratulatory text
            if progress < 0.8:
                size = int(30 + 20 * progress)
                font = pygame.font.SysFont('Arial', size)
                text = font.render("Correct!", True, BLACK)
                text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
                surface.blit(text, text_rect)
                
        else:  # incorrect
            # Red flash effect for wrong answer
            alpha = int(255 * (1.0 - progress))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 0, 0, alpha))
            surface.blit(overlay, (0, 0))
            
            # Draw feedback text
            if progress < 0.8:
                size = int(30 + 20 * progress)
                font = pygame.font.SysFont('Arial', size)
                text = font.render("Oops!", True, BLACK)
                text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
                surface.blit(text, text_rect)