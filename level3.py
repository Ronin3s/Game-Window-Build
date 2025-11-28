"""
Level 3: Complete the Transportation Image
Players match vehicle halves to complete the images
"""
import pygame
import random
from utils import SparkleEffect, ShakeAnimation, ConfettiEffect, create_vehicle_image, draw_text, resource_path, load_sound, create_button

class VehicleHalf:
    """Half of a vehicle image that can be dragged"""
    def __init__(self, image, x, y, vehicle_id, is_left):
        self.image = image
        self.rect = image.get_rect(topleft=(x, y))
        self.original_pos = (x, y)
        self.vehicle_id = vehicle_id
        self.is_left = is_left
        self.dragging = False
        self.matched = False
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

class PuzzleSlot:
    """A slot where the matching half should be placed"""
    def __init__(self, fixed_half, x, y, vehicle_id):
        self.fixed_half = fixed_half
        self.rect = fixed_half.get_rect(topleft=(x, y))
        self.vehicle_id = vehicle_id
        self.matched = False
        self.highlight = False
        self.matching_half = None
    
    def check_match(self, half):
        """Check if the half matches this slot"""
        return half.vehicle_id == self.vehicle_id
    
    def draw(self, screen):
        # Draw the fixed half
        screen.blit(self.fixed_half, self.rect.topleft)
        
        # Draw highlight if hovering
        if self.highlight and not self.matched:
            pygame.draw.rect(screen, (255, 255, 100), self.rect.inflate(10, 10), 3)
        
        # Draw matched half
        if self.matched and self.matching_half:
            # Position right next to the fixed half
            match_pos = (self.rect.right, self.rect.top)
            screen.blit(self.matching_half, match_pos)

class Level3:
    def __init__(self, screen, success_sound=None, error_sound=None, complete_sound=None):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.success_sound = success_sound
        self.error_sound = error_sound
        self.complete_sound = complete_sound
        
        # Load background - Solid pastel color as requested
        self.background = pygame.Surface((self.width, self.height))
        self.background.fill((198, 236, 198))  # Pastel green
        
        # Vehicle data
        vehicle_data = [
            ("car", (255, 100, 100)),
            ("bike", (100, 150, 255)),
            ("plane", (255, 200, 100)),
            ("boat", (100, 255, 150)),
            ("bus", (255, 150, 200)),
            ("helicopter", (200, 100, 255)),
            ("train", (150, 255, 100)),
            ("ship", (100, 200, 200))
        ]
        
        self.puzzle_slots = []
        self.draggable_halves = []
        
        # Increase size for kids view (was 150, now 200)
        full_size = 200
        half_width = full_size // 2
        
        # Create split vehicles
        for i, (vtype, color) in enumerate(vehicle_data):
            # Create full vehicle (larger size)
            full_vehicle = create_vehicle_image(vtype, color, (full_size, full_size))
            
            # Split into halves
            left_half = pygame.Surface((half_width, full_size), pygame.SRCALPHA)
            right_half = pygame.Surface((half_width, full_size), pygame.SRCALPHA)
            
            left_half.blit(full_vehicle, (0, 0), (0, 0, half_width, full_size))
            right_half.blit(full_vehicle, (0, 0), (half_width, 0, half_width, full_size))
            
            # Position slots on left side (adjusted for 1280x800)
            # 8 items total. Use 4 rows x 2 columns
            row = i // 2
            col = i % 2
            # Increase spacing for 200px height
            slot_x = 100 + col * 280
            slot_y = 50 + row * 190 # 4 rows: 50, 240, 430, 620
            
            # Create puzzle slot with left half (fixed)
            slot = PuzzleSlot(left_half, slot_x, slot_y, i)
            self.puzzle_slots.append(slot)
            
            # Create draggable right half on right side
            # Mirror the left side layout
            d_row = i // 2
            d_col = i % 2
            half_x = 800 + d_col * 280
            half_y = 50 + d_row * 190
            
            draggable = VehicleHalf(right_half, half_x, half_y, i, False)
            self.draggable_halves.append(draggable)
        
        # Shuffle draggable halves positions
        positions = [(h.rect.x, h.rect.y) for h in self.draggable_halves]
        random.shuffle(positions)
        for half, pos in zip(self.draggable_halves, positions):
            half.rect.topleft = pos
            half.original_pos = pos
        
        self.dragging_half = None
        self.sparkles = []
        self.matches_found = 0
        self.total_matches = len(self.puzzle_slots)
        self.completed = False
        self.completion_timer = 0
        self.completion_timer = 0
        self.confetti = None
        
        # Load specific level complete sound
        self.level_complete_sound = load_sound(resource_path('assets/sounds/level3_complete.wav'))
            
        # Success Screen Elements (Arabic Images)
        from utils import load_arabic_image
        
        # Note: Using "Start-game.png" for Dashboard button as we don't have a specific Dashboard image
        self.next_button = load_arabic_image('Start-game.png', (200, 80))
        if not self.next_button:
            self.next_button = create_button("Dashboard", 0, 0, 200, 80, (50, 200, 50), font_size=30)
        self.next_button_rect = pygame.Rect((self.width - 200) // 2, self.height // 2 + 150, 200, 80)

        self.restart_button = load_arabic_image('try-agin.png', (200, 80))
        if not self.restart_button:
            self.restart_button = create_button("Restart", 0, 0, 200, 80, (200, 50, 50), font_size=30)
        self.restart_button_rect = pygame.Rect((self.width - 200) // 2, self.height // 2 + 250, 200, 80)
    
    def handle_event(self, event):
        """Handle mouse events"""
        if self.completed:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.next_button_rect.collidepoint(event.pos):
                    return True
                elif self.restart_button_rect.collidepoint(event.pos):
                    return "restart"
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            for half in self.draggable_halves:
                if half.start_drag(event.pos):
                    self.dragging_half = half
                    break
        
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_half:
                self.dragging_half.drag(event.pos)
                
                # Highlight slots - check distance for "magnetic" feel
                for slot in self.puzzle_slots:
                    # Calculate distance between centers
                    dist_x = abs(self.dragging_half.rect.centerx - (slot.rect.right + self.dragging_half.rect.width/2))
                    dist_y = abs(self.dragging_half.rect.centery - slot.rect.centery)
                    
                    # Highlight if close enough (within 100 pixels)
                    is_close = dist_x < 100 and dist_y < 100
                    slot.highlight = (is_close and not slot.matched)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging_half:
                matched = False
                
                # Check if dropped near correct slot
                for slot in self.puzzle_slots:
                    # Calculate distance to target position (right next to slot)
                    target_x = slot.rect.right
                    target_y = slot.rect.top
                    
                    # Check distance (generous 100px radius)
                    dist = ((self.dragging_half.rect.x - target_x)**2 + (self.dragging_half.rect.y - target_y)**2)**0.5
                    
                    if dist < 100 and not slot.matched:
                        if slot.check_match(self.dragging_half):
                            # Correct match!
                            slot.matched = True
                            slot.matching_half = self.dragging_half.image
                            self.dragging_half.matched = True
                            self.matches_found += 1
                            
                            if self.success_sound:
                                self.success_sound.play()
                            
                            # Snap to position
                            self.dragging_half.rect.topleft = (slot.rect.right, slot.rect.top)
                            
                            sparkle = SparkleEffect(slot.rect.centerx + 30, slot.rect.centery)
                            self.sparkles.append(sparkle)
                            
                            matched = True
                            break
                
                if not matched and self.dragging_half.dragging:
                    # Wrong match
                    self.dragging_half.return_to_start()
                    if self.error_sound:
                        self.error_sound.play()
                
                self.dragging_half.stop_drag()
                self.dragging_half = None
                
                # Reset highlights
                for slot in self.puzzle_slots:
                    slot.highlight = False
        
        return False
    
    def update(self):
        """Update animations and check completion"""
        for half in self.draggable_halves:
            half.update()
        
        self.sparkles = [s for s in self.sparkles if s.update()]
        
        if self.confetti:
            if not self.confetti.update():
                self.confetti = None
        
        if self.matches_found >= self.total_matches and not self.completed:
            self.completed = True
            self.completion_timer = pygame.time.get_ticks()
            if self.level_complete_sound:
                self.level_complete_sound.play()
            # Create confetti effect
            self.confetti = ConfettiEffect(self.width, self.height)
        
        # if self.completed and pygame.time.get_ticks() - self.completion_timer > 3000:
        #     return True
        
        return False
    
    def draw(self):
        """Draw the level"""
        self.screen.blit(self.background, (0, 0))
        
        # Draw title
        draw_text(self.screen, "Complete the Vehicle Puzzles", 36, self.width // 2, 40, (80, 80, 80))
        
        # Draw puzzle slots
        for slot in self.puzzle_slots:
            slot.draw(self.screen)
        
        # Draw draggable halves
        for half in self.draggable_halves:
            half.draw(self.screen)
        
        # Draw sparkles
        for sparkle in self.sparkles:
            sparkle.draw(self.screen)
        
        # Draw confetti
        if self.confetti:
            self.confetti.draw(self.screen)
        
        # Draw completion message
        # Draw completion message
        if self.completed:
            # Draw semi-transparent overlay
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            
            draw_text(self.screen, "Level 3 Complete!", 60, self.width // 2, self.height // 2 - 50, (50, 200, 50))
            draw_text(self.screen, "Puzzle Solved!", 40, self.width // 2, self.height // 2 + 20, (255, 215, 0))
            
            self.screen.blit(self.next_button, self.next_button_rect)
            self.screen.blit(self.restart_button, self.restart_button_rect)
