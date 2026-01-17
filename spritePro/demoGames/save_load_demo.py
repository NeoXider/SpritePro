"""
Save/Load System Demo - SpritePro

Демонстрация возможностей системы сохранения и загрузки данных.
Показывает работу с различными типами данных и форматами файлов.
"""

import sys
import os
import time
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import spritePro as s
from spritePro.utils.save_load import SaveLoadManager, DataSerializer


class Player:
    """Пример пользовательского класса для демонстрации сериализации."""

    def __init__(self, name: str, level: int = 1):
        self.name = name
        self.level = level
        self.experience = 0
        self.inventory = []
        self.position = (0, 0)
        self.stats = {"health": 100, "mana": 50, "strength": 10, "agility": 8}

    def __str__(self):
        return f"Player(name='{self.name}', level={self.level}, exp={self.experience})"

    def __eq__(self, other):
        if not isinstance(other, Player):
            return False
        return (
            self.name == other.name
            and self.level == other.level
            and self.experience == other.experience
        )


def register_player_serialization():
    """Регистрация методов сериализации для класса Player."""

    def serialize_player(player):
        return {
            "name": player.name,
            "level": player.level,
            "experience": player.experience,
            "inventory": player.inventory,
            "position": player.position,
            "stats": player.stats,
        }

    def deserialize_player(data):
        player = Player(data["name"], data["level"])
        player.experience = data["experience"]
        player.inventory = data["inventory"]
        player.position = data["position"]
        player.stats = data["stats"]
        return player

    DataSerializer.register_class(Player, serialize_player, deserialize_player)


def demo_basic_operations():
    """Демонстрация базовых операций сохранения/загрузки."""
    s.debug_log_info("=== Демо базовых операций ===")

    # Тестовые данные
    simple_data = {
        "game_name": "SpritePro Adventure",
        "version": "1.0.0",
        "max_level": 50,
        "difficulty_levels": ["easy", "normal", "hard", "nightmare"],
        "default_settings": {"volume": 0.8, "fullscreen": False, "auto_save": True},
    }

    s.debug_log_info("1. Сохранение простых данных...")
    success = s.utils.save(simple_data, "demo_basic.json")
    s.debug_log_info(f"   Результат: {'[OK] Успешно' if success else '[FAIL] Ошибка'}")

    s.debug_log_info("2. Загрузка данных...")
    loaded_data = s.utils.load("demo_basic.json")
    s.debug_log_info(
        f"   Загружено: {loaded_data['game_name']} v{loaded_data['version']}"
    )

    s.debug_log_info("3. Проверка существования файла...")
    exists = s.utils.exists("demo_basic.json")
    s.debug_log_info(f"   Файл существует: {'[OK] Да' if exists else '[FAIL] Нет'}")

    s.debug_log_info("4. Проверка целостности данных...")
    match = simple_data == loaded_data
    s.debug_log_info(f"   Данные совпадают: {'[OK] Да' if match else '[FAIL] Нет'}")

    s.debug_log_info()


def demo_different_formats():
    """Демонстрация работы с различными форматами файлов."""
    s.debug_log_info("=== Демо различных форматов ===")

    # JSON формат
    s.debug_log_info("1. JSON формат...")
    json_data = {
        "player_scores": [1000, 2500, 3200, 4100],
        "achievements": {"first_win", "speed_demon", "collector"},
        "metadata": {"created": time.time(), "platform": "desktop"},
    }
    s.utils.save(json_data, "demo_data.json")
    loaded_json = s.utils.load("demo_data.json")
    s.debug_log_info(f"   JSON: Сохранено и загружено {len(loaded_json)} ключей")

    # Text формат
    s.debug_log_info("2. Text формат...")
    text_data = """
# Конфигурация игры
resolution=1920x1080
fullscreen=false
vsync=true
quality=high

# Управление
move_up=W
move_down=S
move_left=A
move_right=D
    """.strip()
    s.utils.save(text_data, "demo_config.txt", "text")
    loaded_text = s.utils.load("demo_config.txt", "text")
    s.debug_log_info(
        f"   Text: Сохранено {len(text_data)} символов, загружено {len(loaded_text)}"
    )

    # Binary формат
    s.debug_log_info("3. Binary формат...")
    binary_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10"
    s.utils.save(binary_data, "demo_image.bin", "binary")
    loaded_binary = s.utils.load("demo_image.bin", "binary")
    s.debug_log_info(
        f"   Binary: Сохранено {len(binary_data)} байт, загружено {len(loaded_binary)}"
    )

    s.debug_log_info()


def demo_custom_classes():
    """Демонстрация сериализации пользовательских классов."""
    s.debug_log_info("=== Демо пользовательских классов ===")

    # Регистрируем сериализацию для Player
    register_player_serialization()

    s.debug_log_info("1. Создание игрока...")
    player = Player("Герой", 15)
    player.experience = 2500
    player.inventory = ["меч", "зелье здоровья", "ключ"]
    player.position = (100, 200)
    player.stats["health"] = 120
    s.debug_log_info(f"   Создан: {player}")

    s.debug_log_info("2. Сохранение объекта класса...")
    s.utils.save(player, "demo_player.json")
    s.debug_log_info("   [OK] Игрок сохранен")

    s.debug_log_info("3. Загрузка объекта класса...")
    loaded_player = s.utils.load("demo_player.json")
    s.debug_log_info(f"   Загружен: {loaded_player}")

    s.debug_log_info("4. Проверка целостности объекта...")
    match = player == loaded_player
    s.debug_log_info(f"   Объекты совпадают: {'[OK] Да' if match else '[FAIL] Нет'}")

    # Дополнительная проверка атрибутов
    attrs_match = (
        player.inventory == loaded_player.inventory
        and player.position == loaded_player.position
        and player.stats == loaded_player.stats
    )
    s.debug_log_info(
        f"   Атрибуты совпадают: {'[OK] Да' if attrs_match else '[FAIL] Нет'}"
    )

    s.debug_log_info()


def demo_advanced_features():
    """Демонстрация продвинутых возможностей."""
    s.debug_log_info("=== Демо продвинутых возможностей ===")

    # Создание менеджера с настройками
    s.debug_log_info("1. Создание менеджера с резервными копиями и сжатием...")
    manager = SaveLoadManager(
        default_file="demo_advanced.json", auto_backup=True, compression=True
    )

    # Большие данные для демонстрации сжатия
    large_data = {
        "map_data": [[0 for _ in range(100)] for _ in range(100)],
        "entity_data": [{"id": i, "type": "enemy", "health": 100} for i in range(1000)],
        "metadata": {"generated": time.time(), "size": "large"},
    }

    s.debug_log_info("2. Сохранение больших данных со сжатием...")
    manager.save(large_data)
    s.debug_log_info("   [OK] Данные сохранены со сжатием")

    s.debug_log_info("3. Загрузка сжатых данных...")
    loaded_large = manager.load()
    s.debug_log_info(
        f"   Загружено: карта {len(loaded_large['map_data'])}x{len(loaded_large['map_data'][0])}, "
        f"{len(loaded_large['entity_data'])} сущностей"
    )

    s.debug_log_info(
        "4. Создание еще одного сохранения (для демонстрации резервных копий)..."
    )
    time.sleep(1)  # Небольшая задержка для разных временных меток
    manager.save({"version": 2, "data": "updated"})

    s.debug_log_info("5. Просмотр резервных копий...")
    backups = manager.list_backups()
    s.debug_log_info(f"   Найдено резервных копий: {len(backups)}")
    for backup in backups:
        s.debug_log_info(f"   - {backup.name}")

    s.debug_log_info("6. Загрузка с значением по умолчанию...")
    default_value = {"error": "file_not_found", "use_defaults": True}
    result = manager.load("nonexistent_file.json", default_value=default_value)
    s.debug_log_info(f"   Результат для несуществующего файла: {result}")

    s.debug_log_info()


def demo_spritepro_objects():
    """Демонстрация сохранения объектов SpritePro."""
    s.debug_log_info("=== Демо объектов SpritePro ===")

    try:
        s.debug_log_info("1. Создание спрайта...")
        # Создаем простую поверхность вместо загрузки файла
        import pygame

        pygame.init()

        # Создаем цветную поверхность
        surface = pygame.Surface((64, 64))
        surface.fill((255, 100, 100))  # Красный цвет

        sprite = s.Sprite(surface, (64, 64), (100, 150))
        sprite.speed = 5.5
        sprite.angle = 45
        sprite.set_scale(1.5)
        s.debug_log_info(
            f"   Создан спрайт: размер {sprite.size}, позиция {(sprite.rect.x, sprite.rect.y)}"
        )

        s.debug_log_info("2. Сохранение спрайта...")
        s.utils.save(sprite, "demo_sprite.json")
        s.debug_log_info("   [OK] Спрайт сохранен")

        s.debug_log_info("3. Загрузка спрайта...")
        loaded_sprite = s.utils.load("demo_sprite.json")
        s.debug_log_info(
            f"   Загружен спрайт: размер {loaded_sprite.size}, "
            f"позиция {(loaded_sprite.rect.x, loaded_sprite.rect.y)}"
        )

        s.debug_log_info("4. Проверка атрибутов спрайта...")
        attrs_ok = (
            sprite.speed == loaded_sprite.speed
            and sprite.angle == loaded_sprite.angle
            and abs(sprite.scale - loaded_sprite.scale) < 0.01
        )
        s.debug_log_info(
            f"   Атрибуты совпадают: {'[OK] Да' if attrs_ok else '[FAIL] Нет'}"
        )

    except Exception as e:
        s.debug_log_info(f"   [WARN] Ошибка при работе со спрайтами: {e}")

    s.debug_log_info()


def demo_error_handling():
    """Демонстрация обработки ошибок."""
    s.debug_log_info("=== Демо обработки ошибок ===")

    s.debug_log_info("1. Попытка загрузки несуществующего файла...")
    try:
        data = s.utils.load("nonexistent_file.json")
        s.debug_log_info("   [FAIL] Неожиданно успешно")
    except s.utils.SaveLoadError as e:
        s.debug_log_info(f"   [OK] Корректно обработана ошибка: {e}")

    s.debug_log_info("2. Загрузка с значением по умолчанию...")
    default_data = {"status": "default", "message": "файл не найден"}
    data = s.utils.load("nonexistent_file.json", default_value=default_data)
    s.debug_log_info(f"   [OK] Возвращено значение по умолчанию: {data}")

    s.debug_log_info("3. Попытка сохранения в недоступную директорию...")
    try:
        s.utils.save({"test": "data"}, "/root/forbidden/test.json")
        s.debug_log_info("   [FAIL] Неожиданно успешно")
    except s.utils.SaveLoadError as e:
        s.debug_log_info(f"   [OK] Корректно обработана ошибка доступа")

    s.debug_log_info()


def cleanup_demo_files():
    """Очистка демонстрационных файлов."""
    s.debug_log_info("=== Очистка файлов ===")

    demo_files = [
        "demo_basic.json",
        "demo_data.json",
        "demo_config.txt",
        "demo_image.bin",
        "demo_player.json",
        "demo_advanced.json",
        "demo_advanced.json.gz",
        "demo_sprite.json",
    ]

    cleaned = 0
    for filename in demo_files:
        if s.utils.exists(filename):
            if s.utils.delete(filename, include_backups=True):
                cleaned += 1

    s.debug_log_info(f"Очищено файлов: {cleaned}")
    s.debug_log_info()


def main():
    """Главная функция демонстрации."""
    s.debug_log_info("SpritePro Save/Load System Demo")
    s.debug_log_info("=" * 50)
    s.debug_log_info()

    try:
        # Запуск всех демонстраций
        demo_basic_operations()
        demo_different_formats()
        demo_custom_classes()
        demo_advanced_features()
        demo_spritepro_objects()
        demo_error_handling()

        s.debug_log_info("All demos finished successfully.")
        s.debug_log_info()

        # Спросить пользователя о очистке (только если явно включено)
        interactive = os.environ.get("SPRITEPRO_DEMO_INTERACTIVE") == "1"
        if interactive and hasattr(sys.stdin, "isatty") and sys.stdin.isatty():
            response = input("Удалить демонстрационные файлы? (y/n): ").lower().strip()
            if response in ["y", "yes", "да", "д"]:
                cleanup_demo_files()
                s.debug_log_info("Files cleaned")
            else:
                s.debug_log_info("Demo files left for review")

    except KeyboardInterrupt:
        s.debug_log_info("\n\nDemo interrupted by user")
    except Exception as e:
        s.debug_log_info(f"\n\nError during demo: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
