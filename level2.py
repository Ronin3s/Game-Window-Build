"""
Level 2: Connect Transportation to Environment
Players drag vehicles to their correct environments (air, land, sea)
"""
import pygame
import random
from utils import SparkleEffect, ShakeAnimation, create_vehicle_image, draw_text, resource_path

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
        
        # Load background
        try:
            self.background = pygame.image.load(resource_path('assets/images/level2_bg.png'))
            self.background = pygame.transform.scale(self.background, (self.width, self.height))
        except:
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
        
        random.shuffle(vehicle_data)
        
        for i, (vtype, color) in enumerate(vehicle_data):
            vehicle_img = create_vehicle_image(vtype, color, (100, 100)) # Keep draggable slightly smaller than full size
            # Position vehicles in two rows at the top, well above the zones
            row = i // 4  # 4 vehicles per row
            col = i % 4
            x = 200 + col * 180  # Better spacing for 1024 width
            y = 50 + row * 110    # Two rows with proper spacing
            vehicle = DraggableVehicle2(vehicle_img, x, y, vtype)
            self.vehicles.append(vehicle)
        
        self.dragging_vehicle = None
        self.total_vehicles = len(self.vehicles)
        self.completed = False
        self.completion_timer = 0
    
    def handle_event(self, event):
        """Handle mouse events"""
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
        
        self.sparkles = [s for s in self.sparkles if s.update()]
        
        if self.vehicles_placed >= self.total_vehicles and not self.completed:
            self.completed = True
            self.completion_timer = pygame.time.get_ticks()
            if self.complete_sound:
                self.complete_sound.play()
        
        if self.completed and pygame.time.get_ticks() - self.completion_timer > 2000:
            return True
        
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
        if self.completed:
            draw_text(self.screen, "Excellent!", 72, self.width // 2, self.height // 2 - 100, (255, 215, 0))
            for i in range(5):
                x = self.width // 2 - 100 + i * 50
                y = self.height // 2 - 30
                pygame.draw.polygon(self.screen, (255, 215, 0), [
                    (x, y - 15), (x + 5, y), (x + 20, y), (x + 8, y + 10),
                    (x + 12, y + 25), (x, y + 15), (x - 12, y + 25),
                    (x - 8, y + 10), (x - 20, y), (x - 5, y)
                ])
