"""Level Editor for SpritePro - Place sprites and save as JSON"""
import json
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import pygame

@dataclass
class SpriteData:
    """Represents a sprite on the level with its properties"""
    id: int
    x: float
    y: float
    width: float
    height: float
    image_path: str
    visible: bool = True

class LevelEditor:
    """Main level editor class"""
    def __init__(self, width: int = 800, height: int = 600):
        """Инициализирует редактор уровней с размерами сцены."""
        self.width = width
        self.height = height
        self.sprites: List[SpriteData] = []
        self.next_id = 1
        self.selected_sprite: Optional[int] = None
        
    def add_sprite(self, x: float, y: float, width: float, height: float, image_path: str) -> int:
        """Add a sprite to the level"""
        sprite = SpriteData(
            id=self.next_id,
            x=x,
            y=y,
            width=width,
            height=height,
            image_path=image_path
        )
        self.sprites.append(sprite)
        self.next_id += 1
        return sprite.id
        
    def remove_sprite(self, sprite_id: int) -> bool:
        """Remove a sprite by id"""
        for i, sprite in enumerate(self.sprites):
            if sprite.id == sprite_id:
                self.sprites.pop(i)
                return True
        return False
        
    def update_sprite(self, sprite_id: int, **kwargs) -> bool:
        """Update sprite properties"""
        for sprite in self.sprites:
            if sprite.id == sprite_id:
                for key, value in kwargs.items():
                    setattr(sprite, key, value)
                return True
        return False
        
    def get_sprite(self, sprite_id: int) -> Optional[SpriteData]:
        """Get a sprite by id"""
        for sprite in self.sprites:
            if sprite.id == sprite_id:
                return sprite
        return None
        
    def clear(self):
        """Clear all sprites"""
        self.sprites.clear()
        self.next_id = 1
        self.selected_sprite = None
        
    def save_to_json(self, filename: str):
        """Save level to JSON file"""
        data = {
            'width': self.width,
            'height': self.height,
            'sprites': [asdict(sprite) for sprite in self.sprites]
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
            
    def load_from_json(self, filename: str):
        """Load level from JSON file"""
        with open(filename, 'r') as f:
            data = json.load(f)
        self.width = data.get('width', self.width)
        self.height = data.get('height', self.height)
        self.sprites = []
        for sprite_data in data.get('sprites', []):
            sprite = SpriteData(**sprite_data)
            self.sprites.append(sprite)
        # Update next_id to be greater than all existing ids
        if self.sprites:
            max_id = max(sprite.id for sprite in self.sprites)
            self.next_id = max_id + 1
        else:
            self.next_id = 1
            
    def export_to_dict(self) -> Dict:
        """Export level data to dictionary"""
        return {
            'width': self.width,
            'height': self.height,
            'sprites': [asdict(sprite) for sprite in self.sprites]
        }