"""
Валидация входных данных для SpritePro.

Модуль предоставляет функции для валидации различных типов данных:
- Цвета (RGB)
- Векторы и координаты
- Числовые значения с диапазонами
- Строки
- Перечисления
"""

from typing import Union, List, Optional, Any
import pygame.math as pm
from ..exceptions import ValidationError


def validate_color(color: Union[tuple, list], name: str = "color") -> None:
    """
    Валидирует RGB-цвет.

    Args:
        color: Кортеж или список из 3 целых чисел (0-255)
        name: Имя параметра для сообщений об ошибках

    Raises:
        ValidationError: Если валидация не пройдена

    Example:
        >>> validate_color((255, 0, 0), "background")
        >>> validate_color([128, 128, 128], "text_color")
    """
    if not isinstance(color, (tuple, list)):
        raise ValidationError(
            f"{name} должен быть кортежем или списком, получен: {type(color).__name__}"
        )

    if len(color) != 3:
        raise ValidationError(
            f"{name} должен содержать ровно 3 значения (R, G, B), получено: {len(color)}"
        )

    for i, val in enumerate(["R", "G", "B"]):
        if not isinstance(color[i], int):
            raise ValidationError(
                f"Значение {val} в {name} должно быть целым числом, получено: {type(color[i]).__name__}"
            )
        if not (0 <= color[i] <= 255):
            raise ValidationError(
                f"Значение {val} в {name} должно быть от 0 до 255, получено: {color[i]}"
            )


def validate_vector2(vec: Union[pm.Vector2, tuple, list], name: str = "vector") -> None:
    """
    Валидирует Vector2 или координаты.

    Args:
        vec: Vector2, кортеж или список из 2 чисел
        name: Имя параметра для сообщений об ошибках

    Raises:
        ValidationError: Если валидация не пройдена

    Example:
        >>> validate_vector2((100, 200), "position")
        >>> validate_vector2(pm.Vector2(50.5, 75.3), "offset")
    """
    if isinstance(vec, pm.Vector2):
        return

    if not isinstance(vec, (tuple, list)):
        raise ValidationError(
            f"{name} должен быть Vector2, кортежем или списком, получен: {type(vec).__name__}"
        )

    if len(vec) != 2:
        raise ValidationError(
            f"{name} должен содержать ровно 2 значения (X, Y), получено: {len(vec)}"
        )

    for i, val in enumerate(["X", "Y"]):
        if not isinstance(vec[i], (int, float)):
            raise ValidationError(
                f"Значение {val} в {name} должно быть числом, получено: {type(vec[i]).__name__}"
            )


def validate_float(
    value: Union[int, float],
    name: str = "value",
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
) -> None:
    """
    Валидирует числовое значение с возможностью указания диапазона.

    Args:
        value: Числовое значение
        name: Имя параметра для сообщений об ошибках
        min_val: Минимально допустимое значение (None = без ограничения)
        max_val: Максимально допустимое значение (None = без ограничения)

    Raises:
        ValidationError: Если валидация не пройдена

    Example:
        >>> validate_float(0.5, "zoom", min_val=0.1, max_val=5.0)
        >>> validate_float(60, "fps")
    """
    if not isinstance(value, (int, float)):
        raise ValidationError(f"{name} должно быть числом, получено: {type(value).__name__}")

    if min_val is not None and value < min_val:
        raise ValidationError(f"{name} ({value}) меньше минимально допустимого значения {min_val}")

    if max_val is not None and value > max_val:
        raise ValidationError(f"{name} ({value}) больше максимально допустимого значения {max_val}")


def validate_string(
    value: str,
    name: str = "string",
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    allow_empty: bool = True,
) -> None:
    """
    Валидирует строковое значение.

    Args:
        value: Строковое значение
        name: Имя параметра для сообщений об ошибках
        min_length: Минимальная длина строки (None = без ограничения)
        max_length: Максимальная длина строки (None = без ограничения)
        allow_empty: Разрешить ли пустые строки

    Raises:
        ValidationError: Если валидация не пройдена

    Example:
        >>> validate_string("player_name", "username", min_length=3, max_length=20)
        >>> validate_string("", "description", allow_empty=True)
    """
    if not isinstance(value, str):
        raise ValidationError(f"{name} должна быть строкой, получено: {type(value).__name__}")

    if not allow_empty and len(value) == 0:
        raise ValidationError(f"{name} не может быть пустой строкой")

    if min_length is not None and len(value) < min_length:
        raise ValidationError(
            f"{name} ({len(value)} символов) меньше минимальной длины {min_length}"
        )

    if max_length is not None and len(value) > max_length:
        raise ValidationError(
            f"{name} ({len(value)} символов) больше максимальной длины {max_length}"
        )


def validate_enum(value: Any, enum_class: type, name: str = "value") -> None:
    """
    Валидирует значение на соответствие перечислению.

    Args:
        value: Проверяемое значение
        enum_class: Класс перечисления (Enum)
        name: Имя параметра для сообщений об ошибках

    Raises:
        ValidationError: Если валидация не пройдена

    Example:
        >>> from enum import Enum
        >>> class Direction(Enum):
        ...     UP = "up"
        ...     DOWN = "down"
        >>> validate_enum("up", Direction, "direction")
    """
    if not isinstance(value, enum_class):
        valid_values = [e.value for e in enum_class]
        raise ValidationError(f"{name} должно быть одним из {valid_values}, получено: {value}")


def validate_list(
    value: list,
    item_type: type,
    name: str = "list",
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
) -> None:
    """
    Валидирует список элементов определённого типа.

    Args:
        value: Список для проверки
        item_type: Ожидаемый тип элементов
        name: Имя параметра для сообщений об ошибках
        min_length: Минимальная длина списка
        max_length: Максимальная длина списка

    Raises:
        ValidationError: Если валидация не пройдена

    Example:
        >>> validate_list([1, 2, 3], int, "numbers")
        >>> validate_list(["a", "b"], str, "tags", min_length=2)
    """
    if not isinstance(value, list):
        raise ValidationError(f"{name} должен быть списком, получен: {type(value).__name__}")

    for i, item in enumerate(value):
        if not isinstance(item, item_type):
            raise ValidationError(
                f"Элемент {i} в {name} должен быть {item_type.__name__}, "
                f"получено: {type(item).__name__}"
            )

    if min_length is not None and len(value) < min_length:
        raise ValidationError(
            f"{name} ({len(value)} элементов) меньше минимальной длины {min_length}"
        )

    if max_length is not None and len(value) > max_length:
        raise ValidationError(
            f"{name} ({len(value)} элементов) больше максимальной длины {max_length}"
        )


def validate_dict(
    value: dict,
    name: str = "dict",
    required_keys: Optional[List[str]] = None,
    allowed_keys: Optional[List[str]] = None,
) -> None:
    """
    Валидирует словарь с проверкой ключей.

    Args:
        value: Словарь для проверки
        name: Имя параметра для сообщений об ошибках
        required_keys: Список обязательных ключей
        allowed_keys: Список разрешённых ключей (если None, любые ключи допустимы)

    Raises:
        ValidationError: Если валидация не пройдена

    Example:
        >>> validate_dict({"name": "test", "value": 42}, "config",
        ...               required_keys=["name"], allowed_keys=["name", "value"])
    """
    if not isinstance(value, dict):
        raise ValidationError(f"{name} должен быть словарём, получен: {type(value).__name__}")

    if required_keys:
        missing_keys = [key for key in required_keys if key not in value]
        if missing_keys:
            raise ValidationError(f"{name} отсутствуют обязательные ключи: {missing_keys}")

    if allowed_keys:
        invalid_keys = [key for key in value.keys() if key not in allowed_keys]
        if invalid_keys:
            raise ValidationError(f"{name} содержат недопустимые ключи: {invalid_keys}")


# Экспорт функций
__all__ = [
    "validate_color",
    "validate_vector2",
    "validate_float",
    "validate_string",
    "validate_enum",
    "validate_list",
    "validate_dict",
]
