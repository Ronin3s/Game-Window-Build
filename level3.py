"""
Level 3: Complete the Transportation Image
Players match vehicle halves to complete the images
"""
import pygame
import random
from utils import SparkleEffect, ShakeAnimation, ConfettiEffect, create_vehicle_image, draw_text, resource_path

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
        
        # Load background
        try:
            self.background = pygame.image.load(resource_path('assets/images/level3_bg.png'))
            self.background = pygame.transform.scale(self.background, (self.width, self.height))
        except:
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
        
        # Create split vehicles
        for i, (vtype, color) in enumerate(vehicle_data):
            # Create full vehicle (larger size)
            full_vehicle = create_vehicle_image(vtype, color, (150, 150))
            
            # Split into halves
            left_half = pygame.Surface((75, 150), pygame.SRCALPHA)
            right_half = pygame.Surface((75, 150), pygame.SRCALPHA)
            
            left_half.blit(full_vehicle, (0, 0), (0, 0, 75, 150))
            right_half.blit(full_vehicle, (0, 0), (75, 0, 75, 150))
            
            # Position slots on left side (adjusted for 1024x768)
            row = i // 2
            col = i % 2
            slot_x = 100 + col * 250
            slot_y = 150 + row * 160
            
            # Create puzzle slot with left half (fixed)
            slot = PuzzleSlot(left_half, slot_x, slot_y, i)
            self.puzzle_slots.append(slot)
            
            # Create draggable right half
            half_x = 600 + (i % 4) * 100
            half_y = 150 + (i // 4) * 180
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
        self.confetti = None
    
    def handle_event(self, event):
        """Handle mouse events"""
        if self.completed:
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
            if self.complete_sound:
                self.complete_sound.play()
            # Create confetti effect
            self.confetti = ConfettiEffect(self.width, self.height)
        
        if self.completed and pygame.time.get_ticks() - self.completion_timer > 3000:
            return True
        
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
        if self.completed:
            # Draw semi-transparent overlay
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            self.screen.blit(overlay, (0, 0))
            
            draw_text(self.screen, "Congratulations!", 84, self.width // 2, self.height // 2 - 80, (255, 215, 0))
            draw_text(self.screen, "You finished all levels!", 48, self.width // 2, self.height // 2, (255, 255, 255))
            
            # Draw big stars
            for i in range(7):
                x = self.width // 2 - 150 + i * 50
                y = self.height // 2 + 80
                size = 20 if i % 2 == 0 else 15
                pygame.draw.polygon(self.screen, (255, 215, 0), [
                    (x, y - size), (x + size//3, y), (x + size, y),
                    (x + size//2, y + size//2), (x + size*2//3, y + size),
                    (x, y + size*2//3), (x - size*2//3, y + size),
                    (x - size//2, y + size//2), (x - size, y), (x - size//3, y)
                ])
