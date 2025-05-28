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

## 🎯 Demo Games

Explore our demo games to see SpritePro in action:

- [Animation Demo](spritePro/demoGames/animationDemo.py) - Sprite animation demonstration
- [Physics Demo](spritePro/demoGames/demo_physics.py) - Physics simulation example
- [Pymunk Demo](spritePro/demoGames/demo_pymunk.py) - Advanced physics with Pymunk
- [Ping Pong](spritePro/demoGames/ping_pong.py) - Classic Pong game
- [Tweening Demo](spritePro/demoGames/tweenDemo.py) - Animation tweening examples
- [Toggle Demo](spritePro/demoGames/toggle_demo.py) - Interactive toggle buttons showcase

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