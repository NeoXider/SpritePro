# FPS and Camera Demo

This demo showcases advanced SpritePro features including real-time FPS monitoring and camera system implementation.

## Features

### FPS Display
- Real-time FPS counter using TextSprite
- Averaged FPS calculation over 60 frames
- Performance monitoring with object count and frame counter

### Camera System
- 2D camera with smooth movement
- Arrow key controls (↑↓←→)
- Camera position display
- Proper world-to-screen coordinate transformation

### World Objects
- Grid of colored squares
- Random circles scattered around
- Text labels at various locations
- Reference grid for navigation

### Performance Features
- Frustum culling (only draws visible objects)
- Efficient coordinate transformation
- Delta time-based movement

## Controls

- **Arrow Keys**: Move camera around the world
- **R**: Reset camera to origin (0, 0)
- **ESC**: Exit demo

## Technical Implementation

### Camera Class
```python
class Camera:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.speed = 200  # pixels per second
    
    def apply(self, pos):
        """Apply camera offset to a position."""
        return (pos[0] - self.x, pos[1] - self.y)
```

### FPS Calculation
- Uses SpritePro's built-in delta time (`s.dt`)
- Maintains rolling average over 60 frames
- Updates TextSprite in real-time

### World Coordinate System
- Objects have world positions independent of camera
- Camera transforms world coordinates to screen coordinates
- Efficient culling prevents off-screen rendering

## Usage

Run the demo:
```bash
python fps_camera_demo.py
```

Navigate around the world using arrow keys and observe:
- FPS counter in top-left corner
- Camera position updates
- Smooth scrolling of world objects
- Performance metrics

This demo is perfect for understanding:
- Game camera implementation
- Performance monitoring
- Coordinate system transformations
- Efficient rendering techniques