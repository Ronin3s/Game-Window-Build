import pygame
from utils import draw_text, create_button, resource_path

class Dashboard:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        # Load background - Solid pastel color as requested
        self.background = pygame.Surface((self.width, self.height))
        self.background.fill((50, 50, 100)) # Dark blue/purple for dashboard
            
        # Load Checkmark
        try:
            self.check_mark = pygame.image.load(resource_path('assets/images/check_mark.png'))
            self.check_mark = pygame.transform.scale(self.check_mark, (60, 60))
        except:
            self.check_mark = None

        # Start Game Button (Arabic Image)
        from utils import load_arabic_image
        self.start_button = load_arabic_image('Start-game.png', (300, 100))
        if not self.start_button:
            # Fallback to English button if image not found
            self.start_button = create_button("Start Game", 0, 0, 300, 100, (50, 200, 50), font_size=40)
        self.start_button_rect = pygame.Rect((self.width - 300) // 2, self.height - 150, 300, 100)
        
    def handle_event(self, event):
        """Handle events, return 'start' if start button clicked"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_button_rect.collidepoint(event.pos):
                return "start"
        return None
        
    def draw_status_panel(self, x, y, level_num, completed):
        """Draw a status panel for a level"""
        # Panel background
        rect = pygame.Rect(x, y, 250, 300)
        pygame.draw.rect(self.screen, (255, 255, 255, 200), rect, border_radius=15)
        pygame.draw.rect(self.screen, (100, 100, 100), rect, 3, border_radius=15)
        
        # Level Title (English Text)
        draw_text(self.screen, f"Level {level_num}", 40, x + 125, y + 50, (50, 50, 50))
        
        # Status Icon
        center_x = x + 125
        center_y = y + 150
        radius = 60
        
        if completed:
            # Green circle
            pygame.draw.circle(self.screen, (50, 200, 50), (center_x, center_y), radius)
            # Draw Checkmark PNG
            if self.check_mark:
                check_rect = self.check_mark.get_rect(center=(center_x, center_y))
                self.screen.blit(self.check_mark, check_rect)
            else:
                draw_text(self.screen, "Done", 30, center_x, center_y, (255, 255, 255))
            
            draw_text(self.screen, "Completed", 30, center_x, y + 250, (50, 200, 50))
        else:
            # Grey circle
            pygame.draw.circle(self.screen, (200, 200, 200), (center_x, center_y), radius)
            # Lock icon or just empty
            pygame.draw.rect(self.screen, (150, 150, 150), (center_x - 20, center_y - 20, 40, 40))
            pygame.draw.circle(self.screen, (150, 150, 150), (center_x, center_y - 30), 20, 5)
            
            draw_text(self.screen, "Not Yet", 30, center_x, y + 250, (150, 150, 150))

    def draw(self, level_status):
        """Draw the dashboard with current status"""
        self.screen.blit(self.background, (0, 0))
        
        # Title
        draw_text(self.screen, "Progress Dashboard", 60, self.width // 2, 80, (255, 255, 255))
        
        # Draw panels
        start_x = (self.width - (3 * 250 + 2 * 50)) // 2
        y = 150
        
        self.draw_status_panel(start_x, y, 1, level_status.get(1, False))
        self.draw_status_panel(start_x + 300, y, 2, level_status.get(2, False))
        self.draw_status_panel(start_x + 600, y, 3, level_status.get(3, False))
        
        # Draw Start Button
        self.screen.blit(self.start_button, self.start_button_rect)
