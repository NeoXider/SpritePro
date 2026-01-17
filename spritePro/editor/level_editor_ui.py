# spritePro/editor/level_editor_ui.py
"""Interactive Level Editor with Pygame - Enhanced version using SpritePro components"""
import pygame
from typing import List, Dict, Tuple
import os

import pygame
from typing import List, Dict, Tuple
import os

class LevelEditorUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("SpritePro Level Editor")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        
        # Import LevelEditor from editor module
        try:
            from spritePro.editor import LevelEditor as LevelEditorModule
        except ImportError:
            print("[Editor] Could not find LevelEditor module. Please ensure the package structure is correct.")
            exit(1)
            
        # Initialize editor with proper grid settings
        self.editor = LevelEditorModule(width=800, height=500)
        self.grid_size = (10, 8)  # 10x8 grid
        self.tile_size = (80, 60)  # 80x60 pixels per tile
        self.grid_offset = ((800 - self.grid_size[0] * self.tile_size[0]) // 2,
                           (500 - self.grid_size[1] * self.tile_size[1]) // 2)
        
        # Available sprites from readySprites package
        self.available_sprites: List[str] = [
            "bg", "hero", "enemy", "ball", "platforma",
            "barrier", "canister"
        ]
        self.custom_sprites: Dict[str, str] = {}
        self.sprite_images: Dict[str, str] = {}
        
        # Load default sprites
        for sprite in self.available_sprites:
            try:
                # Try to load from readySprites package first, then fallback to demo sprites
                self.sprite_images[sprite] = f"readySprites/{sprite}.py"
            except Exception as e:
                print(f"[Editor] Could not load sprite {sprite} from readySprites: {e}")
                pass
            try:
                self.sprite_images[sprite] = f"demoGames/Sprites/{sprite}.png"
            except Exception as e:
                print(f"[Editor] Could not load sprite {sprite}: {e}")
                pass
        
        # Add custom sprites functionality
        self.custom_sprite_input = ""
        self.adding_custom_sprite = False
        
        self.selected_sprite = "bg"
        self.running = True
        self.sprites_group = pygame.sprite.Group()
        
        # Initialize PageManager for multi-page UI
        try:
            from spritePro.components import Page, PageManager
            self.page_manager = PageManager()
            
            # Create main editor page (default active)
            self.main_editor_page = Page("main_editor")
            self.page_manager.add_page(self.main_editor_page)
            
            # Create properties panel page
            self.properties_page = Page("properties_panel")
            self.page_manager.add_page(self.properties_page)
        except ImportError:
            print("[Editor] Could not import PageManager. Pages feature disabled.")
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update_sprites()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
            
    def handle_events(self):
        """Handle user input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:  # Check for key press events first
                if event.key == pygame.K_s:
                    self.save_level()
                elif event.key == pygame.K_l:
                    self.load_level()
                elif event.key == pygame.K_c:
                    self.editor.clear_sprites()
                # Change selected sprite with number keys
                elif event.key == pygame.K_1:
                    self.selected_sprite = "bg"
                elif event.key == pygame.K_2:
                    self.selected_sprite = "hero"
                elif event.key == pygame.K_3:
                    self.selected_sprite = "enemy"
                elif event.key == pygame.K_4:
                    self.selected_sprite = "ball"
                elif event.key == pygame.K_5:
                    self.selected_sprite = "platforma"
                # Add custom sprite with 'A' key
                elif event.key == pygame.K_a and not self.adding_custom_sprite:
                    self.adding_custom_sprite = True
                    self.custom_sprite_input = ""
                # Enter to confirm custom sprite
                elif event.key == pygame.K_RETURN and self.adding_custom_sprite:
                    if self.custom_sprite_input.strip():
                        self.add_custom_sprite(self.custom_sprite_input)
                    self.adding_custom_sprite = False
                    self.custom_sprite_input = ""
                # Backspace to clear custom input
                elif event.key == pygame.K_BACKSPACE and self.adding_custom_sprite:
                    self.custom_sprite_input = self.custom_sprite_input[:-1]
                # Other keys for navigation when adding custom sprite
                elif self.adding_custom_sprite and event.unicode:
                    if len(self.custom_sprite_input) < 20:  # Limit input length
                        self.custom_sprite_input += event.unicode
                    
            # Page navigation with F1-F2 keys
            elif event.key == pygame.K_f1:
                try:
                    from spritePro.components import Page, PageManager
                    self.page_manager.set_active_page("main_editor")
                except ImportError:
                    pass
            elif event.key == pygame.K_f2:
                try:
                    from spritePro.components import Page, PageManager
                    self.page_manager.set_active_page("properties_panel")
                except ImportError:
                    pass
                
            # Mouse click to place sprite
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.place_sprite()
                elif event.button == 3:  # Right click to remove
                    self.remove_sprite()

   def add_custom_sprite(self, sprite_name):
       """Add a custom sprite from user input"""
       try:
           # Try to load from readySprites package first, then fallback to demo sprites
           path = f"readySprites/{sprite_name}.py"
           if not os.path.exists(path):
               path = f"demoGames/Sprites/{sprite_name}.png"
               
           if os.path.exists(path):
               self.sprite_images[sprite_name] = path
               self.available_sprites.append(sprite_name)
               print(f"Added custom sprite: {sprite_name}")
           else:
               print(f"Could not find sprite file for: {sprite_name}")
       except Exception as e:
           print(f"Error adding custom sprite: {e}")

   def place_sprite(self):
       """Place selected sprite at mouse position"""
       mx, my = pygame.mouse.get_pos()
       x = (mx - self.grid_offset[0]) // self.tile_size[0]
       y = (my - self.grid_offset[1]) // self.tile_size[0]
       
       if 0 <= x < self.grid_size[0] and 0 <= y < self.grid_size[1]:
           # Create a new Sprite object
           sprite_data = self.editor.add_sprite(
               x, y,
               width=self.tile_size[0],
               height=self.tile_size[1],
               image_path=self.sprite_images.get(self.selected_sprite)
           )
           
           # Create and add the actual pygame sprite with animation support
           if sprite_data:
               from spritePro import Sprite  # Import Sprite class here
               
               sprite_obj = Sprite(
                   sprite=sprite_data['image_path'],
                   size=(self.tile_size),
                   pos=((x * self.tile_size[0]) + self.grid_offset[0],
                        (y * self.tile_size[1]) + self.grid_offset[1]),
                   sorting_order=100
               )
               
               # Add animation component if available for this sprite type
               try:
                   from spritePro.components import Animation
                   sprite_obj.add_component(Animation())
               except ImportError:
                   pass
               
               # Add health component based on sprite type
               if self.selected_sprite in ["hero", "enemy"]:
                   try:
                       from spritePro.components import HealthComponent
                       sprite_obj.add_component(HealthComponent(max_health=100))
                   except ImportError:
                       pass
               
               # Add mouse interactor for all sprites (except background)
               if self.selected_sprite != "bg":
                   try:
                       from spritePro.components import MouseInteractor
                       sprite_obj.add_component(MouseInteractor(
                           on_click=lambda: print(f"Clicked {self.selected_sprite} at ({x}, {y})"),
                           on_mouse_down=lambda: print(f"Pressed {self.selected_sprite} at ({x}, {y})")
                       ))
                   except ImportError:
                       pass
               
               # Add tween component for all sprites
               try:
                   from spritePro.components import TweenManager, Tween
                   manager = TweenManager()
                   
                   # Create a simple movement tween
                   manager.add_tween(
                       f"move_{self.selected_sprite}_tween",
                       start_value=0,
                       end_value=1.0,
                       duration=2.0,
                       easing=EasingType.EASE_IN_OUT,
                       loop=True,
                       yoyo=False,
                       on_update=lambda x: setattr(sprite_obj, "scale", 1 + (x * 0.5)),
                   )
                   
                   sprite_obj.add_component(manager)
               except ImportError:
                   pass
               
               self.sprites_group.add(sprite_obj)
               
           print(f"Placed {self.selected_sprite} at ({x}, {y})")

   def remove_sprite(self):
       """Remove sprite at mouse position"""
       mx, my = pygame.mouse.get_pos()
       x = (mx - self.grid_offset[0]) // self.tile_size[0]
       y = (my - self.grid_offset[1]) // self.tile_size[0]
       
       if 0 <= x < self.grid_size[0] and 0 <= y < self.grid_size[1]:
           # Find sprite at this position
           for sprite in self.sprites_group:
               sprite_x, sprite_y = sprite.get_position()
               grid_x = (sprite_x - self.grid_offset[0]) // self.tile_size[0]
               grid_y = (sprite_y - self.grid_offset[1]) // self.tile_size[0]
               
               if abs(grid_x - x) < 1 and abs(grid_y - y) < 1:
                   sprite.kill()
                   # Remove from editor data
                   for i, s in enumerate(self.editor.sprites):
                       if s['x'] == grid_x and s['y'] == grid_y:
                           self.editor.remove_sprite(i)
                           break
                       
           print(f"Removed sprite at ({x}, {y})")

   def save_level(self):
       """Save level to file"""
       try:
           self.editor.save_to_json("demo_level.json")
           print("Level saved!")
       except Exception as e:
           print(f"Error saving level: {e}")
           
   def load_level(self):
       """Load level from file"""
       try:
           # Clear current sprites
           for sprite in self.sprites_group:
               sprite.kill()
               
           # Load data and create sprites with animation support
           self.editor.load_from_json("demo_level.json")
           
           # Create pygame sprites based on loaded data
           for sprite_data in self.editor.sprites:  # Use editor.sprites directly
               if 'image_path' in sprite_data:
                   from spritePro import Sprite
                   
                   sprite_obj = Sprite(
                       sprite=sprite_data['image_path'],
                       size=(self.tile_size),
                       pos=((sprite_data['x'] * self.tile_size[0]) + self.grid_offset[0],
                            (sprite_data['y'] * self.tile_size[1]) + self.grid_offset[1]),
                       sorting_order=100
                   )
                   
                   # Add animation component if available for this sprite type
                   try:
                       from spritePro.components import Animation
                       sprite_obj.add_component(Animation())
                   except ImportError:
                       pass
                   
                   # Add health component based on sprite type
                   if 'type' in sprite_data and sprite_data['type'] in ["hero", "enemy"]:
                       try:
                           from spritePro.components import HealthComponent
                           sprite_obj.add_component(HealthComponent(max_health=100))
                       except ImportError:
                           pass
                       
                   # Add mouse interactor for all sprites (except background)
                   if self.selected_sprite != "bg":
                       try:
                           from spritePro.components import MouseInteractor, EasingType
                           mx, my = pygame.mouse.get_pos()
                           sprite_obj.add_component(MouseInteractor(
                               on_click=lambda: print(f"Clicked {self.selected_sprite} at ({mx}, {my})"),
                               on_mouse_down=lambda: print(f"Pressed {self.selected_sprite} at ({mx}, {my})")
                           ))
                       except ImportError:
                           pass
                       
                   # Add tween component for all sprites
                   try:
                       from spritePro.components import TweenManager, Tween
                       manager = TweenManager()
                       
                       # Create a simple movement tween
                       manager.add_tween(
                           f"move_{self.selected_sprite}_tween",
                           start_value=0,
                           end_value=1.0,
                           duration=2.0,
                           easing=EasingType.EASE_IN_OUT,
                           loop=True,
                           yoyo=False,
                           on_update=lambda x: setattr(sprite_obj, "scale", 1 + (x * 0.5)),
                       )
                       
                       sprite_obj.add_component(manager)
                   except ImportError:
                       pass
                       
                   self.sprites_group.add(sprite_obj)
                   
           print("Level loaded!")
       except FileNotFoundError:
           print("No level file found to load")
       except Exception as e:
           print(f"Error loading level: {e}")
           
   def draw(self):
       """Draw the editor interface"""
       self.screen.fill((20, 20, 20))
       
       # Draw grid lines
       for i in range(self.grid_size[0] + 1):
           x = self.grid_offset[0] + i * self.tile_size[0]
           pygame.draw.line(self.screen, (50, 50, 100),
                          (x, self.grid_offset[1]),
                          (x, self.grid_offset[1] + self.grid_size[1] * self.tile_size[1]))
       for j in range(self.grid_size[1] + 1):
           y = self.grid_offset[1] + j * self.tile_size[1]
           pygame.draw.line(self.screen, (50, 50, 100),
                          (self.grid_offset[0], y),
                          (self.grid_offset[0] + self.grid_size[0] * self.tile_size[0], y))
       
       # Draw sprites
       self.sprites_group.draw(self.screen)
       
       # Draw UI controls based on active page
       if hasattr(self, 'page_manager'):
           current_page = self.page_manager.get_active_page()
           
           ui_y = 540
           
           # Draw page indicator
           text = f"Page: {current_page.name}"
           surf = self.font.render(text, True, (255, 255, 255))
           self.screen.blit(surf, (10, ui_y - 30))
           
           if current_page == self.main_editor_page:
               # Main editor view
               # Draw custom sprite input field if adding
               if self.adding_custom_sprite:
                   pygame.draw.rect(self.screen, (100, 100, 200),
                                  (300, ui_y - 30, 400, 25))
                   text = self.font.render(f"Add Custom Sprite: {self.custom_sprite_input}", True, (255, 255, 255))
                   self.screen.blit(text, (305, ui_y - 27))
               else:
                   # Draw selected sprite info
                   self.draw_button(self.font, "Selected Sprite: ", (100, ui_y), (255, 255, 255))
                   
               # Draw available sprites list with numbers
               for i, sprite in enumerate(self.available_sprites):
                   color = (0, 255, 0) if self.selected_sprite == sprite else (100, 100, 100)
                   text = f"{i+1}. {sprite}"
                   surf = self.font.render(text, True, color)
                   self.screen.blit(surf, (300 + i * 80, ui_y))
               
               # Draw instructions
               instructions = [
                   "Left Click: Place Sprite",
                   "Right Click: Remove Sprite",
                   "S Key: Save Level (demo_level.json)",
                   "L Key: Load Level",
                   "C Key: Clear All Sprites"
               ]
               for i, instr in enumerate(instructions):
                   text = self.font.render(instr, True, (150, 200, 255))
                   self.screen.blit(text, (450, ui_y + i * 30))
               
               # Draw add custom sprite instruction
               if not self.adding_custom_sprite:
                   text = self.font.render("Press 'A' to add custom sprite", True, (200, 150, 50))
                   self.screen.blit(text, (550, 20))
           
           elif current_page == self.properties_page:
               # Properties panel view - placeholder
               pygame.draw.rect(self.screen, (40, 40, 60), (300, ui_y - 30, 400, 200))
               
               text = "Properties Panel"
               surf = self.font.render(text, True, (255, 255, 255))
               self.screen.blit(surf, (310, ui_y + 10))
               
               # Add some sample properties
               props = [
                   f"Selected: {self.selected_sprite}",
                   "Health: 100/100",
                   "Position: ({x}, {y})",
                   "Size: {width}x{height}"
               ]
               
               for i, prop in enumerate(props):
                   text = self.font.render(prop, True, (200, 200, 200))
                   self.screen.blit(text, (310, ui_y + 40 + i * 25))
           
           # Draw page navigation buttons
           if hasattr(self, 'page_manager'):
               pygame.draw.rect(self.screen, (60, 60, 80), (10, 20, 100, 30))
               text = self.font.render("Main", True, (200, 200, 200))
               self.screen.blit(text, (15, 25))
               
               pygame.draw.rect(self.screen, (60, 60, 80), (120, 20, 100, 30))
               text = self.font.render("Props", True, (200, 200, 200))
               self.screen.blit(text, (125, 25))

   def draw_button(self, font, text, pos, color):
       """Draw a button"""
       surf = font.render(text, True, color)
       self.screen.blit(surf, pos)

if __name__ == "__main__":
   editor_ui = LevelEditorUI()
   editor_ui.run()