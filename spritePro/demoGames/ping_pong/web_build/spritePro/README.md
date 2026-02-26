# SpritePro Level Editor Documentation

## Overview
SpritePro Level Editor is a powerful tool for creating and managing game levels by placing sprites on a grid-based layout.

## Features
- **Grid-based level design** - Place sprites in a structured grid system
- **Multiple sprite types** - Use various ready-made sprites from the library
- **Save/Load functionality** - Save levels as JSON files and load them back

## Available Sprites
The editor includes several pre-configured sprites:
1. bg (background)
2. hero 
3. enemy  
4. ball
5. platforma
6. barrier
7. canister

## Controls
### Keyboard Shortcuts
- **S** - Save current level to `demo_level.json`
- **L** - Load level from `demo_level.json`  
- **C** - Clear all sprites from the level
- Number keys 1-5: Select sprite type (1=bg, 2=hero, etc.)

### Mouse Controls
- Left click: Place selected sprite at mouse position
- Right click: Remove sprite at mouse position

## Usage Example
```python
# Start the level editor
editor = LevelEditorUI()
editor.run()
```

The editor will open a window where you can:
1. Select sprites from the list on the right side
2. Click to place them on the grid
3. Save your creation as JSON file
4. Load previously saved levels

## Saving and Loading Levels
- **Save**: Press 'S' key or click "Save Level" button
- **Load**: Press 'L' key or click "Load Level" button

The editor automatically saves to `demo_level.json` in the current directory.

## Technical Details
- Uses SpritePro's built-in sprite system for rendering
- Grid size: 10x8 tiles (80x60 pixels per tile)
- Save format: JSON with sprite data including position, type, and properties