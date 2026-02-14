"""
Главный модуль редактора спрайтов
"""

import os
import sys
import math
import copy
import pygame
from pygame.math import Vector2
from typing import Optional, List, Tuple, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum, auto

# Файловый диалог через pygame
try:
    import tkinter as tk
    from tkinter import filedialog
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    filedialog = None

# Поддержка запуска напрямую и как модуля
try:
    from .scene import Scene, SceneObject, Transform, Camera
except ImportError:
    from scene import Scene, SceneObject, Transform, Camera


class ToolType(Enum):
    SELECT = auto()
    MOVE = auto()
    ROTATE = auto()
    SCALE = auto()


@dataclass
class EditorState:
    """Состояние для Undo/Redo"""
    objects: List[Dict]
    camera: Dict


class SpriteEditor:
    """Главный класс редактора спрайтов"""

    def __init__(self, size: Tuple[int, int] = (1280, 720)):
        pygame.init()
        self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)
        pygame.display.set_caption("Sprite Editor")
        
        self.width, self.height = size
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Цвета
        self.colors = {
            "background": (30, 30, 35),
            "grid": (50, 50, 55),
            "grid_major": (60, 60, 65),
            "selection": (0, 150, 255),
            "gizmo_move": (255, 100, 100),
            "gizmo_rotate": (100, 255, 100),
            "gizmo_scale": (100, 100, 255),
            "ui_bg": (40, 40, 45),
            "ui_border": (60, 60, 65),
            "ui_text": (200, 200, 200),
            "ui_accent": (0, 150, 255),
        }
        
        # Сцена
        self.scene = Scene(name="New Scene")
        self.scene.grid_size = 10
        self.filepath: Optional[str] = None
        self.modified = False
        
        # Папка с ассетами -_relative to project root
        editor_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(editor_dir))
        self.assets_folder = os.path.join(project_root, "assets")
        if not os.path.exists(self.assets_folder):
            self.assets_folder = os.path.join(editor_dir, "assets")
        if not os.path.exists(self.assets_folder):
            self.assets_folder = "assets"
        
        # Камера
        self.camera = Vector2(0, 0)
        self.zoom = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        
        # Инструменты
        self.current_tool = ToolType.SELECT
        self.selected_objects: List[SceneObject] = []
        
        # UI панели
        self.ui_left_width = 200
        self.ui_right_width = 280
        self.ui_top_height = 40
        self.ui_bottom_height = 30
        
        # Состояние мыши
        self.mouse_pos = Vector2(0, 0)
        self.mouse_world_pos = Vector2(0, 0)
        self.mouse_pressed = False
        self.mouse_dragging = False
        self.drag_start = Vector2(0, 0)
        self.camera_drag_start = Vector2(0, 0)
        
        # Undo/Redo стек
        self.undo_stack: List[EditorState] = []
        self.redo_stack: List[EditorState] = []
        self.max_undo = 50
        
        # Кэш загруженных изображений
        self.image_cache: Dict[str, pygame.Surface] = {}
        
        # Шрифты
        self.font = pygame.font.Font(None, 18)
        self.font_bold = pygame.font.Font(None, 20)
        
        # Кнопки тулбара (для кликов)
        self._toolbar_buttons: Dict[str, pygame.Rect] = {}
        
        # Запуск
        self._save_state()

    def _get_viewport_rect(self) -> pygame.Rect:
        """Возвращает прямоугольник viewport"""
        return pygame.Rect(
            self.ui_left_width,
            self.ui_top_height,
            self.width - self.ui_left_width - self.ui_right_width,
            self.height - self.ui_top_height - self.ui_bottom_height
        )

    def screen_to_world(self, screen_pos: Vector2) -> Vector2:
        """Преобразует экранные координаты в мировые"""
        viewport = self._get_viewport_rect()
        center = Vector2(viewport.center)
        offset = screen_pos - center
        return self.camera + offset / self.zoom

    def world_to_screen(self, world_pos: Vector2) -> Vector2:
        """Преобразует мировые координаты в экранные"""
        viewport = self._get_viewport_rect()
        center = Vector2(viewport.center)
        return (world_pos - self.camera) * self.zoom + center

    def _save_state(self) -> None:
        """Сохраняет состояние для Undo"""
        state = EditorState(
            objects=[obj.to_dict() for obj in self.scene.objects],
            camera=self.scene.camera.to_dict()
        )
        self.undo_stack.append(state)
        if len(self.undo_stack) > self.max_undo:
            self.undo_stack.pop(0)
        self.redo_stack.clear()
        self.modified = True

    def undo(self) -> None:
        """Отменяет последнее действие"""
        if len(self.undo_stack) <= 1:
            return
        current = self.undo_stack.pop()
        self.redo_stack.append(current)
        prev = self.undo_stack[-1]
        self._restore_state(prev)

    def redo(self) -> None:
        """Повторяет отменённое действие"""
        if not self.redo_stack:
            return
        next_state = self.redo_stack.pop()
        self.undo_stack.append(next_state)
        self._restore_state(next_state)

    def _restore_state(self, state: EditorState) -> None:
        """Восстанавливает состояние из сохранённого"""
        self.scene.objects = [SceneObject.from_dict(obj) for obj in state.objects]
        self.scene.camera = Camera.from_dict(state.camera)
        self.camera.x = self.scene.camera.x
        self.camera.y = self.scene.camera.y
        self.zoom = self.scene.camera.zoom
        self.selected_objects.clear()

    def add_sprite(self, sprite_path: str, world_pos: Optional[Vector2] = None) -> SceneObject:
        """Добавляет новый спрайт на сцену"""
        # Сохраняем полный путь для удобства
        full_path = os.path.abspath(sprite_path) if os.path.exists(sprite_path) else sprite_path
        
        obj = SceneObject(
            name=os.path.splitext(os.path.basename(sprite_path))[0],
            sprite_path=full_path
        )
        
        if world_pos is not None:
            obj.transform.x = world_pos.x
            obj.transform.y = world_pos.y
        
        # Автоматический z_index
        if self.scene.objects:
            obj.z_index = max(o.z_index for o in self.scene.objects) + 1
        
        self.scene.add_object(obj)
        self._save_state()
        return obj

    def delete_selected(self) -> None:
        """Удаляет выделенные объекты"""
        if not self.selected_objects:
            return
        for obj in self.selected_objects[:]:
            self.scene.remove_object(obj.id)
        self.selected_objects.clear()
        self._save_state()

    def copy_selected(self) -> List[SceneObject]:
        """Копирует выделенные объекты"""
        if not self.selected_objects:
            return []
        new_objects = []
        for obj in self.selected_objects:
            new_obj = obj.copy()
            new_obj.transform.x += 50
            new_obj.transform.y += 50
            self.scene.add_object(new_obj)
            new_objects.append(new_obj)
        self.selected_objects = new_objects
        self._save_state()
        return new_objects

    def select_object(self, obj: Optional[SceneObject], add_to_selection: bool = False) -> None:
        """Выделяет объект"""
        if not add_to_selection:
            self.selected_objects.clear()
        if obj and obj not in self.selected_objects:
            self.selected_objects.append(obj)

    def deselect_all(self) -> None:
        """Снимает выделение со всех объектов"""
        self.selected_objects.clear()

    def get_object_at(self, world_pos: Vector2) -> Optional[SceneObject]:
        """Получает объект по мировым координатам (проверка сверху вниз)"""
        for obj in reversed(self.scene.objects):
            if not obj.visible:
                continue
            sprite = self._get_sprite_image(obj)
            if sprite:
                w, h = sprite.get_size()
                w *= obj.transform.scale_x
                h *= obj.transform.scale_y
                x = obj.transform.x - w / 2
                y = obj.transform.y - h / 2
                if x <= world_pos.x <= x + w and y <= world_pos.y <= y + h:
                    return obj
        return None

    def _get_sprite_image(self, obj: SceneObject) -> Optional[pygame.Surface]:
        """Получает изображение спрайта (из кэша или загружает)"""
        if not obj.sprite_path:
            return None
        
        # Проверяем кэш
        if obj.sprite_path in self.image_cache:
            return self.image_cache[obj.sprite_path]
        
        # Базовые директории для поиска
        editor_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(editor_dir))
        
        # Пробуем разные варианты пути
        search_paths = [
            obj.sprite_path,
            os.path.abspath(obj.sprite_path),
            os.path.join(self.assets_folder, obj.sprite_path),
            os.path.join(self.assets_folder, "images", obj.sprite_path),
            os.path.join(editor_dir, "assets", obj.sprite_path),
            os.path.join(editor_dir, "assets", "images", obj.sprite_path),
            os.path.join(project_root, "assets", obj.sprite_path),
            os.path.join(project_root, "assets", "images", obj.sprite_path),
            os.path.join("assets", obj.sprite_path),
            os.path.join("assets", "images", obj.sprite_path),
        ]
        
        for path in search_paths:
            try:
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    self.image_cache[obj.sprite_path] = img
                    return img
            except Exception:
                continue
        
        return None

    def _snap_to_grid(self, value: float) -> float:
        """Привязка к сетке"""
        if self.scene.snap_to_grid:
            return round(value / self.scene.grid_size) * self.scene.grid_size
        return value

    def handle_events(self) -> None:
        """Обрабатывает события"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.VIDEORESIZE:
                self.width, self.height = event.w, event.h
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
            
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mousedown(event)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self._handle_mouseup(event)
            
            elif event.type == pygame.MOUSEWHEEL:
                self._handle_mousewheel(event)
            
            elif event.type == pygame.DROPFILE:
                self._handle_dropfile(event)

    def _handle_keydown(self, event: pygame.event.Event) -> None:
        """Обработка нажатий клавиш"""
        keys = pygame.key.get_pressed()
        
        # Инструменты
        if event.key == pygame.K_v:
            self.current_tool = ToolType.SELECT
        elif event.key == pygame.K_g:
            self.current_tool = ToolType.MOVE
        elif event.key == pygame.K_r:
            self.current_tool = ToolType.ROTATE
        elif event.key == pygame.K_t:
            self.current_tool = ToolType.SCALE
        
        # Ctrl
        elif keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            if event.key == pygame.K_z:
                self.undo()
            elif event.key == pygame.K_y:
                self.redo()
            elif event.key == pygame.K_c:
                self.copy_selected()
            elif event.key == pygame.K_v:
                self.copy_selected()
            elif event.key == pygame.K_s:
                self._save_scene()
        
        # Delete
        elif event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
            self.delete_selected()
        
        # Escape - deselect
        elif event.key == pygame.K_ESCAPE:
            self.deselect_all()

    def _handle_mousedown(self, event: pygame.event.Event) -> None:
        """Обработка нажатия кнопки мыши"""
        self.mouse_pos = Vector2(event.pos)
        self.mouse_world_pos = self.screen_to_world(self.mouse_pos)
        
        if event.button == 1:  # Левая кнопка
            self.mouse_pressed = True
            
            # Проверяем клик по toolbar (выбор инструментов)
            if self.mouse_pos.y <= self.ui_top_height:
                self._handle_toolbar_click(self.mouse_pos)
                return
            
            # Проверяем клик по hierarchy (левая панель)
            if self.mouse_pos.x <= self.ui_left_width:
                obj = self._handle_hierarchy_click(self.mouse_pos)
                if obj:
                    keys = pygame.key.get_pressed()
                    self.select_object(obj, add_to_selection=keys[pygame.K_LSHIFT])
                    return
            
            # Проверяем клик по объекту в viewport
            viewport = self._get_viewport_rect()
            if viewport.collidepoint(self.mouse_pos):
                obj = self.get_object_at(self.mouse_world_pos)
                if obj:
                    keys = pygame.key.get_pressed()
                    self.select_object(obj, add_to_selection=keys[pygame.K_LSHIFT])
                else:
                    # Клик по пустому пространству
                    if self.current_tool == ToolType.SELECT:
                        self.deselect_all()
                
                # Сохраняем позиции для перетаскивания
                self.drag_start = self.mouse_world_pos.copy()
                self.camera_drag_start = Vector2(event.pos)  # Для pan
                self.mouse_dragging = True
        
        elif event.button == 2:  # Средняя кнопка - панорамирование
            self.mouse_pressed = True
            self.camera_drag_start = Vector2(event.pos)
        
        elif event.button == 3:  # ПКМ - панорамирование
            self.mouse_pressed = True
            self.camera_drag_start = Vector2(event.pos)

    def _handle_toolbar_click(self, pos: Vector2) -> None:
        """Обработка клика по тулбару"""
        # Проверяем кнопки Save, New, Grid
        if hasattr(self, '_toolbar_buttons'):
            if self._toolbar_buttons.get("load", pygame.Rect(0,0,0,0)).collidepoint(pos.x, pos.y):
                self._load_scene()
                return
            elif self._toolbar_buttons.get("save", pygame.Rect(0,0,0,0)).collidepoint(pos.x, pos.y):
                self._save_scene()
                return
            elif self._toolbar_buttons.get("new", pygame.Rect(0,0,0,0)).collidepoint(pos.x, pos.y):
                self._new_scene()
                return
            elif self._toolbar_buttons.get("add", pygame.Rect(0,0,0,0)).collidepoint(pos.x, pos.y):
                self._add_sprite_dialog()
                return
            elif self._toolbar_buttons.get("grid", pygame.Rect(0,0,0,0)).collidepoint(pos.x, pos.y):
                self.scene.grid_visible = not self.scene.grid_visible
                return
        
        # Проверяем выбор инструментов
        tools = [
            (ToolType.SELECT, "V", "Select"),
            (ToolType.MOVE, "G", "Move"),
            (ToolType.ROTATE, "R", "Rotate"),
            (ToolType.SCALE, "T", "Scale"),
        ]
        
        x = 10
        for tool_type, key, name in tools:
            text = self.font_bold.render(f"{name} ({key})", True, self.colors["ui_text"])
            btn_width = text.get_width() + 20
            btn_rect = pygame.Rect(x, 5, btn_width, self.ui_top_height - 10)
            
            if btn_rect.collidepoint(pos.x, pos.y):
                self.current_tool = tool_type
                return
            
            x += btn_width + 20

    def _new_scene(self) -> None:
        """Создать новую сцену"""
        self.scene = Scene(name="New Scene")
        self.selected_objects.clear()
        self.image_cache.clear()
        self._save_state()

    def _add_sprite_dialog(self) -> None:
        """Открыть диалог выбора файла для добавления спрайта"""
        if not TKINTER_AVAILABLE:
            self.add_sprite("placeholder", Vector2(400, 300))
            return
        
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            
            filepath = filedialog.askopenfilename(
                title="Выберите изображение",
                filetypes=[
                    ("Images", "*.png *.jpg *.jpeg *.bmp *.gif"),
                    ("All files", "*.*")
                ],
                initialdir=self.assets_folder
            )
            
            root.destroy()
            
            if filepath:
                self.add_sprite(filepath, Vector2(400, 300))
        except Exception:
            self.add_sprite("placeholder", Vector2(400, 300))

    def _handle_hierarchy_click(self, pos: Vector2) -> Optional[SceneObject]:
        """Обработка клика по иерархии"""
        y = self.ui_top_height + 35
        for obj in self.scene.objects:
            if y > self.height - self.ui_bottom_height - 20:
                break
            
            item_rect = pygame.Rect(10, y, self.ui_left_width - 20, 22)
            if item_rect.collidepoint(pos.x, pos.y):
                return obj
            
            y += 22
        return None

    def _handle_mouseup(self, event: pygame.event.Event) -> None:
        """Обработка отжатия кнопки мыши"""
        if event.button == 1 and self.mouse_dragging:
            self._save_state()
        
        self.mouse_pressed = False
        self.mouse_dragging = False

    def _handle_mousewheel(self, event: pygame.event.Event) -> None:
        """Обработка колеса мыши (zoom)"""
        zoom_factor = 1.1 if event.y > 0 else 1 / 1.1
        new_zoom = self.zoom * zoom_factor
        
        if self.min_zoom <= new_zoom <= self.max_zoom:
            # Zoom к позиции мыши
            mouse_pos = pygame.mouse.get_pos()
            mouse_world_before = self.screen_to_world(Vector2(mouse_pos))
            self.zoom = new_zoom
            mouse_world_after = self.screen_to_world(Vector2(mouse_pos))
            self.camera += mouse_world_before - mouse_world_after

    def _handle_dropfile(self, event: pygame.event.Event) -> None:
        """Обработка перетаскивания файлов"""
        filepath = event.file
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
            # Перетаскивание изображения - добавляем спрайт
            world_pos = self.screen_to_world(Vector2(pygame.mouse.get_pos()))
            self.add_sprite(filepath, world_pos)

    def update(self) -> None:
        """Обновление логики"""
        self.mouse_pos = Vector2(pygame.mouse.get_pos())
        self.mouse_world_pos = self.screen_to_world(self.mouse_pos)
        
        keys = pygame.key.get_pressed()
        
        # Перемещение камеры клавишами WASD или стрелками
        speed = 10 / self.zoom
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.camera.y -= speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.camera.y += speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.camera.x -= speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.camera.x += speed
        
        # Панорамирование камеры средней кнопкой или ПКМ
        mouse_buttons = pygame.mouse.get_pressed()
        if self.mouse_pressed and (mouse_buttons[1] or mouse_buttons[2]):
            current_pos = Vector2(pygame.mouse.get_pos())
            dx = current_pos.x - self.camera_drag_start.x
            dy = current_pos.y - self.camera_drag_start.y
            self.camera.x -= dx / self.zoom
            self.camera.y -= dy / self.zoom
            self.camera_drag_start = current_pos
        
        # Перемещение выделенных объектов
        elif self.mouse_dragging and self.selected_objects and self.mouse_pressed:
            if self.current_tool == ToolType.MOVE:
                self._update_move()
            elif self.current_tool == ToolType.ROTATE:
                self._update_rotate()
            elif self.current_tool == ToolType.SCALE:
                self._update_scale()

    def _update_move(self) -> None:
        """Обновление позиции при перетаскивании"""
        dx = self.mouse_world_pos.x - self.drag_start.x
        dy = self.mouse_world_pos.y - self.drag_start.y
        
        for obj in self.selected_objects:
            if obj.locked:
                continue
            obj.transform.x = self._snap_to_grid(self.drag_start.x + dx)
            obj.transform.y = self._snap_to_grid(self.drag_start.y + dy)

    def _update_rotate(self) -> None:
        """Обновление вращения при перетаскивании"""
        if not self.selected_objects:
            return
        
        obj = self.selected_objects[0]
        if obj.locked:
            return
        
        # Вычисляем угол от центра объекта до курсора мыши
        dx = self.mouse_world_pos.x - obj.transform.x
        dy = self.mouse_world_pos.y - obj.transform.y
        
        # Угол в градусах
        angle = math.degrees(math.atan2(-dy, dx)) - 90
        obj.transform.rotation = angle

    def _update_scale(self) -> None:
        """Обновление масштаба при перетаскивании"""
        for obj in self.selected_objects:
            if obj.locked:
                continue
            dx = (self.mouse_world_pos.x - obj.transform.x) / 50
            dy = (self.mouse_world_pos.y - obj.transform.y) / 50
            scale = max(0.1, 1 + dx + dy)
            obj.transform.scale_x = max(0.1, scale)
            obj.transform.scale_y = max(0.1, scale)

    def render(self) -> None:
        """Отрисовка"""
        self.screen.fill(self.colors["background"])
        
        self._render_viewport()
        self._render_ui()
        
        pygame.display.flip()

    def _render_viewport(self) -> None:
        """Отрисовка области редактирования"""
        viewport = self._get_viewport_rect()
        
        # Заливка viewport
        pygame.draw.rect(self.screen, self.colors["background"], viewport)
        
        # Сетка
        if self.scene.grid_visible:
            self._render_grid(viewport)
        
        # Спрайты
        for obj in self.scene.objects:
            if not obj.visible:
                continue
            self._render_sprite(obj)
        
        # Gizmo для выделенных объектов
        for obj in self.selected_objects:
            self._render_gizmo(obj)
        
        # Рамка viewport
        pygame.draw.rect(self.screen, self.colors["ui_border"], viewport, 2)

    def _render_grid(self, viewport: pygame.Rect) -> None:
        """Отрисовка сетки"""
        grid_size = self.scene.grid_size * self.zoom
        
        # Определяем видимую область в мировых координатах
        top_left = self.screen_to_world(Vector2(viewport.topleft))
        bottom_right = self.screen_to_world(Vector2(viewport.bottomright))
        
        start_x = int(top_left.x / self.scene.grid_size) * self.scene.grid_size
        start_y = int(top_left.y / self.scene.grid_size) * self.scene.grid_size
        
        # Цвета для разных уровней сетки
        grid_color = (35, 35, 40)      # 10px - самая тусклая
        major_color = (50, 50, 55)     # 50px - средняя
        super_color = (70, 70, 80)     # 500px - самая яркая
        
        # Вертикальные линии
        x = start_x
        while x <= bottom_right.x:
            screen_pos = self.world_to_screen(Vector2(x, 0))
            
            # Определяем уровень линии
            if abs(x % 500) < 0.1:
                color = super_color
                width = 2
            elif abs(x % 50) < 0.1:
                color = major_color
                width = 1
            else:
                color = grid_color
                width = 1
            
            pygame.draw.line(
                self.screen, color,
                (screen_pos.x, viewport.top),
                (screen_pos.x, viewport.bottom),
                width
            )
            x += self.scene.grid_size
        
        # Горизонтальные линии
        y = start_y
        while y <= bottom_right.y:
            screen_pos = self.world_to_screen(Vector2(0, y))
            
            # Определяем уровень линии
            if abs(y % 500) < 0.1:
                color = super_color
                width = 2
            elif abs(y % 50) < 0.1:
                color = major_color
                width = 1
            else:
                color = grid_color
                width = 1
            
            pygame.draw.line(
                self.screen, color,
                (viewport.left, screen_pos.y),
                (viewport.right, screen_pos.y),
                width
            )
            y += self.scene.grid_size

    def _render_sprite(self, obj: SceneObject) -> None:
        """Отрисовка спрайта"""
        sprite = self._get_sprite_image(obj)
        if not sprite:
            # Заглушка если нет изображения
            pos = self.world_to_screen(Vector2(obj.transform.x, obj.transform.y))
            size = 50 * obj.transform.scale_x * self.zoom
            rect = pygame.Rect(0, 0, size, size)
            rect.center = (int(pos.x), int(pos.y))
            pygame.draw.rect(self.screen, (80, 80, 80), rect)
            return
        
        # Применяем трансформации
        w, h = sprite.get_size()
        w *= obj.transform.scale_x * self.zoom
        h *= obj.transform.scale_y * self.zoom
        
        # Масштабируем изображение
        scaled = pygame.transform.scale(sprite, (int(w), int(h)))
        
        # Вращение
        if obj.transform.rotation != 0:
            angle = -obj.transform.rotation
            center = (w // 2, h // 2)
            scaled = pygame.transform.rotate(scaled, angle)
            # Корректировка центра после поворота
            new_w, new_h = scaled.get_size()
            offset_x = (new_w - w) // 2
            offset_y = (new_h - h) // 2
        else:
            offset_x, offset_y = 0, 0
        
        # Позиция на экране
        pos = self.world_to_screen(Vector2(obj.transform.x, obj.transform.y))
        x = int(pos.x - w / 2 - offset_x)
        y = int(pos.y - h / 2 - offset_y)
        
        self.screen.blit(scaled, (x, y))

    def _render_gizmo(self, obj: SceneObject) -> None:
        """Отрисовка gizmo (маркеры выделения)"""
        center_screen = self.world_to_screen(Vector2(obj.transform.x, obj.transform.y))
        
        # Размер рамки
        sprite = self._get_sprite_image(obj)
        if sprite:
            w = sprite.get_size()[0] * obj.transform.scale_x * self.zoom
            h = sprite.get_size()[1] * obj.transform.scale_y * self.zoom
        else:
            w, h = 50 * obj.transform.scale_x * self.zoom, 50 * obj.transform.scale_y * self.zoom
        
        # В зависимости от инструмента рисуем разное
        if self.current_tool == ToolType.MOVE:
            self._render_gizmo_move(center_screen, w, h)
        elif self.current_tool == ToolType.ROTATE:
            self._render_gizmo_rotate(center_screen, w, h)
        elif self.current_tool == ToolType.SCALE:
            self._render_gizmo_scale(center_screen, w, h)
        else:
            # Select - обычная рамка
            rect = pygame.Rect(0, 0, w + 10, h + 10)
            rect.center = (int(center_screen.x), int(center_screen.y))
            pygame.draw.rect(self.screen, self.colors["selection"], rect, 2)
            
            # Угловые маркеры
            for pos in [rect.topleft, rect.topright, rect.bottomleft, rect.bottomright]:
                pygame.draw.circle(self.screen, self.colors["selection"], pos, 6)
            pygame.draw.circle(self.screen, self.colors["selection"], rect.center, 4)

    def _render_gizmo_move(self, center: Vector2, w: float, h: float) -> None:
        """Gizmo для перемещения - стрелки по осям"""
        base_size = 20 * self.zoom
        
        # Ось X (красная)
        end_x = (center.x + base_size, center.y)
        pygame.draw.line(self.screen, (255, 80, 80), center, end_x, 3)
        pygame.draw.polygon(self.screen, (255, 80, 80), [
            end_x, (end_x[0] - 6, end_x[1] - 3), (end_x[0] - 6, end_x[1] + 3)
        ])
        
        # Ось Y (зеленая)
        end_y = (center.x, center.y - base_size)
        pygame.draw.line(self.screen, (80, 255, 80), center, end_y, 3)
        pygame.draw.polygon(self.screen, (80, 255, 80), [
            end_y, (end_y[0] - 3, end_y[1] + 6), (end_y[0] + 3, end_y[1] + 6)
        ])
        
        # Рамка выделения (тонкая)
        rect = pygame.Rect(0, 0, w + 10, h + 10)
        rect.center = (int(center.x), int(center.y))
        pygame.draw.rect(self.screen, (255, 80, 80), rect, 1)

    def _render_gizmo_rotate(self, center: Vector2, w: float, h: float) -> None:
        """Gizmo для вращения - круг вокруг объекта"""
        radius = max(w, h) / 2 + 15 * self.zoom
        
        # Круг вращения
        pygame.draw.circle(self.screen, (80, 255, 80), (int(center.x), int(center.y)), int(radius), 2)
        
        # Линия от центра к верху
        top_point = (center.x, center.y - radius)
        pygame.draw.line(self.screen, (80, 255, 80), center, top_point, 2)
        
        # Маркер верха
        pygame.draw.circle(self.screen, (80, 255, 80), (int(top_point[0]), int(top_point[1])), 5)
        
        # Рамка выделения (тонкая)
        rect = pygame.Rect(0, 0, w + 10, h + 10)
        rect.center = (int(center.x), int(center.y))
        pygame.draw.rect(self.screen, (80, 255, 80), rect, 1)

    def _render_gizmo_scale(self, center: Vector2, w: float, h: float) -> None:
        """Gizmo для масштабирования - угловые маркеры"""
        rect = pygame.Rect(0, 0, w + 10, h + 10)
        rect.center = (int(center.x), int(center.y))
        
        # Рамка
        pygame.draw.rect(self.screen, (100, 100, 255), rect, 2)
        
        # Угловые маркеры (синие)
        corners = [rect.topleft, rect.topright, rect.bottomleft, rect.bottomright]
        for pos in corners:
            pygame.draw.circle(self.screen, (100, 100, 255), pos, 8)
            pygame.draw.circle(self.screen, (255, 255, 255), pos, 4)
        
        # Боковые маркеры
        mid_top = (rect.centerx, rect.top)
        mid_bottom = (rect.centerx, rect.bottom)
        mid_left = (rect.left, rect.centery)
        mid_right = (rect.right, rect.centery)
        
        for pos in [mid_top, mid_bottom, mid_left, mid_right]:
            pygame.draw.circle(self.screen, (100, 100, 255), pos, 6)

    def _render_ui(self) -> None:
        """Отрисовка UI"""
        self._render_toolbar()
        self._render_hierarchy()
        self._render_inspector()
        self._render_statusbar()

    def _render_toolbar(self) -> None:
        """Отрисовка тулбара"""
        # Фон
        rect = pygame.Rect(0, 0, self.width, self.ui_top_height)
        pygame.draw.rect(self.screen, self.colors["ui_bg"], rect)
        pygame.draw.line(self.screen, self.colors["ui_border"], (0, self.ui_top_height), (self.width, self.ui_top_height), 1)
        
        # Инструменты как кнопки
        tools = [
            (ToolType.SELECT, "V", "Select"),
            (ToolType.MOVE, "G", "Move"),
            (ToolType.ROTATE, "R", "Rotate"),
            (ToolType.SCALE, "T", "Scale"),
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        x = 10
        
        for tool_type, key, name in tools:
            text = self.font_bold.render(f"{name} ({key})", True, self.colors["ui_text"])
            btn_width = text.get_width() + 20
            btn_rect = pygame.Rect(x, 5, btn_width, self.ui_top_height - 10)
            
            # Проверка наведения
            is_hovered = btn_rect.collidepoint(mouse_pos)
            is_selected = self.current_tool == tool_type
            
            # Фон кнопки
            if is_selected:
                pygame.draw.rect(self.screen, self.colors["ui_accent"], btn_rect, border_radius=4)
                color = (30, 30, 35)
            elif is_hovered:
                pygame.draw.rect(self.screen, (50, 50, 55), btn_rect, border_radius=4)
                color = self.colors["ui_text"]
            else:
                color = self.colors["ui_text"]
            
            text = self.font_bold.render(f"{name} ({key})", True, color)
            self.screen.blit(text, (x + 10, 12))
            x += btn_width + 10
        
        # Название сцены
        scene_name = self.scene.name + ("*" if self.modified else "")
        text = self.font_bold.render(scene_name, True, self.colors["ui_text"])
        self.screen.blit(text, (self.width // 2 - text.get_width() // 2, 12))
        
        # Кнопки справа
        btn_x = self.width - 175
        
        # Кнопка Add Sprite
        add_rect = pygame.Rect(btn_x, 8, 45, 24)
        is_add_hover = add_rect.collidepoint(mouse_pos)
        pygame.draw.rect(self.screen, (50, 100, 50) if is_add_hover else (40, 60, 40), add_rect, border_radius=4)
        add_text = self.font.render("Add", True, self.colors["ui_text"])
        self.screen.blit(add_text, (btn_x + 8, 13))
        
        # Кнопка Load
        load_rect = pygame.Rect(btn_x + 50, 8, 45, 24)
        is_load_hover = load_rect.collidepoint(mouse_pos)
        pygame.draw.rect(self.screen, (50, 50, 80) if is_load_hover else (40, 40, 60), load_rect, border_radius=4)
        load_text = self.font.render("Load", True, self.colors["ui_text"])
        self.screen.blit(load_text, (btn_x + 55, 13))
        
        # Кнопка Save
        save_rect = pygame.Rect(btn_x + 100, 8, 45, 24)
        is_save_hover = save_rect.collidepoint(mouse_pos)
        pygame.draw.rect(self.screen, (50, 50, 55) if is_save_hover else (40, 40, 45), save_rect, border_radius=4)
        save_text = self.font.render("Save", True, self.colors["ui_text"])
        self.screen.blit(save_text, (btn_x + 105, 13))
        
        # Кнопка New
        new_rect = pygame.Rect(btn_x + 150, 8, 45, 24)
        is_new_hover = new_rect.collidepoint(mouse_pos)
        pygame.draw.rect(self.screen, (50, 50, 55) if is_new_hover else (40, 40, 45), new_rect, border_radius=4)
        new_text = self.font.render("New", True, self.colors["ui_text"])
        self.screen.blit(new_text, (btn_x + 158, 13))
        
        # Кнопка Toggle Grid
        grid_rect = pygame.Rect(btn_x + 150, 8, 35, 24)
        is_grid_hover = grid_rect.collidepoint(mouse_pos)
        bg_color = self.colors["ui_accent"] if self.scene.grid_visible else (40, 40, 45)
        pygame.draw.rect(self.screen, bg_color if is_grid_hover else (40, 40, 45), grid_rect, border_radius=4)
        grid_text = self.font.render("Grid", True, (30, 30, 35) if self.scene.grid_visible else self.colors["ui_text"])
        self.screen.blit(grid_text, (btn_x + 148, 13))
        
        # Сохраняем rect кнопок для обработки кликов
        self._toolbar_buttons = {
            "add": add_rect,
            "load": load_rect,
            "save": save_rect,
            "new": new_rect,
            "grid": grid_rect
        }

    def _render_hierarchy(self) -> None:
        """Отрисовка панели иерархии (слева)"""
        rect = pygame.Rect(0, self.ui_top_height, self.ui_left_width, 
                          self.height - self.ui_top_height - self.ui_bottom_height)
        pygame.draw.rect(self.screen, self.colors["ui_bg"], rect)
        pygame.draw.line(self.screen, self.colors["ui_border"], 
                        (self.ui_left_width, self.ui_top_height), 
                        (self.ui_left_width, self.height - self.ui_bottom_height), 1)
        
        # Заголовок
        text = self.font_bold.render("Objects", True, self.colors["ui_text"])
        self.screen.blit(text, (10, self.ui_top_height + 10))
        
        # Список объектов
        mouse_pos = pygame.mouse.get_pos()
        y = self.ui_top_height + 35
        
        for obj in self.scene.objects:
            if y > self.height - self.ui_bottom_height - 20:
                break
            
            is_selected = obj in self.selected_objects
            
            # Подсветка при наведении и выделении
            text_rect = pygame.Rect(5, y, self.ui_left_width - 10, 22)
            is_hovered = text_rect.collidepoint(mouse_pos)
            
            if is_selected:
                pygame.draw.rect(self.screen, self.colors["ui_accent"], text_rect, border_radius=3)
                color = (30, 30, 35)
            elif is_hovered:
                pygame.draw.rect(self.screen, (50, 50, 55), text_rect, border_radius=3)
                color = self.colors["ui_text"]
            else:
                color = self.colors["ui_text"]
            
            # Индикатор видимости
            visibility = "👁" if obj.visible else "○"
            text = self.font.render(f"{visibility} {obj.name}", True, color)
            
            self.screen.blit(text, (15, y + 3))
            y += 22

    def _render_inspector(self) -> None:
        """Отрисовка панели свойств (справа)"""
        x = self.width - self.ui_right_width
        rect = pygame.Rect(x, self.ui_top_height, self.ui_right_width,
                          self.height - self.ui_top_height - self.ui_bottom_height)
        pygame.draw.rect(self.screen, self.colors["ui_bg"], rect)
        pygame.draw.line(self.screen, self.colors["ui_border"], 
                        (x, self.ui_top_height), (x, self.height - self.ui_bottom_height), 1)
        
        # Заголовок
        text = self.font_bold.render("Properties", True, self.colors["ui_text"])
        self.screen.blit(text, (x + 10, self.ui_top_height + 10))
        
        if not self.selected_objects:
            hint = self.font.render("No selection", True, (100, 100, 100))
            self.screen.blit(hint, (x + 10, self.ui_top_height + 40))
            return
        
        obj = self.selected_objects[0]
        y = self.ui_top_height + 40
        
        # Name
        y = self._render_property_row(x, y, "Name", obj.name)
        
        # Transform
        y += 10
        y = self._render_property_row(x, y, "Position X", f"{obj.transform.x:.1f}")
        y = self._render_property_row(x, y, "Position Y", f"{obj.transform.y:.1f}")
        y = self._render_property_row(x, y, "Rotation", f"{obj.transform.rotation:.1f}°")
        y = self._render_property_row(x, y, "Scale X", f"{obj.transform.scale_x:.2f}")
        y = self._render_property_row(x, y, "Scale Y", f"{obj.transform.scale_y:.2f}")
        
        # Sprite path
        y += 10
        sprite_text = os.path.basename(obj.sprite_path) if obj.sprite_path else "None"
        y = self._render_property_row(x, y, "Sprite", sprite_text)
        
        # Z-Index
        y = self._render_property_row(x, y, "Z-Index", str(obj.z_index))

    def _render_property_row(self, x: int, y: int, label: str, value: str) -> int:
        """Отрисовка строки свойства"""
        label_text = self.font.render(label, True, self.colors["ui_text"])
        value_text = self.font.render(value, True, (150, 150, 150))
        
        self.screen.blit(label_text, (x + 10, y))
        self.screen.blit(value_text, (x + self.ui_right_width - value_text.get_width() - 10, y))
        
        return y + 20

    def _render_statusbar(self) -> None:
        """Отрисовка статусбара"""
        rect = pygame.Rect(0, self.height - self.ui_bottom_height, 
                          self.width, self.ui_bottom_height)
        pygame.draw.rect(self.screen, self.colors["ui_bg"], rect)
        pygame.draw.line(self.screen, self.colors["ui_border"], 
                        (0, self.height - self.ui_bottom_height), 
                        (self.width, self.height - self.ui_bottom_height), 1)
        
        # Координаты мыши
        mouse_text = self.font.render(
            f"X: {self.mouse_world_pos.x:.0f}  Y: {self.mouse_world_pos.y:.0f}",
            True, self.colors["ui_text"]
        )
        self.screen.blit(mouse_text, (10, self.height - 22))
        
        # Zoom
        zoom_text = self.font.render(f"Zoom: {self.zoom * 100:.0f}%", True, self.colors["ui_text"])
        self.screen.blit(zoom_text, (self.width - 100, self.height - 22))
        
        # Grid
        grid_text = self.font.render(f"Grid: {self.scene.grid_size}px", True, self.colors["ui_text"])
        self.screen.blit(grid_text, (self.width // 2 - 50, self.height - 22))

    def _save_scene(self, filepath: Optional[str] = None) -> None:
        """Сохранение сцены"""
        if filepath is None:
            filepath = self.filepath
        
        if filepath is None:
            filepath = self._show_save_dialog()
            if not filepath:
                return
        
        self.scene.save(filepath)
        self.filepath = filepath
        self.scene.name = os.path.splitext(os.path.basename(filepath))[0]
        self.modified = False

    def _load_scene(self, filepath: Optional[str] = None) -> None:
        """Загрузка сцены"""
        if filepath is None:
            filepath = self._show_open_dialog()
            if not filepath:
                return
        
        try:
            self.scene = Scene.load(filepath)
            self.filepath = filepath
            self.selected_objects.clear()
            self.image_cache.clear()
            self.camera.x = self.scene.camera.x
            self.camera.y = self.scene.camera.y
            self.zoom = self.scene.camera.zoom
            self._save_state()
        except Exception as e:
            print(f"Error loading scene: {e}")

    def _show_save_dialog(self) -> Optional[str]:
        """Показать диалог сохранения"""
        if not TKINTER_AVAILABLE:
            return f"{self.scene.name}.json"
        
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            
            filepath = filedialog.asksaveasfilename(
                title="Сохранить сцену",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile=self.scene.name
            )
            
            root.destroy()
            return filepath if filepath else None
        except Exception:
            return f"{self.scene.name}.json"

    def _show_open_dialog(self) -> Optional[str]:
        """Показать диалог открытия"""
        if not TKINTER_AVAILABLE:
            return None
        
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            
            filepath = filedialog.askopenfilename(
                title="Открыть сцену",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialdir=os.path.dirname(self.filepath) if self.filepath else "."
            )
            
            root.destroy()
            return filepath if filepath else None
        except Exception:
            return None

    def run(self) -> None:
        """Главный цикл редактора"""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)
        
        pygame.quit()


def main():
    """Точка входа"""
    editor = SpriteEditor()
    editor.run()


if __name__ == "__main__":
    main()
