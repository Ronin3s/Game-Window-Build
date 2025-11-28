"""
Level 1: Shadow Matching Game
Players drag transportation images to match their shadows
"""
import pygame
import random
from utils import SparkleEffect, ShakeAnimation, create_shadow, create_vehicle_image, draw_text, resource_path

class DraggableVehicle:
    """A vehicle that can be dragged"""
    def __init__(self, image, x, y, vehicle_id):
        self.original_image = image
        self.image = image
        self.rect = image.get_rect(topleft=(x, y))
        self.original_pos = (x, y)
        self.dragging = False
        self.matched = False
        self.vehicle_id = vehicle_id
        self.shake = None
    
    def start_drag(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos) and not self.matched:
            self.dragging = True
            return True
        return False
    
    def drag(self, mouse_pos):
        if self.dragging:
            self.rect.center = mouse_pos
    
    def stop_drag(self):
        self.dragging = False
    
    def return_to_start(self):
        self.rect.topleft = self.original_pos
        self.shake = ShakeAnimation(20)
    
    def update(self):
        if self.shake and self.shake.update():
            return True
        self.shake = None
        return False
    
    def draw(self, screen):
        pos = self.rect.topleft
        if self.shake:
            offset = self.shake.get_offset()
            pos = (pos[0] + offset[0], pos[1] + offset[1])
        
        if not self.matched:
            screen.blit(self.image, pos)

class ShadowSlot:
    """A shadow slot where vehicles can be matched"""
    def __init__(self, shadow_image, x, y, vehicle_id):
        self.shadow = shadow_image
        self.rect = shadow_image.get_rect(topleft=(x, y))
        self.vehicle_id = vehicle_id
        self.matched = False
        self.highlight = False
    
    def check_match(self, vehicle):
        """Check if vehicle matches this shadow"""
        return self.vehicle_id == vehicle.vehicle_id
    
    def draw(self, screen):
        if not self.matched:
            # Draw highlight if hovering
            if self.highlight:
                pygame.draw.rect(screen, (255, 255, 100), self.rect.inflate(10, 10), 3)
            screen.blit(self.shadow, self.rect.topleft)

class Level1:
    def __init__(self, screen, success_sound=None, error_sound=None, complete_sound=None):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.success_sound = success_sound
        self.error_sound = error_sound
        self.complete_sound = complete_sound
        
        # Load background
        try:
            self.background = pygame.image.load(resource_path('assets/images/level1_bg.png'))
            self.background = pygame.transform.scale(self.background, (self.width, self.height))
        except:
            self.background = pygame.Surface((self.width, self.height))
            self.background.fill((173, 216, 230))  # Pastel blue
        
        # Vehicle definitions
        vehicle_types = [
            ("car", (255, 100, 100)),
            ("bike", (100, 150, 255)),
            ("plane", (255, 200, 100)),
            ("boat", (100, 255, 150)),
            ("bus", (255, 150, 200)),
            ("helicopter", (200, 100, 255)),
            ("train", (150, 255, 100)),
            ("ship", (100, 200, 200))
        ]
        
        # Create vehicles and shadows
        self.vehicles = []
        self.shadows = []
        self.sparkles = []
        
        # Randomize positions
        random.shuffle(vehicle_types)
        
        # Create 8 vehicles in two rows
        for i, (vtype, color) in enumerate(vehicle_types):
            # Create vehicle image (larger)
            vehicle_img = create_vehicle_image(vtype, color, (120, 120))
            
            # Position vehicles on left side (adjusted for 1024x768)
            row = i // 4
            col = i % 4
            x = 50 + col * 110  # Reduced spacing to fit
            y = 200 + row * 200
            vehicle = DraggableVehicle(vehicle_img, x, y, i)
            self.vehicles.append(vehicle)
            
            # Create shadow and position on right side
            shadow_img = create_shadow(vehicle_img, vtype)
            shadow_x = 550 + col * 110  # Reduced spacing to fit
            shadow_y = 200 + row * 200
            shadow = ShadowSlot(shadow_img, shadow_x, shadow_y, i)
            self.shadows.append(shadow)
        
        # Shuffle shadow positions
        shadow_positions = [(s.rect.x, s.rect.y) for s in self.shadows]
        random.shuffle(shadow_positions)
        for shadow, pos in zip(self.shadows, shadow_positions):
            shadow.rect.topleft = pos
        
        self.dragging_vehicle = None
        self.matches_found = 0
        self.total_matches = len(self.vehicles)
        self.completed = False
        self.completion_timer = 0
        
    def handle_event(self, event):
        """Handle mouse events for dragging"""
        if self.completed:
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            for vehicle in self.vehicles:
                if vehicle.start_drag(event.pos):
                    self.dragging_vehicle = vehicle
                    break
        
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_vehicle:
                self.dragging_vehicle.drag(event.pos)
                
                # Check hover over shadows
                for shadow in self.shadows:
                    shadow.highlight = shadow.rect.collidepoint(event.pos) and not shadow.matched
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging_vehicle:
                # Check if dropped on correct shadow
                matched = False
                for shadow in self.shadows:
                    if shadow.rect.colliderect(self.dragging_vehicle.rect) and not shadow.matched:
                        if shadow.check_match(self.dragging_vehicle):
                            # Correct match!
                            self.dragging_vehicle.matched = True
                            shadow.matched = True
                            self.matches_found += 1
                            
                            # Play success sound
                            if self.success_sound:
                                self.success_sound.play()
                            
                            # Create sparkle effect
                            sparkle = SparkleEffect(shadow.rect.centerx, shadow.rect.centery)
                            self.sparkles.append(sparkle)
                            
                            matched = True
                            break
                
                if not matched and self.dragging_vehicle.dragging:
                    # Wrong match - return to start with shake
                    self.dragging_vehicle.return_to_start()
                    if self.error_sound:
                        self.error_sound.play()
                
                self.dragging_vehicle.stop_drag()
                self.dragging_vehicle = None
        
        return False
    
    def update(self):
        """Update animations and check completion"""
        # Update vehicle animations
        for vehicle in self.vehicles:
            vehicle.update()
        
        # Update sparkles
        self.sparkles = [s for s in self.sparkles if s.update()]
        
        # Check completion
        if self.matches_found >= self.total_matches and not self.completed:
            self.completed = True
            self.completion_timer = pygame.time.get_ticks()
            if self.complete_sound:
                self.complete_sound.play()
        
        # Return True when ready to move to next level
        if self.completed and pygame.time.get_ticks() - self.completion_timer > 2000:
            return True
        
        return False
    
    def draw(self):
        """Draw the level"""
        self.screen.blit(self.background, (0, 0))
        
        # Draw title
        draw_text(self.screen, "Match Vehicles with their Shadows", 36, self.width // 2, 50, (80, 80, 80))
        
        # Draw shadows
        for shadow in self.shadows:
            shadow.draw(self.screen)
        
        # Draw vehicles
        for vehicle in self.vehicles:
            vehicle.draw(self.screen)
        
        # Draw sparkles
        for sparkle in self.sparkles:
            sparkle.draw(self.screen)
        
        # Draw completion message
        if self.completed:
            draw_text(self.screen, "Well Done!", 72, self.width // 2, self.height // 2, (255, 215, 0))
            # Draw stars
            for i in range(5):
                x = self.width // 2 - 100 + i * 50
                y = self.height // 2 + 60
                pygame.draw.polygon(self.screen, (255, 215, 0), [
                    (x, y - 15), (x + 5, y), (x + 20, y), (x + 8, y + 10),
                    (x + 12, y + 25), (x, y + 15), (x - 12, y + 25),
                    (x - 8, y + 10), (x - 20, y), (x - 5, y)
                ])
