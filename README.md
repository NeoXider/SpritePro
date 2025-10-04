# SpritePro

SpritePro - a powerful and flexible game development library built on top of Pygame. Provides a comprehensive set of tools for creating 2D games with advanced capabilities.
![gg0c31829550](https://github.com/user-attachments/assets/db56e1fd-0db5-4353-945d-c4a31c6b9d7f)

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
import spritePro as s
import pygame

# Initialize the library
s.init()

# Create a window
s.get_screen((800, 600), "My Game")

# Create a basic sprite
player = s.Sprite(
    "",
    size=(100, 100),
    pos=s.WH_C,
    speed=3,
)

# Main game loop
while True:
    s.update(fill_color=(0, 0, 100))
    player.handle_keyboard_input()
    player.update()
```

### PlayerPrefs Quick Save
### Camera Helpers

SpriteProGame управляет глобальной камерой. Для перемещения достаточно вызвать `s.process_camera_input()` и передать скорость или свои клавиши. Для слежения за объектом используйте `s.set_camera_follow(sprite, offset=(0, 0))`; `s.clear_camera_follow()` возвращает ручной режим. Внутри `s.update(...)` камера обновляется автоматически, поэтому дополнительный код не требуется.

### Particle Emitter

Модуль `spritePro.particles` предоставляет `ParticleEmitter`. Создайте конфигурацию `ParticleConfig`, затем вызовите `emit(position)` для быстрого запуска эффекта. Частицы — полноценные `Sprite`, поддерживающие камеру и `set_screen_space`.


SpritePro �������� ����� ���� ������ ������� ���������� � `PlayerPrefs`. �� ��������� ������ � ���������� ������� �������� (�����, ������ � ����������) ����� ������� � ���������� ��� �� ������ JSON, ��� � ��������� �������.

```python
import spritePro as s

# �������������
s.init()
s.get_screen((800, 600), "My Game")

# ������ ���� ������������ ��� �������
prefs = s.PlayerPrefs("quick_start_state.json")

# ��������� ����������� ��������� ������
player_pos = prefs.get_vector2("player_pos", s.WH_C)

# ... ������ ������ � ������� ��� ...

# ��������� ���������� ������
prefs.set_vector2("player_pos", (player.rect.x, player.rect.y))
prefs.set_float("audio/master", 0.75)
prefs.set_string("profile/name", "Hero")
```

`PlayerPrefs` ����� ������� ����� �����, ������� ������ ������������ �� ����� �������� (`audio/master`, `profile/name`). ������ ������������ `SaveLoadManager`, ��� ��� ������ ����� � ������� JSON-����� ��� ������ ������������.

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
- [Camera & Particles](docs/camera_and_particles.md) - Camera helpers and configurable particle emitter

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
- [Fireworks Demo](spritePro/demoGames/fireworks_demo.py) - Camera controls and particle emitter in action
- [Particle Demo](spritePro/demoGames/particle_demo.py) - Minimal example of ParticleEmitter usage
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
