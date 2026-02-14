"""
Главный модуль редактора спрайтов
"""

import os
import importlib.util
import re
from pathlib import Path
import pygame
from pygame.math import Vector2
from typing import Optional, List, Tuple, Dict, Callable
from dataclasses import dataclass
from enum import Enum, auto

# Файловый диалог через tkinter
TKINTER_AVAILABLE = importlib.util.find_spec("tkinter") is not None

from .scene import Scene, SceneObject, Camera
from .ui.windows import SettingsWindow, WindowManager


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
    grid_size: int
    grid_visible: bool
    snap_to_grid: bool


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
        self.min_zoom = 0.01  # 1%
        self.max_zoom = 10.0  # 1000%
        self.min_grid_size = 8
        self.max_grid_size = 256
        self.camera_preview_enabled = True
        self.camera_preview_size = Vector2(800, 600)
        
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
        self._drag_object_starts: Dict[str, Dict[str, float]] = {}
        self._transform_changed_during_drag = False
        
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
        self._inspector_actions: List[Tuple[pygame.Rect, Callable[[], None]]] = []
        self._statusbar_controls: Dict[str, pygame.Rect] = {}
        self._active_slider: Optional[str] = None
        self._active_text_input: Optional[str] = None
        self._text_input_buffers: Dict[str, str] = {"zoom_input": "", "grid_input": ""}
        self._property_input_rects: Dict[str, pygame.Rect] = {}

        # Иерархия
        self.hierarchy_scroll = 0
        self.hierarchy_item_height = 22
        self._hierarchy_visible_capacity = 0

        # Окна/страницы
        self.window_manager = WindowManager()
        self.settings_window = SettingsWindow(
            pygame.Rect(self.width // 2 - 190, self.height // 2 - 140, 380, 280)
        )
        self.window_manager.register(self.settings_window)

        # Строка состояния
        self.status_message = "Ready"
        self.status_message_timer = 2.0
        
        # Запуск
        self._save_state(mark_modified=False)

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

    def _sync_scene_camera(self) -> None:
        """Синхронизирует параметры камеры в модели сцены."""
        self.scene.camera.x = self.camera.x
        self.scene.camera.y = self.camera.y
        self.scene.camera.zoom = self.zoom

    def _set_status(self, message: str, ttl: float = 2.0) -> None:
        """Показывает краткий статус в нижней панели."""
        self.status_message = message
        self.status_message_timer = ttl

    def _save_state(self, mark_modified: bool = True) -> None:
        """Сохраняет состояние для Undo"""
        self._sync_scene_camera()
        state = EditorState(
            objects=[obj.to_dict() for obj in self.scene.objects],
            camera=self.scene.camera.to_dict(),
            grid_size=self.scene.grid_size,
            grid_visible=self.scene.grid_visible,
            snap_to_grid=self.scene.snap_to_grid,
        )
        self.undo_stack.append(state)
        if len(self.undo_stack) > self.max_undo:
            self.undo_stack.pop(0)
        self.redo_stack.clear()
        if mark_modified:
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
        self.scene.grid_size = state.grid_size
        self.scene.grid_visible = state.grid_visible
        self.scene.snap_to_grid = state.snap_to_grid
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
        used_names = {obj.name for obj in self.scene.objects}
        for obj in self.selected_objects:
            new_obj = obj.copy()
            base_name = self._get_clone_base_name(obj.name)
            new_obj.name = self._make_next_clone_name(base_name, used_names)
            used_names.add(new_obj.name)
            new_obj.transform.x += 50
            new_obj.transform.y += 50
            self.scene.add_object(new_obj)
            new_objects.append(new_obj)
        self.selected_objects = new_objects
        self._save_state()
        return new_objects

    def _get_clone_base_name(self, name: str) -> str:
        match = re.match(r"^(.*)\s\((\d+)\)$", name.strip())
        if match:
            return match.group(1).strip()
        return name.strip()

    def _make_next_clone_name(self, base_name: str, used_names: set[str]) -> str:
        i = 1
        while True:
            candidate = f"{base_name} ({i})"
            if candidate not in used_names:
                return candidate
            i += 1

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
                self.settings_window.rect.center = (self.width // 2, self.height // 2)
            
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)

            elif event.type == pygame.TEXTINPUT:
                self._handle_text_input_text(event)
            
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
        if self._handle_text_input_keydown(event):
            return

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
        elif event.key == pygame.K_F1:
            self.window_manager.toggle("settings")
        
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
            self._transform_changed_during_drag = False

            # Если активен текстовый ввод в статусбаре, клик вне поля подтверждает значение
            if self._active_text_input and not self._click_in_any_text_input(event.pos):
                self._deactivate_text_input(apply=True)
            
            # Модальные окна/страницы
            if self.window_manager.handle_click((int(self.mouse_pos.x), int(self.mouse_pos.y))):
                return
            
            # Status bar (слайдеры/переключатели)
            if self._handle_statusbar_click(self.mouse_pos):
                return
            
            # Проверяем клик по toolbar (выбор инструментов)
            if self.mouse_pos.y <= self.ui_top_height:
                self._handle_toolbar_click(self.mouse_pos)
                return
            
            # Проверяем клик по inspector (правая панель)
            if self.mouse_pos.x >= self.width - self.ui_right_width:
                if self._handle_inspector_click(self.mouse_pos):
                    return
            
            # Проверяем клик по hierarchy (левая панель)
            if self.mouse_pos.x <= self.ui_left_width:
                obj = self._handle_hierarchy_click(self.mouse_pos)
                if obj:
                    keys = pygame.key.get_pressed()
                    self.select_object(obj, add_to_selection=keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])
                    return
            
            # Проверяем клик по объекту в viewport
            viewport = self._get_viewport_rect()
            if viewport.collidepoint(self.mouse_pos):
                obj = self.get_object_at(self.mouse_world_pos)
                if obj:
                    keys = pygame.key.get_pressed()
                    self.select_object(obj, add_to_selection=keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])
                else:
                    # Клик по пустому пространству
                    if self.current_tool == ToolType.SELECT:
                        self.deselect_all()
                
                # Сохраняем позиции для перетаскивания
                self.drag_start = self.mouse_world_pos.copy()
                self.camera_drag_start = Vector2(event.pos)  # Для pan
                self._capture_drag_state()
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
                self._save_state()
                return
            elif self._toolbar_buttons.get("settings", pygame.Rect(0,0,0,0)).collidepoint(pos.x, pos.y):
                self.window_manager.toggle("settings")
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
        self.scene.grid_size = 10
        self.filepath = None
        self.selected_objects.clear()
        self.image_cache.clear()
        self.camera = Vector2(0, 0)
        self.zoom = 1.0
        self.undo_stack.clear()
        self.redo_stack.clear()
        self._save_state(mark_modified=False)
        self.modified = False
        self._set_status("New scene created")

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
        list_top = self.ui_top_height + 35
        list_bottom = self.height - self.ui_bottom_height - 8
        if pos.y < list_top or pos.y > list_bottom:
            return None

        self._clamp_hierarchy_scroll()
        index = int((pos.y - list_top) // self.hierarchy_item_height) + self.hierarchy_scroll
        if 0 <= index < len(self.scene.objects):
            return self.scene.objects[index]
        return None

    def _handle_mouseup(self, event: pygame.event.Event) -> None:
        """Обработка отжатия кнопки мыши"""
        if event.button == 1:
            if self._active_slider is not None:
                self._active_slider = None
                self._save_state()
            elif self.mouse_dragging and self._transform_changed_during_drag:
                self._save_state()
        
        self.mouse_pressed = False
        self.mouse_dragging = False
        self._drag_object_starts.clear()
        self._transform_changed_during_drag = False

    def _handle_mousewheel(self, event: pygame.event.Event) -> None:
        """Обработка колеса мыши (zoom)"""
        mouse_pos = Vector2(pygame.mouse.get_pos())
        hierarchy_rect = pygame.Rect(
            0,
            self.ui_top_height,
            self.ui_left_width,
            self.height - self.ui_top_height - self.ui_bottom_height,
        )
        viewport_rect = self._get_viewport_rect()

        if hierarchy_rect.collidepoint(mouse_pos.x, mouse_pos.y):
            self.hierarchy_scroll -= event.y
            self._clamp_hierarchy_scroll()
            return
        if not viewport_rect.collidepoint(mouse_pos.x, mouse_pos.y):
            return

        zoom_factor = 1.1 if event.y > 0 else 1 / 1.1
        self._set_zoom(self.zoom * zoom_factor, Vector2(pygame.mouse.get_pos()))

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
        self._sync_scene_camera()
        
        if self.status_message_timer > 0:
            self.status_message_timer = max(0.0, self.status_message_timer - (self.clock.get_time() / 1000.0))
        
        if self._active_slider and pygame.mouse.get_pressed()[0]:
            self._update_active_slider(self.mouse_pos.x)
        
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
            start = self._drag_object_starts.get(obj.id)
            if start is None:
                continue
            new_x = self._snap_to_grid(start["x"] + dx)
            new_y = self._snap_to_grid(start["y"] + dy)
            if abs(new_x - obj.transform.x) > 1e-6 or abs(new_y - obj.transform.y) > 1e-6:
                self._transform_changed_during_drag = True
            obj.transform.x = new_x
            obj.transform.y = new_y

    def _update_rotate(self) -> None:
        """Обновление вращения при перетаскивании"""
        if not self.selected_objects:
            return
        mouse_dx = self.mouse_pos.x - self.camera_drag_start.x
        angle_delta = mouse_dx * 0.5
        keys = pygame.key.get_pressed()
        snap_angle = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        for obj in self.selected_objects:
            if obj.locked:
                continue
            start = self._drag_object_starts.get(obj.id)
            if start is None:
                continue
            new_angle = start["rotation"] + angle_delta
            if snap_angle:
                new_angle = round(new_angle / 15.0) * 15.0
            if abs(new_angle - obj.transform.rotation) > 1e-6:
                self._transform_changed_during_drag = True
            obj.transform.rotation = new_angle

    def _update_scale(self) -> None:
        """Обновление масштаба при перетаскивании"""
        dx = (self.mouse_world_pos.x - self.drag_start.x) / 100.0
        dy = (self.mouse_world_pos.y - self.drag_start.y) / 100.0
        keys = pygame.key.get_pressed()
        uniform = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        for obj in self.selected_objects:
            if obj.locked:
                continue
            start = self._drag_object_starts.get(obj.id)
            if start is None:
                continue
            if uniform:
                delta = (dx + dy) * 0.5
                new_sx = max(0.05, start["scale_x"] + delta)
                new_sy = max(0.05, start["scale_y"] + delta)
            else:
                new_sx = max(0.05, start["scale_x"] + dx)
                new_sy = max(0.05, start["scale_y"] + dy)
            if abs(new_sx - obj.transform.scale_x) > 1e-6 or abs(new_sy - obj.transform.scale_y) > 1e-6:
                self._transform_changed_during_drag = True
            obj.transform.scale_x = new_sx
            obj.transform.scale_y = new_sy

    def render(self) -> None:
        """Отрисовка"""
        self.screen.fill(self.colors["background"])
        
        self._render_viewport()
        self._render_ui()
        self._render_windows()
        
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

        if self.camera_preview_enabled:
            self._render_camera_preview_frame(viewport)
        
        # Рамка viewport
        pygame.draw.rect(self.screen, self.colors["ui_border"], viewport, 2)

    def _render_camera_preview_frame(self, viewport: pygame.Rect) -> None:
        frame_w = max(8, int(self.camera_preview_size.x))
        frame_h = max(8, int(self.camera_preview_size.y))
        frame_rect = pygame.Rect(0, 0, frame_w, frame_h)
        frame_rect.center = viewport.center

        outer_rect = frame_rect.inflate(2, 2)
        pygame.draw.rect(self.screen, (25, 25, 28), outer_rect, 2)
        pygame.draw.rect(self.screen, (255, 210, 80), frame_rect, 1)

        label = self.font.render(f"Camera {frame_w}x{frame_h}", True, (255, 210, 80))
        label_bg = pygame.Rect(frame_rect.x + 4, frame_rect.y + 4, label.get_width() + 8, label.get_height() + 4)
        pygame.draw.rect(self.screen, (20, 20, 24), label_bg, border_radius=3)
        pygame.draw.rect(self.screen, (80, 70, 30), label_bg, 1, border_radius=3)
        self.screen.blit(label, (label_bg.x + 4, label_bg.y + 2))

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
        scaled_w = max(1, int(w))
        scaled_h = max(1, int(h))
        scaled = pygame.transform.scale(sprite, (scaled_w, scaled_h))
        
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
        buttons = [
            ("settings", "Settings", 72),
            ("grid", "Grid", 52),
            ("new", "New", 45),
            ("save", "Save", 45),
            ("load", "Load", 45),
            ("add", "Add", 45),
        ]
        gap = 6
        total_width = sum(btn[2] for btn in buttons) + gap * (len(buttons) - 1)
        btn_x = self.width - total_width - 10
        self._toolbar_buttons = {}

        for key, label, width in buttons:
            rect = pygame.Rect(btn_x, 8, width, 24)
            is_hovered = rect.collidepoint(mouse_pos)
            if key == "add":
                color = (50, 100, 50) if is_hovered else (40, 60, 40)
            elif key == "load":
                color = (50, 50, 80) if is_hovered else (40, 40, 60)
            elif key == "grid":
                base = self.colors["ui_accent"] if self.scene.grid_visible else (40, 40, 45)
                color = base if not is_hovered else (70, 170, 255) if self.scene.grid_visible else (50, 50, 55)
            elif key == "settings":
                color = (62, 58, 82) if is_hovered else (48, 44, 66)
            else:
                color = (50, 50, 55) if is_hovered else (40, 40, 45)
            pygame.draw.rect(self.screen, color, rect, border_radius=4)
            text_color = (25, 25, 30) if key == "grid" and self.scene.grid_visible else self.colors["ui_text"]
            label_surface = self.font.render(label, True, text_color)
            self.screen.blit(
                label_surface,
                (rect.centerx - label_surface.get_width() // 2, rect.y + 5),
            )
            self._toolbar_buttons[key] = rect
            btn_x += width + gap

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
        
        # Список объектов со скроллом
        list_top = self.ui_top_height + 35
        list_bottom = self.height - self.ui_bottom_height - 8
        list_height = max(0, list_bottom - list_top)
        self._hierarchy_visible_capacity = max(1, list_height // self.hierarchy_item_height)
        self._clamp_hierarchy_scroll()

        start_index = self.hierarchy_scroll
        end_index = min(len(self.scene.objects), start_index + self._hierarchy_visible_capacity)

        mouse_pos = pygame.mouse.get_pos()
        y = list_top
        for obj in self.scene.objects[start_index:end_index]:
            
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
            max_name_width = self.ui_left_width - 30
            clipped_name = self._fit_text_to_width(f"{visibility} {obj.name}", max_name_width, self.font)
            text = self.font.render(clipped_name, True, color)
            
            self.screen.blit(text, (15, y + 3))
            y += self.hierarchy_item_height

        self._render_hierarchy_scrollbar(list_top, list_bottom)

    def _fit_text_to_width(self, text: str, max_width: int, font: pygame.font.Font) -> str:
        if font.size(text)[0] <= max_width:
            return text
        ellipsis = "..."
        left, right = 0, len(text)
        best = ellipsis
        while left <= right:
            mid = (left + right) // 2
            candidate = text[:mid].rstrip() + ellipsis
            if font.size(candidate)[0] <= max_width:
                best = candidate
                left = mid + 1
            else:
                right = mid - 1
        return best

    def _clamp_hierarchy_scroll(self) -> None:
        max_scroll = max(0, len(self.scene.objects) - max(1, self._hierarchy_visible_capacity))
        self.hierarchy_scroll = max(0, min(self.hierarchy_scroll, max_scroll))

    def _render_hierarchy_scrollbar(self, list_top: int, list_bottom: int) -> None:
        total = len(self.scene.objects)
        visible = max(1, self._hierarchy_visible_capacity)
        if total <= visible:
            return
        track_rect = pygame.Rect(self.ui_left_width - 8, list_top, 4, list_bottom - list_top)
        pygame.draw.rect(self.screen, (50, 50, 55), track_rect, border_radius=2)

        ratio = visible / total
        thumb_h = max(20, int(track_rect.height * ratio))
        max_scroll = max(1, total - visible)
        t = self.hierarchy_scroll / max_scroll
        thumb_y = track_rect.y + int((track_rect.height - thumb_h) * t)
        thumb_rect = pygame.Rect(track_rect.x, thumb_y, track_rect.width, thumb_h)
        pygame.draw.rect(self.screen, (110, 110, 120), thumb_rect, border_radius=2)

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
        self._inspector_actions = []
        self._property_input_rects = {}
        
        if not self.selected_objects:
            hint = self.font.render("No selection", True, (100, 100, 100))
            self.screen.blit(hint, (x + 10, self.ui_top_height + 40))
            return
        
        obj = self.selected_objects[0]
        y = self.ui_top_height + 40
        
        # Name
        y = self._render_property_row(x, y, "Name", obj.name)
        
        # Transform (editable)
        y += 10
        y = self._render_numeric_property_row(
            x, y, "Position X", obj.transform.x, -10.0, 10.0, "x", "{:.1f}"
        )
        y = self._render_numeric_property_row(
            x, y, "Position Y", obj.transform.y, -10.0, 10.0, "y", "{:.1f}"
        )
        y = self._render_numeric_property_row(
            x, y, "Rotation", obj.transform.rotation, -5.0, 5.0, "rotation", "{:.1f} deg"
        )
        y = self._render_numeric_property_row(
            x, y, "Scale X", obj.transform.scale_x, -0.1, 0.1, "scale_x", "{:.2f}"
        )
        y = self._render_numeric_property_row(
            x, y, "Scale Y", obj.transform.scale_y, -0.1, 0.1, "scale_y", "{:.2f}"
        )
        
        # Размеры
        native_w, native_h = self._get_object_native_size(obj)
        size_x, size_y = self._get_object_display_size(obj)
        y += 8
        y = self._render_property_row(x, y, "Image Size", f"{native_w} x {native_h}")
        y = self._render_numeric_property_row(x, y, "Size X", size_x, -8.0, 8.0, "width", "{:.1f}px")
        y = self._render_numeric_property_row(x, y, "Size Y", size_y, -8.0, 8.0, "height", "{:.1f}px")
        
        # Sprite path
        y += 10
        sprite_text = os.path.basename(obj.sprite_path) if obj.sprite_path else "None"
        y = self._render_property_row(x, y, "Sprite", sprite_text)
        
        # Z-Index и флаги
        y = self._render_numeric_property_row(x, y, "Z-Index", float(obj.z_index), -1.0, 1.0, "z_index", "{:.0f}")
        y += 8
        y = self._render_toggle_property_row(x, y, "Visible", obj.visible, "visible")
        y = self._render_toggle_property_row(x, y, "Locked", obj.locked, "locked")

    def _render_numeric_property_row(
        self,
        x: int,
        y: int,
        label: str,
        value: float,
        dec_step: float,
        inc_step: float,
        prop: str,
        fmt: str,
    ) -> int:
        label_text = self.font.render(label, True, self.colors["ui_text"])
        self.screen.blit(label_text, (x + 10, y))

        minus_rect = pygame.Rect(x + self.ui_right_width - 112, y + 1, 18, 18)
        input_rect = pygame.Rect(x + self.ui_right_width - 90, y + 1, 60, 18)
        plus_rect = pygame.Rect(x + self.ui_right_width - 24, y + 1, 18, 18)
        input_name = f"prop_input_{prop}"
        self._property_input_rects[input_name] = input_rect

        self._draw_property_input_box(
            name=input_name,
            rect=input_rect,
            value_display=self._format_numeric_for_input(prop, value),
        )
        self._draw_small_button(minus_rect, "-")
        self._draw_small_button(plus_rect, "+")

        self._inspector_actions.append(
            (
                input_rect,
                lambda n=input_name, v=self._format_numeric_for_input(prop, value): self._activate_text_input(n, v),
            )
        )
        self._inspector_actions.append(
            (minus_rect, lambda p=prop, d=dec_step: self._adjust_selected_property(p, d))
        )
        self._inspector_actions.append(
            (plus_rect, lambda p=prop, d=inc_step: self._adjust_selected_property(p, d))
        )
        return y + 20

    def _draw_property_input_box(self, name: str, rect: pygame.Rect, value_display: str) -> None:
        active = self._active_text_input == name
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        bg = (62, 62, 70) if active else (48, 48, 56) if hovered else (42, 42, 50)
        border = self.colors["ui_accent"] if active else (95, 95, 110)
        pygame.draw.rect(self.screen, bg, rect, border_radius=3)
        pygame.draw.rect(self.screen, border, rect, 1, border_radius=3)
        if active:
            display = f"{self._text_input_buffers.get(name, '')}|"
        else:
            display = value_display
        text_surface = self.font.render(display, True, (235, 235, 240))
        self.screen.blit(text_surface, (rect.x + 3, rect.y + 2))

    def _format_numeric_for_input(self, prop: str, value: float) -> str:
        if prop == "z_index":
            return str(int(round(value)))
        text = f"{value:.3f}".rstrip("0").rstrip(".")
        return text if text else "0"

    def _render_toggle_property_row(
        self,
        x: int,
        y: int,
        label: str,
        value: bool,
        prop: str,
    ) -> int:
        label_text = self.font.render(label, True, self.colors["ui_text"])
        self.screen.blit(label_text, (x + 10, y))
        
        btn_rect = pygame.Rect(x + self.ui_right_width - 60, y + 1, 50, 18)
        color = self.colors["ui_accent"] if value else (55, 55, 62)
        fg = (25, 25, 30) if value else self.colors["ui_text"]
        pygame.draw.rect(self.screen, color, btn_rect, border_radius=3)
        text = self.font.render("ON" if value else "OFF", True, fg)
        self.screen.blit(text, (btn_rect.centerx - text.get_width() // 2, y + 2))
        self._inspector_actions.append((btn_rect, lambda p=prop: self._toggle_selected_property(p)))
        return y + 20

    def _draw_small_button(self, rect: pygame.Rect, caption: str) -> None:
        mouse_pos = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse_pos)
        pygame.draw.rect(
            self.screen,
            (58, 58, 64) if hovered else (44, 44, 50),
            rect,
            border_radius=3,
        )
        cap = self.font.render(caption, True, self.colors["ui_text"])
        self.screen.blit(cap, (rect.centerx - cap.get_width() // 2, rect.y + 1))

    def _handle_inspector_click(self, pos: Vector2) -> bool:
        for rect, action in self._inspector_actions:
            if rect.collidepoint(pos.x, pos.y):
                action()
                return True
        return True

    def _get_object_native_size(self, obj: SceneObject) -> Tuple[int, int]:
        sprite = self._get_sprite_image(obj)
        if sprite is None:
            return (0, 0)
        return sprite.get_width(), sprite.get_height()

    def _get_object_display_size(self, obj: SceneObject) -> Tuple[float, float]:
        native_w, native_h = self._get_object_native_size(obj)
        return native_w * obj.transform.scale_x, native_h * obj.transform.scale_y

    def _adjust_selected_property(self, prop: str, delta: float) -> None:
        changed = False
        for obj in self.selected_objects:
            if obj.locked and prop not in ("visible", "locked"):
                continue
            if prop == "x":
                obj.transform.x += delta
                changed = True
            elif prop == "y":
                obj.transform.y += delta
                changed = True
            elif prop == "rotation":
                obj.transform.rotation += delta
                changed = True
            elif prop == "scale_x":
                obj.transform.scale_x = max(0.05, obj.transform.scale_x + delta)
                changed = True
            elif prop == "scale_y":
                obj.transform.scale_y = max(0.05, obj.transform.scale_y + delta)
                changed = True
            elif prop == "z_index":
                obj.z_index += int(delta)
                changed = True
            elif prop in ("width", "height"):
                native_w, native_h = self._get_object_native_size(obj)
                if prop == "width" and native_w > 0:
                    current_w = native_w * obj.transform.scale_x
                    obj.transform.scale_x = max(0.05, (current_w + delta) / native_w)
                    changed = True
                if prop == "height" and native_h > 0:
                    current_h = native_h * obj.transform.scale_y
                    obj.transform.scale_y = max(0.05, (current_h + delta) / native_h)
                    changed = True
        if changed:
            self.scene._sort_by_z_index()
            self._save_state()

    def _toggle_selected_property(self, prop: str) -> None:
        if not self.selected_objects:
            return
        changed = False
        if prop == "visible":
            new_value = not self.selected_objects[0].visible
            for obj in self.selected_objects:
                obj.visible = new_value
                changed = True
        elif prop == "locked":
            new_value = not self.selected_objects[0].locked
            for obj in self.selected_objects:
                obj.locked = new_value
                changed = True
        if changed:
            self._save_state()

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
        
        slider_y = self.height - 19
        slider_h = 9
        zoom_slider = pygame.Rect(max(180, self.width // 2 - 180), slider_y, 140, slider_h)
        grid_slider = pygame.Rect(zoom_slider.right + 120, slider_y, 140, slider_h)
        self._statusbar_controls["zoom"] = zoom_slider
        self._statusbar_controls["grid"] = grid_slider

        zoom_label = self.font.render("Zoom", True, self.colors["ui_text"])
        grid_label = self.font.render("Grid", True, self.colors["ui_text"])
        self.screen.blit(zoom_label, (zoom_slider.x - 40, self.height - 23))
        self.screen.blit(grid_label, (grid_slider.x - 34, self.height - 23))

        self._draw_slider(
            zoom_slider,
            value=self.zoom,
            min_value=self.min_zoom,
            max_value=self.max_zoom,
            accent=self.colors["ui_accent"],
        )
        self._draw_slider(
            grid_slider,
            value=float(self.scene.grid_size),
            min_value=float(self.min_grid_size),
            max_value=float(self.max_grid_size),
            accent=(150, 130, 255),
        )

        # Переключатель snap
        snap_rect = pygame.Rect(grid_slider.right + 14, self.height - 24, 80, 18)
        self._statusbar_controls["snap"] = snap_rect
        snap_color = self.colors["ui_accent"] if self.scene.snap_to_grid else (55, 55, 62)
        snap_fg = (25, 25, 30) if self.scene.snap_to_grid else self.colors["ui_text"]
        pygame.draw.rect(self.screen, snap_color, snap_rect, border_radius=3)
        snap_text = self.font.render("Snap ON" if self.scene.snap_to_grid else "Snap OFF", True, snap_fg)
        self.screen.blit(snap_text, (snap_rect.centerx - snap_text.get_width() // 2, snap_rect.y + 2))

        # Текстовые значения справа
        zoom_input_rect = pygame.Rect(self.width - 190, self.height - 24, 72, 18)
        grid_input_rect = pygame.Rect(self.width - 108, self.height - 24, 72, 18)
        self._statusbar_controls["zoom_input"] = zoom_input_rect
        self._statusbar_controls["grid_input"] = grid_input_rect

        self._draw_status_input_box(
            name="zoom_input",
            rect=zoom_input_rect,
            value_display=f"{self.zoom * 100:.0f}",
            suffix="%",
        )
        self._draw_status_input_box(
            name="grid_input",
            rect=grid_input_rect,
            value_display=str(self.scene.grid_size),
            suffix="px",
        )

        # Статус
        if self.status_message_timer > 0:
            status = self.font.render(self.status_message, True, (160, 160, 170))
            self.screen.blit(status, (self.width // 2 - status.get_width() // 2, self.height - 22))

    def _draw_slider(
        self,
        rect: pygame.Rect,
        value: float,
        min_value: float,
        max_value: float,
        accent: Tuple[int, int, int],
    ) -> None:
        pygame.draw.rect(self.screen, (55, 55, 62), rect, border_radius=4)
        ratio = 0.0 if max_value <= min_value else (value - min_value) / (max_value - min_value)
        ratio = max(0.0, min(1.0, ratio))
        fill_width = int(rect.width * ratio)
        if fill_width > 0:
            pygame.draw.rect(
                self.screen,
                accent,
                pygame.Rect(rect.x, rect.y, fill_width, rect.height),
                border_radius=4,
            )
        thumb_x = rect.x + int(rect.width * ratio)
        thumb_rect = pygame.Rect(thumb_x - 3, rect.y - 2, 6, rect.height + 4)
        pygame.draw.rect(self.screen, (225, 225, 230), thumb_rect, border_radius=3)

    def _draw_status_input_box(self, name: str, rect: pygame.Rect, value_display: str, suffix: str) -> None:
        active = self._active_text_input == name
        bg = (62, 62, 70) if active else (45, 45, 52)
        pygame.draw.rect(self.screen, bg, rect, border_radius=3)
        pygame.draw.rect(self.screen, self.colors["ui_border"], rect, 1, border_radius=3)

        if active:
            text = self._text_input_buffers.get(name, "")
            display = f"{text}|"
        else:
            display = f"{value_display}{suffix}"
        text_surface = self.font.render(display, True, self.colors["ui_text"])
        self.screen.blit(text_surface, (rect.x + 4, rect.y + 2))

    def _handle_statusbar_click(self, pos: Vector2) -> bool:
        if pos.y < self.height - self.ui_bottom_height:
            return False
        zoom_rect = self._statusbar_controls.get("zoom")
        grid_rect = self._statusbar_controls.get("grid")
        snap_rect = self._statusbar_controls.get("snap")
        zoom_input_rect = self._statusbar_controls.get("zoom_input")
        grid_input_rect = self._statusbar_controls.get("grid_input")

        if zoom_input_rect and zoom_input_rect.collidepoint(pos.x, pos.y):
            self._activate_text_input("zoom_input", f"{self.zoom * 100:.0f}")
            return True
        if grid_input_rect and grid_input_rect.collidepoint(pos.x, pos.y):
            self._activate_text_input("grid_input", str(self.scene.grid_size))
            return True

        if self._active_text_input:
            self._deactivate_text_input(apply=True)

        if zoom_rect and zoom_rect.collidepoint(pos.x, pos.y):
            self._active_slider = "zoom"
            self._update_active_slider(pos.x)
            return True
        if grid_rect and grid_rect.collidepoint(pos.x, pos.y):
            self._active_slider = "grid"
            self._update_active_slider(pos.x)
            return True
        if snap_rect and snap_rect.collidepoint(pos.x, pos.y):
            self.scene.snap_to_grid = not self.scene.snap_to_grid
            self._save_state()
            return True
        return False

    def _click_in_status_input(self, pos: tuple[int, int]) -> bool:
        for key in ("zoom_input", "grid_input"):
            rect = self._statusbar_controls.get(key)
            if rect and rect.collidepoint(pos):
                return True
        return False

    def _click_in_property_input(self, pos: tuple[int, int]) -> bool:
        for rect in self._property_input_rects.values():
            if rect.collidepoint(pos):
                return True
        return False

    def _click_in_any_text_input(self, pos: tuple[int, int]) -> bool:
        return self._click_in_status_input(pos) or self._click_in_property_input(pos)

    def _activate_text_input(self, name: str, initial_value: str = "") -> None:
        if self._active_text_input is not None and self._active_text_input != name:
            self._deactivate_text_input(apply=True)
        self._text_input_buffers[name] = initial_value
        self._active_text_input = name

    def _deactivate_text_input(self, apply: bool) -> None:
        if self._active_text_input is None:
            return
        if apply:
            self._apply_text_input_value(self._active_text_input)
        self._active_text_input = None

    def _handle_text_input_keydown(self, event: pygame.event.Event) -> bool:
        name = self._active_text_input
        if name is None:
            return False

        if event.key == pygame.K_RETURN:
            self._deactivate_text_input(apply=True)
            return True
        if event.key == pygame.K_ESCAPE:
            self._deactivate_text_input(apply=False)
            return True
        if event.key == pygame.K_BACKSPACE:
            self._text_input_buffers[name] = self._text_input_buffers[name][:-1]
            return True

        ch = event.unicode
        if ch and self._is_allowed_input_char(ch):
            self._text_input_buffers[name] += ch
            return True
        keypad_map = {
            pygame.K_KP0: "0",
            pygame.K_KP1: "1",
            pygame.K_KP2: "2",
            pygame.K_KP3: "3",
            pygame.K_KP4: "4",
            pygame.K_KP5: "5",
            pygame.K_KP6: "6",
            pygame.K_KP7: "7",
            pygame.K_KP8: "8",
            pygame.K_KP9: "9",
            pygame.K_KP_PERIOD: ".",
            pygame.K_KP_MINUS: "-",
            pygame.K_MINUS: "-",
            pygame.K_PERIOD: ".",
            pygame.K_COMMA: ",",
        }
        if event.key in keypad_map:
            self._text_input_buffers[name] += keypad_map[event.key]
        return True

    def _handle_text_input_text(self, event: pygame.event.Event) -> bool:
        name = self._active_text_input
        if name is None:
            return False
        text = event.text or ""
        filtered = "".join(ch for ch in text if self._is_allowed_input_char(ch))
        if filtered:
            self._text_input_buffers[name] += filtered
        return True

    def _is_allowed_input_char(self, ch: str) -> bool:
        return ch in "0123456789.,-"

    def _apply_text_input_value(self, name: str) -> None:
        raw = self._text_input_buffers.get(name, "").strip().replace(",", ".")
        if not raw:
            return
        try:
            if name == "zoom_input":
                percent = float(raw)
                value = percent * 0.01
                prev = self.zoom
                self._set_zoom(value, Vector2(pygame.mouse.get_pos()))
                if abs(self.zoom - prev) > 1e-9:
                    self._save_state()
            elif name == "grid_input":
                value = int(float(raw))
                value = max(self.min_grid_size, min(self.max_grid_size, value))
                if value != self.scene.grid_size:
                    self.scene.grid_size = value
                    self._save_state()
            elif name.startswith("prop_input_"):
                prop = name.replace("prop_input_", "", 1)
                value = float(raw)
                self._set_selected_property_value(prop, value)
        except ValueError:
            self._set_status("Invalid input", ttl=2.0)

    def _set_selected_property_value(self, prop: str, value: float) -> None:
        if not self.selected_objects:
            return
        changed = False
        for obj in self.selected_objects:
            if obj.locked and prop not in ("visible", "locked"):
                continue
            if prop == "x":
                if abs(obj.transform.x - value) > 1e-9:
                    obj.transform.x = value
                    changed = True
            elif prop == "y":
                if abs(obj.transform.y - value) > 1e-9:
                    obj.transform.y = value
                    changed = True
            elif prop == "rotation":
                if abs(obj.transform.rotation - value) > 1e-9:
                    obj.transform.rotation = value
                    changed = True
            elif prop == "scale_x":
                new_value = max(0.05, value)
                if abs(obj.transform.scale_x - new_value) > 1e-9:
                    obj.transform.scale_x = new_value
                    changed = True
            elif prop == "scale_y":
                new_value = max(0.05, value)
                if abs(obj.transform.scale_y - new_value) > 1e-9:
                    obj.transform.scale_y = new_value
                    changed = True
            elif prop == "z_index":
                new_value = int(round(value))
                if obj.z_index != new_value:
                    obj.z_index = new_value
                    changed = True
            elif prop in ("width", "height"):
                native_w, native_h = self._get_object_native_size(obj)
                if prop == "width" and native_w > 0:
                    new_scale = max(0.05, value / native_w)
                    if abs(obj.transform.scale_x - new_scale) > 1e-9:
                        obj.transform.scale_x = new_scale
                        changed = True
                if prop == "height" and native_h > 0:
                    new_scale = max(0.05, value / native_h)
                    if abs(obj.transform.scale_y - new_scale) > 1e-9:
                        obj.transform.scale_y = new_scale
                        changed = True
        if changed:
            self.scene._sort_by_z_index()
            self._save_state()

    def _update_active_slider(self, mouse_x: float) -> None:
        if self._active_slider is None:
            return
        rect = self._statusbar_controls.get(self._active_slider)
        if rect is None or rect.width <= 0:
            return
        ratio = (mouse_x - rect.x) / rect.width
        ratio = max(0.0, min(1.0, ratio))
        if self._active_slider == "zoom":
            value = self.min_zoom + ratio * (self.max_zoom - self.min_zoom)
            self._set_zoom(value, Vector2(pygame.mouse.get_pos()))
            return
        if self._active_slider == "grid":
            value = int(round(self.min_grid_size + ratio * (self.max_grid_size - self.min_grid_size)))
            self._set_grid_size(value)

    def _capture_drag_state(self) -> None:
        self._drag_object_starts = {}
        for obj in self.selected_objects:
            self._drag_object_starts[obj.id] = {
                "x": obj.transform.x,
                "y": obj.transform.y,
                "rotation": obj.transform.rotation,
                "scale_x": obj.transform.scale_x,
                "scale_y": obj.transform.scale_y,
            }

    def _set_zoom(self, new_zoom: float, mouse_pos: Optional[Vector2] = None) -> None:
        clamped = max(self.min_zoom, min(self.max_zoom, new_zoom))
        if abs(clamped - self.zoom) < 1e-6:
            return
        if mouse_pos is None:
            mouse_pos = Vector2(pygame.mouse.get_pos())
        mouse_world_before = self.screen_to_world(mouse_pos)
        self.zoom = clamped
        mouse_world_after = self.screen_to_world(mouse_pos)
        self.camera += mouse_world_before - mouse_world_after

    def _set_grid_size(self, new_size: int) -> None:
        clamped = max(self.min_grid_size, min(self.max_grid_size, int(new_size)))
        self.scene.grid_size = clamped

    def _render_windows(self) -> None:
        self.settings_window.render(
            self.screen,
            self.font,
            self.font_bold,
            self.colors,
            scene_grid_visible=self.scene.grid_visible,
            scene_snap_to_grid=self.scene.snap_to_grid,
            on_toggle_grid=self._toggle_grid_visibility,
            on_toggle_snap=self._toggle_snap,
            zoom_text=f"{self.zoom * 100:.0f}%",
            grid_text=f"{self.scene.grid_size}px",
        )

    def _toggle_grid_visibility(self) -> None:
        self.scene.grid_visible = not self.scene.grid_visible
        self._save_state()

    def _toggle_snap(self) -> None:
        self.scene.snap_to_grid = not self.scene.snap_to_grid
        self._save_state()

    def _save_scene(self, filepath: Optional[str] = None) -> None:
        """Сохранение сцены"""
        if filepath is None:
            filepath = self.filepath
        
        if filepath is None:
            filepath = self._show_save_dialog()
            if not filepath:
                return
        filepath = str(Path(filepath).expanduser())
        self._sync_scene_camera()
        try:
            self.scene.save(filepath)
        except Exception as e:
            self._set_status(f"Save failed: {e}", ttl=4.0)
            return
        self.filepath = filepath
        self.scene.name = os.path.splitext(os.path.basename(filepath))[0]
        self.modified = False
        self._set_status(f"Saved: {os.path.basename(filepath)}")

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
            self.undo_stack.clear()
            self.redo_stack.clear()
            self._save_state(mark_modified=False)
            self.modified = False
            self._set_status(f"Loaded: {os.path.basename(filepath)}")
        except Exception as e:
            self._set_status(f"Load failed: {e}", ttl=4.0)

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
                initialfile=self.scene.name,
                initialdir=os.path.dirname(self.filepath) if self.filepath else ".",
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
