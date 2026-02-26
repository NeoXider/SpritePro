"""Object pooling utilities for SpritePro."""

from __future__ import annotations

from typing import Callable, Generic, Optional, TypeVar, Any
from collections import deque
import inspect

T = TypeVar("T")


class ObjectPool(Generic[T]):
    """Пул объектов для переиспользования экземпляров и снижения нагрузки на GC.

    Attributes:
        factory (Callable[[], T]): Фабрика для создания новых объектов.
        reset_fn (Optional[Callable[[T], None]]): Функция сброса объекта при возврате в пул.
        max_size (int): Максимальный размер пула (0 = без ограничений).
        initial_size (int): Начальное количество объектов в пуле.

    Example:
        >>> pool = ObjectPool(lambda: MySprite(), reset_fn=lambda s: s.reset())
        >>> obj = pool.acquire()
        >>> pool.release(obj)
    """

    def __init__(
        self,
        factory: Callable[[], T],
        reset_fn: Optional[Callable[[T], None]] = None,
        max_size: int = 0,
        initial_size: int = 0,
    ):
        """Инициализирует пул объектов.

        Args:
            factory (Callable[[], T]): Фабрика для создания новых объектов.
            reset_fn (Optional[Callable[[T], None]], optional): Функция сброса при возврате. По умолчанию None.
            max_size (int, optional): Максимальный размер пула (0 = без ограничений). По умолчанию 0.
            initial_size (int, optional): Начальное количество объектов. По умолчанию 0.
        """
        self.factory = factory
        self.reset_fn = reset_fn
        self.max_size = max_size
        self._pool: deque[T] = deque()
        self._active_count: int = 0
        self._total_created: int = 0

        if initial_size > 0:
            self._prefill(initial_size)

    def _prefill(self, count: int) -> None:
        """Заполняет пул предсозданными объектами."""
        for _ in range(count):
            self._pool.append(self.factory())
            self._total_created += 1

    def acquire(self) -> T:
        """Получает объект из пула.

        Returns:
            T: Объект из пула или новый объект.

        Note:
            Если пул пуст, создаётся новый объект через фабрику.
        """
        self._active_count += 1

        if self._pool:
            obj = self._pool.popleft()
        else:
            obj = self.factory()
            self._total_created += 1

        return obj

    def release(self, obj: T) -> bool:
        """Возвращает объект в пул.

        Args:
            obj (T): Объект для возврата.

        Returns:
            bool: True если объект принят в пул, False если отклонён (достигнут максимальный размер).
        """
        self._active_count -= 1

        if self.reset_fn:
            self.reset_fn(obj)

        if self.max_size > 0 and len(self._pool) >= self.max_size:
            return False

        self._pool.append(obj)
        return True

    def clear(self) -> None:
        """Очищает пул, удаляя все неактивные объекты."""
        self._pool.clear()

    @property
    def size(self) -> int:
        """Количество объектов в пуле (неактивных)."""
        return len(self._pool)

    @property
    def active_count(self) -> int:
        """Количество активных (используемых) объектов."""
        return self._active_count

    @property
    def total_created(self) -> int:
        """Общее количество созданных объектов (включая те, что были отклонены при max_size)."""
        return self._total_created


class PooledSpritePool(ObjectPool):
    """Специализированный пул для спрайтов SpritePro.

    Предоставляет методы для создания и сброса спрайтов с поддержкой
    всех параметров конструктора Sprite.
    """

    def __init__(
        self,
        sprite_class: type,
        max_size: int = 100,
        initial_size: int = 0,
        **default_kwargs: Any,
    ):
        """Инициализирует пул спрайтов.

        Args:
            sprite_class (type): Класс спрайта (должен быть подклассом Sprite).
            max_size (int, optional): Максимальный размер пула. По умолчанию 100.
            initial_size (int, optional): Начальное количество объектов. По умолчанию 0.
            **default_kwargs: Параметры по умолчанию для создания спрайтов.
        """
        self.sprite_class = sprite_class
        self.default_kwargs = default_kwargs

        def create_sprite() -> T:
            return sprite_class(**default_kwargs)

        def reset_sprite(sprite: T) -> None:
            if hasattr(sprite, "kill"):
                sprite.kill()
            if hasattr(sprite, "reset_sprite"):
                sprite.reset_sprite(**default_kwargs)
            elif hasattr(sprite, "_pool_release"):
                sprite._pool_release = None

        super().__init__(create_sprite, reset_sprite, max_size, initial_size)


class PoolManager:
    """Глобальный менеджер пулов для централизованного управления.

    Позволяет регистрировать и получать пулы по имени, автоматически
    создавая их при первом обращении.
    """

    _instance: Optional["PoolManager"] = None
    _pools: dict[str, ObjectPool] = {}

    def __new__(cls) -> "PoolManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._pools = {}
        return cls._instance

    @classmethod
    def get(cls, name: str) -> Optional[ObjectPool]:
        """Получает пул по имени."""
        return cls._instance._pools.get(name)

    @classmethod
    def register(cls, name: str, pool: ObjectPool) -> None:
        """Регистрирует пул под именем."""
        cls._instance._pools[name] = pool

    @classmethod
    def create_pool(
        cls,
        name: str,
        factory: Callable[[], Any],
        reset_fn: Optional[Callable[[Any], None]] = None,
        max_size: int = 0,
    ) -> ObjectPool:
        """Создаёт и регистрирует пул.

        Returns:
            ObjectPool: Созданный пул.
        """
        pool = ObjectPool(factory, reset_fn, max_size)
        cls.register(name, pool)
        return pool

    @classmethod
    def clear_all(cls) -> None:
        """Очищает все пулы."""
        for pool in cls._instance._pools.values():
            pool.clear()


def pool_acquire(pool_name: str) -> Any:
    """Получает объект из именованного пула.

    Args:
        pool_name (str): Имя пула.

    Returns:
        Any: Объект из пула.

    Raises:
        KeyError: Если пул с указанным именем не найден.
    """
    pool = PoolManager.get(pool_name)
    if pool is None:
        raise KeyError(f"Pool '{pool_name}' not found")
    return pool.acquire()


def pool_release(pool_name: str, obj: Any) -> bool:
    """Возвращает объект в именованный пул.

    Args:
        pool_name (str): Имя пула.
        obj (Any): Объект для возврата.

    Returns:
        bool: True если объект принят.

    Raises:
        KeyError: Если пул не найден.
    """
    pool = PoolManager.get(pool_name)
    if pool is None:
        raise KeyError(f"Pool '{pool_name}' not found")
    return pool.release(obj)
