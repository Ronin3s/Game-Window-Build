"""
Start Screen for the Transportation Game
Displays background and Start Game button
"""
import pygame
from utils import draw_text, create_button, resource_path

class StartScreen:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        # Load background
        try:
            self.background = pygame.image.load(resource_path('assets/images/start_background.png'))
            self.background = pygame.transform.scale(self.background, (self.width, self.height))
        except:
            # Fallback: create a colorful gradient background
            self.background = pygame.Surface((self.width, self.height))
            for i in range(self.height):
                color_value = int(150 + (i / self.height) * 105)
                pygame.draw.line(self.background, (100, color_value, 255), (0, i), (self.width, i))
        
        # Create start button
        self.button_width = 300
        self.button_height = 100
        self.button_x = (self.width - self.button_width) // 2
        self.button_y = (self.height - self.button_height) // 2 + 50
        self.button = create_button("Start Game", 0, 0, self.button_width, self.button_height, (50, 200, 50), font_size=40)
        self.button_rect = pygame.Rect(self.button_x, self.button_y, self.button_width, self.button_height)
        
        # Create Dashboard button
        self.dash_button_y = self.button_y + 120
        self.dash_button = create_button("Dashboard", 0, 0, self.button_width, self.button_height, (50, 150, 200), font_size=40)
        self.dash_button_rect = pygame.Rect(self.button_x, self.dash_button_y, self.button_width, self.button_height)
        
        # Hover effect
        self.button_hover = False
        self.dash_button_hover = False
    
    def handle_event(self, event):
        """Handle mouse events, return 'start', 'dashboard', or None"""
        if event.type == pygame.MOUSEMOTION:
            self.button_hover = self.button_rect.collidepoint(event.pos)
            self.dash_button_hover = self.dash_button_rect.collidepoint(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                return "start"
            elif self.dash_button_rect.collidepoint(event.pos):
                return "dashboard"
        
        return None
    
    def draw(self):
        """Draw the start screen"""
        self.screen.blit(self.background, (0, 0))
        
        # Draw title
        draw_text(self.screen, "Transport Adventure", 72, self.width // 2, 150, (255, 255, 255))
        draw_text(self.screen, "Match, Learn, and Play!", 36, self.width // 2, 220, (255, 255, 150))
        
        # Draw button with hover effect
        if self.button_hover:
            # Scale up slightly when hovering
            scaled = pygame.transform.scale(self.button, (self.button_width + 10, self.button_height + 10))
            pos = (self.button_x - 5, self.button_y - 5)
        else:
            scaled = self.button
            pos = (self.button_x, self.button_y)
        
        self.screen.blit(scaled, pos)
        
        # Draw Dashboard button
        if self.dash_button_hover:
            scaled_dash = pygame.transform.scale(self.dash_button, (self.button_width + 10, self.button_height + 10))
            pos_dash = (self.button_x - 5, self.dash_button_y - 5)
        else:
            scaled_dash = self.dash_button
            pos_dash = (self.button_x, self.dash_button_y)
            
        self.screen.blit(scaled_dash, pos_dash)
