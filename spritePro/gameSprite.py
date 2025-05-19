from typing import Callable, List, Optional
import pygame
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
import spritePro
from spritePro.sprite import Sprite

# Импортируем наш компонент здоровья
from spritePro.components.health import HealthComponent, DamageCallback, DeathCallback


class GameSprite(Sprite):
    _last_obstacles_hash = None
    _last_obstacles_rects = None
    collision_step: int = 1

    def __init__(
        self,
        sprite: str,
        size: tuple = (50, 50),
        pos: tuple = (0, 0),
        speed: float = 0,
        max_health: int = 100,
        # Возможность передать начальное HP, по умолчанию равно max_health
        current_health: Optional[int] = None,
    ):
        """
        Инициализация игрового спрайта с компонентом здоровья.

        Аргументы:
            sprite: Путь к изображению спрайта или имя ресурса
            size: Размер спрайта (ширина, высота) по умолчанию (50, 50)
            pos: Начальная позиция спрайта (x, y) по умолчанию (0, 0)
            speed: Скорость движения спрайта по умолчанию 0
            max_health: Максимальное количество здоровья спрайта (по умолчанию 100).
                        Это значение используется для инициализации HealthComponent.
            current_health: Начальное текущее здоровье. Если None, равно max_health.
        """
        super().__init__(sprite, size, pos, speed)

        # >>> Создаем компонент здоровья вместо старых атрибутов <<<
        # Начальное текущее здоровье либо переданное, либо равно max_health
        initial_current_health = (
            current_health if current_health is not None else max_health
        )
        self.health_component: HealthComponent = HealthComponent(
            max_health=max_health,
            current_health=initial_current_health,
            owner_sprite=self,  # Ссылка на этот спрайт как владельца
            # Колбэки смерти и урона будут управляться через HealthComponent
            on_death=self._handle_death_event,  # Наш внутренний обработчик смерти
            on_damage=self._handle_damage_state,  # Наш внутренний обработчик урона для смены состояния
        )

        # Коллбэки для событий, которые пользователь может установить извне
        # Теперь они будут вызываться из наших внутренних обработчиков HealthComponent
        self.on_collision: Optional[Callable] = None
        # Старый on_death теперь хранится здесь и вызывается из _handle_death_event
        self._user_on_death_callback: Optional[Callable[["GameSprite"], None]] = None

    # --- Новые внутренние методы для обработки колбэков HealthComponent ---

    def _handle_damage_state(self, amount: float):
        """
        Внутренний колбэк HealthComponent, вызывается при получении урона.
        Устанавливает состояние спрайта в 'hit'.
        """
        print(
            f"{self.name if hasattr(self, 'name') else type(self).__name__} получил урон. Устанавливаем состояние 'hit'."
        )
        self.state = "hit"  # Устанавливаем состояние "hit"

    def _handle_death_event(self, dead_sprite: "Sprite"):
        """
        Внутренний колбэк HealthComponent, вызывается при смерти спрайта.
        Устанавливает состояние спрайта в 'dead' и вызывает пользовательский колбэк.
        """
        print(
            f"{self.name if hasattr(self, 'name') else type(self).__name__} умер. Устанавливаем состояние 'dead'."
        )
        # self.alive = False # Этот атрибут теперь управляется в HealthComponent (is_alive)
        self.state = "dead"  # Устанавливаем состояние "dead"

        # Вызываем пользовательский колбэк смерти, если он установлен
        if self._user_on_death_callback:
            # Передаем ссылку на GameSprite, как в старом коде
            self._user_on_death_callback(self)

    # --- Методы установки пользовательских колбэков (теперь просто сохраняют ссылку) ---

    def on_collision_event(self, callback: Callable):
        """Установка функции обратного вызова для событий столкновения."""
        self.on_collision = callback  # TODO: Возможно, стоит интегрировать коллизии и урон через компоненты

    def on_death_event(self, callback: Callable[["GameSprite"], None]):
        """
        Установка функции обратного вызова для событий смерти.
        Эта функция будет вызвана после того, как HealthComponent
        обработает смерть.
        """
        # Сохраняем пользовательский колбэк
        if callable(callback):
            self._user_on_death_callback = callback
        else:
            print("Предупреждение: Попытка установить некорректный колбэк смерти.")

    # --- Остальные методы GameSprite (collide_with, collide_with_group, etc.) без изменений ---
    # Они не зависят напрямую от внутренней реализации здоровья, только от наличия спрайта.

    def collide_with(self, other_sprite) -> bool:
        """
        Проверка столкновения с другим спрайтом, используя маски для точности.

        Аргументы:
            other_sprite: Другой экземпляр GameSprite для проверки столкновения

        Возвращает:
            bool: True если есть столкновение, False иначе
        """
        if pygame.sprite.collide_rect(self, other_sprite):
            offset = (
                other_sprite.rect.x - self.rect.x,
                other_sprite.rect.y - self.rect.y,
            )
            if other_sprite.mask is not None and self.mask is not None:
                return self.mask.overlap(other_sprite.mask, offset) is not None
            return True
        return False

    def collide_with_group(self, group: pygame.sprite.Group) -> List:
        """
        Проверка столкновения с группой спрайтов, используя маски для точности.

        Аргументы:
            group: Группа спрайтов для проверки столкновения

        Возвращает:
            list: Список спрайтов, с которыми сталкивается данный спрайт
        """
        return pygame.sprite.spritecollide(
            self, group, False, pygame.sprite.collide_mask
        )

    def collide_with_tag(self, group: pygame.sprite.Group, tag: str) -> List:
        """Проверка столкновения с группой спрайтов по тегу."""
        return [
            sprite
            for sprite in group
            if sprite.tag == tag and self.collide_with(sprite)
        ]

    def _get_collision_side(self, prev_x, prev_y, rect):
        # Определяет сторону столкновения: 'top', 'bottom', 'left', 'right', 'inside'
        cx, cy = self.rect.center
        if prev_y + self.rect.height // 2 <= rect.top:
            return "bottom"  # мы сверху
        elif prev_y - self.rect.height // 2 >= rect.bottom:
            return "top"  # мы снизу
        elif prev_x + self.rect.width // 2 <= rect.left:
            return "right"  # мы слева
        elif prev_x - self.rect.width // 2 >= rect.right:
            return "left"  # мы справа
        else:
            return "inside"

    def resolve_collisions(self, *obstacles):
        """
        Останавливает движение при столкновении с любыми препятствиями.
        obstacles — любое количество спрайтов, ректов, групп или списков.
        Возвращает список кортежей (rect, side), где side — сторона столкновения.
        """

        def flatten_ids(objs):
            ids = []
            for obj in objs:
                if isinstance(obj, (list, tuple, pygame.sprite.Group)):
                    ids.extend(flatten_ids(obj))
                else:
                    ids.append(id(obj))
            return ids

        obstacles_hash = hash(tuple(flatten_ids(obstacles)))
        if (
            obstacles_hash == self._last_obstacles_hash
            and self._last_obstacles_rects is not None
        ):
            rects = self._last_obstacles_rects
        else:
            rects = []
            for obj in obstacles:
                if isinstance(obj, pygame.sprite.Sprite):
                    rects.append(obj.rect)
                elif isinstance(obj, pygame.Rect):
                    rects.append(obj)
                elif isinstance(obj, (pygame.sprite.Group, list, tuple)):
                    for o in obj:
                        if isinstance(o, pygame.sprite.Sprite):
                            rects.append(o.rect)
                        elif isinstance(o, pygame.Rect):
                            rects.append(o)
            self._last_obstacles_hash = obstacles_hash
            self._last_obstacles_rects = rects
        # --- Шаг проверки теперь задается через self.collision_step ---
        step = max(1, int(getattr(self, "collision_step", 1)))
        total_steps = int(max(abs(self.velocity.x), abs(self.velocity.y)) // step)
        if total_steps == 0:
            return []
        dx = self.velocity.x / (total_steps * step) if total_steps else 0
        dy = self.velocity.y / (total_steps * step) if total_steps else 0
        collisions = []
        for _ in range(total_steps * step):
            prev_x = self.position.x
            prev_y = self.position.y
            self.position.x += dx
            self.position.y += dy
            self.rect.center = (int(self.position.x), int(self.position.y))
            for r in rects:
                if self.rect.colliderect(r):
                    side = self._get_collision_side(prev_x, prev_y, r)
                    collisions.append((r, side))
                    self.position.x -= dx
                    self.position.y -= dy
                    self.rect.center = (int(self.position.x), int(self.position.y))
                    if abs(dx) > abs(dy):
                        self.velocity.x = 0
                    else:
                        self.velocity.y = 0
                    return collisions
        return collisions


# --- Простая демонстрация использования ---
if __name__ == "__main__":
    spritePro.init()
    screen = spritePro.get_screen((800, 600), "GameSprite Demo")

    def player_death_handler(player_sprite: GameSprite):
        print(
            f"Демо: Игрок {player_sprite.name if hasattr(player_sprite, 'name') else 'без имени'} умер!"
        )
        print("Демо: Останавливаем цикл игры.")
        global running
        running = False  # Останавливаем основной цикл

    def player_change_hp(hp, amount):
        player.set_scale(
            player.health_component.current_health / player.health_component.max_health
        )

    # Создаем экземпляр GameSprite
    # Пустая строка для спрайта означает, что Pygame создаст Surface
    player = GameSprite(
        sprite="",
        size=(250, 250),
        pos=(spritePro.WH[0] // 4, spritePro.WH_CENTER[1]),
        max_health=100,
        speed=5,
    )
    player.name = "Игрок"  # Даем имя для вывода в консоль

    # Устанавливаем колбэк смерти GameSprite (он будет вызван из HealthComponent)
    player.on_death_event(player_death_handler)

    player.health_component.add_on_hp_change_callback(player_change_hp)

    # Можно установить начальный цвет, чтобы видеть спрайт
    player.set_color((0, 255, 0))  # Зеленый цвет

    # Враг для демонстрации урона (не будет получать урон в этой демо)
    enemy = GameSprite(
        sprite="",
        size=(40, 40),
        pos=(spritePro.WH[0] * 3 // 4, spritePro.WH_CENTER[1]),
        max_health=10,
        speed=0,
    )
    enemy.name = "Враг"
    enemy.set_color((255, 0, 0))  # Красный цвет

    all_sprites = pygame.sprite.Group()
    all_sprites.add(player, enemy)

    running = True

    print("Демо: Начинаем. Игрок HP:", player.health_component.current_health)

    damage_taken = False  # Флаг, чтобы нанести урон один раз

    while True:
        spritePro.update()

        for event in spritePro.events:
            if event.type == pygame.QUIT:
                running = False
            # Простой ввод для нанесения урона, лечения и воскрешения
            if event.type == pygame.KEYDOWN:
                if (
                    event.key == pygame.K_s and player.health_component.is_alive
                ):  # Проверяем, жив ли, прежде чем нанести урон
                    print("Демо: Наносим игроку 30 урона (пробел).")
                    # Используем метод take_damage из HealthComponent
                    player.health_component.take_damage(10)
                    print(
                        "Демо: Игрок HP после урона:",
                        player.health_component.current_health,
                    )

                if (
                    event.key == pygame.K_w and player.health_component.is_alive
                ):  # Лечить только если жив (пока без логики воскрешения через лечение)
                    print("Демо: Лечим игрока на 10 (H).")
                    # Используем оператор += (перегружен в HealthComponent)
                    player.health_component += 10
                    print(
                        "Демо: Игрок HP после лечения:",
                        player.health_component.current_health,
                    )

                if event.key == pygame.K_r:
                    print("Демо: Воскрешаем игрока (R)...")
                    player.health_component.resurrect()
                    print(
                        "Демо: Игрок HP после воскрешения:",
                        player.health_component.current_health,
                    )

        # Обновление спрайтов (включая родительский update в Sprite) - пока HealthComponent.update() пустой, можно его не вызывать.
        # Если добавите DoT/HoT, нужно будет добавить вызов health_component.update(dt) сюда.
        # for sprite in all_sprites:
        #    sprite.update(screen) # Вызываем update для всех спрайтов в группе - не нужно, draw сделает blit

        # Отрисовка
        screen.fill((30, 30, 30))  # Темный фон

        # Отрисовываем все спрайты
        all_sprites.update(
            screen
        )  # Этот метод группы сам вызывает blit для каждого спрайта

        if not running:
            pass
