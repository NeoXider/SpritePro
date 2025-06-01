"""
Простой пример использования системы сохранения/загрузки SpritePro

Демонстрирует основные возможности сохранения и загрузки игровых данных.
"""

import spritePro as s

def main():
    print("SpritePro Save/Load System - Простой пример")
    print("=" * 45)
    
    # === 1. Сохранение и загрузка простых данных ===
    print("\n1. Работа с игровыми данными:")
    
    # Данные игрока
    player_data = {
        'name': 'Герой',
        'level': 10,
        'experience': 2500,
        'gold': 1250,
        'inventory': ['меч', 'щит', 'зелье здоровья'],
        'stats': {
            'health': 100,
            'mana': 80,
            'strength': 15,
            'agility': 12
        }
    }
    
    # Сохранение
    print("   Сохранение данных игрока...")
    if s.utils.save(player_data, 'player_save.json'):
        print("   ✓ Данные сохранены успешно!")
    
    # Загрузка
    print("   Загрузка данных игрока...")
    loaded_data = s.utils.load('player_save.json')
    print(f"   ✓ Загружен игрок: {loaded_data['name']}, уровень {loaded_data['level']}")
    
    # === 2. Работа с настройками ===
    print("\n2. Работа с настройками игры:")
    
    settings = {
        'graphics': {
            'resolution': (1920, 1080),
            'fullscreen': False,
            'quality': 'high'
        },
        'audio': {
            'master_volume': 0.8,
            'music_volume': 0.6,
            'sfx_volume': 0.9
        },
        'controls': {
            'move_up': 'W',
            'move_down': 'S',
            'move_left': 'A',
            'move_right': 'D'
        }
    }
    
    # Сохранение настроек
    s.utils.save(settings, 'game_settings.json')
    print("   ✓ Настройки сохранены")
    
    # Загрузка с значением по умолчанию
    default_settings = {'audio': {'master_volume': 1.0}}
    loaded_settings = s.utils.load('game_settings.json', default_value=default_settings)
    print(f"   ✓ Загружены настройки, разрешение: {loaded_settings['graphics']['resolution']}")
    
    # === 3. Проверка существования файлов ===
    print("\n3. Проверка файлов сохранения:")
    
    if s.utils.exists('player_save.json'):
        print("   ✓ Файл сохранения игрока найден")
    
    if s.utils.exists('nonexistent_file.json'):
        print("   ✓ Несуществующий файл найден")
    else:
        print("   ✓ Несуществующий файл корректно не найден")
    
    # === 4. Работа с текстовыми данными ===
    print("\n4. Сохранение текстовых данных:")
    
    game_log = """
Игровой лог:
- Игрок начал новую игру
- Достигнут уровень 5
- Найден редкий предмет
- Побежден босс
- Игра сохранена
    """.strip()
    
    s.utils.save(game_log, 'game_log.txt', 'text')
    loaded_log = s.utils.load('game_log.txt', 'text')
    print(f"   ✓ Сохранен и загружен лог ({len(loaded_log)} символов)")
    
    # === 5. Работа с менеджером сохранений ===
    print("\n5. Использование менеджера сохранений:")
    
    # Создание менеджера с автоматическими резервными копиями
    from spritePro.utils import SaveLoadManager
    
    manager = SaveLoadManager(
        default_file="game_state.json",
        auto_backup=True,
        compression=False
    )
    
    # Сохранение состояния игры
    game_state = {
        'current_level': 3,
        'enemies_defeated': 25,
        'secrets_found': 7,
        'play_time': 3600,  # секунды
        'last_checkpoint': (150, 200)
    }
    
    manager.save(game_state)
    print("   ✓ Состояние игры сохранено с резервной копией")
    
    # Загрузка состояния
    loaded_state = manager.load()
    print(f"   ✓ Загружено состояние: уровень {loaded_state['current_level']}, "
          f"время игры {loaded_state['play_time']}с")
    
    # === 6. Демонстрация обработки ошибок ===
    print("\n6. Обработка ошибок:")
    
    try:
        # Попытка загрузить несуществующий файл без значения по умолчанию
        s.utils.load('missing_file.json')
    except s.utils.SaveLoadError:
        print("   ✓ Корректно обработана ошибка загрузки")
    
    # Загрузка с безопасным значением по умолчанию
    safe_data = s.utils.load('missing_file.json', default_value={'status': 'new_game'})
    print(f"   ✓ Безопасная загрузка: {safe_data}")
    
    # === 7. Очистка (опционально) ===
    print("\n7. Управление файлами:")
    
    # Показать какие файлы существуют
    files_to_check = ['player_save.json', 'game_settings.json', 'game_log.txt', 'game_state.json']
    existing_files = [f for f in files_to_check if s.utils.exists(f)]
    print(f"   Создано файлов: {len(existing_files)}")
    
    # Спросить о удалении
    print("\n   Файлы сохранения созданы для демонстрации.")
    response = input("   Удалить демонстрационные файлы? (y/n): ").lower().strip()
    
    if response in ['y', 'yes', 'да', 'д']:
        deleted_count = 0
        for filename in files_to_check:
            if s.utils.delete(filename, include_backups=True):
                deleted_count += 1
        print(f"   ✓ Удалено файлов: {deleted_count}")
    else:
        print("   ℹ Файлы оставлены для изучения")
    
    print("\n🎉 Демонстрация завершена!")
    print("\nДля более подробных примеров запустите:")
    print("python spritePro/demoGames/save_load_demo.py")


if __name__ == "__main__":
    main()