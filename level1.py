"""
Level 1: Shadow Matching Game
Players drag transportation images to match their shadows
"""
import pygame
import random
from utils import SparkleEffect, ShakeAnimation, create_shadow, create_vehicle_image, draw_text, resource_path, load_sound, create_button

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
        
        # Load background - Solid pastel color as requested
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
        
        # Load specific level complete sound and images
        self.level_complete_sound = load_sound(resource_path('assets/sounds/level1_complete.wav'))
        
        # Success Screen Elements (Arabic Images)
        from utils import load_arabic_image
        
        self.next_button = load_arabic_image('go-to-the-next-level.png', (250, 80))
        if not self.next_button:
            self.next_button = create_button("Next Level", 0, 0, 200, 80, (50, 200, 50), font_size=30)
        self.next_button_rect = pygame.Rect((self.width - 250) // 2, self.height // 2 + 150, 250, 80)

        self.restart_button = load_arabic_image('try-agin.png', (200, 80))
        if not self.restart_button:
            self.restart_button = create_button("Restart", 0, 0, 200, 80, (200, 50, 50), font_size=30)
        self.restart_button_rect = pygame.Rect((self.width - 200) // 2, self.height // 2 + 250, 200, 80)

        # Randomize order of vehicle types for initial display
        # random.shuffle(vehicle_types) # Keep fixed order for alignment as requested
        
        # Calculate positions for images and shadows
        num_vehicles = len(vehicle_types)
        
        # Adjust size to fit all 8 in one column
        # Window is 1280x800.
        # 90px was too big (overflowed).
        # 80px * 8 = 640. + 8px * 7 = 56. Total = 696.
        # 800 - 696 = 104px slack. Perfect.
        display_size = 80
        
        # Define column parameters
        column_gap = 450 # Wider gap for wider screen
        
        # Calculate the starting X position for the left column
        total_cols_width = (display_size * 2) + column_gap
        start_x_left_column = (self.width - total_cols_width) // 2
        start_x_right_column = start_x_left_column + display_size + column_gap
        
        # Vertical spacing
        vertical_spacing = 8
        
        # Calculate start y for vertical centering
        # Ensure it starts below the title (y=50)
        total_column_height = (num_vehicles * display_size) + ((num_vehicles - 1) * vertical_spacing)
        start_y = max(80, (self.height - total_column_height) // 2)
        
        # Create indices for left (vehicles) and right (shadows) columns
        # Shuffle left column to add randomness as requested
        left_indices = list(range(num_vehicles))
        random.shuffle(left_indices)
        
        # Keep right column fixed (or shuffle independently if desired, but fixed is good for stability)
        right_indices = list(range(num_vehicles))
        
        # Create Vehicles (Left Column)
        for row, v_idx in enumerate(left_indices):
            vtype, color = vehicle_types[v_idx]
            
            # Create at default size then scale
            raw_img = create_vehicle_image(vtype, color, (120, 120))
            vehicle_img = pygame.transform.scale(raw_img, (display_size, display_size))
            
            x_main = start_x_left_column
            y_main = start_y + row * (display_size + vertical_spacing)
            
            # Pass v_idx as the ID so it matches the shadow with the same v_idx
            vehicle = DraggableVehicle(vehicle_img, x_main, y_main, v_idx)
            self.vehicles.append(vehicle)
            
        # Create Shadows (Right Column)
        for row, s_idx in enumerate(right_indices):
            vtype, color = vehicle_types[s_idx]
            
            # Create shadow from the vehicle image
            raw_img = create_vehicle_image(vtype, color, (120, 120))
            vehicle_img = pygame.transform.scale(raw_img, (display_size, display_size))
            shadow_img = create_shadow(vehicle_img, vtype)
            
            x_shadow = start_x_right_column
            y_shadow = start_y + row * (display_size + vertical_spacing)
            
            # Pass s_idx as the ID
            shadow = ShadowSlot(shadow_img, x_shadow, y_shadow, s_idx)
            self.shadows.append(shadow)
        
        self.dragging_vehicle = None
        self.matches_found = 0
        self.total_matches = len(self.vehicles)
        self.completed = False
        self.completion_timer = 0
        
    def handle_event(self, event):
        """Handle mouse events for dragging"""
        if self.completed:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.next_button_rect.collidepoint(event.pos):
                    return True
                elif self.restart_button_rect.collidepoint(event.pos):
                    return "restart"
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
        # Check completion
        if self.matches_found >= self.total_matches and not self.completed:
            self.completed = True
            self.completion_timer = pygame.time.get_ticks()
            if self.level_complete_sound:
                self.level_complete_sound.play()
        
        # Return True when ready to move to next level
        # if self.completed and pygame.time.get_ticks() - self.completion_timer > 2000:
        #     return True
        
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
        # Draw completion message
        if self.completed:
            # Draw semi-transparent overlay
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            
            # Load and display Level 1 Complete Arabic image
            from utils import load_arabic_image
            level_complete_img = load_arabic_image('level-1-complet.png', (600, 100))
            
            if level_complete_img:
                img_rect = level_complete_img.get_rect(center=(self.width // 2, self.height // 2 - 50))
                self.screen.blit(level_complete_img, img_rect)
            else:
                # Fallback to English text
                draw_text(self.screen, "Level 1 Complete!", 60, self.width // 2, self.height // 2 - 50, (50, 200, 50))
                draw_text(self.screen, "Great Job!", 40, self.width // 2, self.height // 2 + 20, (255, 215, 0))
            
            self.screen.blit(self.next_button, self.next_button_rect)
            self.screen.blit(self.restart_button, self.restart_button_rect)
