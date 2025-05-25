# spritePro

[Русская версия](README.ru.md)

A powerful and flexible Python game development library built on top of Pygame, created by neoxider.

## Overview

spritePro is a comprehensive game development framework that provides a rich set of tools and components for creating 2D games in Python. It extends Pygame's functionality with advanced sprite management, physics, UI components, and utility functions.

## Features

### Core Features
- **Advanced Sprite System**: Base sprite class with built-in support for:
  - Movement and velocity control
  - Rotation and scaling
  - Transparency and color tinting
  - State management
  - Collision detection
  - Movement boundaries

### Physics System
- **Physics Integration**: Physics-based sprites with:
  - Real-world units (meters, m/s, m/s²)
  - Gravity and ground detection
  - Force application and acceleration
  - Bouncing mechanics
  - Ground friction
  - Collision resolution

### Game Components
- **Text System**: Advanced text rendering with:
  - Custom fonts support
  - Color and size control
  - Text input handling
  - Dynamic updates

- **Button System**: Interactive UI buttons featuring:
  - Hover and press animations
  - Customizable appearance
  - Event callbacks
  - Text label support

- **Timer System**: Precise timing control with:
  - Callback support
  - Pause/resume functionality
  - Repeating timers
  - Progress tracking

- **Health System**: Comprehensive health management:
  - Health tracking
  - Damage/healing mechanics
  - Death state management
  - Event callbacks

- **Mouse Interaction**: Advanced mouse handling:
  - Hover detection
  - Click/press tracking
  - Custom event callbacks
  - Automatic state updates

### Utility Functions
- Surface manipulation
- Collision detection helpers
- Resource management
- Game state utilities

## Installation

Currently, spritePro is not available through pip. To use it in your project:

1. Clone the repository or download the `spritePro` folder
2. Place the `spritePro` folder in your project directory
3. Import it in your code:
```python
import spritePro
```

Note: In the future, spritePro will be available through pip installation.

## Quick Start

```python
import spritePro

# Initialize the library
spritePro.init()

# Create a window
spritePro.get_screen((800, 600), "My Game")

# Create a basic sprite
player = spritePro.Sprite("player.png", size=(50, 50), pos=(400, 300))

# Main game loop
while True:
    spritePro.update()
    player.update(spritePro.screen)
```

## Examples

### Basic Sprite
```python
# Create a sprite with custom properties
sprite = spritePro.Sprite(
    "sprite.png",
    size=(100, 100),
    pos=(400, 300),
    speed=5
)

# Add movement and effects
sprite.move_towards((500, 400))
sprite.set_scale(1.5)
sprite.set_alpha(200)
```

### Physics Sprite
```python
# Create a physics-enabled sprite
physics_sprite = spritePro.PhysicalSprite(
    "ball.png",
    mass=1.0,
    gravity=9.8,
    bounce_enabled=True
)

# Apply forces and handle physics
physics_sprite.apply_force(pygame.math.Vector2(10, 0))
physics_sprite.update_physics(60)
```

### UI Components
```python
# Create a button
button = spritePro.Button(
    text="Click Me",
    pos=(400, 300),
    on_click=lambda: print("Clicked!")
)

# Create text
text = spritePro.TextSprite(
    text="Hello World",
    font_size=32,
    color=(255, 255, 255)
)
```

## Documentation

For detailed documentation on how to use spritePro, please refer to the [Documentation](DOCUMENTATION.md) file.

## Demo Games

spritePro comes with a demo game showcasing its capabilities:

**Ping Pong**: Classic ping pong game with physics

![Demo Game](https://github.com/user-attachments/assets/153ddc64-18d7-4d8a-b0c2-baa12b4e77bc)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Created by neoxider

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Contributing Guidelines
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

If you encounter any issues or have questions, please:
1. Check the [Documentation](DOCUMENTATION.md)
2. Search for existing issues
3. Create a new issue if needed

## Acknowledgments

- Thanks to the Pygame community for their excellent work
- Special thanks to all contributors who have helped improve spritePro


![image](https://github.com/user-attachments/assets/153ddc64-18d7-4d8a-b0c2-baa12b4e77bc)
![image](https://github.com/user-attachments/assets/ca405e6c-06b7-4494-8c8c-8a04fb173e8d)


![image](https://github.com/user-attachments/assets/feef0139-9605-4890-a28f-9c7f7e1f4e5a)
![image](https://github.com/user-attachments/assets/12998d5d-cf32-46c3-806b-49d9f37c1a29)
![image](https://github.com/user-attachments/assets/e8034e50-7724-4456-aaa4-ff75fa7447e5)
![image](https://github.com/user-attachments/assets/599fa2e8-e57a-4822-bebb-6b424d50fd86)
![image](https://github.com/user-attachments/assets/c7a00c20-3e8a-438e-8e84-08e260217d81)
![image](https://github.com/user-attachments/assets/43b29fbc-957a-4da0-9753-80f2a632d55e)








