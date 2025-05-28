# SpritePro Documentation

Welcome to the comprehensive documentation for SpritePro, a powerful Python game development library built on top of Pygame.

## Quick Navigation

### Core Modules
These are the main sprite classes that form the foundation of SpritePro:

- **[Sprite](sprite.md)** - Base sprite class with movement, visual effects, and state management
- **[GameSprite](gameSprite.md)** - Game sprite with health management and collision handling  
- **[PhysicalSprite](physicSprite.md)** - Physics-enabled sprite with gravity, forces, and realistic movement
- **[Button](button.md)** - Interactive UI button with hover effects and event handling

### Components
Modular components that can be attached to sprites for additional functionality:

- **[Animation](animation.md)** - Frame-based animation system with state management
- **[Health](health.md)** - Comprehensive health management with damage, healing, and regeneration
- **[MouseInteractor](mouse_interactor.md)** - Mouse interaction handling for hover, click, and drag events
- **[Text](text.md)** - Advanced text rendering with custom fonts and dynamic updates
- **[Timer](timer.md)** - Precise timing system for delays, cooldowns, and scheduled events
- **[Tween](tween.md)** - Smooth animation transitions with easing functions

### Utilities
Helper functions and utilities for common game development tasks:

- **[Surface](surface.md)** - Surface manipulation utilities including rounded corners and masking

## Getting Started

If you're new to SpritePro, we recommend starting with these modules in order:

1. **[Sprite](sprite.md)** - Learn the basics of sprite creation and movement
2. **[Text](text.md)** - Add text elements to your game
3. **[Button](button.md)** - Create interactive UI elements
4. **[GameSprite](gameSprite.md)** - Add health and collision systems
5. **[Animation](animation.md)** - Bring your sprites to life with animations

## Advanced Topics

Once you're comfortable with the basics, explore these advanced features:

- **[PhysicalSprite](physicSprite.md)** - Realistic physics simulation
- **[Timer](timer.md)** - Complex timing and scheduling
- **[Tween](tween.md)** - Smooth animations and transitions
- **[Health](health.md)** - Advanced health management systems
- **[MouseInteractor](mouse_interactor.md)** - Custom mouse interactions

## Module Relationships

```
Sprite (Base)
├── GameSprite (+ Health System)
│   └── PhysicalSprite (+ Physics)
└── Button (+ Text + MouseInteractor)

Components (Can be added to any sprite):
├── Animation
├── Health  
├── MouseInteractor
├── Text
├── Timer
└── Tween

Utilities:
└── Surface
```

## Code Examples

### Basic Sprite Setup
```python
import spritePro as s

# Initialize
s.init()
s.get_screen((800, 600), "My Game")

# Create sprite
player = s.Sprite("player.png", pos=(400, 300), speed=5)

# Game loop
while True:
    s.update(fill_color=(0, 0, 100))
    player.update()
```

### Game Entity with Health
```python
# Create game sprite with health
enemy = s.GameSprite(
    "enemy.png",
    max_health=100,
    pos=(200, 200)
)

# Add damage handling
enemy.set_damage_callback(lambda sprite, damage, health: print(f"Ouch! {damage} damage"))
enemy.take_damage(25)
```

### Interactive Button
```python
# Create button with callback
button = s.Button(
    text="Start Game",
    pos=(400, 300),
    on_click=lambda: print("Game started!")
)

button.update()
```

## Language Support

Documentation is available in multiple languages:
- **English**: All modules documented in English
- **Russian**: Selected modules have Russian documentation (animation_ru.md, tween_ru.md)

## Contributing to Documentation

If you'd like to improve the documentation:

1. Each module should have clear examples
2. Include both basic and advanced usage
3. Show integration with other modules
4. Provide performance tips where relevant
5. Keep code examples simple and focused

## Support

For questions about specific modules, refer to their individual documentation pages. For general questions about SpritePro, check the main [README](../../README.md) file.