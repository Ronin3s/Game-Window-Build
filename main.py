"""
Main Game File - Educational Transportation Game
Entry point and game state management
"""
import pygame
import sys
from start_screen import StartScreen
from level1 import Level1
from level2 import Level2
from level3 import Level3
from utils import load_sound, resource_path

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Game states
STATE_START = "start"
STATE_LEVEL1 = "level1"
STATE_LEVEL2 = "level2"
STATE_LEVEL3 = "level3"
STATE_COMPLETE = "complete"

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Transportation Adventure")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = STATE_START
        
        # Load sounds
        self.success_sound = load_sound(resource_path('assets/sounds/success.wav'))
        self.error_sound = load_sound(resource_path('assets/sounds/error.wav'))
        self.complete_sound = load_sound(resource_path('assets/sounds/level_complete.wav'))
        
        # Load and play background music
        try:
            pygame.mixer.music.load(resource_path('assets/music/background.wav'))
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)  # Loop indefinitely
        except:
            print("Background music not found, continuing without music")
        
        # Initialize screens/levels
        self.start_screen = StartScreen(self.screen)
        self.current_level = None
        
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            
            # Pass events to current screen/level
            if self.state == STATE_START:
                if self.start_screen.handle_event(event):
                    # Start button clicked
                    self.state = STATE_LEVEL1
                    self.current_level = Level1(self.screen, self.success_sound, 
                                               self.error_sound, self.complete_sound)
            
            elif self.current_level:
                self.current_level.handle_event(event)
    
    def update(self):
        """Update game logic"""
        if self.current_level:
            # Check if level is complete
            if self.current_level.update():
                # Move to next level
                if self.state == STATE_LEVEL1:
                    self.state = STATE_LEVEL2
                    self.current_level = Level2(self.screen, self.success_sound,
                                               self.error_sound, self.complete_sound)
                elif self.state == STATE_LEVEL2:
                    self.state = STATE_LEVEL3
                    self.current_level = Level3(self.screen, self.success_sound,
                                               self.error_sound, self.complete_sound)
                elif self.state == STATE_LEVEL3:
                    self.state = STATE_COMPLETE
                    self.current_level = None
    
    def draw(self):
        """Draw current screen"""
        if self.state == STATE_START:
            self.start_screen.draw()
        elif self.current_level:
            self.current_level.draw()
        elif self.state == STATE_COMPLETE:
            # Game complete screen (Level 3 already shows this)
            pass
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
