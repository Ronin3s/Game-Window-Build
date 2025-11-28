"""
Level 2: Connect Transportation to Environment
Players drag vehicles to their correct environments (air, land, sea)
"""
import pygame
import random
from utils import SparkleEffect, ShakeAnimation, ConfettiEffect, create_vehicle_image, draw_text, resource_path, load_sound, create_button

class EnvironmentZone:
    """An environment zone where vehicles can be placed"""
    def __init__(self, name, rect, color, vehicle_types, max_vehicles=3, display_name=None):
        self.name = name
        self.display_name = display_name if display_name else name
        self.rect = rect
        self.color = color
        self.vehicle_types = vehicle_types  # List of vehicle types that belong here
        self.vehicles = []  # Vehicles placed in this zone
        self.highlight = False
        self.max_vehicles = max_vehicles  # Now customizable per zone
    
    def can_accept(self, vehicle_type):
        """Check if this zone accepts this vehicle type"""
        return vehicle_type in self.vehicle_types and len(self.vehicles) < self.max_vehicles
    
    def add_vehicle(self, vehicle):
        """Add a vehicle to this zone"""
        self.vehicles.append(vehicle)
    
    def draw(self, screen):
        """Draw the environment zone"""
        # Draw zone background
        if self.highlight:
            pygame.draw.rect(screen, (255, 255, 100), self.rect, 5)
        pygame.draw.rect(screen, self.color, self.rect, 3)
        
        # Draw zone label
        # Use draw_text from utils to get Arabic support
        draw_text(screen, self.display_name, 48, self.rect.centerx, self.rect.top - 30, (50, 50, 50))
        
        # Draw icon/symbol for environment
        icon_name = ""
        if self.name == "AIR":
            icon_name = "sky_environment.png"
        elif self.name == "LAND":
            icon_name = "road_environment.png"
        elif self.name == "SEA":
            icon_name = "ocean_environment.png"
            
        if icon_name:
            try:
                icon = pygame.image.load(resource_path(f'assets/images/{icon_name}'))
                # Scale icon to fit nicely in the zone
                icon = pygame.transform.scale(icon, (150, 150))
                icon_rect = icon.get_rect(center=(self.rect.centerx, self.rect.centery))
                screen.blit(icon, icon_rect)
            except:
                pass

class Level2:
    def __init__(self, screen, success_sound=None, error_sound=None, complete_sound=None):
        # ... (init code) ...
        
        # Create environment zones
        zone_width = 280
        zone_height = 450
        zone_y = 250
        
        self.zones = [
            EnvironmentZone("AIR", pygame.Rect(50, zone_y, zone_width, zone_height), 
                          (173, 216, 230), ["plane", "helicopter"], max_vehicles=2, display_name="Air"),
            EnvironmentZone("LAND", pygame.Rect(370, zone_y, zone_width, zone_height),
                          (144, 238, 144), ["car", "bike", "bus", "train"], max_vehicles=4, display_name="Land"),
            EnvironmentZone("SEA", pygame.Rect(690, zone_y, zone_width, zone_height),
                          (135, 206, 250), ["boat", "ship"], max_vehicles=2, display_name="Sea")
        ]
        
        # ... (rest of init) ...

    # ... (handle_event and update methods) ...

    def draw(self):
        """Draw the level"""
        self.screen.blit(self.background, (0, 0))
        
        # Draw title
        draw_text(self.screen, "Sort Vehicles to their Environments", 48, self.width // 2, 50, (80, 80, 80))
        
        # Draw zones
        for zone in self.zones:
            zone.draw(self.screen)
            
        # Draw vehicles
        for vehicle in self.vehicles:
            vehicle.draw(self.screen)
            
        # Draw sparkles
        for sparkle in self.sparkles:
            sparkle.draw(self.screen)
            
        # Draw confetti
        if self.confetti:
            self.confetti.draw(self.screen)
        
        # Draw completion message
        if self.completed:
            draw_text(self.screen, "Excellent!", 72, self.width // 2, self.height // 2, (255, 215, 0))

class DraggableVehicle2:
    """A vehicle that can be dragged to environment zones"""
    def __init__(self, image, x, y, vehicle_type):
        self.image = image
        self.rect = image.get_rect(topleft=(x, y))
        self.original_pos = (x, y)
        self.vehicle_type = vehicle_type
        self.dragging = False
        self.placed = False
        self.shake = None
    
    def start_drag(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos) and not self.placed:
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
    
    def place_in_zone(self, zone_rect):
        """Snap to position in zone"""
        num_in_zone = len([v for z in [] for v in z.vehicles])
        self.rect.center = zone_rect.center
        self.placed = True
    
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
        screen.blit(self.image, pos)

class Level2:
    def __init__(self, screen, success_sound=None, error_sound=None, complete_sound=None):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.success_sound = success_sound
        self.error_sound = error_sound
        self.complete_sound = complete_sound
        
        # Load background - Solid pastel color as requested
        self.background = pygame.Surface((self.width, self.height))
        self.background.fill((255, 253, 208))  # Pastel yellow
        
        # Create environment zones
        zone_width = 280
        zone_height = 450
        zone_y = 250
        
        self.zones = [
            EnvironmentZone("AIR", pygame.Rect(50, zone_y, zone_width, zone_height), 
                          (173, 216, 230), ["plane", "helicopter"], max_vehicles=2, display_name="Air"),
            EnvironmentZone("LAND", pygame.Rect(370, zone_y, zone_width, zone_height),
                          (144, 238, 144), ["car", "bike", "bus", "train"], max_vehicles=4, display_name="Land"),
            EnvironmentZone("SEA", pygame.Rect(690, zone_y, zone_width, zone_height),
                          (135, 206, 250), ["boat", "ship"], max_vehicles=2, display_name="Sea")
        ]
        
        # Create vehicles
        vehicle_data = [
            ("plane", (255, 200, 100)),
            ("helicopter", (200, 100, 255)),
            ("car", (255, 100, 100)),
            ("bike", (100, 150, 255)),
            ("boat", (100, 255, 150)),
            ("bus", (255, 150, 200)),
            ("train", (150, 255, 100)),
            ("ship", (100, 200, 200))
        ]
        
        self.vehicles = []
        self.sparkles = []
        self.vehicles_placed = 0
        self.total_vehicles = len(vehicle_data)
        self.completed = False
        self.completion_timer = 0
        self.confetti = None
        
        # Load specific level complete sound
        self.level_complete_sound = load_sound(resource_path('assets/sounds/level2_complete.wav'))
            
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
        # Create draggable vehicles
        # Increase size for kids view (was 80, now 100)
        random.shuffle(vehicle_data)
        
        # Grid Layout: All objects fixed below the title
        self.vehicles = []
        
        # 8 vehicles total. 2 rows of 4.
        # Title is at y=50, so position vehicles below it
        start_x = 200
        start_y = 120 # Below the title "Sort Vehicles to their Environments"
        
        for i, (vtype, color) in enumerate(vehicle_data):
            # Create at larger size
            raw_img = create_vehicle_image(vtype, color, (150, 150))
            vehicle_img = pygame.transform.scale(raw_img, (100, 100))
            
            row = i // 4
            col = i % 4
            
            x = start_x + col * 220
            y = start_y + row * 110
            
            vehicle = DraggableVehicle2(vehicle_img, x, y, vtype)
            # Store initial pos for resetting if dropped in wrong place
            vehicle.initial_x = x
            vehicle.initial_y = y
            self.vehicles.append(vehicle)
        
        self.dragging_vehicle = None
        self.total_vehicles = len(self.vehicles)
        self.completed = False
        self.completion_timer = 0
    
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
            for vehicle in self.vehicles:
                if vehicle.start_drag(event.pos):
                    self.dragging_vehicle = vehicle
                    break
        
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_vehicle:
                self.dragging_vehicle.drag(event.pos)
                
                # Highlight zones
                for zone in self.zones:
                    zone.highlight = (zone.rect.collidepoint(event.pos) and 
                                    zone.can_accept(self.dragging_vehicle.vehicle_type))
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging_vehicle:
                placed = False
                
                # Check if dropped in correct zone
                for zone in self.zones:
                    if zone.rect.colliderect(self.dragging_vehicle.rect):
                        if zone.can_accept(self.dragging_vehicle.vehicle_type):
                            # Correct placement!
                            zone.add_vehicle(self.dragging_vehicle)
                            self.dragging_vehicle.place_in_zone(zone.rect)
                            self.vehicles_placed += 1
                            
                            # Calculate position in zone
                            slot = len(zone.vehicles) - 1
                            self.dragging_vehicle.rect.center = (
                                zone.rect.centerx + (slot - 1) * 30,
                                zone.rect.centery + 80 + slot * 40
                            )
                            
                            if self.success_sound:
                                self.success_sound.play()
                            
                            sparkle = SparkleEffect(self.dragging_vehicle.rect.centerx,
                                                   self.dragging_vehicle.rect.centery)
                            self.sparkles.append(sparkle)
                            placed = True
                            break
                
                if not placed and self.dragging_vehicle.dragging:
                    # Wrong placement
                    self.dragging_vehicle.return_to_start()
                    if self.error_sound:
                        self.error_sound.play()
                
                self.dragging_vehicle.stop_drag()
                self.dragging_vehicle = None
                
                # Reset highlights
                for zone in self.zones:
                    zone.highlight = False
        
        return False
    
    def update(self):
        """Update animations and check completion"""
        for vehicle in self.vehicles:
            vehicle.update()
            # If placed, it stays placed (or disappears? usually stays in zone)
            # In original logic, they stayed.
        
        self.sparkles = [s for s in self.sparkles if s.update()]
        
        # Check completion
        # Count placed vehicles
        placed_count = sum(1 for v in self.vehicles if v.placed)
        
        if placed_count >= self.total_vehicles and not self.completed:
            self.completed = True
            self.completion_timer = pygame.time.get_ticks()
            if self.level_complete_sound:
                self.level_complete_sound.play()
        
        # if self.completed and pygame.time.get_ticks() - self.completion_timer > 2000:
        #     return True
        
        return False
    
    def draw(self):
        """Draw the level"""
        self.screen.blit(self.background, (0, 0))
        
        # Draw title
        draw_text(self.screen, "Sort Vehicles to their Environments", 48, self.width // 2, 50, (80, 80, 80))
        
        # Draw zones
        for zone in self.zones:
            zone.draw(self.screen)
        
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
            
            draw_text(self.screen, "Level 2 Complete!", 60, self.width // 2, self.height // 2 - 50, (50, 200, 50))
            draw_text(self.screen, "Environment Sorted!", 40, self.width // 2, self.height // 2 + 20, (255, 215, 0))
            
            self.screen.blit(self.next_button, self.next_button_rect)
            self.screen.blit(self.restart_button, self.restart_button_rect)
