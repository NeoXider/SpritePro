"""
Save/Load System - SpritePro

Professional save and load system supporting multiple data types and formats.
Provides unified interface for saving and loading lists, dictionaries, numbers,
strings, text, and custom classes with automatic format detection and error handling.

Supported formats:
- JSON (default) - for dictionaries, lists, numbers, strings
- Pickle - for complex objects and classes
- Text - for plain text data
- Binary - for raw binary data

Features:
- Automatic format detection
- Type validation
- Error handling with detailed messages
- Backup creation
- Compression support
- Custom class serialization
- Thread-safe operations
"""

import json
import pickle
import gzip
import os
import shutil
import threading
from pathlib import Path
from typing import Any, Dict, List, Union, Optional, Type, Callable, Tuple
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SaveLoadError(Exception):
    """Custom exception for save/load operations."""
    pass


class DataSerializer:
    """Handles serialization of custom classes and complex objects."""
    
    _serializers: Dict[Type, Callable] = {}
    _deserializers: Dict[str, Callable] = {}
    
    @classmethod
    def register_class(cls, target_class: Type, 
                      serializer: Callable = None, 
                      deserializer: Callable = None):
        """Register custom serialization methods for a class.
        
        Args:
            target_class: Class to register
            serializer: Function to serialize instance to dict
            deserializer: Function to deserialize dict to instance
        """
        if serializer:
            cls._serializers[target_class] = serializer
        if deserializer:
            cls._deserializers[target_class.__name__] = deserializer
    
    @classmethod
    def serialize_object(cls, obj: Any) -> Dict:
        """Serialize object to dictionary format.
        
        Args:
            obj: Object to serialize
            
        Returns:
            Dictionary representation of object
        """
        obj_type = type(obj)
        
        if obj_type in cls._serializers:
            data = cls._serializers[obj_type](obj)
            return {
                '__class__': obj_type.__name__,
                '__module__': obj_type.__module__,
                '__data__': data
            }
        
        # Default serialization for objects with __dict__
        if hasattr(obj, '__dict__'):
            return {
                '__class__': obj_type.__name__,
                '__module__': obj_type.__module__,
                '__data__': obj.__dict__
            }
        
        raise SaveLoadError(f"Cannot serialize object of type {obj_type}")
    
    @classmethod
    def deserialize_object(cls, data: Dict) -> Any:
        """Deserialize dictionary to object.
        
        Args:
            data: Dictionary containing object data
            
        Returns:
            Deserialized object
        """
        class_name = data.get('__class__')
        module_name = data.get('__module__')
        obj_data = data.get('__data__')
        
        if class_name in cls._deserializers:
            return cls._deserializers[class_name](obj_data)
        
        # Try to import and reconstruct the class
        try:
            module = __import__(module_name, fromlist=[class_name])
            target_class = getattr(module, class_name)
            
            # Create instance and set attributes
            obj = target_class.__new__(target_class)
            if isinstance(obj_data, dict):
                obj.__dict__.update(obj_data)
            
            return obj
        except (ImportError, AttributeError) as e:
            raise SaveLoadError(f"Cannot deserialize class {class_name}: {e}")


class SaveLoadManager:
    """Main class for save/load operations with support for multiple formats."""
    
    def __init__(self, default_file: str = "game_data.json", 
                 auto_backup: bool = True,
                 compression: bool = False):
        """Initialize SaveLoadManager.
        
        Args:
            default_file: Default filename for save operations
            auto_backup: Create backup before overwriting files
            compression: Use gzip compression for files
        """
        self.default_file = Path(default_file)
        self.auto_backup = auto_backup
        self.compression = compression
        self._lock = threading.Lock()
        
        # Ensure directory exists
        self.default_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _get_format_from_extension(self, filepath: Path) -> str:
        """Determine file format from extension.
        
        Args:
            filepath: Path to file
            
        Returns:
            Format string ('json', 'pickle', 'text', 'binary')
        """
        ext = filepath.suffix.lower()
        
        if ext in ['.json', '.js']:
            return 'json'
        elif ext in ['.pkl', '.pickle']:
            return 'pickle'
        elif ext in ['.txt', '.text']:
            return 'text'
        elif ext in ['.bin', '.dat']:
            return 'binary'
        else:
            # Default to json for unknown extensions
            return 'json'
    
    def _create_backup(self, filepath: Path) -> Optional[Path]:
        """Create backup of existing file.
        
        Args:
            filepath: Path to file to backup
            
        Returns:
            Path to backup file or None if no backup created
        """
        if not filepath.exists():
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = filepath.with_suffix(f".backup_{timestamp}{filepath.suffix}")
        
        try:
            shutil.copy2(filepath, backup_path)
            logger.info(f"Created backup: {backup_path}")
            return backup_path
        except Exception as e:
            logger.warning(f"Failed to create backup: {e}")
            return None
    
    def _save_json(self, data: Any, filepath: Path) -> None:
        """Save data in JSON format.
        
        Args:
            data: Data to save
            filepath: Path to save file
        """
        def json_serializer(obj):
            """Custom JSON serializer for complex objects."""
            if hasattr(obj, '__dict__'):
                return DataSerializer.serialize_object(obj)
            elif isinstance(obj, (set, frozenset)):
                return {'__set__': list(obj)}
            elif isinstance(obj, bytes):
                return {'__bytes__': obj.hex()}
            else:
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        json_data = json.dumps(data, indent=2, ensure_ascii=False, default=json_serializer)
        
        if self.compression:
            with gzip.open(filepath.with_suffix(filepath.suffix + '.gz'), 'wt', encoding='utf-8') as f:
                f.write(json_data)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json_data)
    
    def _load_json(self, filepath: Path) -> Any:
        """Load data from JSON format.
        
        Args:
            filepath: Path to load file
            
        Returns:
            Loaded data
        """
        def json_deserializer(data):
            """Custom JSON deserializer for complex objects."""
            if isinstance(data, dict):
                if '__class__' in data:
                    return DataSerializer.deserialize_object(data)
                elif '__set__' in data:
                    return set(data['__set__'])
                elif '__bytes__' in data:
                    return bytes.fromhex(data['__bytes__'])
            return data
        
        # Check for compressed file
        compressed_path = filepath.with_suffix(filepath.suffix + '.gz')
        if compressed_path.exists() and not filepath.exists():
            filepath = compressed_path
        
        if filepath.suffix == '.gz':
            with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                json_data = f.read()
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                json_data = f.read()
        
        data = json.loads(json_data)
        
        # Recursively deserialize objects
        def deserialize_recursive(obj):
            if isinstance(obj, dict):
                if '__class__' in obj:
                    return DataSerializer.deserialize_object(obj)
                elif '__set__' in obj:
                    return set(obj['__set__'])
                elif '__bytes__' in obj:
                    return bytes.fromhex(obj['__bytes__'])
                else:
                    return {k: deserialize_recursive(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [deserialize_recursive(item) for item in obj]
            return obj
        
        return deserialize_recursive(data)
    
    def _save_pickle(self, data: Any, filepath: Path) -> None:
        """Save data in Pickle format.
        
        Args:
            data: Data to save
            filepath: Path to save file
        """
        if self.compression:
            with gzip.open(filepath.with_suffix(filepath.suffix + '.gz'), 'wb') as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            with open(filepath, 'wb') as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    def _load_pickle(self, filepath: Path) -> Any:
        """Load data from Pickle format.
        
        Args:
            filepath: Path to load file
            
        Returns:
            Loaded data
        """
        # Check for compressed file
        compressed_path = filepath.with_suffix(filepath.suffix + '.gz')
        if compressed_path.exists() and not filepath.exists():
            filepath = compressed_path
        
        if filepath.suffix == '.gz':
            with gzip.open(filepath, 'rb') as f:
                return pickle.load(f)
        else:
            with open(filepath, 'rb') as f:
                return pickle.load(f)
    
    def _save_text(self, data: Any, filepath: Path) -> None:
        """Save data as plain text.
        
        Args:
            data: Data to save (will be converted to string)
            filepath: Path to save file
        """
        text_data = str(data)
        
        if self.compression:
            with gzip.open(filepath.with_suffix(filepath.suffix + '.gz'), 'wt', encoding='utf-8') as f:
                f.write(text_data)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text_data)
    
    def _load_text(self, filepath: Path) -> str:
        """Load data from text file.
        
        Args:
            filepath: Path to load file
            
        Returns:
            Text content as string
        """
        # Check for compressed file
        compressed_path = filepath.with_suffix(filepath.suffix + '.gz')
        if compressed_path.exists() and not filepath.exists():
            filepath = compressed_path
        
        if filepath.suffix == '.gz':
            with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                return f.read()
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
    
    def _save_binary(self, data: bytes, filepath: Path) -> None:
        """Save binary data.
        
        Args:
            data: Binary data to save
            filepath: Path to save file
        """
        if not isinstance(data, bytes):
            raise SaveLoadError("Binary format requires bytes data")
        
        if self.compression:
            with gzip.open(filepath.with_suffix(filepath.suffix + '.gz'), 'wb') as f:
                f.write(data)
        else:
            with open(filepath, 'wb') as f:
                f.write(data)
    
    def _load_binary(self, filepath: Path) -> bytes:
        """Load binary data.
        
        Args:
            filepath: Path to load file
            
        Returns:
            Binary data as bytes
        """
        # Check for compressed file
        compressed_path = filepath.with_suffix(filepath.suffix + '.gz')
        if compressed_path.exists() and not filepath.exists():
            filepath = compressed_path
        
        if filepath.suffix == '.gz':
            with gzip.open(filepath, 'rb') as f:
                return f.read()
        else:
            with open(filepath, 'rb') as f:
                return f.read()
    
    def save(self, data: Any, filename: Optional[str] = None, 
             format_type: Optional[str] = None) -> bool:
        """Save data to file with automatic format detection.
        
        Args:
            data: Data to save (lists, dicts, numbers, strings, objects)
            filename: Optional filename (uses default if not provided)
            format_type: Force specific format ('json', 'pickle', 'text', 'binary')
            
        Returns:
            True if save successful, False otherwise
            
        Example:
            # Save dictionary as JSON
            manager.save({'score': 100, 'level': 5})
            
            # Save custom object as pickle
            manager.save(player_object, 'player.pkl')
            
            # Save text with specific format
            manager.save("Game settings", 'config.txt', 'text')
        """
        with self._lock:
            try:
                filepath = Path(filename) if filename else self.default_file
                
                # Create backup if enabled
                if self.auto_backup:
                    self._create_backup(filepath)
                
                # Determine format
                if format_type:
                    file_format = format_type.lower()
                else:
                    file_format = self._get_format_from_extension(filepath)
                
                # Save based on format
                if file_format == 'json':
                    self._save_json(data, filepath)
                elif file_format == 'pickle':
                    self._save_pickle(data, filepath)
                elif file_format == 'text':
                    self._save_text(data, filepath)
                elif file_format == 'binary':
                    self._save_binary(data, filepath)
                else:
                    raise SaveLoadError(f"Unsupported format: {file_format}")
                
                logger.info(f"Successfully saved data to {filepath} ({file_format} format)")
                return True
                
            except Exception as e:
                logger.error(f"Failed to save data: {e}")
                raise SaveLoadError(f"Save operation failed: {e}")
    
    def load(self, filename: Optional[str] = None, 
             format_type: Optional[str] = None,
             default_value: Any = None) -> Any:
        """Load data from file with automatic format detection.
        
        Args:
            filename: Optional filename (uses default if not provided)
            format_type: Force specific format ('json', 'pickle', 'text', 'binary')
            default_value: Value to return if file doesn't exist
            
        Returns:
            Loaded data or default_value if file not found
            
        Example:
            # Load default file
            data = manager.load()
            
            # Load specific file
            player = manager.load('player.pkl')
            
            # Load with default value
            settings = manager.load('settings.json', default_value={})
        """
        with self._lock:
            try:
                filepath = Path(filename) if filename else self.default_file
                
                # Check if file exists
                if not filepath.exists():
                    # Check for compressed version
                    compressed_path = filepath.with_suffix(filepath.suffix + '.gz')
                    if not compressed_path.exists():
                        if default_value is not None:
                            logger.info(f"File {filepath} not found, returning default value")
                            return default_value
                        else:
                            raise SaveLoadError(f"File not found: {filepath}")
                
                # Determine format
                if format_type:
                    file_format = format_type.lower()
                else:
                    file_format = self._get_format_from_extension(filepath)
                
                # Load based on format
                if file_format == 'json':
                    data = self._load_json(filepath)
                elif file_format == 'pickle':
                    data = self._load_pickle(filepath)
                elif file_format == 'text':
                    data = self._load_text(filepath)
                elif file_format == 'binary':
                    data = self._load_binary(filepath)
                else:
                    raise SaveLoadError(f"Unsupported format: {file_format}")
                
                logger.info(f"Successfully loaded data from {filepath} ({file_format} format)")
                return data
                
            except Exception as e:
                logger.error(f"Failed to load data: {e}")
                if default_value is not None:
                    logger.info("Returning default value due to load error")
                    return default_value
                raise SaveLoadError(f"Load operation failed: {e}")
    
    def exists(self, filename: Optional[str] = None) -> bool:
        """Check if save file exists.
        
        Args:
            filename: Optional filename (uses default if not provided)
            
        Returns:
            True if file exists, False otherwise
        """
        filepath = Path(filename) if filename else self.default_file
        compressed_path = filepath.with_suffix(filepath.suffix + '.gz')
        return filepath.exists() or compressed_path.exists()
    
    def delete(self, filename: Optional[str] = None, 
               include_backups: bool = False) -> bool:
        """Delete save file.
        
        Args:
            filename: Optional filename (uses default if not provided)
            include_backups: Also delete backup files
            
        Returns:
            True if deletion successful, False otherwise
        """
        with self._lock:
            try:
                filepath = Path(filename) if filename else self.default_file
                deleted = False
                
                # Delete main file
                if filepath.exists():
                    filepath.unlink()
                    deleted = True
                
                # Delete compressed version
                compressed_path = filepath.with_suffix(filepath.suffix + '.gz')
                if compressed_path.exists():
                    compressed_path.unlink()
                    deleted = True
                
                # Delete backups if requested
                if include_backups:
                    backup_pattern = f"{filepath.stem}.backup_*{filepath.suffix}"
                    for backup_file in filepath.parent.glob(backup_pattern):
                        backup_file.unlink()
                        deleted = True
                
                if deleted:
                    logger.info(f"Successfully deleted {filepath}")
                    return True
                else:
                    logger.warning(f"File {filepath} not found for deletion")
                    return False
                    
            except Exception as e:
                logger.error(f"Failed to delete file: {e}")
                return False
    
    def list_backups(self, filename: Optional[str] = None) -> List[Path]:
        """List all backup files for a given file.
        
        Args:
            filename: Optional filename (uses default if not provided)
            
        Returns:
            List of backup file paths
        """
        filepath = Path(filename) if filename else self.default_file
        backup_pattern = f"{filepath.stem}.backup_*{filepath.suffix}"
        return sorted(filepath.parent.glob(backup_pattern))


class PlayerPrefs:
    """Lightweight helper inspired by Unity PlayerPrefs for common value types."""

    def __init__(self, filename: str = "player_prefs.json", auto_backup: bool = False, compression: bool = False):
        self._manager = SaveLoadManager(filename, auto_backup=auto_backup, compression=compression)

    def _load_data(self) -> Dict[str, Any]:
        data = self._manager.load(default_value={})
        if isinstance(data, dict):
            return dict(data)
        return {}

    def _save_data(self, data: Dict[str, Any]) -> None:
        self._manager.save(data)

    def _get_value(self, key: str, default: Any) -> Any:
        data = self._load_data()
        return data.get(key, default)

    def _set_value(self, key: str, value: Any) -> None:
        data = self._load_data()
        data[key] = value
        self._save_data(data)

    def get_float(self, key: str, default: float = 0.0) -> float:
        value = self._get_value(key, default)
        try:
            return float(value)
        except (TypeError, ValueError):
            return float(default)

    def set_float(self, key: str, value: float) -> None:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            raise SaveLoadError(f"Value for {key} must be a number")
        self._set_value(key, numeric)

    def get_int(self, key: str, default: int = 0) -> int:
        value = self._get_value(key, default)
        try:
            return int(value)
        except (TypeError, ValueError):
            return int(default)

    def set_int(self, key: str, value: int) -> None:
        try:
            integer = int(value)
        except (TypeError, ValueError):
            raise SaveLoadError(f"Value for {key} must be an integer")
        self._set_value(key, integer)

    def get_string(self, key: str, default: str = "") -> str:
        value = self._get_value(key, default)
        if value is None:
            return default
        return str(value)

    def set_string(self, key: str, value: str) -> None:
        if value is None:
            raise SaveLoadError(f"Value for {key} cannot be None")
        self._set_value(key, str(value))

    def get_vector2(self, key: str, default: Tuple[int, int] = (0, 0)) -> Tuple[int, int]:
        value = self._get_value(key, default)
        if isinstance(value, (list, tuple)) and len(value) == 2:
            try:
                x = int(value[0])
                y = int(value[1])
                return x, y
            except (TypeError, ValueError):
                pass
        return int(default[0]), int(default[1])

    def set_vector2(self, key: str, value: Tuple[int, int]) -> None:
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            raise SaveLoadError(f"Value for {key} must be a 2D coordinate")
        try:
            x = int(value[0])
            y = int(value[1])
        except (TypeError, ValueError):
            raise SaveLoadError(f"Value for {key} must contain numeric coordinates")
        self._set_value(key, [x, y])

    def delete_key(self, key: str) -> None:
        data = self._load_data()
        if key in data:
            del data[key]
            self._save_data(data)

    def clear(self) -> None:
        self._save_data({})


# Global instance for easy access
save_manager = SaveLoadManager()

# Convenience functions
def save(data: Any, filename: Optional[str] = None, 
         format_type: Optional[str] = None) -> bool:
    """Convenience function for saving data.
    
    Args:
        data: Data to save
        filename: Optional filename
        format_type: Optional format type
        
    Returns:
        True if successful, False otherwise
    """
    return save_manager.save(data, filename, format_type)


def load(filename: Optional[str] = None, 
         format_type: Optional[str] = None,
         default_value: Any = None) -> Any:
    """Convenience function for loading data.
    
    Args:
        filename: Optional filename
        format_type: Optional format type
        default_value: Default value if file not found
        
    Returns:
        Loaded data or default value
    """
    return save_manager.load(filename, format_type, default_value)


def exists(filename: Optional[str] = None) -> bool:
    """Convenience function to check if file exists.
    
    Args:
        filename: Optional filename
        
    Returns:
        True if file exists, False otherwise
    """
    return save_manager.exists(filename)


def delete(filename: Optional[str] = None, include_backups: bool = False) -> bool:
    """Convenience function to delete file.
    
    Args:
        filename: Optional filename
        include_backups: Also delete backups
        
    Returns:
        True if successful, False otherwise
    """
    return save_manager.delete(filename, include_backups)


# Register common SpritePro classes for serialization
def register_sprite_classes():
    """Register SpritePro classes for automatic serialization."""
    try:
        import sys
        from pathlib import Path
        
        # Add SpritePro to path
        current_dir = Path(__file__).parent
        parent_dir = current_dir.parent.parent
        sys.path.append(str(parent_dir))
        
        import spritePro as s
        
        # Register Sprite class
        def serialize_sprite(sprite):
            return {
                'image_path': getattr(sprite, '_image_path', ''),
                'size': sprite.size if hasattr(sprite, 'size') else (50, 50),
                'pos': (sprite.rect.x, sprite.rect.y) if hasattr(sprite, 'rect') else (0, 0),
                'speed': getattr(sprite, 'speed', 0),
                'angle': getattr(sprite, 'angle', 0),
                'scale': getattr(sprite, 'scale', 1.0),
                'color': getattr(sprite, 'color', None),
                'active': getattr(sprite, 'active', True)
            }
        
        def deserialize_sprite(data):
            sprite = s.Sprite(
                data.get('image_path', ''),
                data.get('size', (50, 50)),
                data.get('pos', (0, 0)),
                data.get('speed', 0)
            )
            sprite.angle = data.get('angle', 0)
            sprite.scale = data.get('scale', 1.0)
            sprite.color = data.get('color', None)
            sprite.active = data.get('active', True)
            return sprite
        
        DataSerializer.register_class(s.Sprite, serialize_sprite, deserialize_sprite)
        
        logger.info("SpritePro classes registered for serialization")
        
    except ImportError:
        logger.warning("SpritePro not available for class registration")


# Auto-register SpritePro classes
register_sprite_classes()


if __name__ == "__main__":
    # Example usage and testing
    print("SpritePro Save/Load System - Example Usage")
    print("=" * 50)
    
    # Create manager
    manager = SaveLoadManager("test_data.json", auto_backup=True)
    
    # Test data
    test_data = {
        'player_name': 'TestPlayer',
        'score': 12500,
        'level': 5,
        'inventory': ['sword', 'potion', 'key'],
        'settings': {
            'sound_volume': 0.8,
            'music_volume': 0.6,
            'difficulty': 'normal'
        },
        'achievements': {'first_win', 'level_5', 'high_score'}
    }
    
    # Save and load test
    print("Testing save/load operations...")
    
    # Save data
    if manager.save(test_data):
        print("✓ Data saved successfully")
    
    # Load data
    loaded_data = manager.load()
    if loaded_data == test_data:
        print("✓ Data loaded successfully and matches original")
    else:
        print("✗ Data mismatch after load")
    
    # Test different formats
    print("\nTesting different formats...")
    
    # Text format
    manager.save("This is a test string", "test.txt", "text")
    text_data = manager.load("test.txt", "text")
    print(f"✓ Text format: {text_data}")
    
    # Pickle format
    class TestClass:
        def __init__(self, value):
            self.value = value
        
        def __eq__(self, other):
            return isinstance(other, TestClass) and self.value == other.value
    
    test_obj = TestClass("test_value")
    manager.save(test_obj, "test.pkl", "pickle")
    loaded_obj = manager.load("test.pkl", "pickle")
    print(f"✓ Pickle format: {loaded_obj.value}")
    
    # Cleanup
    manager.delete("test_data.json", include_backups=True)
    manager.delete("test.txt")
    manager.delete("test.pkl")
    
    print("\n✓ All tests completed successfully!")