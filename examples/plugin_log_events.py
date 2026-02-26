"""
Пример плагина для логирования событий.

Этот плагин демонстрирует использование системы плагинов SpritePro:
- Регистрация хуков для различных событий
- Логирование создания/удаления спрайтов
- Логирование изменений сцены
"""

from spritePro.plugins import hook, get_plugin_manager
import spritePro as s


def log_events_plugin():
    """
    Плагин для логирования событий.
    
    Этот плагин автоматически логирует:
    - Создание и удаление спрайтов
    - Загрузку/выгрузку сцен
    - Нажатие клавиш и клики мыши
    """
    pass  # Функция-заглушка для декоратора


# Регистрация хуков для логирования событий
@hook("sprite_created")
def on_sprite_created(sprite):
    """Логирование создания спрайта."""
    sprite_info = f"Sprite: {type(sprite).__name__} at ({sprite.rect.x}, {sprite.rect.y})"
    s.debug_log_info(f"[LOG_EVENTS] Created: {sprite_info}")


@hook("sprite_removed")
def on_sprite_removed(sprite):
    """Логирование удаления спрайта."""
    sprite_info = f"Sprite: {type(sprite).__name__} at ({sprite.rect.x}, {sprite.rect.y})"
    s.debug_log_warning(f"[LOG_EVENTS] Removed: {sprite_info}")


@hook("scene_loaded")
def on_scene_loaded(scene=None, **kwargs):
    """Логирование загрузки сцены."""
    name = getattr(scene, "name", None) or (scene.__class__.__name__ if scene else "?")
    s.debug_log_info(f"[LOG_EVENTS] Scene loaded: {name}")


@hook("scene_unloaded")
def on_scene_unloaded(scene_name):
    """Логирование выгрузки сцены."""
    s.debug_log_warning(f"[LOG_EVENTS] Scene unloaded: {scene_name}")


@hook("key_pressed")
def on_key_pressed(key, event):
    """Логирование нажатия клавиш."""
    key_names = {
        257: 'SPACE',
        256: 'ENTER',
        260: 'UP',
        261: 'DOWN',
        262: 'LEFT',
        263: 'RIGHT',
    }
    key_name = key_names.get(key, f"KEY_{key}")
    s.debug_log_info(f"[LOG_EVENTS] Key pressed: {key_name}")


@hook("mouse_clicked")
def on_mouse_clicked(button, pos, event):
    """Логирование кликов мыши."""
    button_names = {
        0: 'LEFT',
        1: 'MIDDLE',
        2: 'RIGHT'
    }
    button_name = button_names.get(button, f"BUTTON_{button}")
    s.debug_log_info(f"[LOG_EVENTS] Mouse clicked: {button_name} at {pos}")


# Функция для инициализации плагина
def init_plugin():
    """
    Инициализация плагина логирования.
    
    Вызывается при старте игры для подключения всех хуков.
    """
    pm = get_plugin_manager()
    s.debug_log_info("[LOG_EVENTS] Plugin initialized")


# Функция для очистки плагина
def shutdown_plugin():
    """
    Очистка плагина при завершении игры.
    
    Удаляет все хуки и освобождает ресурсы.
    """
    pm = get_plugin_manager()
    s.debug_log_info("[LOG_EVENTS] Plugin shutdown")


# Экспорт функций
__all__ = ['log_events_plugin', 'init_plugin', 'shutdown_plugin']
