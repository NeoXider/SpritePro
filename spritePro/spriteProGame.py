from typing import List
import pygame
from pygame.math import Vector2


class SpriteProGame:
    """Одиночный игровой контекст с общей группой спрайтов и камерой.

    Управляет всеми спрайтами игры, камерой и их взаимодействием.
    Использует паттерн Singleton для обеспечения единственного экземпляра.

    Attributes:
        all_sprites (pygame.sprite.LayeredUpdates): Группа всех спрайтов с поддержкой слоев.
        camera (Vector2): Позиция камеры.
        camera_target (pygame.sprite.Sprite | None): Целевой спрайт для следования камеры.
        camera_offset (Vector2): Смещение камеры относительно цели.
        _instance (SpriteProGame | None): Единственный экземпляр класса.
    """

    _instance: "SpriteProGame | None" = None

    def __init__(self) -> None:
        """Инициализирует SpriteProGame.

        Создает группу спрайтов, инициализирует камеру и устанавливает экземпляр как единственный.
        """
        if SpriteProGame._instance is not None:
            return
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.camera = Vector2()
        self.camera_target: pygame.sprite.Sprite | None = None
        self.camera_offset = Vector2()
        self.update_objects: list = []  # Объекты для автоматического обновления
        SpriteProGame._instance = self

    @classmethod
    def get(cls) -> "SpriteProGame":
        """Получает единственный экземпляр SpriteProGame.

        Returns:
            SpriteProGame: Единственный экземпляр игрового контекста.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_sprite(self, sprite: pygame.sprite.Sprite) -> None:
        """Регистрирует спрайт в игровом контексте.

        Добавляет спрайт в группу всех спрайтов. Если у спрайта есть атрибут sorting_order,
        он будет добавлен на соответствующий слой.

        Args:
            sprite (pygame.sprite.Sprite): Спрайт для регистрации.
        """
        if sprite not in self.all_sprites:
            # If sprite has a declared sorting order, add it at that layer
            layer = getattr(sprite, "sorting_order", None)
            if layer is not None:
                try:
                    self.all_sprites.add(sprite, layer=int(layer))
                except Exception:
                    # Fallback to default add if layer add fails
                    self.all_sprites.add(sprite)
            else:
                self.all_sprites.add(sprite)
        if hasattr(sprite, "_game_registered"):
            sprite._game_registered = True

    def unregister_sprite(self, sprite: pygame.sprite.Sprite) -> None:
        """Отменяет регистрацию спрайта в игровом контексте.

        Удаляет спрайт из группы всех спрайтов.

        Args:
            sprite (pygame.sprite.Sprite): Спрайт для отмены регистрации.
        """
        self.all_sprites.remove(sprite)
        if hasattr(sprite, "_game_registered"):
            sprite._game_registered = False

    def enable_sprite(self, sprite: pygame.sprite.Sprite) -> None:
        """Включает спрайт (регистрирует его).

        Args:
            sprite (pygame.sprite.Sprite): Спрайт для включения.
        """
        self.register_sprite(sprite)

    def disable_sprite(self, sprite: pygame.sprite.Sprite) -> None:
        """Отключает спрайт (отменяет его регистрацию).

        Args:
            sprite (pygame.sprite.Sprite): Спрайт для отключения.
        """
        self.unregister_sprite(sprite)

    def set_sprite_layer(self, sprite: pygame.sprite.Sprite, layer: int) -> None:
        """Устанавливает слой отрисовки для спрайта в глобальной группе со слоями.

        Args:
            sprite (pygame.sprite.Sprite): Спрайт для установки слоя.
            layer (int): Номер слоя для отрисовки.
        """
        try:
            # If sprite is not in the group yet, add with layer
            if sprite not in self.all_sprites:
                self.all_sprites.add(sprite, layer=int(layer))
            else:
                self.all_sprites.change_layer(sprite, int(layer))
        except Exception:
            # Silently ignore if the underlying group does not support layers
            pass

    def set_camera(self, position: Vector2 | tuple[float, float]) -> None:
        """Устанавливает позицию камеры.

        Устанавливает камеру в указанную позицию и отменяет следование за целью.

        Args:
            position (Vector2 | tuple[float, float]): Позиция камеры (x, y).
        """
        if isinstance(position, Vector2):
            self.camera.update(position)
        else:
            self.camera.update(float(position[0]), float(position[1]))
        self.camera_target = None
        self.camera_offset.update(0.0, 0.0)

    def move_camera(self, dx: float, dy: float) -> None:
        """Перемещает камеру на указанное смещение.

        Если камера следует за целью, смещение добавляется к offset.
        Иначе камера перемещается напрямую.

        Args:
            dx (float): Смещение по оси X.
            dy (float): Смещение по оси Y.
        """
        if self.camera_target is not None:
            self.camera_offset.x += dx
            self.camera_offset.y += dy
        else:
            self.camera.x += dx
            self.camera.y += dy

    def get_camera(self) -> Vector2:
        """Получает текущую позицию камеры.

        Returns:
            Vector2: Позиция камеры.
        """
        return self.camera

    def set_camera_follow(
        self,
        target: pygame.sprite.Sprite | None,
        offset: Vector2 | tuple[float, float] = (0.0, 0.0),
    ) -> None:
        """Устанавливает цель для следования камеры.

        Камера будет автоматически следовать за указанным спрайтом с заданным смещением.

        Args:
            target (pygame.sprite.Sprite | None): Целевой спрайт для следования или None для отмены.
            offset (Vector2 | tuple[float, float], optional): Смещение камеры относительно цели. По умолчанию (0.0, 0.0).
        """
        if target is None:
            self.clear_camera_follow()
            return
        self.camera_target = target
        if isinstance(offset, Vector2):
            self.camera_offset = offset.copy()
        else:
            self.camera_offset = Vector2(offset[0], offset[1])
        # При установке цели WH_C может быть еще не инициализирован, используем значение по умолчанию
        self._update_camera_follow()

    def clear_camera_follow(self) -> None:
        """Отменяет следование камеры за целью."""
        self.camera_target = None
        self.camera_offset.update(0.0, 0.0)

    def _update_camera_follow(self, wh_c: Vector2 | None = None) -> None:
        """Обновляет позицию камеры при следовании за целью.
        
        Args:
            wh_c (Vector2 | None, optional): Центр экрана. Если None, используется значение по умолчанию (400, 300).
        """
        target = self.camera_target
        if not target:
            return
        alive_attr = getattr(target, "alive", None)
        if callable(alive_attr) and not alive_attr():
            self.clear_camera_follow()
            return
        center = Vector2(target.rect.center)
        if wh_c is None:
            wh_c = Vector2(400, 300)  # Значение по умолчанию
        desired = center - wh_c + self.camera_offset
        self.camera.update(desired)

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает все спрайты на указанной поверхности.

        Args:
            surface (pygame.Surface): Поверхность для отрисовки.
        """
        self.all_sprites.draw(surface)

    def register_update_object(self, obj) -> None:
        """Регистрирует объект для автоматического обновления.

        Объект должен иметь метод update(), который будет вызываться каждый кадр с dt.

        Args:
            obj: Объект для обновления (TweenManager, Animation, Timer и т.д.).
        """
        if obj not in self.update_objects:
            self.update_objects.append(obj)

    def unregister_update_object(self, obj) -> None:
        """Отменяет регистрацию объекта для автоматического обновления.

        Args:
            obj: Объект для отмены регистрации.
        """
        if obj in self.update_objects:
            self.update_objects.remove(obj)

    def get_sprites_by_class(self, sprite_class: type, active_only: bool = True) -> List:
        """Получает список всех спрайтов указанного класса.

        Args:
            sprite_class (type): Класс спрайтов для поиска.
            active_only (bool, optional): Если True, возвращает только активные спрайты. По умолчанию True.

        Returns:
            List: Список спрайтов указанного класса.

        Example:
            >>> fountain_particles = game.get_sprites_by_class(FountainParticle)
            >>> all_sprites = game.get_sprites_by_class(Sprite, active_only=False)
        """
        result = [
            sprite for sprite in self.all_sprites
            if isinstance(sprite, sprite_class)
        ]
        
        if active_only:
            result = [sprite for sprite in result if hasattr(sprite, 'active') and sprite.active]
        
        return result

    def update(self, *args, wh_c: Vector2 | None = None, **kwargs) -> None:
        """Обновляет камеру и все спрайты.

        Args:
            *args: Позиционные аргументы для передачи в update спрайтов.
            wh_c (Vector2 | None, optional): Центр экрана для обновления камеры. По умолчанию None.
            **kwargs: Именованные аргументы для передачи в update спрайтов.
        """
        self._update_camera_follow(wh_c)
        
        # Автоматически обновляем зарегистрированные объекты
        dt = kwargs.pop('dt', None)
        if dt is None:
            try:
                import spritePro as sp
                dt = sp.dt
            except (AttributeError, NameError):
                dt = None
        
        for obj in self.update_objects:
            if hasattr(obj, 'update'):
                # Пытаемся вызвать update с dt, если доступен
                try:
                    import inspect
                    sig = inspect.signature(obj.update)
                    params = list(sig.parameters.keys())
                    # Убираем 'self' из параметров
                    if 'self' in params:
                        params.remove('self')
                    
                    if params and dt is not None:
                        # Метод принимает параметры, передаем dt
                        obj.update(dt)
                    else:
                        # Метод не принимает параметров или dt недоступен
                        obj.update()
                except (TypeError, ValueError):
                    # Если не удалось определить сигнатуру, пробуем вызвать без параметров
                    try:
                        obj.update()
                    except TypeError:
                        try: 
                            obj.update(dt)
                        except TypeError:
                            print(f"Error update object {obj}")
                         
        
        self.all_sprites.update(*args, **kwargs)