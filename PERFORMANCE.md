# Оптимизация производительности SpritePro

Этот документ описывает стратегии и планы по улучшению производительности библиотеки SpritePro.

## 🎯 Цели производительности

### Целевые метрики
- **FPS**: Стабильные 60 FPS для игр с 1000+ спрайтов
- **Память**: Не более 100MB для типичной игры
- **Загрузка**: Время загрузки ресурсов < 3 секунд
- **Отзывчивость**: Задержка ввода < 16ms (1 кадр)

### Платформы
- **Desktop**: Windows, macOS, Linux
- **Mobile**: Android, iOS (через Kivy/BeeWare)
- **Web**: Браузеры с WebGL поддержкой

## 🚀 Текущие оптимизации

### Рендеринг
```python
class OptimizedRenderer:
    """Оптимизированный рендерер для SpritePro"""
    
    def __init__(self):
        self.sprite_batches = {}  # Группировка по текстурам
        self.dirty_regions = []   # Области для перерисовки
        self.culling_enabled = True
        self.vsync_enabled = True
    
    def batch_sprites_by_texture(self, sprites):
        """Группировка спрайтов по текстурам для батчинга"""
        batches = {}
        for sprite in sprites:
            texture_id = id(sprite.image)
            if texture_id not in batches:
                batches[texture_id] = []
            batches[texture_id].append(sprite)
        return batches
    
    def frustum_culling(self, sprites, camera_rect):
        """Отсечение невидимых спрайтов"""
        visible_sprites = []
        for sprite in sprites:
            if sprite.rect.colliderect(camera_rect):
                visible_sprites.append(sprite)
        return visible_sprites
    
    def dirty_rectangle_optimization(self, surface, sprites):
        """Перерисовка только измененных областей"""
        dirty_rects = []
        for sprite in sprites:
            if sprite.dirty:
                dirty_rects.append(sprite.rect)
                sprite.dirty = False
        
        if dirty_rects:
            pygame.display.update(dirty_rects)
        else:
            pygame.display.flip()
```

### Управление памятью
```python
class ResourceManager:
    """Менеджер ресурсов с кэшированием"""
    
    def __init__(self, max_cache_size=100):
        self.texture_cache = {}
        self.sound_cache = {}
        self.max_cache_size = max_cache_size
        self.access_times = {}
    
    def load_texture(self, path):
        """Загрузка текстуры с кэшированием"""
        if path in self.texture_cache:
            self.access_times[path] = time.time()
            return self.texture_cache[path]
        
        # Проверка размера кэша
        if len(self.texture_cache) >= self.max_cache_size:
            self._evict_oldest()
        
        texture = pygame.image.load(path).convert_alpha()
        self.texture_cache[path] = texture
        self.access_times[path] = time.time()
        return texture
    
    def _evict_oldest(self):
        """Удаление самой старой текстуры из кэша"""
        oldest_path = min(self.access_times.keys(), 
                         key=lambda k: self.access_times[k])
        del self.texture_cache[oldest_path]
        del self.access_times[oldest_path]
```

## 📊 Профилирование и мониторинг

### Встроенный профайлер
```python
class PerformanceProfiler:
    """Профайлер производительности"""
    
    def __init__(self):
        self.timers = {}
        self.counters = {}
        self.memory_usage = []
        self.fps_history = []
        self.enabled = False
    
    def start_timer(self, name):
        """Начать измерение времени"""
        if self.enabled:
            self.timers[name] = time.perf_counter()
    
    def end_timer(self, name):
        """Закончить измерение времени"""
        if self.enabled and name in self.timers:
            duration = time.perf_counter() - self.timers[name]
            if f"{name}_times" not in self.counters:
                self.counters[f"{name}_times"] = []
            self.counters[f"{name}_times"].append(duration)
    
    def record_fps(self, fps):
        """Записать FPS"""
        if self.enabled:
            self.fps_history.append(fps)
            if len(self.fps_history) > 1000:
                self.fps_history.pop(0)
    
    def record_memory(self):
        """Записать использование памяти"""
        if self.enabled:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            self.memory_usage.append(memory_mb)
    
    def get_report(self):
        """Получить отчет о производительности"""
        report = {
            'avg_fps': sum(self.fps_history) / len(self.fps_history) if self.fps_history else 0,
            'min_fps': min(self.fps_history) if self.fps_history else 0,
            'max_fps': max(self.fps_history) if self.fps_history else 0,
            'avg_memory_mb': sum(self.memory_usage) / len(self.memory_usage) if self.memory_usage else 0,
            'timers': {}
        }
        
        for name, times in self.counters.items():
            if times:
                report['timers'][name] = {
                    'avg': sum(times) / len(times),
                    'min': min(times),
                    'max': max(times),
                    'count': len(times)
                }
        
        return report
```

### Автоматическое тестирование производительности
```python
class PerformanceTest:
    """Автоматические тесты производительности"""
    
    def __init__(self):
        self.profiler = PerformanceProfiler()
        self.test_results = {}
    
    def test_sprite_rendering(self, sprite_count=1000):
        """Тест рендеринга спрайтов"""
        sprites = []
        for i in range(sprite_count):
            sprite = s.Sprite("test.png", (32, 32), (i % 800, i % 600))
            sprites.append(sprite)
        
        self.profiler.enabled = True
        start_time = time.time()
        
        # Симуляция игрового цикла
        for frame in range(60):  # 1 секунда при 60 FPS
            self.profiler.start_timer("render")
            
            for sprite in sprites:
                sprite.update(1/60)
            
            self.profiler.end_timer("render")
            self.profiler.record_fps(60)
        
        duration = time.time() - start_time
        self.test_results['sprite_rendering'] = {
            'sprite_count': sprite_count,
            'duration': duration,
            'fps': 60 / (duration / 60)
        }
    
    def test_collision_detection(self, object_count=500):
        """Тест обнаружения коллизий"""
        objects = []
        for i in range(object_count):
            obj = s.GameSprite("test.png", (32, 32), 
                              (random.randint(0, 768), random.randint(0, 568)))
            objects.append(obj)
        
        start_time = time.time()
        
        # Тест всех коллизий
        collisions = 0
        for i, obj1 in enumerate(objects):
            for obj2 in objects[i+1:]:
                if obj1.rect.colliderect(obj2.rect):
                    collisions += 1
        
        duration = time.time() - start_time
        self.test_results['collision_detection'] = {
            'object_count': object_count,
            'collisions_found': collisions,
            'duration': duration,
            'checks_per_second': (object_count * (object_count - 1) / 2) / duration
        }
```

## 🔧 Планируемые оптимизации

### Рендеринг

#### Sprite Batching
```python
class SpriteBatcher:
    """Батчинг спрайтов для эффективного рендеринга"""
    
    def __init__(self):
        self.batches = {}
        self.vertex_buffer = []
        self.index_buffer = []
    
    def add_sprite(self, sprite):
        """Добавить спрайт в батч"""
        texture_id = id(sprite.image)
        if texture_id not in self.batches:
            self.batches[texture_id] = {
                'texture': sprite.image,
                'sprites': [],
                'vertices': [],
                'indices': []
            }
        
        batch = self.batches[texture_id]
        batch['sprites'].append(sprite)
        
        # Добавить вершины спрайта
        x, y = sprite.rect.x, sprite.rect.y
        w, h = sprite.rect.width, sprite.rect.height
        
        vertices = [
            (x, y, 0, 0),         # Верхний левый
            (x + w, y, 1, 0),     # Верхний правый
            (x + w, y + h, 1, 1), # Нижний правый
            (x, y + h, 0, 1)      # Нижний левый
        ]
        
        start_index = len(batch['vertices'])
        batch['vertices'].extend(vertices)
        
        # Добавить индексы для двух треугольников
        indices = [
            start_index, start_index + 1, start_index + 2,
            start_index, start_index + 2, start_index + 3
        ]
        batch['indices'].extend(indices)
    
    def render_all(self, surface):
        """Отрендерить все батчи"""
        for batch in self.batches.values():
            if batch['sprites']:
                self._render_batch(surface, batch)
        
        # Очистить батчи
        self.batches.clear()
```

#### Level of Detail (LOD)
```python
class LODManager:
    """Менеджер уровней детализации"""
    
    def __init__(self):
        self.lod_distances = [100, 300, 500]  # Расстояния для LOD
        self.sprite_lods = {}  # Кэш LOD версий спрайтов
    
    def get_lod_sprite(self, sprite, distance):
        """Получить спрайт нужного уровня детализации"""
        lod_level = self._calculate_lod_level(distance)
        
        sprite_id = id(sprite.image)
        if sprite_id not in self.sprite_lods:
            self.sprite_lods[sprite_id] = self._generate_lod_versions(sprite)
        
        return self.sprite_lods[sprite_id][lod_level]
    
    def _calculate_lod_level(self, distance):
        """Вычислить уровень детализации по расстоянию"""
        for i, threshold in enumerate(self.lod_distances):
            if distance < threshold:
                return i
        return len(self.lod_distances)
    
    def _generate_lod_versions(self, sprite):
        """Создать версии спрайта разных уровней детализации"""
        lod_versions = [sprite.image]  # Оригинал
        
        current_image = sprite.image
        for scale in [0.5, 0.25, 0.125]:  # Уменьшение в 2, 4, 8 раз
            size = (int(current_image.get_width() * scale),
                   int(current_image.get_height() * scale))
            if size[0] > 0 and size[1] > 0:
                scaled = pygame.transform.scale(current_image, size)
                lod_versions.append(scaled)
        
        return lod_versions
```

### Физика

#### Spatial Partitioning
```python
class QuadTree:
    """Квадродерево для оптимизации коллизий"""
    
    def __init__(self, bounds, max_objects=10, max_levels=5, level=0):
        self.bounds = bounds  # pygame.Rect
        self.max_objects = max_objects
        self.max_levels = max_levels
        self.level = level
        self.objects = []
        self.nodes = [None, None, None, None]  # 4 квадранта
    
    def clear(self):
        """Очистить дерево"""
        self.objects.clear()
        for i in range(4):
            if self.nodes[i] is not None:
                self.nodes[i].clear()
                self.nodes[i] = None
    
    def split(self):
        """Разделить узел на 4 квадранта"""
        sub_width = self.bounds.width // 2
        sub_height = self.bounds.height // 2
        x, y = self.bounds.x, self.bounds.y
        
        self.nodes[0] = QuadTree(
            pygame.Rect(x + sub_width, y, sub_width, sub_height),
            self.max_objects, self.max_levels, self.level + 1
        )
        self.nodes[1] = QuadTree(
            pygame.Rect(x, y, sub_width, sub_height),
            self.max_objects, self.max_levels, self.level + 1
        )
        self.nodes[2] = QuadTree(
            pygame.Rect(x, y + sub_height, sub_width, sub_height),
            self.max_objects, self.max_levels, self.level + 1
        )
        self.nodes[3] = QuadTree(
            pygame.Rect(x + sub_width, y + sub_height, sub_width, sub_height),
            self.max_objects, self.max_levels, self.level + 1
        )
    
    def get_index(self, rect):
        """Определить квадрант для объекта"""
        index = -1
        vertical_midpoint = self.bounds.x + self.bounds.width // 2
        horizontal_midpoint = self.bounds.y + self.bounds.height // 2
        
        top_quadrant = rect.y < horizontal_midpoint and rect.y + rect.height < horizontal_midpoint
        bottom_quadrant = rect.y > horizontal_midpoint
        
        if rect.x < vertical_midpoint and rect.x + rect.width < vertical_midpoint:
            if top_quadrant:
                index = 1
            elif bottom_quadrant:
                index = 2
        elif rect.x > vertical_midpoint:
            if top_quadrant:
                index = 0
            elif bottom_quadrant:
                index = 3
        
        return index
    
    def insert(self, obj):
        """Вставить объект в дерево"""
        if self.nodes[0] is not None:
            index = self.get_index(obj.rect)
            if index != -1:
                self.nodes[index].insert(obj)
                return
        
        self.objects.append(obj)
        
        if len(self.objects) > self.max_objects and self.level < self.max_levels:
            if self.nodes[0] is None:
                self.split()
            
            i = 0
            while i < len(self.objects):
                index = self.get_index(self.objects[i].rect)
                if index != -1:
                    self.nodes[index].insert(self.objects.pop(i))
                else:
                    i += 1
    
    def retrieve(self, return_objects, rect):
        """Получить объекты, которые могут пересекаться с rect"""
        index = self.get_index(rect)
        if index != -1 and self.nodes[0] is not None:
            self.nodes[index].retrieve(return_objects, rect)
        
        return_objects.extend(self.objects)
        return return_objects
```

### Многопоточность

#### Асинхронная загрузка ресурсов
```python
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

class AsyncResourceLoader:
    """Асинхронный загрузчик ресурсов"""
    
    def __init__(self, max_workers=4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.loading_queue = asyncio.Queue()
        self.loaded_resources = {}
        self.loading_progress = {}
    
    async def load_texture_async(self, path):
        """Асинхронная загрузка текстуры"""
        if path in self.loaded_resources:
            return self.loaded_resources[path]
        
        if path in self.loading_progress:
            # Ждем завершения загрузки
            while path in self.loading_progress:
                await asyncio.sleep(0.01)
            return self.loaded_resources[path]
        
        self.loading_progress[path] = True
        
        loop = asyncio.get_event_loop()
        texture = await loop.run_in_executor(
            self.executor, self._load_texture_sync, path
        )
        
        self.loaded_resources[path] = texture
        del self.loading_progress[path]
        return texture
    
    def _load_texture_sync(self, path):
        """Синхронная загрузка текстуры"""
        return pygame.image.load(path).convert_alpha()
    
    async def preload_resources(self, resource_list):
        """Предварительная загрузка списка ресурсов"""
        tasks = []
        for resource_path in resource_list:
            task = asyncio.create_task(self.load_texture_async(resource_path))
            tasks.append(task)
        
        await asyncio.gather(*tasks)
```

#### Параллельная обработка физики
```python
class ParallelPhysicsProcessor:
    """Параллельная обработка физики"""
    
    def __init__(self, num_threads=None):
        self.num_threads = num_threads or os.cpu_count()
        self.thread_pool = ThreadPoolExecutor(max_workers=self.num_threads)
    
    def update_physics_parallel(self, sprites, dt):
        """Параллельное обновление физики спрайтов"""
        chunk_size = len(sprites) // self.num_threads
        chunks = [sprites[i:i + chunk_size] 
                 for i in range(0, len(sprites), chunk_size)]
        
        futures = []
        for chunk in chunks:
            future = self.thread_pool.submit(self._update_chunk, chunk, dt)
            futures.append(future)
        
        # Ждем завершения всех потоков
        for future in futures:
            future.result()
    
    def _update_chunk(self, sprite_chunk, dt):
        """Обновление физики для части спрайтов"""
        for sprite in sprite_chunk:
            if hasattr(sprite, 'velocity'):
                sprite.rect.x += sprite.velocity[0] * dt
                sprite.rect.y += sprite.velocity[1] * dt
            
            if hasattr(sprite, 'acceleration'):
                sprite.velocity[0] += sprite.acceleration[0] * dt
                sprite.velocity[1] += sprite.acceleration[1] * dt
```

## 📈 Мониторинг производительности

### Метрики в реальном времени
```python
class RealTimeMetrics:
    """Метрики производительности в реальном времени"""
    
    def __init__(self):
        self.fps_counter = 0
        self.frame_times = []
        self.last_fps_update = time.time()
        self.current_fps = 0
        
        self.draw_calls = 0
        self.sprites_rendered = 0
        self.memory_usage = 0
    
    def update(self, dt):
        """Обновить метрики"""
        self.fps_counter += 1
        self.frame_times.append(dt)
        
        current_time = time.time()
        if current_time - self.last_fps_update >= 1.0:
            self.current_fps = self.fps_counter
            self.fps_counter = 0
            self.last_fps_update = current_time
            
            # Обновить использование памяти
            self._update_memory_usage()
        
        # Ограничить историю времени кадров
        if len(self.frame_times) > 60:
            self.frame_times.pop(0)
    
    def get_average_frame_time(self):
        """Получить среднее время кадра"""
        if self.frame_times:
            return sum(self.frame_times) / len(self.frame_times)
        return 0
    
    def get_frame_time_variance(self):
        """Получить дисперсию времени кадров"""
        if len(self.frame_times) < 2:
            return 0
        
        avg = self.get_average_frame_time()
        variance = sum((t - avg) ** 2 for t in self.frame_times) / len(self.frame_times)
        return variance
    
    def _update_memory_usage(self):
        """Обновить информацию об использовании памяти"""
        try:
            import psutil
            process = psutil.Process()
            self.memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            self.memory_usage = 0
```

### Визуализация метрик
```python
class PerformanceOverlay:
    """Оверлей с метриками производительности"""
    
    def __init__(self, font_size=16):
        self.font = pygame.font.Font(None, font_size)
        self.visible = False
        self.metrics = RealTimeMetrics()
        self.graph_history = []
    
    def toggle_visibility(self):
        """Переключить видимость оверлея"""
        self.visible = not self.visible
    
    def update(self, dt):
        """Обновить метрики"""
        self.metrics.update(dt)
        
        # Добавить в историю для графика
        self.graph_history.append(self.metrics.current_fps)
        if len(self.graph_history) > 100:
            self.graph_history.pop(0)
    
    def render(self, surface):
        """Отрендерить оверлей"""
        if not self.visible:
            return
        
        # Фон оверлея
        overlay_rect = pygame.Rect(10, 10, 300, 150)
        pygame.draw.rect(surface, (0, 0, 0, 128), overlay_rect)
        pygame.draw.rect(surface, (255, 255, 255), overlay_rect, 2)
        
        # Текстовые метрики
        y_offset = 20
        metrics_text = [
            f"FPS: {self.metrics.current_fps}",
            f"Frame Time: {self.metrics.get_average_frame_time():.3f}ms",
            f"Frame Variance: {self.metrics.get_frame_time_variance():.6f}",
            f"Memory: {self.metrics.memory_usage:.1f}MB",
            f"Draw Calls: {self.metrics.draw_calls}",
            f"Sprites: {self.metrics.sprites_rendered}"
        ]
        
        for text in metrics_text:
            text_surface = self.font.render(text, True, (255, 255, 255))
            surface.blit(text_surface, (20, y_offset))
            y_offset += 20
        
        # График FPS
        if len(self.graph_history) > 1:
            self._draw_fps_graph(surface, pygame.Rect(320, 10, 200, 100))
    
    def _draw_fps_graph(self, surface, rect):
        """Нарисовать график FPS"""
        if not self.graph_history:
            return
        
        # Фон графика
        pygame.draw.rect(surface, (0, 0, 0, 128), rect)
        pygame.draw.rect(surface, (255, 255, 255), rect, 1)
        
        # Масштабирование данных
        max_fps = max(self.graph_history) if self.graph_history else 60
        min_fps = min(self.graph_history) if self.graph_history else 0
        fps_range = max_fps - min_fps if max_fps != min_fps else 1
        
        # Рисование линии графика
        points = []
        for i, fps in enumerate(self.graph_history):
            x = rect.x + (i / len(self.graph_history)) * rect.width
            y = rect.y + rect.height - ((fps - min_fps) / fps_range) * rect.height
            points.append((x, y))
        
        if len(points) > 1:
            pygame.draw.lines(surface, (0, 255, 0), False, points, 2)
        
        # Линия 60 FPS
        if min_fps <= 60 <= max_fps:
            y_60fps = rect.y + rect.height - ((60 - min_fps) / fps_range) * rect.height
            pygame.draw.line(surface, (255, 255, 0), 
                           (rect.x, y_60fps), (rect.x + rect.width, y_60fps), 1)
```

## 🎯 Бенчмарки и тесты

### Автоматические бенчмарки
```python
class PerformanceBenchmark:
    """Автоматические бенчмарки производительности"""
    
    def __init__(self):
        self.results = {}
    
    def run_all_benchmarks(self):
        """Запустить все бенчмарки"""
        self.results['sprite_creation'] = self.benchmark_sprite_creation()
        self.results['sprite_rendering'] = self.benchmark_sprite_rendering()
        self.results['collision_detection'] = self.benchmark_collision_detection()
        self.results['texture_loading'] = self.benchmark_texture_loading()
        self.results['memory_usage'] = self.benchmark_memory_usage()
        
        return self.results
    
    def benchmark_sprite_creation(self, count=10000):
        """Бенчмарк создания спрайтов"""
        start_time = time.perf_counter()
        
        sprites = []
        for i in range(count):
            sprite = s.Sprite("test.png", (32, 32), (0, 0))
            sprites.append(sprite)
        
        end_time = time.perf_counter()
        duration = end_time - start_time
        
        return {
            'count': count,
            'duration': duration,
            'sprites_per_second': count / duration
        }
    
    def benchmark_sprite_rendering(self, count=1000, frames=60):
        """Бенчмарк рендеринга спрайтов"""
        sprites = []
        for i in range(count):
            sprite = s.Sprite("test.png", (32, 32), 
                            (random.randint(0, 768), random.randint(0, 568)))
            sprites.append(sprite)
        
        surface = pygame.Surface((800, 600))
        start_time = time.perf_counter()
        
        for frame in range(frames):
            surface.fill((0, 0, 0))
            for sprite in sprites:
                sprite.draw(surface)
        
        end_time = time.perf_counter()
        duration = end_time - start_time
        
        return {
            'sprite_count': count,
            'frames': frames,
            'duration': duration,
            'fps': frames / duration,
            'sprites_per_second': (count * frames) / duration
        }
    
    def generate_report(self):
        """Создать отчет о производительности"""
        report = "SpritePro Performance Report\n"
        report += "=" * 40 + "\n\n"
        
        for test_name, results in self.results.items():
            report += f"{test_name.replace('_', ' ').title()}:\n"
            for key, value in results.items():
                if isinstance(value, float):
                    report += f"  {key}: {value:.3f}\n"
                else:
                    report += f"  {key}: {value}\n"
            report += "\n"
        
        return report
```

## 🔧 Инструменты оптимизации

### Автоматический оптимизатор
```python
class AutoOptimizer:
    """Автоматический оптимизатор настроек"""
    
    def __init__(self):
        self.settings = {
            'vsync': True,
            'sprite_batching': True,
            'frustum_culling': True,
            'lod_enabled': False,
            'max_sprites': 1000,
            'texture_cache_size': 100
        }
        self.performance_history = []
    
    def optimize_settings(self, target_fps=60):
        """Автоматическая оптимизация настроек"""
        current_fps = self._measure_current_fps()
        
        if current_fps < target_fps:
            # Производительность низкая, включаем оптимизации
            if not self.settings['sprite_batching']:
                self.settings['sprite_batching'] = True
                print("Включен sprite batching")
            
            if not self.settings['frustum_culling']:
                self.settings['frustum_culling'] = True
                print("Включен frustum culling")
            
            if not self.settings['lod_enabled']:
                self.settings['lod_enabled'] = True
                print("Включен LOD")
            
            if self.settings['max_sprites'] > 500:
                self.settings['max_sprites'] = 500
                print("Уменьшено максимальное количество спрайтов")
        
        elif current_fps > target_fps * 1.5:
            # Производительность высокая, можно улучшить качество
            if self.settings['max_sprites'] < 2000:
                self.settings['max_sprites'] += 100
                print("Увеличено максимальное количество спрайтов")
    
    def _measure_current_fps(self):
        """Измерить текущий FPS"""
        # Заглушка - в реальности измеряем FPS
        return 45  # Пример низкого FPS
```

---

Эти оптимизации помогут SpritePro работать эффективно на различных устройствах и обеспечат плавный геймплей даже в сложных играх с большим количеством объектов. 🚀