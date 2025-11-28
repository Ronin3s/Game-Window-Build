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

def load_arabic_image(image_name, default_size=None):
    """Load an Arabic UI image from assets/arabic-image folder
    
    Args:
        image_name: Name of the image file (e.g., 'Start-game.png')
        default_size: Optional tuple (width, height) to scale the image
    
    Returns:
        Scaled pygame Surface or None if image not found
    """
    try:
        image_path = resource_path(f'assets/arabic-image/{image_name}')
        image = pygame.image.load(image_path)
        if default_size:
            image = pygame.transform.scale(image, default_size)
        return image
    except:
        print(f"Warning: Arabic image '{image_name}' not found")
        return None

def play_sound(sound):
    """Play a sound if it exists"""
    if sound:
        sound.play()



def get_font(size):
    """Get a font, trying bundled, then system, then default."""
    # Helper to test font
    def test_font(f):
        try:
            f.render("test", True, (255, 255, 255))
            return True
        except Exception:
            return False

    # 1. Try bundled font
    try:
        bundled_font_path = resource_path("assets/fonts/DejaVuSans.ttf")
        if os.path.exists(bundled_font_path):
            font = pygame.font.Font(bundled_font_path, size)
            if test_font(font):
                return font
    except Exception as e:
        print(f"Could not load bundled font: {e}")

    # 2. Try common system fonts
    font_paths = [
        # Linux
        "/usr/share/fonts/X11/TTF/luxisr.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
        # Windows
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/cour.ttf",
        # MacOS
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                font = pygame.font.Font(path, size)
                if test_font(font):
                    return font
            except Exception:
                continue
    
    # 3. Try pygame's default font
    try:
        font = pygame.font.Font(None, size)
        if test_font(font):
            return font
    except Exception as e:
        print(f"Could not load pygame's default font: {e}")

    # 4. If all else fails, raise an error
    raise RuntimeError("Could not load any font.")

def render_text(text, font, color):
    """Render text."""
    return font.render(text, True, color)

def create_button(text, x, y, width, height, color, text_color=WHITE, font_size=48):
    """Create a simple button surface"""
    button = pygame.Surface((width, height))
    button.fill(color)
    pygame.draw.rect(button, WHITE, button.get_rect(), 3)
    
    font = get_font(font_size)
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

    # Create silhouette using mask (cleaner and faster than pixel iteration)
    try:
        mask = pygame.mask.from_surface(image)
        # Create a surface from the mask, setting set bits to black with alpha
        shadow = mask.to_surface(setcolor=(0, 0, 0, 100), unsetcolor=(0, 0, 0, 0))
        return shadow
    except:
        # Fallback if mask fails
        return pygame.Surface(image.get_size(), pygame.SRCALPHA)

def create_vehicle_image(vtype, color, size):
    """Create a simple vehicle image surface with transparent background"""
    surface = pygame.Surface(size, pygame.SRCALPHA)
    # No fill needed, or fill with (0,0,0,0) which is default for SRCALPHA
    
    width, height = size
    
    # Draw based on type
    if vtype == "car":
        # Car body
        pygame.draw.rect(surface, color, (width*0.1, height*0.4, width*0.8, height*0.4), border_radius=10)
        # Roof
        pygame.draw.rect(surface, color, (width*0.2, height*0.2, width*0.6, height*0.3), border_radius=5)
        # Wheels
        pygame.draw.circle(surface, (50, 50, 50), (int(width*0.25), int(height*0.8)), int(width*0.12))
        pygame.draw.circle(surface, (50, 50, 50), (int(width*0.75), int(height*0.8)), int(width*0.12))
        
    elif vtype == "bus":
        # Bus body
        pygame.draw.rect(surface, color, (width*0.1, height*0.2, width*0.8, height*0.6), border_radius=5)
        # Windows
        for i in range(3):
            pygame.draw.rect(surface, (200, 240, 255), (width*(0.15 + i*0.25), height*0.3, width*0.2, height*0.2))
        # Wheels
        pygame.draw.circle(surface, (50, 50, 50), (int(width*0.25), int(height*0.8)), int(width*0.12))
        pygame.draw.circle(surface, (50, 50, 50), (int(width*0.75), int(height*0.8)), int(width*0.12))
        
    elif vtype == "truck":
        # Cab
        pygame.draw.rect(surface, color, (width*0.7, height*0.4, width*0.2, height*0.4), border_radius=5)
        # Trailer
        pygame.draw.rect(surface, (max(0, color[0]-50), max(0, color[1]-50), max(0, color[2]-50)), 
                         (width*0.1, height*0.2, width*0.55, height*0.6))
        # Wheels
        pygame.draw.circle(surface, (50, 50, 50), (int(width*0.2), int(height*0.8)), int(width*0.12))
        pygame.draw.circle(surface, (50, 50, 50), (int(width*0.5), int(height*0.8)), int(width*0.12))
        pygame.draw.circle(surface, (50, 50, 50), (int(width*0.8), int(height*0.8)), int(width*0.12))
        
    elif vtype == "bike":
        # Frame
        pygame.draw.line(surface, color, (width*0.25, height*0.6), (width*0.5, height*0.6), 5)
        pygame.draw.line(surface, color, (width*0.5, height*0.6), (width*0.75, height*0.4), 5)
        pygame.draw.line(surface, color, (width*0.25, height*0.6), (width*0.4, height*0.3), 5)
        # Wheels
        pygame.draw.circle(surface, (50, 50, 50), (int(width*0.25), int(height*0.6)), int(width*0.15), 5)
        pygame.draw.circle(surface, (50, 50, 50), (int(width*0.75), int(height*0.6)), int(width*0.15), 5)
        
    elif vtype == "plane":
        # Fuselage
        pygame.draw.ellipse(surface, color, (width*0.1, height*0.35, width*0.8, height*0.3))
        # Wings
        pygame.draw.polygon(surface, (max(0, color[0]-30), max(0, color[1]-30), max(0, color[2]-30)), 
                           [(width*0.4, height*0.45), (width*0.5, height*0.1), (width*0.6, height*0.45)])
        # Tail
        pygame.draw.polygon(surface, (max(0, color[0]-30), max(0, color[1]-30), max(0, color[2]-30)), 
                           [(width*0.1, height*0.45), (width*0.1, height*0.2), (width*0.2, height*0.45)])
                           
    elif vtype == "helicopter":
        # Cockpit
        pygame.draw.ellipse(surface, color, (width*0.2, height*0.3, width*0.5, height*0.4))
        # Tail
        pygame.draw.rect(surface, color, (width*0.6, height*0.45, width*0.3, height*0.1))
        # Rotors
        pygame.draw.line(surface, (50, 50, 50), (width*0.45, height*0.3), (width*0.45, height*0.1), 3)
        pygame.draw.line(surface, (200, 200, 200), (width*0.1, height*0.1), (width*0.8, height*0.1), 5)
        
    elif vtype == "boat":
        # Hull
        pygame.draw.polygon(surface, color, 
                           [(width*0.1, height*0.4), (width*0.9, height*0.4), 
                            (width*0.7, height*0.8), (width*0.3, height*0.8)])
        # Cabin
        pygame.draw.rect(surface, (255, 255, 255), (width*0.3, height*0.2, width*0.4, height*0.2))
        # Mast/Flag
        pygame.draw.line(surface, (100, 50, 0), (width*0.5, height*0.2), (width*0.5, height*0.05), 3)
        
    elif vtype == "ship":
        # Hull
        pygame.draw.polygon(surface, color, 
                           [(width*0.05, height*0.4), (width*0.95, height*0.4), 
                            (width*0.8, height*0.8), (width*0.2, height*0.8)])
        # Decks
        pygame.draw.rect(surface, (240, 240, 240), (width*0.2, height*0.25, width*0.6, height*0.15))
        pygame.draw.rect(surface, (240, 240, 240), (width*0.3, height*0.15, width*0.4, height*0.1))
        # Smokestacks
        pygame.draw.rect(surface, (50, 50, 50), (width*0.4, height*0.05, width*0.08, height*0.1))
        pygame.draw.rect(surface, (50, 50, 50), (width*0.55, height*0.05, width*0.08, height*0.1))
        
    elif vtype == "train":
        # Engine body
        pygame.draw.rect(surface, color, (width*0.1, height*0.3, width*0.6, height*0.4))
        # Cab
        pygame.draw.rect(surface, (max(0, color[0]-40), max(0, color[1]-40), max(0, color[2]-40)), 
                        (width*0.7, height*0.2, width*0.2, height*0.5))
        # Chimney
        pygame.draw.rect(surface, (50, 50, 50), (width*0.2, height*0.1, width*0.1, height*0.2))
        # Wheels
        pygame.draw.circle(surface, (50, 50, 50), (int(width*0.25), int(height*0.8)), int(width*0.12))
        pygame.draw.circle(surface, (50, 50, 50), (int(width*0.5), int(height*0.8)), int(width*0.12))
        pygame.draw.circle(surface, (50, 50, 50), (int(width*0.8), int(height*0.8)), int(width*0.12))
        
    else:
        # Default box fallback
        pygame.draw.rect(surface, color, (width*0.1, height*0.1, width*0.8, height*0.8), border_radius=10)
        
    return surface
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
