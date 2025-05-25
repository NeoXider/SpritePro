from typing import Callable, List, Optional
import pygame
import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

import spritePro
from spritePro.sprite import Sprite

# Импортируем наш компонент здоровья
from spritePro.components.health import HealthComponent, DamageCallback, DeathCallback


class GameSprite(Sprite):
    """A game sprite with health management and collision handling.

    This class extends the base Sprite with:
    - Health system with damage and death handling
    - Collision detection and resolution
    - Event callbacks for collisions and death
    - State management for hit/death conditions

    Attributes:
        collision_step (int): Step size for collision resolution. Defaults to 1.
        health_component (HealthComponent): Manages health-related functionality.
        on_collision (Optional[Callable]): Callback for collision events.
    """

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
        """Initializes a game sprite with health management.

        Args:
            sprite (str): Path to sprite image or resource name.
            size (tuple, optional): Sprite dimensions (width, height). Defaults to (50, 50).
            pos (tuple, optional): Initial position (x, y). Defaults to (0, 0).
            speed (float, optional): Movement speed. Defaults to 0.
            max_health (int, optional): Maximum health value. Defaults to 100.
            current_health (Optional[int], optional): Initial health value. If None, equals max_health.
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
        """Internal callback for handling damage events.

        Sets sprite state to 'hit' when damage is taken.

        Args:
            amount (float): Amount of damage taken.
        """
        print(
            f"{self.name if hasattr(self, 'name') else type(self).__name__} получил урон. Устанавливаем состояние 'hit'."
        )
        self.state = "hit"  # Устанавливаем состояние "hit"

    def _handle_death_event(self, dead_sprite: "Sprite"):
        """Internal callback for handling death events.

        Sets sprite state to 'dead' and calls user death callback if set.

        Args:
            dead_sprite (Sprite): The sprite that died.
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
        """Sets callback function for collision events.

        Args:
            callback (Callable): Function to call on collision.
        """
        self.on_collision = callback  # TODO: Возможно, стоит интегрировать коллизии и урон через компоненты

    def on_death_event(self, callback: Callable[["GameSprite"], None]):
        """Sets callback function for death events.

        This callback is called after HealthComponent processes the death event.

        Args:
            callback (Callable[[GameSprite], None]): Function to call on death.
        """
        # Сохраняем пользовательский колбэк
        if callable(callback):
            self._user_on_death_callback = callback
        else:
            print("Предупреждение: Попытка установить некорректный колбэк смерти.")

    # --- Остальные методы GameSprite (collide_with, collide_with_group, etc.) без изменений ---
    # Они не зависят напрямую от внутренней реализации здоровья, только от наличия спрайта.

    def collide_with(self, other_sprite) -> bool:
        """Checks collision with another sprite using pixel-perfect masks.

        Args:
            other_sprite (GameSprite): Other sprite to check collision with.

        Returns:
            bool: True if collision detected, False otherwise.
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
        """Checks collision with a group of sprites using pixel-perfect masks.

        Args:
            group (pygame.sprite.Group): Group of sprites to check collision with.

        Returns:
            List: List of sprites that collide with this sprite.
        """
        return pygame.sprite.spritecollide(
            self, group, False, pygame.sprite.collide_mask
        )

    def collide_with_tag(self, group: pygame.sprite.Group, tag: str) -> List:
        """Checks collision with sprites in a group that have a specific tag.

        Args:
            group (pygame.sprite.Group): Group of sprites to check.
            tag (str): Tag to filter sprites by.

        Returns:
            List: List of tagged sprites that collide with this sprite.
        """
        return [
            sprite
            for sprite in group
            if sprite.tag == tag and self.collide_with(sprite)
        ]

    def _get_collision_side(self, prev_x, prev_y, rect):
        """Determines which side of a rectangle the collision occurred on.

        Args:
            prev_x (float): Previous X position.
            prev_y (float): Previous Y position.
            rect (pygame.Rect): Rectangle to check collision side against.

        Returns:
            str: Collision side ('top', 'bottom', 'left', 'right', or 'inside').
        """
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
        """Resolves collisions with obstacles and stops movement.

        Args:
            *obstacles: Variable number of sprites, rects, groups, or lists to check against.

        Returns:
            List[Tuple[pygame.Rect, str]]: List of (rect, side) tuples for collisions.
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
        print("==================================\nДля воскрешения нажмите R.\n")
        global running
        running = False

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

        screen.fill((30, 30, 30))  # Темный фон

        # Отрисовываем все спрайты
        all_sprites.update(
            screen
        )  # Этот метод группы сам вызывает blit для каждого спрайта

        if not running:
            pass
