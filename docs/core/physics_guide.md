# Physics (Физика)

Подсистема физики на базе **pymunk**. Управляет движением тел, гравитацией, трением и коллизиями.

## Глобальный мир

Мир создаётся автоматически при инициализации игры. Доступ: `s.physics`

```python
s.physics.set_gravity(980)  # Гравитация по умолчанию 980
```

## Типы тел (BodyType)

| Тип | Описание |
|-----|----------|
| `DYNAMIC` | Полная физика (игрок, мяч) |
| `STATIC` | Неподвижное (стены, пол) |
| `KINEMATIC` | Движение вручную (платформы) |

## Создание тел

```python
player = s.Sprite("player.png", pos=(100, 100), size=(40, 40))
player_body = s.add_physics(player, s.PhysicsConfig(mass=1.0, bounce=0.5, friction=0.95))

floor = s.Sprite("", pos=(400, 570), size=(800, 40))
s.add_static_physics(floor)

platform = s.Sprite("", pos=(300, 400), size=(120, 20))
plat_body = s.add_kinematic_physics(platform)
plat_body.velocity.x = 150
```

## PhysicsConfig

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `mass` | Масса тела | 1.0 |
| `gravity` | Гравитация тела | 980.0 |
| `friction` | Трение | 0.98 |
| `bounce` | Отскок (0-1) | 0.5 |
| `body_type` | Тип тела | DYNAMIC |

## Форма коллайдера (PhysicsShape)

`AUTO` (по умолчанию), `BOX`, `CIRCLE`, `LINE`

```python
s.add_physics(ball, shape=s.PhysicsShape.CIRCLE)
```

## PhysicsBody: методы

| Метод | Описание |
|-------|----------|
| `set_velocity(x, y)` | Установить скорость |
| `set_bounce(v)` | Отскок |
| `set_friction(v)` | Трение |
| `apply_force(force)` | Приложить силу |
| `apply_impulse(impulse)` | Импульс |
| `stop()` | Остановить |

## Коллизии

```python
ball_body.on_collision = lambda other: ball.set_circle_shape(radius=15, color=(255, 100, 255))
```

## Работа с объектами из редактора

```python
body = s.get_physics(sprite)  # Получить тело спрайта
body.velocity.x = 200         # Задать скорость
body.set_bounce(0)            # Без отскока (платформер)
```

## Границы мира

```python
s.physics.set_bounds(pygame.Rect(0, 0, 800, 600))
```

## Демо

```bash
python -m spritePro.demoGames.physics_demo
python -m spritePro.demoGames.hoop_bounce_demo
```

## См. также

- [Sprite](sprite.md)
