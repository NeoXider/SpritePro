"""Система сохранения/загрузки для SpritePro.

Профессиональная система сохранения и загрузки, поддерживающая различные типы данных и форматы.
Предоставляет унифицированный интерфейс для сохранения и загрузки списков, словарей, чисел,
строк, текста и пользовательских классов с автоматическим определением формата и обработкой ошибок.

Поддерживаемые форматы:
- JSON (по умолчанию) - для словарей, списков, чисел, строк
- Pickle - для сложных объектов и классов
- Text - для обычных текстовых данных
- Binary - для сырых бинарных данных

Возможности:
- Автоматическое определение формата
- Валидация типов
- Обработка ошибок с подробными сообщениями
- Создание резервных копий
- Поддержка сжатия
- Сериализация пользовательских классов
- Потокобезопасные операции
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
    """Пользовательское исключение для операций сохранения/загрузки."""
    pass


class DataSerializer:
    """Обрабатывает сериализацию пользовательских классов и сложных объектов.
    
    Attributes:
        _serializers (Dict[Type, Callable]): Словарь сериализаторов для классов.
        _deserializers (Dict[str, Callable]): Словарь десериализаторов для классов.
    """
    
    _serializers: Dict[Type, Callable] = {}
    _deserializers: Dict[str, Callable] = {}
    
    @classmethod
    def register_class(cls, target_class: Type, 
                      serializer: Callable = None, 
                      deserializer: Callable = None):
        """Регистрирует пользовательские методы сериализации для класса.
        
        Args:
            target_class (Type): Класс для регистрации.
            serializer (Callable, optional): Функция для сериализации экземпляра в словарь.
            deserializer (Callable, optional): Функция для десериализации словаря в экземпляр.
        """
        if serializer:
            cls._serializers[target_class] = serializer
        if deserializer:
            cls._deserializers[target_class.__name__] = deserializer
    
    @classmethod
    def serialize_object(cls, obj: Any) -> Dict:
        """Сериализует объект в формат словаря.
        
        Args:
            obj (Any): Объект для сериализации.
            
        Returns:
            Dict: Словарное представление объекта.
            
        Raises:
            SaveLoadError: Если объект не может быть сериализован.
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
        """Десериализует словарь в объект.
        
        Args:
            data (Dict): Словарь, содержащий данные объекта.
            
        Returns:
            Any: Десериализованный объект.
            
        Raises:
            SaveLoadError: Если объект не может быть десериализован.
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
    """Основной класс для операций сохранения/загрузки с поддержкой нескольких форматов.
    
    Attributes:
        default_file (Path): Путь к файлу по умолчанию для операций сохранения.
        auto_backup (bool): Создавать ли резервную копию перед перезаписью файлов.
        compression (bool): Использовать ли сжатие gzip для файлов.
        _lock (threading.Lock): Блокировка для потокобезопасности.
    """
    
    def __init__(self, default_file: str = "game_data.json", 
                 auto_backup: bool = True,
                 compression: bool = False):
        """Инициализирует SaveLoadManager.
        
        Args:
            default_file (str, optional): Имя файла по умолчанию для операций сохранения. По умолчанию "game_data.json".
            auto_backup (bool, optional): Создавать ли резервную копию перед перезаписью файлов. По умолчанию True.
            compression (bool, optional): Использовать ли сжатие gzip для файлов. По умолчанию False.
        """
        self.default_file = Path(default_file)
        self.auto_backup = auto_backup
        self.compression = compression
        self._lock = threading.Lock()
        
        # Ensure directory exists
        self.default_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _get_format_from_extension(self, filepath: Path) -> str:
        """Определяет формат файла по расширению.
        
        Args:
            filepath (Path): Путь к файлу.
            
        Returns:
            str: Строка формата ('json', 'pickle', 'text', 'binary').
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
        """Создает резервную копию существующего файла.
        
        Args:
            filepath (Path): Путь к файлу для резервного копирования.
            
        Returns:
            Optional[Path]: Путь к файлу резервной копии или None, если копия не создана.
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
        """Сохраняет данные в формате JSON.
        
        Args:
            data (Any): Данные для сохранения.
            filepath (Path): Путь к файлу для сохранения.
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
        """Загружает данные из формата JSON.
        
        Args:
            filepath (Path): Путь к файлу для загрузки.
            
        Returns:
            Any: Загруженные данные.
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
        """Сохраняет данные в формате Pickle.
        
        Args:
            data (Any): Данные для сохранения.
            filepath (Path): Путь к файлу для сохранения.
        """
        if self.compression:
            with gzip.open(filepath.with_suffix(filepath.suffix + '.gz'), 'wb') as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            with open(filepath, 'wb') as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    def _load_pickle(self, filepath: Path) -> Any:
        """Загружает данные из формата Pickle.
        
        Args:
            filepath (Path): Путь к файлу для загрузки.
            
        Returns:
            Any: Загруженные данные.
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
        """Сохраняет данные как обычный текст.
        
        Args:
            data (Any): Данные для сохранения (будут преобразованы в строку).
            filepath (Path): Путь к файлу для сохранения.
        """
        text_data = str(data)
        
        if self.compression:
            with gzip.open(filepath.with_suffix(filepath.suffix + '.gz'), 'wt', encoding='utf-8') as f:
                f.write(text_data)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text_data)
    
    def _load_text(self, filepath: Path) -> str:
        """Загружает данные из текстового файла.
        
        Args:
            filepath (Path): Путь к файлу для загрузки.
            
        Returns:
            str: Текстовое содержимое в виде строки.
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
        """Сохраняет бинарные данные.
        
        Args:
            data (bytes): Бинарные данные для сохранения.
            filepath (Path): Путь к файлу для сохранения.
            
        Raises:
            SaveLoadError: Если данные не являются байтами.
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
        """Загружает бинарные данные.
        
        Args:
            filepath (Path): Путь к файлу для загрузки.
            
        Returns:
            bytes: Бинарные данные в виде байтов.
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
        """Сохраняет данные в файл с автоматическим определением формата.
        
        Args:
            data (Any): Данные для сохранения (списки, словари, числа, строки, объекты).
            filename (Optional[str], optional): Имя файла (используется значение по умолчанию, если не указано).
            format_type (Optional[str], optional): Принудительный формат ('json', 'pickle', 'text', 'binary').
            
        Returns:
            bool: True, если сохранение успешно, False в противном случае.
            
        Raises:
            SaveLoadError: Если операция сохранения не удалась.
            
        Example:
            # Сохранить словарь как JSON
            manager.save({'score': 100, 'level': 5})
            
            # Сохранить пользовательский объект как pickle
            manager.save(player_object, 'player.pkl')
            
            # Сохранить текст с указанным форматом
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
        """Загружает данные из файла с автоматическим определением формата.
        
        Args:
            filename (Optional[str], optional): Имя файла (используется значение по умолчанию, если не указано).
            format_type (Optional[str], optional): Принудительный формат ('json', 'pickle', 'text', 'binary').
            default_value (Any, optional): Значение для возврата, если файл не существует.
            
        Returns:
            Any: Загруженные данные или default_value, если файл не найден.
            
        Raises:
            SaveLoadError: Если операция загрузки не удалась и default_value не указан.
            
        Example:
            # Загрузить файл по умолчанию
            data = manager.load()
            
            # Загрузить конкретный файл
            player = manager.load('player.pkl')
            
            # Загрузить со значением по умолчанию
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
        """Проверяет, существует ли файл сохранения.
        
        Args:
            filename (Optional[str], optional): Имя файла (используется значение по умолчанию, если не указано).
            
        Returns:
            bool: True, если файл существует, False в противном случае.
        """
        filepath = Path(filename) if filename else self.default_file
        compressed_path = filepath.with_suffix(filepath.suffix + '.gz')
        return filepath.exists() or compressed_path.exists()
    
    def delete(self, filename: Optional[str] = None, 
               include_backups: bool = False) -> bool:
        """Удаляет файл сохранения.
        
        Args:
            filename (Optional[str], optional): Имя файла (используется значение по умолчанию, если не указано).
            include_backups (bool, optional): Также удалить файлы резервных копий. По умолчанию False.
            
        Returns:
            bool: True, если удаление успешно, False в противном случае.
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
        """Выводит список всех файлов резервных копий для указанного файла.
        
        Args:
            filename (Optional[str], optional): Имя файла (используется значение по умолчанию, если не указано).
            
        Returns:
            List[Path]: Список путей к файлам резервных копий.
        """
        filepath = Path(filename) if filename else self.default_file
        backup_pattern = f"{filepath.stem}.backup_*{filepath.suffix}"
        return sorted(filepath.parent.glob(backup_pattern))


class PlayerPrefs:
    """Одиночный класс для управления настройками игрока, такими как настройки игры и данные сохранения.
    
    Позволяет хранить и получать различные типы данных, включая целые числа, числа с плавающей точкой,
    строки и булевы значения.
    
    Можно получить экземпляр, вызвав PlayerPrefs(), или использовать методы класса напрямую,
    например PlayerPrefs.get_int("score").
    
    Attributes:
        _instance (PlayerPrefs | None): Единственный экземпляр класса.
        _initialized (bool): Флаг инициализации.
        _manager (SaveLoadManager): Менеджер сохранения/загрузки.
    """
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PlayerPrefs, cls).__new__(cls)
        return cls._instance

    def __init__(self, filename: str = "player_prefs.json", auto_backup: bool = False, compression: bool = False):
        """Инициализирует PlayerPrefs.
        
        Args:
            filename (str, optional): Имя файла для настроек. По умолчанию "player_prefs.json".
            auto_backup (bool, optional): Создавать ли резервные копии автоматически. По умолчанию False.
            compression (bool, optional): Использовать ли сжатие. По умолчанию False.
        """
        if self._initialized:
            return
        self._manager = SaveLoadManager(filename, auto_backup=auto_backup, compression=compression)
        self._initialized = True

    @classmethod
    def _get_instance(cls):
        """Получает единственный экземпляр класса.
        
        Returns:
            PlayerPrefs: Экземпляр PlayerPrefs.
        """
        return cls()

    @classmethod
    def _load_data(cls) -> Dict[str, Any]:
        """Загружает данные настроек.
        
        Returns:
            Dict[str, Any]: Словарь с данными настроек.
        """
        data = cls._get_instance()._manager.load(default_value={})
        if isinstance(data, dict):
            return dict(data)
        return {}

    @classmethod
    def _save_data(cls, data: Dict[str, Any]) -> None:
        """Сохраняет данные настроек.
        
        Args:
            data (Dict[str, Any]): Данные для сохранения.
        """
        cls._get_instance()._manager.save(data)

    @classmethod
    def _get_value(cls, key: str, default: Any) -> Any:
        """Получает значение по ключу.
        
        Args:
            key (str): Ключ для получения значения.
            default (Any): Значение по умолчанию.
            
        Returns:
            Any: Значение по ключу или значение по умолчанию.
        """
        data = cls._load_data()
        return data.get(key, default)

    @classmethod
    def _set_value(cls, key: str, value: Any) -> None:
        """Устанавливает значение по ключу.
        
        Args:
            key (str): Ключ для установки значения.
            value (Any): Значение для установки.
        """
        data = cls._load_data()
        data[key] = value
        cls._save_data(data)

    @classmethod
    def get_float(cls, key: str, default: float = 0.0) -> float:
        """Получает значение с плавающей точкой по ключу.
        
        Args:
            key (str): Ключ для получения значения.
            default (float, optional): Значение по умолчанию. По умолчанию 0.0.
            
        Returns:
            float: Значение с плавающей точкой.
        """
        value = cls._get_value(key, default)
        try:
            return float(value)
        except (TypeError, ValueError):
            return float(default)

    @classmethod
    def set_float(cls, key: str, value: float) -> None:
        """Устанавливает значение с плавающей точкой по ключу.
        
        Args:
            key (str): Ключ для установки значения.
            value (float): Значение для установки.
            
        Raises:
            SaveLoadError: Если значение не является числом.
        """
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            raise SaveLoadError(f"Value for {key} must be a number")
        cls._set_value(key, numeric)

    @classmethod
    def get_int(cls, key: str, default: int = 0) -> int:
        """Получает целочисленное значение по ключу.
        
        Args:
            key (str): Ключ для получения значения.
            default (int, optional): Значение по умолчанию. По умолчанию 0.
            
        Returns:
            int: Целочисленное значение.
        """
        value = cls._get_value(key, default)
        try:
            return int(value)
        except (TypeError, ValueError):
            return int(default)

    @classmethod
    def set_int(cls, key: str, value: int) -> None:
        """Устанавливает целочисленное значение по ключу.
        
        Args:
            key (str): Ключ для установки значения.
            value (int): Значение для установки.
            
        Raises:
            SaveLoadError: Если значение не является целым числом.
        """
        try:
            integer = int(value)
        except (TypeError, ValueError):
            raise SaveLoadError(f"Value for {key} must be an integer")
        cls._set_value(key, integer)

    @classmethod
    def get_string(cls, key: str, default: str = "") -> str:
        """Получает строковое значение по ключу.
        
        Args:
            key (str): Ключ для получения значения.
            default (str, optional): Значение по умолчанию. По умолчанию "".
            
        Returns:
            str: Строковое значение.
        """
        value = cls._get_value(key, default)
        if value is None:
            return default
        return str(value)

    @classmethod
    def set_string(cls, key: str, value: str) -> None:
        """Устанавливает строковое значение по ключу.
        
        Args:
            key (str): Ключ для установки значения.
            value (str): Значение для установки.
            
        Raises:
            SaveLoadError: Если значение равно None.
        """
        if value is None:
            raise SaveLoadError(f"Value for {key} cannot be None")
        cls._set_value(key, str(value))

    @classmethod
    def get_vector2(cls, key: str, default: Tuple[int, int] = (0, 0)) -> Tuple[int, int]:
        """Получает 2D координату (вектор) по ключу.
        
        Args:
            key (str): Ключ для получения значения.
            default (Tuple[int, int], optional): Значение по умолчанию. По умолчанию (0, 0).
            
        Returns:
            Tuple[int, int]: 2D координата (x, y).
        """
        value = cls._get_value(key, default)
        if isinstance(value, (list, tuple)) and len(value) == 2:
            try:
                x = int(value[0])
                y = int(value[1])
                return x, y
            except (TypeError, ValueError):
                pass
        return int(default[0]), int(default[1])

    @classmethod
    def set_vector2(cls, key: str, value: Tuple[int, int]) -> None:
        """Устанавливает 2D координату (вектор) по ключу.
        
        Args:
            key (str): Ключ для установки значения.
            value (Tuple[int, int]): 2D координата для установки.
            
        Raises:
            SaveLoadError: Если значение не является 2D координатой.
        """
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            raise SaveLoadError(f"Value for {key} must be a 2D coordinate")
        try:
            x = int(value[0])
            y = int(value[1])
        except (TypeError, ValueError):
            raise SaveLoadError(f"Value for {key} must contain numeric coordinates")
        cls._set_value(key, [x, y])

    @classmethod
    def delete_key(cls, key: str) -> None:
        """Удаляет ключ из настроек.
        
        Args:
            key (str): Ключ для удаления.
        """
        data = cls._load_data()
        if key in data:
            del data[key]
            cls._save_data(data)

    @classmethod
    def clear(cls) -> None:
        """Очищает все настройки."""
        cls._save_data({})


# Global instance for easy access
save_manager = SaveLoadManager()

# Convenience functions
def save(data: Any, filename: Optional[str] = None, 
         format_type: Optional[str] = None) -> bool:
    """Удобная функция для сохранения данных.
    
    Args:
        data (Any): Данные для сохранения.
        filename (Optional[str], optional): Имя файла.
        format_type (Optional[str], optional): Тип формата.
        
    Returns:
        bool: True, если успешно, False в противном случае.
    """
    return save_manager.save(data, filename, format_type)


def load(filename: Optional[str] = None, 
         format_type: Optional[str] = None,
         default_value: Any = None) -> Any:
    """Удобная функция для загрузки данных.
    
    Args:
        filename (Optional[str], optional): Имя файла.
        format_type (Optional[str], optional): Тип формата.
        default_value (Any, optional): Значение по умолчанию, если файл не найден.
        
    Returns:
        Any: Загруженные данные или значение по умолчанию.
    """
    return save_manager.load(filename, format_type, default_value)


def exists(filename: Optional[str] = None) -> bool:
    """Удобная функция для проверки существования файла.
    
    Args:
        filename (Optional[str], optional): Имя файла.
        
    Returns:
        bool: True, если файл существует, False в противном случае.
    """
    return save_manager.exists(filename)


def delete(filename: Optional[str] = None, include_backups: bool = False) -> bool:
    """Удобная функция для удаления файла.
    
    Args:
        filename (Optional[str], optional): Имя файла.
        include_backups (bool, optional): Также удалить резервные копии.
        
    Returns:
        bool: True, если успешно, False в противном случае.
    """
    return save_manager.delete(filename, include_backups)


# Register common SpritePro classes for serialization
def register_sprite_classes():
    """Регистрирует классы SpritePro для автоматической сериализации."""
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