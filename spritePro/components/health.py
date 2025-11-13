from typing import TYPE_CHECKING, Callable, Optional, List, Union

# Используем TYPE_CHECKING, чтобы избежать циклического импорта,
# если HealthComponent будет ссылаться на Sprite для тайп-хинтинга
if TYPE_CHECKING:
    from ..sprite import Sprite  # Указываем путь относительно spritePro

# Определяем типы колбэков для лучшей читаемости
# Колбэк на изменение HP: принимает текущее здоровье и разницу
HpChangeCallback = Callable[[float, float], None]
# Колбэк на получение урона: принимает количество урона
DamageCallback = Callable[[float], None]
# Колбэк на лечение: принимает количество лечения
HealCallback = Callable[[float], None]
# Колбэк на смерть: принимает объект спрайта-владельца
DeathCallback = Callable[["Sprite"], None]


class HealthComponent:
    """Компонент для управления здоровьем спрайта.

    Предоставляет функционал для отслеживания текущего и максимального здоровья,
    получения урона, лечения, а также вызывает пользовательские функции (колбэки)
    при различных событиях (изменение HP, получение урона, лечение, смерть).
    Поддерживает сравнение и изменение здоровья с использованием операторов.

    Attributes:
        max_health (float): Максимальное количество здоровья.
        current_health (float): Текущее количество здоровья.
        is_alive (bool): Жив ли спрайт (текущее здоровье > 0).
        owner_sprite (Optional[Sprite]): Спрайт-владелец компонента.
    """

    def __init__(
        self,
        max_health: float,
        current_health: Optional[float] = None,
        owner_sprite: Optional[
            "Sprite"
        ] = None,  # Ссылка на спрайт-владелец для колбэков
        on_hp_change: Optional[Union[HpChangeCallback, List[HpChangeCallback]]] = None,
        on_damage: Optional[Union[DamageCallback, List[DamageCallback]]] = None,
        on_heal: Optional[Union[HealCallback, List[HealCallback]]] = None,
        on_death: Optional[Union[DeathCallback, List[DeathCallback]]] = None,
    ):
        """Инициализирует компонент здоровья.

        Args:
            max_health (float): Максимальное количество здоровья. Должно быть > 0.
            current_health (Optional[float], optional): Текущее количество здоровья. Если None, устанавливается равным max_health.
            owner_sprite (Optional[Sprite], optional): Ссылка на объект спрайта, которому принадлежит этот компонент. Используется в колбэке смерти.
            on_hp_change (Optional[Union[HpChangeCallback, List[HpChangeCallback]]], optional): Функция или список функций, вызываемых при ЛЮБОМ изменении здоровья (урон или лечение). Принимает (новое_текущее_hp, разница_hp).
            on_damage (Optional[Union[DamageCallback, List[DamageCallback]]], optional): Функция или список функций, вызываемых при получении урона. Принимает (количество_урона).
            on_heal (Optional[Union[HealCallback, List[HealCallback]]], optional): Функция или список функций, вызываемых при лечении. Принимает (количество_лечения).
            on_death (Optional[Union[DeathCallback, List[DeathCallback]]], optional): Функция или список функций, вызываемых при смерти спрайта (когда текущее здоровье становится <= 0). Принимает (sprite_владелец).

        Raises:
            ValueError: Если max_health <= 0.
        """
        if max_health <= 0:
            raise ValueError(
                "Максимальное здоровье (max_health) должно быть положительным числом."
            )

        # Приватные атрибуты для хранения значений
        self._max_health: float = float(max_health)
        self._current_health: float = float(
            current_health if current_health is not None else max_health
        )
        self.owner_sprite: Optional["Sprite"] = owner_sprite

        # Сохранение колбэков в списках
        self._on_hp_change_callbacks: List[HpChangeCallback] = self._to_list(
            on_hp_change
        )
        self._on_damage_callbacks: List[DamageCallback] = self._to_list(on_damage)
        self._on_heal_callbacks: List[HealCallback] = self._to_list(on_heal)
        self._on_death_callbacks: List[DeathCallback] = self._to_list(on_death)

        # Убедимся, что начальное здоровье в допустимых пределах
        if self._current_health > self._max_health:
            self._current_health = self._max_health
        if self._current_health < 0:
            self._current_health = 0

        # Определение начального состояния живости
        self._is_alive: bool = self._current_health > 0

        # Проверка смерти при инициализации, если начальное HP <= 0
        self._check_death()

    def _to_list(
        self, callbacks: Optional[Union[Callable, List[Callable]]]
    ) -> List[Callable]:
        """Вспомогательный метод для преобразования одиночного колбэка в список."""
        if callbacks is None:
            return []
        if isinstance(callbacks, list):
            # Фильтруем на случай, если в списке None
            return [cb for cb in callbacks if cb is not None]
        return [callbacks]

    # --- Свойства (Properties) ---

    @property
    def max_health(self) -> float:
        """Максимальное количество здоровья.
        
        Returns:
            float: Максимальное количество здоровья.
        """
        return self._max_health

    @max_health.setter
    def max_health(self, value: float):
        """Устанавливает новое максимальное здоровье, корректируя текущее.

        Args:
            value (float): Новое максимальное значение здоровья.

        Raises:
            ValueError: Если value <= 0.
        """
        if value <= 0:
            raise ValueError(
                "Новое максимальное здоровье должно быть положительным числом."
            )
        if value != self._max_health:
            self._max_health = float(value)
            if self._current_health > self._max_health:
                self.current_health = self._max_health

            # print(f"Максимальное здоровье изменено на {self._max_health}.")

    @property
    def current_health(self) -> float:
        """Текущее количество здоровья.
        
        Returns:
            float: Текущее количество здоровья.
        """
        return self._current_health

    @current_health.setter
    def current_health(self, value: float):
        """Устанавливает новое текущее здоровье.

        Этот сеттер автоматически вызывает колбэк изменения HP,
        ограничивает значение в пределах [0, max_health] и
        проверяет состояние смерти.

        Args:
            value (float): Новое значение текущего здоровья.
        """
        old_health = self._current_health
        new_health = max(
            0.0, min(float(value), self._max_health)
        )  # Ограничиваем в пределах [0, max_health]

        if new_health != old_health:
            self._current_health = new_health
            hp_difference = new_health - old_health

            # Вызываем колбэки изменения HP
            self._call_callbacks(
                self._on_hp_change_callbacks, new_health, hp_difference
            )

            # Проверяем состояние смерти после изменения HP
            self._check_death()

    @property
    def is_alive(self) -> bool:
        """Проверяет, жив ли спрайт.
        
        Returns:
            bool: True, если спрайт жив (текущее здоровье > 0).
        """
        return self._is_alive

    # --- Методы изменения здоровья ---

    def take_damage(self, amount: float, damage_type: Optional[str] = None):
        """Наносит урон спрайту.

        Если спрайт уже мертв, метод ничего не делает. Значение amount
        должно быть положительным.

        Args:
            amount (float): Количество урона. Должно быть > 0.
            damage_type (Optional[str], optional): Тип урона (опционально, для продвинутых систем резистов/уязвимостей).

        Raises:
            ValueError: Если amount <= 0.
        """
        if amount <= 0:
            raise ValueError(
                "Количество урона (amount) должно быть положительным числом."
            )
        if not self._is_alive:
            # print("Попытка нанести урон уже мертвому спрайту.") # Можно закомментировать в финальной версии
            return

        # TODO: Применить логику резистов/уязвимостей на основе damage_type перед изменением HP

        # Изменяем текущее HP с использованием сеттера, который вызовет колбэки HP change и death
        self.current_health -= amount  # Используем оператор вычитания, который вызовет сеттер current_health

        # Вызываем колбэки получения урона
        self._call_callbacks(self._on_damage_callbacks, amount)

        print(
            f"Спрайт получил {amount} урона. Осталось {self._current_health}/{self._max_health} HP."
        )

    def heal(self, amount: float, heal_type: Optional[str] = None):
        """Лечит спрайт.

        Если спрайт уже мертв и компонент не настроен на воскрешение
        (по умолчанию не настроен), метод ничего не делает. Значение amount
        должно быть положительным.

        Args:
            amount (float): Количество лечения. Должно быть > 0.
            heal_type (Optional[str], optional): Тип лечения (опционально).

        Raises:
            ValueError: Если amount <= 0.
        """
        if amount <= 0:
            raise ValueError(
                "Количество лечения (amount) должно быть положительным числом."
            )
        if not self._is_alive:
            # TODO: Добавить логику воскрешения, если требуется. Пока просто выходим.
            # print("Попытка вылечить мертвого спрайта.")
            return

        # Изменяем текущее HP с использованием сеттера, который вызовет колбэки HP change
        self.current_health += amount  # Используем оператор сложения, который вызовет сеттер current_health

        # Вызываем колбэки лечения
        self._call_callbacks(self._on_heal_callbacks, amount)

        print(
            f"Спрайт вылечен на {amount}. Текущее HP: {self._current_health}/{self._max_health}."
        )

    def resurrect(self, heal_to_max: bool = True):
        """Воскрешает спрайт.

        Если спрайт в данный момент мертв, этот метод устанавливает флаг is_alive
        в True и опционально восстанавливает здоровье до максимального значения.

        Args:
            heal_to_max (bool, optional): Если True (по умолчанию), устанавливает текущее здоровье равным максимальному после воскрешения. Если False, текущее здоровье остается как есть.
        """
        # print(f"Спрайт {self.owner_sprite} воскресает!")
        self._is_alive = True  # Устанавливаем флаг живости

        if heal_to_max:
            # Используем сеттер current_health, чтобы вызвать колбэк изменения HP
            self.current_health = self._max_health

        # TODO: Возможно, вызвать отдельный колбэк на воскрешение, если он нужен

    # --- Методы управления колбэками ---

    def add_on_hp_change_callback(self, callback: HpChangeCallback):
        """Добавляет функцию в список колбэков на изменение HP.
        
        Args:
            callback (HpChangeCallback): Функция обратного вызова для добавления.
        """
        if callable(callback):
            self._on_hp_change_callbacks.append(callback)
        else:
            print(
                "Предупреждение: Попытка добавить некорректный колбэк на изменение HP."
            )

    def remove_on_hp_change_callback(self, callback: HpChangeCallback):
        """Удаляет функцию из списка колбэков на изменение HP.
        
        Args:
            callback (HpChangeCallback): Функция обратного вызова для удаления.
        """
        if callback in self._on_hp_change_callbacks:
            self._on_hp_change_callbacks.remove(callback)

    def add_on_damage_callback(self, callback: DamageCallback):
        """Добавляет функцию в список колбэков на получение урона.
        
        Args:
            callback (DamageCallback): Функция обратного вызова для добавления.
        """
        if callable(callback):
            self._on_damage_callbacks.append(callback)
        else:
            print(
                "Предупреждение: Попытка добавить некорректный колбэк на получение урона."
            )

    def remove_on_damage_callback(self, callback: DamageCallback):
        """Удаляет функцию из списка колбэков на получение урона.
        
        Args:
            callback (DamageCallback): Функция обратного вызова для удаления.
        """
        if callback in self._on_damage_callbacks:
            self._on_damage_callbacks.remove(callback)

    def add_on_heal_callback(self, callback: HealCallback):
        """Добавляет функцию в список колбэков на лечение.
        
        Args:
            callback (HealCallback): Функция обратного вызова для добавления.
        """
        if callable(callback):
            self._on_heal_callbacks.append(callback)
        else:
            print("Предупреждение: Попытка добавить некорректный колбэк на лечение.")

    def remove_on_heal_callback(self, callback: HealCallback):
        """Удаляет функцию из списка колбэков на лечение.
        
        Args:
            callback (HealCallback): Функция обратного вызова для удаления.
        """
        if callback in self._on_heal_callbacks:
            self._on_heal_callbacks.remove(callback)

    def add_on_death_callback(self, callback: DeathCallback):
        """Добавляет функцию в список колбэков на смерть.
        
        Args:
            callback (DeathCallback): Функция обратного вызова для добавления.
        """
        if callable(callback):
            self._on_death_callbacks.append(callback)
        else:
            print("Предупреждение: Попытка добавить некорректный колбэк на смерть.")

    def remove_on_death_callback(self, callback: DeathCallback):
        """Удаляет функцию из списка колбэков на смерть.
        
        Args:
            callback (DeathCallback): Функция обратного вызова для удаления.
        """
        if callback in self._on_death_callbacks:
            self._on_death_callbacks.remove(callback)

    def _call_callbacks(self, callbacks: List[Callable], *args, **kwargs):
        """Вспомогательный метод для безопасного вызова списка колбэков."""
        for callback in callbacks:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                print(f"Ошибка при вызове колбэка {callback.__name__}: {e}")

    # --- Внутренние методы ---

    def _check_death(self):
        """
        Проверяет, умер ли спрайт.

        Если текущее здоровье <= 0 и спрайт считался живым,
        устанавливает флаг is_alive в False и вызывает колбэки смерти.
        """
        if self._is_alive and self._current_health <= 0:
            self._is_alive = False
            print(f"Спрайт {self.owner_sprite} умер.")
            # Вызываем колбэки смерти, передавая спрайт-владелец
            self._call_callbacks(self._on_death_callbacks, self.owner_sprite)

        # Если здоровье стало > 0, а считался мертвым (например, воскрешение),
        # можно добавить логику обработки воскрешения
        # elif not self._is_alive and self._current_health > 0:
        #     self._is_alive = True
        #     print(f"Спрайт {self.owner_sprite} воскрес!")
        # TODO: Вызвать колбэк воскрешения, если он есть

    # --- Перегрузка операторов для удобства ---

    def __lt__(self, other: Union[float, int, bool, "HealthComponent"]) -> bool:
        """
        Сравнение: здоровье < other. Сравнивается текущее HP.
        При сравнении с bool: True трактуется как 1, False как 0.
        """
        if isinstance(other, (int, float)):
            return self._current_health < other
        elif isinstance(other, bool):
            # Сравниваем текущее HP с 1.0 для True и 0.0 для False
            return self._current_health < float(other)
        elif isinstance(other, HealthComponent):
            return self._current_health < other.current_health
        return NotImplemented  # Возвращаем NotImplemented для обработки других типов

    def __le__(self, other: Union[float, int, bool, "HealthComponent"]) -> bool:
        """
        Сравнение: здоровье <= other. Сравнивается текущее HP.
        При сравнении с bool: True трактуется как 1, False как 0.
        """
        if isinstance(other, (int, float)):
            return self._current_health <= other
        elif isinstance(other, bool):
            return self._current_health <= float(other)
        elif isinstance(other, HealthComponent):
            return self._current_health <= other.current_health
        return NotImplemented

    def __gt__(self, other: Union[float, int, bool, "HealthComponent"]) -> bool:
        """
        Сравнение: здоровье > other. Сравнивается текущее HP.
        При сравнении с bool: True трактуется как 1, False как 0.
        """
        if isinstance(other, (int, float)):
            return self._current_health > other
        elif isinstance(other, bool):
            return self._current_health > float(other)
        elif isinstance(other, HealthComponent):
            return self._current_health > other.current_health
        return NotImplemented

    def __ge__(self, other: Union[float, int, bool, "HealthComponent"]) -> bool:
        """
        Сравнение: здоровье >= other. Сравнивается текущее HP.
        При сравнении с bool: True трактуется как 1, False как 0.
        """
        if isinstance(other, (int, float)):
            return self._current_health >= other
        elif isinstance(other, bool):
            return self._current_health >= float(other)
        elif isinstance(other, HealthComponent):
            return self._current_health >= other.current_health
        return NotImplemented

    def __eq__(self, other: Union[float, int, bool, "HealthComponent"]) -> bool:
        """
        Сравнение: здоровье == other.
        При сравнении с числом: сравнивается текущее HP.
        При сравнении с bool: сравнивается состояние живости (is_alive).
        """
        if isinstance(other, (int, float)):
            # Используем небольшую дельту для сравнения float
            return abs(self._current_health - other) < 1e-9
        elif isinstance(other, bool):
            # Сравниваем состояние живости с булевым значением
            return self._is_alive == other
        elif isinstance(other, HealthComponent):
            # Сравниваем текущее HP двух компонентов
            return abs(self._current_health - other.current_health) < 1e-9
        return NotImplemented  # Возвращаем NotImplemented для обработки других типов

    def __ne__(self, other: Union[float, int, bool, "HealthComponent"]) -> bool:
        """
        Сравнение: здоровье != other.
        При сравнении с числом: сравнивается текущее HP.
        При сравнении с bool: сравнивается состояние живости (is_alive).
        """
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def __iadd__(self, amount: float) -> "HealthComponent":
        """Перегрузка оператора '+='. Лечит спрайт на указанное количество.
        
        `health_component += amount` эквивалентно `health_component.heal(amount)`.

        Args:
            amount (float): Количество лечения. Должно быть > 0.

        Returns:
            HealthComponent: Сам объект компонента здоровья (для цепочки операций).

        Raises:
            ValueError: Если amount <= 0.
        """
        # Важно: вызываем метод heal, чтобы использовать его логику (проверка живости, колбэки)
        # Метод heal уже использует сеттер current_health
        self.heal(amount)
        return self

    def __isub__(self, amount: float) -> "HealthComponent":
        """Перегрузка оператора '-='. Наносит урон спрайту на указанное количество.
        
        `health_component -= amount` эквивалентно `health_component.take_damage(amount)`.

        Args:
            amount (float): Количество урона. Должно быть > 0.

        Returns:
            HealthComponent: Сам объект компонента здоровья.

        Raises:
            ValueError: Если amount <= 0.
        """
        # Важно: вызываем метод take_damage, чтобы использовать его логику (проверка живости, колбэки)
        # Метод take_damage уже использует сеттер current_health
        self.take_damage(amount)
        return self

    def __str__(self) -> str:
        """Возвращает строковое представление компонента здоровья.
        
        Returns:
            str: Строковое представление в формате "Health(текущее/максимальное, Alive: bool)".
        """
        return f"Health({self._current_health}/{self._max_health}, Alive: {self._is_alive})"

    def __repr__(self) -> str:
        """Возвращает формальное строковое представление компонента здоровья.
        
        Returns:
            str: Формальное строковое представление компонента.
        """
        return f"HealthComponent(max_health={self._max_health}, current_health={self._current_health}, is_alive={self._is_alive}, owner_sprite={self.owner_sprite})"

    # TODO: Реализовать метод update(self, dt: float) для обработки DoT/HoT эффектов


# Пример использования (для тестирования компонента отдельно от спрайтов)
if __name__ == "__main__":

    class DummySprite:  # Простой класс-заглушка для спрайта-владельца
        def __init__(self, name):
            self.name = name

        def __str__(self):
            return self.name

    def handle_hp_change(new_hp, diff):
        print(f"  Колбэк HP Change: Новое HP = {new_hp}, Изменение = {diff}")

    def handle_damage(amount):
        print(f"  Колбэк Damage: Получено урона = {amount}")

    def handle_heal(amount):
        print(f"  Колбэк Heal: Получено лечения = {amount}")

    def handle_death(sprite):
        print(f"  Колбэк Death: {sprite} ============================ мертв!")

    print("Создаем компонент здоровья с HP = 50/100")
    dummy_owner = DummySprite("Тестовый Объект")
    health = HealthComponent(
        max_health=100,
        current_health=50,
        owner_sprite=dummy_owner,
        on_hp_change=[handle_hp_change],  # Список колбэков
        on_damage=handle_damage,  # Один колбэк
        on_death=handle_death,
    )
    print(health)
    print(f"Жив ли? {health.is_alive}")
    print("-" * 20)

    print("Наносим 20 урона (health -= 20)")
    health -= 20  # Используем перегруженный оператор -=
    print(health)
    print(f"Жив ли? {health.is_alive}")
    print("-" * 20)

    print("Наносим 40 урона (health.take_damage(40))")
    health.take_damage(40)  # Используем метод take_damage
    print(health)
    print(f"Жив ли? {health.is_alive}")
    print("-" * 20)

    print("Наносим 50 урона (health.take_damage(50))")
    health.take_damage(50)  # Это должно убить спрайт
    print(health)
    print(f"Жив ли? {health.is_alive}")
    print("-" * 20)

    print("Попытка нанести еще 10 урона (health -= 10)")
    health -= 10  # Спрайт мертв, не должно сработать
    print(health)
    print(f"Жив ли? {health.is_alive}")
    print("-" * 20)

    print("Пытаемся вылечить на 30 (health.heal(30))")
    health.heal(30)  # Спрайт мертв, не должно сработать
    print(health)
    print(f"Жив ли? {health.is_alive}")
    print("-" * 20)

    print("Устанавливаем максимальное HP = 50 (health.max_health = 50)")
    health.max_health = 50  # Спрайт мертв (HP 0), max_health изменится, HP останется 0
    print(health)
    print(f"Жив ли? {health.is_alive}")
    print("-" * 20)

    print("Устанавливаем текущее HP = 20 (health.current_health = 20)")
    # Это должно воскресить спрайт (если бы _check_death обрабатывал воскрешение)
    # С текущей логикой, просто меняется HP. is_alive все еще False.
    health.current_health = 20
    print(health)
    print(f"Жив ли? {health.is_alive}")  # Пока False
    print("-" * 20)

    print("Добавляем колбэк лечения и лечим на 10 (health += 10)")
    health.add_on_heal_callback(handle_heal)
    health += 10  # Теперь лечение должно сработать и вызвать колбэк heal и hp_change
    print(health)
    print(f"Жив ли? {health.is_alive}")  # Пока False
    print("-" * 20)

    # Пример сравнения с числами
    print("Примеры сравнения с числами:")
    print(f"health < 30: {health < 30}")
    print(f"health >= 30: {health >= 30}")
    print(f"health == 0: {health == 0}")
    print(f"health != 50: {health != 50}")

    print(f"живой: {health is True}")
