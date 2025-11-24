"""Тест для проверки particle_template в ParticleEmitter.
Демонстрирует интерактивные частицы: фонтан (толкает спрайты) и падающие частицы.
"""

import pygame
import sys
import random
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))

import spritePro as s
from spritePro.particles import Particle, ParticleConfig, ParticleEmitter
from pygame.math import Vector2

# Создаем пользовательский класс частицы фонтана (толкает спрайты)
class FountainParticle(Particle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.push_force = 200.0  # Сила толчка
        self.has_pushed = set()  # Множество спрайтов, которые уже были оттолкнуты
        self.has_collided_with_falling = False  # Флаг столкновения с падающей частицей
        self.collision_effect_timer = 0.0  # Таймер для эффекта столкновения
        
    def check_collision_and_push(self, targets):
        """Проверка коллизии с целями и толчок их."""
        for target in targets:
            if target not in self.has_pushed and self.rect.colliderect(target.rect):
                # Вычисляем направление от частицы к цели
                dx = target.rect.centerx - self.rect.centerx
                dy = target.rect.centery - self.rect.centery
                distance = (dx**2 + dy**2)**0.5
                
                if distance > 0:
                    # Нормализуем направление и применяем силу
                    push_dir = Vector2(dx / distance, dy / distance)
                    if hasattr(target, 'velocity'):
                        target.velocity += push_dir * self.push_force * s.dt
                    elif hasattr(target, 'rect'):
                        # Если нет velocity, двигаем напрямую
                        target.rect.x += int(push_dir.x * self.push_force * s.dt)
                        target.rect.y += int(push_dir.y * self.push_force * s.dt)
                    
                    self.has_pushed.add(target)
                    print(f"Fountain particle pushed target! Force: {self.push_force}")
    
    def check_collision_with_falling(self, falling_particle, collision_messages_list, collision_count_ref):
        """Проверка столкновения с падающей частицей."""
        if (not self.has_collided_with_falling and 
            isinstance(falling_particle, FallingParticle) and 
            not falling_particle.has_collided and
            self.rect.colliderect(falling_particle.rect)):
            # Столкновение обнаружено
            self.has_collided_with_falling = True
            falling_particle.has_collided = True
            self.collision_effect_timer = 0.3
            falling_particle.collision_effect_timer = 0.3
            # Визуальный эффект - увеличиваем размер
            self.scale = 2.0
            falling_particle.scale = 2.0
            
            # Увеличиваем счетчик
            collision_count_ref[0] += 1
            
            # Создаем сообщение на экране
            collision_pos = Vector2(
                (self.rect.centerx + falling_particle.rect.centerx) // 2,
                (self.rect.centery + falling_particle.rect.centery) // 2
            )
            collision_messages_list.append([collision_pos, 0.5, "SPLASH!"])  # [pos, timer, text]
            
            print(f"Fountain particle collided with falling particle! Destroying both. Total collisions: {collision_count_ref[0]}")
            return True
        return False
    
    def update(self, screen=None):
        """Обновление с визуальным эффектом столкновения."""
        super().update(screen)
        # Уменьшаем эффект столкновения с падающей частицей
        if self.collision_effect_timer > 0:
            self.collision_effect_timer -= s.dt
            if self.collision_effect_timer <= 0:
                # Уничтожаем частицу после эффекта
                self.kill()

# Создаем пользовательский класс падающей частицы
class FallingParticle(Particle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.damage = 5  # Урон при падении
        self.has_hit_ground = False
        self.impact_effect_timer = 0.0  # Таймер для визуального эффекта
        self.collision_effect_timer = 0.0  # Таймер для эффекта столкновения с другой частицей
        self.has_collided = False  # Флаг столкновения с другой частицей
        
    def check_ground_collision(self, ground_y):
        """Проверка столкновения с землей."""
        if not self.has_hit_ground and self.rect.bottom >= ground_y:
            self.has_hit_ground = True
            self.impact_effect_timer = 0.3  # Эффект на 0.3 секунды
            # Визуальный эффект - увеличиваем размер при столкновении
            self.scale = 1.5
            print(f"Falling particle hit ground at y={ground_y}")
    
    def check_particle_collision(self, other_particle, collision_messages_list, collision_count_ref):
        """Проверка столкновения с другой частицей."""
        if (not self.has_collided and 
            isinstance(other_particle, FallingParticle) and 
            not other_particle.has_collided and
            self.rect.colliderect(other_particle.rect) and
            self != other_particle):
            # Столкновение обнаружено
            self.has_collided = True
            other_particle.has_collided = True
            self.collision_effect_timer = 0.3  # Эффект на 0.3 секунды
            other_particle.collision_effect_timer = 0.3
            # Визуальный эффект - увеличиваем размер
            self.scale = 2.0
            other_particle.scale = 2.0
            
            # Увеличиваем счетчик
            collision_count_ref[0] += 1
            
            # Создаем сообщение на экране
            collision_pos = Vector2(
                (self.rect.centerx + other_particle.rect.centerx) // 2,
                (self.rect.centery + other_particle.rect.centery) // 2
            )
            collision_messages_list.append([collision_pos, 0.5, "BOOM!"])  # [pos, timer, text]
            
            print(f"Falling particles collided! Destroying both. Total collisions: {collision_count_ref[0]}")
            return True
        return False
    
    def update(self, screen=None):
        """Обновление с визуальным эффектом столкновения."""
        super().update(screen)
        # Уменьшаем эффект столкновения с землей со временем
        if self.impact_effect_timer > 0:
            self.impact_effect_timer -= s.dt
            if self.impact_effect_timer <= 0:
                self.scale = 1.0
        # Уменьшаем эффект столкновения с частицей
        if self.collision_effect_timer > 0:
            self.collision_effect_timer -= s.dt
            if self.collision_effect_timer <= 0:
                # Уничтожаем частицу после эффекта
                self.kill()

# Инициализация
s.init()
screen = s.get_screen((800, 600), "Particle Template Test - Fountain & Falling")

# Создаем шаблон частицы фонтана (увеличиваем размер)
fountain_image = pygame.Surface((25, 25), pygame.SRCALPHA)
pygame.draw.circle(fountain_image, (100, 200, 255), (12, 12), 12)
pygame.draw.circle(fountain_image, (200, 230, 255), (12, 12), 8)

fountain_template = FountainParticle(
    image=fountain_image,
    pos=(0, 0),
    velocity=Vector2(0, 0),
    lifetime_ms=1500,  # Увеличиваем время жизни
    fade_speed=100.0,  # Уменьшаем скорость затухания
    gravity=Vector2(0, -100),  # Отрицательная гравитация для фонтана (вверх)
    screen_space=False,
)
fountain_template.set_color((100, 200, 255))

# Создаем шаблон падающей частицы (увеличиваем размер и убираем затухание)
falling_image = pygame.Surface((20, 20), pygame.SRCALPHA)  # Увеличиваем размер
pygame.draw.circle(falling_image, (255, 150, 50), (10, 10), 10)  # Более яркий цвет
pygame.draw.circle(falling_image, (255, 200, 100), (10, 10), 6)
pygame.draw.circle(falling_image, (255, 255, 200), (10, 10), 3)  # Яркое ядро

falling_template = FallingParticle(
    image=falling_image,
    pos=(0, 0),
    velocity=Vector2(0, 0),
    lifetime_ms=5000,  # Увеличиваем время жизни
    fade_speed=0.0,  # Отключаем затухание - частицы остаются видимыми
    gravity=Vector2(0, 300),  # Гравитация вниз
    screen_space=False,
)
falling_template.set_color((255, 200, 100))
falling_template.alpha = 255  # Полная непрозрачность

# Создаем конфигурацию фонтана (увеличиваем количество и время жизни)
fountain_config = ParticleConfig(
    amount=40,  # Увеличиваем количество частиц
    particle_template=fountain_template,
    speed_range=(200.0, 350.0),  # Увеличиваем скорость
    angle_range=(260.0, 280.0),  # Вверх (в pygame 270 градусов = вверх)
    lifetime_range=(1.0, 1.8),  # Увеличиваем время жизни
    fade_speed=100.0,  # Уменьшаем скорость затухания
    gravity=Vector2(0, -100),  # Отрицательная гравитация для фонтана (вверх)
)

# Создаем конфигурацию падающих частиц (без затухания)
falling_config = ParticleConfig(
    amount=15,  # Еще больше частиц для лучшей видимости столкновений
    particle_template=falling_template,
    speed_range=(0.0, 80.0),  # Немного увеличиваем начальную скорость для разнообразия
    angle_range=(85.0, 95.0),  # Почти прямо вниз
    lifetime_range=(4.0, 5.5),  # Увеличиваем время жизни
    fade_speed=0.0,  # Отключаем затухание
    gravity=Vector2(0, 300),  # Гравитация вниз
    spawn_rect=pygame.Rect(0, 0, s.WH.x, 0),  # Спавн по всей ширине сверху
)

# Создаем эмиттеры
fountain_emitter = ParticleEmitter(fountain_config)
fountain_emitter.set_position((400, 550))  # Внизу экрана

falling_emitter = ParticleEmitter(falling_config)
falling_emitter.set_position((0, 0))  # Сверху

# Создаем тестовые цели для фонтана
targets = []
for i in range(3):
    target = s.Sprite("", size=(60, 60), pos=(200 + i * 200, 400))
    target.set_color((255, 100, 100))
    target.velocity = Vector2(0, 0)
    targets.append(target)

# Счетчики для периодического выпуска частиц
fountain_timer = 0
fountain_interval = 0.05  # секунды (чаще выпускаем)
falling_timer = 0
falling_interval = 0.15  # секунды (чаще выпускаем для большего количества частиц)

ground_y = s.WH.y - 20  # Уровень земли

# Счетчик столкновений
collision_count = 0

# Список сообщений о столкновениях (позиция, время жизни)
collision_messages = []  # [(pos, timer, text_surface)]

# Инструкции
instructions = s.TextSprite(
    "Fountain (bottom) pushes sprites | Falling particles collide and destroy each other",
    24,
    (255, 255, 255),
    (s.WH_C.x, 30),
    anchor=s.Anchor.MID_TOP
)

# Счетчик столкновений на экране
collision_counter_text = s.TextSprite(
    "Collisions: 0",
    20,
    (255, 200, 100),
    (10, 60),
    anchor=s.Anchor.TOP_LEFT
)

while True:
    s.update(fill_color=(20, 20, 30))
    
    # Обновляем таймеры
    fountain_timer += s.dt
    falling_timer += s.dt
    
    # Выпускаем фонтан
    if fountain_timer >= fountain_interval:
        fountain_timer = 0
        fountain_particles = fountain_emitter.emit()
        
        # Проверяем коллизии с целями
        for particle in fountain_particles:
            if isinstance(particle, FountainParticle):
                particle.check_collision_and_push(targets)
    
    # Выпускаем падающие частицы
    if falling_timer >= falling_interval:
        falling_timer = 0
        # Спавним в случайной позиции сверху
        spawn_x = Vector2(random.randint(50, int(s.WH.x - 50)), 0)
        falling_particles = falling_emitter.emit(spawn_x)
        
        # Устанавливаем полную непрозрачность для новых частиц
        for particle in falling_particles:
            if isinstance(particle, FallingParticle):
                particle.alpha = 255  # Полная непрозрачность
                particle.check_ground_collision(ground_y)
    
    # Получаем все активные падающие частицы
    falling_particles_list = s.get_sprites_by_class(FallingParticle)
    
    # Проверяем столкновение с землей для всех существующих падающих частиц
    for particle in falling_particles_list:
        particle.check_ground_collision(ground_y)
    
    # Получаем все активные частицы фонтана
    fountain_particles_list = s.get_sprites_by_class(FountainParticle)
    
    # Проверяем столкновения между падающими частицами
    collision_count_ref = [collision_count]  # Используем список для передачи по ссылке
    for i, particle1 in enumerate(falling_particles_list):
        if particle1.has_collided:  # Пропускаем уже столкнувшиеся
            continue
        for particle2 in falling_particles_list[i + 1:]:
            if particle2.has_collided:  # Пропускаем уже столкнувшиеся
                continue
            if particle1.check_particle_collision(particle2, collision_messages, collision_count_ref):
                break  # Эта частица уже столкнулась, переходим к следующей
    
    # Проверяем столкновения между частицами фонтана и падающими частицами
    for fountain_particle in fountain_particles_list:
        if fountain_particle.has_collided_with_falling:  # Пропускаем уже столкнувшиеся
            continue
        for falling_particle in falling_particles_list:
            if falling_particle.has_collided:  # Пропускаем уже столкнувшиеся
                continue
            if fountain_particle.check_collision_with_falling(falling_particle, collision_messages, collision_count_ref):
                break  # Эта частица фонтана уже столкнулась, переходим к следующей
    
    collision_count = collision_count_ref[0]  # Обновляем счетчик
    
    # Применяем гравитацию к целям (чтобы они падали обратно)
    for target in targets:
        if hasattr(target, 'velocity'):
            target.velocity.y += 500 * s.dt  # Гравитация
            target.velocity *= 0.95  # Трение
            target.rect.centerx += int(target.velocity.x * s.dt)
            target.rect.centery += int(target.velocity.y * s.dt)
            
            # Ограничиваем движение в пределах экрана
            target.rect.x = max(0, min(int(s.WH.x - target.rect.width), target.rect.x))
            target.rect.y = max(0, min(int(s.WH.y - target.rect.height), target.rect.y))
    
    # Обновляем счетчик столкновений
    collision_counter_text.set_text(f"Collisions: {collision_count}")
    
    # Обновляем и рисуем сообщения о столкновениях
    messages_to_remove = []
    font = pygame.font.Font(None, 40)
    for i, msg_data in enumerate(collision_messages):
        msg_pos, msg_timer, msg_text = msg_data
        msg_timer -= s.dt
        collision_messages[i][1] = msg_timer  # Обновляем таймер в списке
        if msg_timer <= 0:
            messages_to_remove.append(i)
        else:
            # Вычисляем прозрачность и цвет
            alpha_ratio = msg_timer / 0.5
            # Яркость цвета уменьшается со временем
            color_intensity = int(255 * alpha_ratio)
            color = (255, min(100 + color_intensity, 255), min(100 + color_intensity, 255))
            # Создаем текст с текущим цветом
            text_surface = font.render(msg_text, True, color)
            # Смещаем вверх со временем
            offset_y = int((0.5 - msg_timer) * 50)
            # Рисуем с тенью для лучшей видимости
            shadow_surface = font.render(msg_text, True, (0, 0, 0))
            s.screen.blit(shadow_surface, (int(msg_pos.x - shadow_surface.get_width() // 2) + 2, 
                                          int(msg_pos.y - offset_y - shadow_surface.get_height() // 2) + 2))
            s.screen.blit(text_surface, (int(msg_pos.x - text_surface.get_width() // 2), 
                                        int(msg_pos.y - offset_y - text_surface.get_height() // 2)))
    
    # Удаляем истекшие сообщения
    for i in reversed(messages_to_remove):
        collision_messages.pop(i)
    
    # Рисуем линию земли (более заметную)
    pygame.draw.line(s.screen, (150, 150, 150), (0, ground_y), (s.WH.x, ground_y), 3)
    
    # Рисуем визуальные эффекты столкновений
    for particle in s.get_game().all_sprites:
        if isinstance(particle, FallingParticle) and particle.active:
            # Эффект столкновения с землей
            if particle.impact_effect_timer > 0:
                # Рисуем желтый круг при столкновении с землей
                effect_radius = int(30 * (particle.impact_effect_timer / 0.3))
                effect_alpha = int(200 * (particle.impact_effect_timer / 0.3))
                effect_surface = pygame.Surface((effect_radius * 2, effect_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(effect_surface, (255, 255, 0, effect_alpha), (effect_radius, effect_radius), effect_radius)
                s.screen.blit(effect_surface, (particle.rect.centerx - effect_radius, particle.rect.centery - effect_radius))
            
            # Эффект столкновения с другой частицей
            if particle.collision_effect_timer > 0:
                # Рисуем яркий красный/белый круг при столкновении частиц
                effect_radius = int(60 * (particle.collision_effect_timer / 0.3))
                effect_alpha = int(255 * (particle.collision_effect_timer / 0.3))
                effect_surface = pygame.Surface((effect_radius * 2, effect_radius * 2), pygame.SRCALPHA)
                # Внешний красный круг
                pygame.draw.circle(effect_surface, (255, 50, 50, effect_alpha), (effect_radius, effect_radius), effect_radius)
                # Средний оранжевый круг
                pygame.draw.circle(effect_surface, (255, 150, 50, effect_alpha), (effect_radius, effect_radius), int(effect_radius * 0.7))
                # Внутренний белый круг
                pygame.draw.circle(effect_surface, (255, 255, 255, effect_alpha), (effect_radius, effect_radius), effect_radius // 2)
                s.screen.blit(effect_surface, (particle.rect.centerx - effect_radius, particle.rect.centery - effect_radius))
        
        elif isinstance(particle, FountainParticle) and particle.active:
            # Эффект столкновения фонтана с падающей частицей
            if particle.collision_effect_timer > 0:
                # Рисуем синий/голубой круг при столкновении
                effect_radius = int(60 * (particle.collision_effect_timer / 0.3))
                effect_alpha = int(255 * (particle.collision_effect_timer / 0.3))
                effect_surface = pygame.Surface((effect_radius * 2, effect_radius * 2), pygame.SRCALPHA)
                # Внешний синий круг
                pygame.draw.circle(effect_surface, (50, 150, 255, effect_alpha), (effect_radius, effect_radius), effect_radius)
                # Средний голубой круг
                pygame.draw.circle(effect_surface, (100, 200, 255, effect_alpha), (effect_radius, effect_radius), int(effect_radius * 0.7))
                # Внутренний белый круг
                pygame.draw.circle(effect_surface, (255, 255, 255, effect_alpha), (effect_radius, effect_radius), effect_radius // 2)
                s.screen.blit(effect_surface, (particle.rect.centerx - effect_radius, particle.rect.centery - effect_radius))
    
    # Проверяем события
    for event in s.events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_SPACE:
                # Ручной запуск фонтана
                fountain_emitter.emit((400, 550))
