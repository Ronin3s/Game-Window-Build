"""
Utility functions for the educational transportation game.
Includes animations, sound helpers, and visual effects.
"""
import pygame
import random
import math
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Initialize pygame mixer
pygame.mixer.init()

# Colors
PASTEL_BLUE = (173, 216, 230)
PASTEL_YELLOW = (255, 253, 208)
PASTEL_GREEN = (198, 236, 198)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
SPARKLE_COLORS = [(255, 255, 100), (255, 200, 100), (255, 255, 255), (255, 215, 0)]

class Particle:
    """Simple particle for visual effects"""
    def __init__(self, x, y, color, vx=0, vy=0, lifetime=60):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = random.randint(3, 7)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3  # gravity
        self.lifetime -= 1
        return self.lifetime > 0
    
    def draw(self, screen):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        size = int(self.size * (self.lifetime / self.max_lifetime))
        if size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)

class SparkleEffect:
    """Sparkle animation for correct matches"""
    def __init__(self, x, y):
        self.particles = []
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            color = random.choice(SPARKLE_COLORS)
            self.particles.append(Particle(x, y, color, vx, vy, random.randint(30, 60)))
    
    def update(self):
        self.particles = [p for p in self.particles if p.update()]
        return len(self.particles) > 0
    
    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)

class ConfettiEffect:
    """Confetti animation for level completion"""
    def __init__(self, screen_width, screen_height):
        self.particles = []
        colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255), 
                  (255, 255, 100), (255, 100, 255), (100, 255, 255)]
        for _ in range(100):
            x = random.randint(0, screen_width)
            y = random.randint(-50, -10)
            vx = random.uniform(-2, 2)
            vy = random.uniform(2, 5)
            color = random.choice(colors)
            self.particles.append(Particle(x, y, color, vx, vy, 120))
    
    def update(self):
        self.particles = [p for p in self.particles if p.update()]
        return len(self.particles) > 0
    
    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)

class ShakeAnimation:
    """Shake animation for incorrect matches"""
    def __init__(self, duration=20):
        self.duration = duration
        self.time = 0
        self.amplitude = 10
    
    def update(self):
        self.time += 1
        return self.time < self.duration
    
    def get_offset(self):
        if self.time >= self.duration:
            return (0, 0)
        progress = self.time / self.duration
        shake = self.amplitude * (1 - progress) * math.sin(self.time * 2)
        return (int(shake), 0)

def load_sound(filename):
    """Load a sound file, return None if not found"""
    try:
        return pygame.mixer.Sound(filename)
    except:
        return None

def play_sound(sound):
    """Play a sound if it exists"""
    if sound:
        sound.play()

# Try to import Arabic support libraries
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False
    print("Arabic support libraries not found. Text will not be reshaped.")

def get_font(size):
    """Get a font that supports Arabic"""
    # Prefer bundled font
    bundled_font = resource_path("assets/fonts/NotoSansArabic-Regular.ttf")
    if os.path.exists(bundled_font):
        try:
            return pygame.font.Font(bundled_font, size)
        except Exception as e:
            print(f"Error loading bundled font '{bundled_font}': {e}")

    # If bundled font fails, try to find system fonts
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
        "arial.ttf"
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                return pygame.font.Font(path, size)
            except:
                continue
                
    # Fallback to default
    print("Warning: No suitable Arabic font found. Using default font.")
    return pygame.font.Font(None, size)

def render_text(text, font, color):
    """Render text with Arabic support"""
    if ARABIC_SUPPORT:
        try:
            reshaped_text = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped_text)
            return font.render(bidi_text, True, color)
        except:
            pass
    return font.render(text, True, color)

def create_button(text, x, y, width, height, color, text_color=WHITE):
    """Create a simple button surface"""
    button = pygame.Surface((width, height))
    button.fill(color)
    pygame.draw.rect(button, WHITE, button.get_rect(), 3)
    
    font = get_font(48)
    text_surf = render_text(text, font, text_color)
    text_rect = text_surf.get_rect(center=(width//2, height//2))
    button.blit(text_surf, text_rect)
    
    return button

def draw_text(screen, text, font_size, x, y, color=WHITE, center=True):
    """Draw text on screen"""
    font = get_font(font_size)
    text_surf = render_text(text, font, color)
    if center:
        text_rect = text_surf.get_rect(center=(x, y))
    else:
        text_rect = text_surf.get_rect(topleft=(x, y))
    screen.blit(text_surf, text_rect)

def create_shadow(image, vehicle_type=None):
    """Create a shadow version of an image, or load from file"""
    # Try to load shadow image from file first if vehicle_type is provided
    if vehicle_type:
        shadow_path = resource_path(f'assets/images/{vehicle_type}_shadow.png')
        if os.path.exists(shadow_path):
            try:
                shadow = pygame.image.load(shadow_path)
                shadow = pygame.transform.scale(shadow, image.get_size())
                return shadow
            except:
                pass

    shadow = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    # Don't fill with background color - keep transparent!
    
    # Create a silhouette by checking alpha
    # Lock surfaces for faster pixel access
    try:
        image.lock()
        shadow.lock()
        for x in range(image.get_width()):
            for y in range(image.get_height()):
                if image.get_at((x, y)).a > 50:  # Threshold for transparency
                    shadow.set_at((x, y), (0, 0, 0, 100))  # Black semi-transparent shadow
        image.unlock()
        shadow.unlock()
    except:
        # Fallback if locking fails
        for x in range(image.get_width()):
            for y in range(image.get_height()):
                if image.get_at((x, y)).a > 50:
                    shadow.set_at((x, y), (0, 0, 0, 100))
    return shadow

def create_vehicle_image(vehicle_type, color, size=(150, 150)):
    """Load vehicle image from file, or create using pygame drawing as fallback"""
    # Try to load from file first
    image_path = resource_path(f'assets/images/{vehicle_type}.png')
    if os.path.exists(image_path):
        try:
            image = pygame.image.load(image_path)
            # Scale to requested size while maintaining aspect ratio
            image = pygame.transform.scale(image, size)
            return image
        except:
            pass  # Fall through to procedural generation
    
    # Fallback: Create procedurally
    surface = pygame.Surface(size, pygame.SRCALPHA)
    
    if vehicle_type == "car":
        # Simple car shape
        pygame.draw.rect(surface, color, (20, 40, 60, 30))
        pygame.draw.rect(surface, color, (30, 25, 40, 20))
        pygame.draw.circle(surface, (40, 40, 40), (35, 70), 10)
        pygame.draw.circle(surface, (40, 40, 40), (65, 70), 10)
    
    elif vehicle_type == "bike":
        # Simple bike shape
        pygame.draw.circle(surface, (40, 40, 40), (30, 60), 15)
        pygame.draw.circle(surface, (40, 40, 40), (70, 60), 15)
        pygame.draw.line(surface, color, (30, 60), (50, 30), 5)
        pygame.draw.line(surface, color, (50, 30), (70, 60), 5)
        pygame.draw.line(surface, color, (30, 60), (70, 60), 3)
    
    elif vehicle_type == "plane":
        # Simple plane shape
        pygame.draw.polygon(surface, color, [(50, 30), (80, 50), (50, 45), (20, 50)])
        pygame.draw.rect(surface, color, (45, 35, 10, 20))
        pygame.draw.polygon(surface, color, [(25, 55), (35, 70), (40, 55)])
    
    elif vehicle_type == "boat":
        # Simple boat shape
        pygame.draw.polygon(surface, color, [(20, 50), (80, 50), (70, 70), (30, 70)])
        pygame.draw.rect(surface, color, (40, 30, 20, 20))
        pygame.draw.polygon(surface, (255, 255, 255), [(45, 30), (45, 10), (55, 20)])
    
    elif vehicle_type == "bus":
        # Simple bus shape
        pygame.draw.rect(surface, color, (15, 30, 70, 40))
        pygame.draw.rect(surface, (200, 230, 255), (20, 35, 15, 15))
        pygame.draw.rect(surface, (200, 230, 255), (40, 35, 15, 15))
        pygame.draw.rect(surface, (200, 230, 255), (60, 35, 15, 15))
        pygame.draw.circle(surface, (40, 40, 40), (30, 70), 8)
        pygame.draw.circle(surface, (40, 40, 40), (70, 70), 8)
    
    elif vehicle_type == "helicopter":
        # Simple helicopter shape
        pygame.draw.ellipse(surface, color, (30, 40, 40, 25))
        pygame.draw.rect(surface, color, (45, 25, 10, 20))
        pygame.draw.line(surface, (100, 100, 100), (20, 30), (80, 30), 3)
        pygame.draw.line(surface, (100, 100, 100), (50, 65), (50, 75), 3)
    
    elif vehicle_type == "train":
        # Simple train shape
        pygame.draw.rect(surface, color, (20, 30, 60, 35))
        pygame.draw.rect(surface, (200, 230, 255), (25, 35, 20, 18))
        pygame.draw.rect(surface, (200, 230, 255), (55, 35, 20, 18))
        pygame.draw.circle(surface, (40, 40, 40), (35, 65), 8)
        pygame.draw.circle(surface, (40, 40, 40), (65, 65), 8)
        pygame.draw.rect(surface, (100, 100, 100), (15, 25, 10, 10))
    
    elif vehicle_type == "ship":
        # Simple ship shape
        pygame.draw.polygon(surface, color, [(15, 55), (85, 55), (75, 70), (25, 70)])
        pygame.draw.rect(surface, color, (35, 35, 30, 20))
        pygame.draw.rect(surface, (255, 100, 100), (40, 25, 20, 12))
        pygame.draw.circle(surface, (255, 230, 150), (70, 40), 5)
    
    return surface

def check_file_exists(filepath):
    """Check if a file exists"""
    return os.path.exists(filepath)
