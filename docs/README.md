# SpritePro Documentation

Welcome to SpritePro documentation! Here you will find detailed information about all modules and components of the library.

## Module Overview

SpritePro consists of several core modules, each providing specific functionality for game development.

### Core Components

#### [Sprite](sprite.md)
Base sprite class with core functionality: positioning, rendering, updating, and component management.

#### [GameSprite](gameSprite.md) 
Extended sprite with game logic, including health system, mouse interaction, and additional game capabilities.

#### [PhysicSprite](physicSprite.md)
Sprite with physics support: gravity, velocity, acceleration, friction, and collision detection.

### UI Components

#### [Button](button.md)
Interactive button with support for different states (normal, hover, pressed) and event handling.

#### [ToggleButton](toggle_button.md)
Toggle button that switches between ON/OFF states with different colors and text labels.

#### [Text](text.md)
Component for text rendering and management with support for different fonts, sizes, and colors.

#### [Mouse Interactor](mouse_interactor.md)
Component for handling mouse interaction: hover detection, clicks, and other mouse events.

### Game Systems

#### [Animation](animation.md)
Animation system with support for states, frames, parallel animations, and tweening integration.

#### [Tween](tween.md)
System for smooth transitions and animations with various easing types and time management.

#### [Timer](timer.md)
Timer system for precise time management in games: countdowns, delays, repeating events.

#### [Health](health.md)
Health management system: damage, healing, regeneration, maximum health, and death handling.

### Utilities

#### [Surface](surface.md)
Set of utilities for working with Pygame surfaces: rounded corners, masking, and other effects.

#### [Color Effects](color_effects.md)
Dynamic color effects and animations: pulse, rainbow, breathing, wave, and other visual effects.

### Ready Sprites

#### [Text_fps](text_fps.md)
Ready-to-use FPS counter sprite that automatically displays and updates frame rate with customizable appearance.

## Quick Navigation

### By Functionality Type

**Base Components:**
- [Sprite](sprite.md) - Foundation of all game objects
- [GameSprite](gameSprite.md) - Game objects with logic
- [PhysicSprite](physicSprite.md) - Objects with physics

**User Interface:**
- [Button](button.md) - Interactive buttons
- [ToggleButton](toggle_button.md) - Toggle switches
- [Text](text.md) - Text elements
- [Mouse Interactor](mouse_interactor.md) - Mouse handling

**Animation and Effects:**
- [Animation](animation.md) - Frame-based animation
- [Tween](tween.md) - Smooth transitions

**Game Logic:**
- [Timer](timer.md) - Time management
- [Health](health.md) - Health system

**Helper Tools:**
- [Surface](surface.md) - Surface operations
- [Color Effects](color_effects.md) - Dynamic color effects and utilities

**Ready Sprites:**
- [Text_fps](text_fps.md) - Automatic FPS counter display

## Usage Examples

Each module contains detailed usage examples and API explanations. It's recommended to start with [Sprite](sprite.md) as the foundation, then study specialized components based on your needs.

## Module Integration

SpritePro modules are designed to work together. For example:
- `GameSprite` can use `Health`, `MouseInteractor`, and `Timer` components
- `Animation` can integrate with `Tween` to create complex effects
- `PhysicSprite` can use `Timer` for temporary effects

Study the documentation of each module to understand integration possibilities.