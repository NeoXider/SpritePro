# SpritePro

SpritePro - a powerful and flexible game development library built on top of Pygame. Provides a comprehensive set of tools for creating 2D games with advanced capabilities.

## 🎮 Key Features

- **Sprite System**: Flexible sprite management with built-in physics and game logic
- **Physics Engine**: Realistic physics simulation with collision detection and handling
- **Animation System**: Smooth animations with tweening and state management
- **UI Components**: Ready-to-use buttons, text elements, and interactive components
- **Timer System**: Precise time management for game events and animations
- **Health System**: Complete health management with damage, healing, and callbacks
- **Mouse Interaction**: Simple mouse handling with hover and click detection
- **Surface Utilities**: Advanced tools for working with surfaces
- **Color Effects**: Dynamic color effects and animations for visual appeal
- **Save/Load System**: Professional data persistence with multiple formats and automatic backups

## 🚀 Quick Start

### Installation

```bash
pip install pygame
git clone https://github.com/NeoXider/SpritePro.git
cd SpritePro
```

### Basic Usage

```python
import pygame
import spritePro as s

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Create sprite
sprite = s.Sprite("assets/player.png", (64, 64), (400, 300))

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Update
    sprite.update()
    
    # Render
    screen.fill((0, 0, 0))
    sprite.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
```

## 📚 Documentation

### 📋 Project Documentation
- [📖 Documentation Index](DOCUMENTATION_INDEX.md) - Complete documentation guide
- [📋 Changelog](CHANGELOG.md) - Version history and changes
- [Roadmap](ROADMAP.md) - Future features and development plans
- [Technical Specifications](TECHNICAL_SPECS.md) - Detailed technical specs for planned features
- [Contributing Guide](CONTRIBUTING.md) - How to contribute to the project
- [Game Ideas](GAME_IDEAS.md) - Ideas for demo games and examples
- [Performance Guide](PERFORMANCE.md) - Performance optimization strategies

### Core Components
- [Sprite System](docs/sprite.md) - Basic sprite functionality
- [Game Sprite](docs/gameSprite.md) - Extended sprites with game logic
- [Physics Sprite](docs/physicSprite.md) - Sprites with physics support

### UI Components
- [Button](docs/button.md) - Interactive button component
- [ToggleButton](docs/toggle_button.md) - Toggle switch component
- [Text](docs/text.md) - Text rendering and management
- [Mouse Interaction](docs/mouse_interactor.md) - Mouse interaction handling

### Game Systems
- [Animation](docs/animation.md) - Animation and state management
- [Tweening](docs/tween.md) - Smooth transitions and easing
- [Timer](docs/timer.md) - Time system and scheduling
- [Health](docs/health.md) - Health and damage management

### Utilities
- [Surface Utilities](docs/surface.md) - Tools for working with surfaces
- [Color Effects](docs/color_effects.md) - Dynamic color effects and animations
- [Save/Load System](docs/save_load.md) - Professional save and load system for game data

### Ready Sprites
- [Ready Sprites Overview](docs/readySprites.md) - Pre-built game components guide
- [Text_fps](docs/text_fps.md) - Ready-to-use FPS counter with automatic updates

## 🎯 Demo Games

Explore our demo games to see SpritePro in action:

- [Animation Demo](spritePro/demoGames/animationDemo.py) - Sprite animation demonstration
- [Physics Demo](spritePro/demoGames/demo_physics.py) - Physics simulation example
- [Pymunk Demo](spritePro/demoGames/demo_pymunk.py) - Advanced physics with Pymunk
- [Ping Pong](spritePro/demoGames/ping_pong.py) - Classic Pong game
- [Tweening Demo](spritePro/demoGames/tweenDemo.py) - Animation tweening examples
- [Toggle Demo](spritePro/demoGames/toggle_demo.py) - Interactive toggle buttons showcase
- [Color Effects Demo](spritePro/demoGames/color_effects_demo.py) - Dynamic color effects showcase
- [Color Text Demo](spritePro/demoGames/color_text_demo.py) - Text with color effects
- [FPS Camera Demo](spritePro/demoGames/fps_camera_demo/fps_camera_demo.py) - FPS counter and camera system
- [Text FPS Demo](spritePro/demoGames/text_fps_demo.py) - Ready-to-use FPS counter showcase
- [Save/Load Demo](spritePro/demoGames/save_load_demo.py) - Comprehensive save and load system demonstration

## 🛠️ Requirements

- Python 3.7+
- Pygame 2.0+
- Optional: Pymunk (for advanced physics)

## 📖 API Reference

For detailed API documentation, visit our [documentation folder](docs/).

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues, feature requests, or pull requests.

## 📄 License

This project is open source. Please check the license file for more information.

Start working with SpritePro today and bring your game ideas to life! 🚀