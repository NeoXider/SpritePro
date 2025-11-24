"""Централизованное управление звуком и музыкой в SpritePro."""

import pygame
from typing import Optional


class Sound:
    """Обертка над звуком в AudioManager для удобного использования.
    
    Позволяет сохранять звуки в переменные и воспроизводить их с автоматическим
    применением настроек AudioManager (громкость, включение/выключение).
    
    Example:
        >>> audio = spritePro.audio_manager
        >>> audio.load_sound("bounce", "sounds/bounce.mp3")
        >>> bounce_sound = audio.get_sound("bounce")
        >>> bounce_sound.play()  # Воспроизвести с настройками AudioManager
    """
    
    def __init__(self, audio_manager: 'AudioManager', name: str):
        """Инициализирует обертку над звуком.
        
        Args:
            audio_manager (AudioManager): Экземпляр AudioManager.
            name (str): Имя звука в AudioManager.
        """
        self._audio_manager = audio_manager
        self._name = name
    
    def play(self, volume: Optional[float] = None) -> None:
        """Воспроизвести звук через AudioManager.
        
        Args:
            volume (float, optional): Громкость (0.0 - 1.0). Если None, используется sfx_volume из AudioManager.
        """
        self._audio_manager.play_sound(self._name, volume)
    
    @property
    def name(self) -> str:
        """Имя звука."""
        return self._name
    
    @property
    def sound(self) -> Optional[pygame.mixer.Sound]:
        """Прямой доступ к pygame.mixer.Sound (если нужен)."""
        return self._audio_manager.sounds.get(self._name)


class AudioManager:
    """Централизованное управление звуком.
    
    Предоставляет единый интерфейс для работы со звуковыми эффектами и музыкой,
    включая управление громкостью и включением/выключением звука.
    
    Attributes:
        music_volume (float): Громкость музыки (0.0 - 1.0).
        sfx_volume (float): Громкость звуковых эффектов (0.0 - 1.0).
        music_enabled (bool): Включена ли музыка.
        sfx_enabled (bool): Включены ли звуковые эффекты.
        sounds (dict[str, pygame.mixer.Sound]): Словарь загруженных звуков.
        current_music (str | None): Путь к текущей музыке.
    """
    
    def __init__(self):
        """Инициализирует AudioManager с настройками по умолчанию."""
        self.music_volume = 0.5
        self.sfx_volume = 1.0
        self.music_enabled = True
        self.sfx_enabled = True
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.current_music: Optional[str] = None
        
    def load_sound(self, name: str, path: str) -> 'Sound':
        """Загрузить звуковой эффект и вернуть объект Sound.
        
        Args:
            name (str): Имя звука для последующего использования.
            path (str): Путь к файлу звука.
            
        Returns:
            Sound: Объект Sound для воспроизведения.
            
        Example:
            >>> jump_sound = audio.load_sound("jump", "sounds/jump.mp3")
            >>> jump_sound.play()  # Можно сразу использовать!
        """
        try:
            self.sounds[name] = pygame.mixer.Sound(path)
            return Sound(self, name)
        except pygame.error as e:
            print(f"Error loading sound '{name}' from '{path}': {e}")
            return Sound(self, name)  # Возвращаем объект даже при ошибке
        
    def play_sound(self, name_or_path: str, volume: Optional[float] = None) -> None:
        """Воспроизвести звуковой эффект.
        
        Может воспроизвести звук по имени (если он был загружен через load_sound)
        или напрямую по пути к файлу (автоматически загрузит и воспроизведет).
        
        Args:
            name_or_path (str): Имя звука (загруженного через load_sound) или путь к файлу звука.
            volume (float, optional): Громкость (0.0 - 1.0). Если None, используется sfx_volume.
            
        Example:
            >>> # Воспроизведение загруженного звука
            >>> audio.load_sound("bounce", "sounds/bounce.mp3")
            >>> audio.play_sound("bounce")
            
            >>> # Прямое воспроизведение по пути (автоматическая загрузка)
            >>> audio.play_sound("sounds/jump.mp3")
            >>> audio.play_sound("sounds/coin.wav", volume=0.8)
        """
        if not self.sfx_enabled:
            return
        
        # Проверяем, есть ли звук в словаре (загружен ранее)
        if name_or_path in self.sounds:
            sound = self.sounds[name_or_path]
            sound.set_volume(volume if volume is not None else self.sfx_volume)
            sound.play()
        else:
            # Пытаемся загрузить и воспроизвести напрямую из файла
            try:
                sound = pygame.mixer.Sound(name_or_path)
                sound.set_volume(volume if volume is not None else self.sfx_volume)
                sound.play()
            except pygame.error as e:
                print(f"Error playing sound from '{name_or_path}': {e}")
                print("Hint: Load the sound first with load_sound() or provide a valid file path.")
    
    def play_music(self, path: str, loop: bool = True, volume: Optional[float] = None) -> None:
        """Воспроизвести музыку.
        
        Args:
            path (str): Путь к файлу музыки.
            loop (bool, optional): Зациклить ли музыку. По умолчанию True.
            volume (float, optional): Громкость (0.0 - 1.0). Если None, используется music_volume.
            
        Example:
            >>> audio.play_music("music/background.mp3")
            >>> audio.play_music("music/intro.mp3", loop=False, volume=0.7)
        """
        if not self.music_enabled:
            return
        try:
            pygame.mixer.music.load(path)
            # Используем переданную громкость или текущую настройку
            music_vol = volume if volume is not None else self.music_volume
            pygame.mixer.music.set_volume(music_vol)
            pygame.mixer.music.play(-1 if loop else 0)
            self.current_music = path
        except pygame.error as e:
            print(f"Error loading music from '{path}': {e}")
    
    def stop_music(self) -> None:
        """Остановить воспроизведение музыки."""
        pygame.mixer.music.stop()
        self.current_music = None
    
    def pause_music(self) -> None:
        """Приостановить воспроизведение музыки."""
        pygame.mixer.music.pause()
    
    def unpause_music(self) -> None:
        """Возобновить воспроизведение музыки."""
        if self.music_enabled:
            pygame.mixer.music.unpause()
    
    def set_music_volume(self, volume: float) -> None:
        """Установить громкость музыки.
        
        Args:
            volume (float): Громкость (0.0 - 1.0). Автоматически ограничивается этим диапазоном.
            
        Example:
            >>> audio.set_music_volume(0.3)
        """
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume: float) -> None:
        """Установить громкость звуковых эффектов.
        
        Args:
            volume (float): Громкость (0.0 - 1.0). Автоматически ограничивается этим диапазоном.
            
        Example:
            >>> audio.set_sfx_volume(0.8)
        """
        self.sfx_volume = max(0.0, min(1.0, volume))
        # Обновляем громкость всех загруженных звуков
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)
    
    def set_music_enabled(self, enabled: bool) -> None:
        """Включить или выключить музыку.
        
        Args:
            enabled (bool): True для включения, False для выключения.
            
        Example:
            >>> audio.set_music_enabled(False)  # Выключить музыку
        """
        self.music_enabled = enabled
        if not enabled:
            self.pause_music()
        else:
            self.unpause_music()
    
    def set_sfx_enabled(self, enabled: bool) -> None:
        """Включить или выключить звуковые эффекты.
        
        Args:
            enabled (bool): True для включения, False для выключения.
            
        Example:
            >>> audio.set_sfx_enabled(False)  # Выключить звуки
        """
        self.sfx_enabled = enabled
    
    def get_sound(self, name: str) -> Optional['Sound']:
        """Получить обертку Sound для удобного использования.
        
        Args:
            name (str): Имя звука, загруженного через load_sound().
            
        Returns:
            Sound | None: Обертка над звуком или None, если звук не найден.
            
        Example:
            >>> audio.load_sound("bounce", "sounds/bounce.mp3")
            >>> bounce_sound = audio.get_sound("bounce")
            >>> bounce_sound.play()  # Воспроизвести
        """
        if name in self.sounds:
            return Sound(self, name)
        return None

