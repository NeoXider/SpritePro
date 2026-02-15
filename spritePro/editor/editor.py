"""
Главный модуль редактора спрайтов
"""

import os
import importlib.util
import re
import time
from pathlib import Path
import pygame
from pygame.math import Vector2
from typing import Optional, List, Tuple, Dict, Callable
from dataclasses import dataclass
from enum import Enum, auto

# Файловый диалог через tkinter
TKINTER_AVAILABLE = importlib.util.find_spec("tkinter") is not None

try:
    from .scene import Scene, SceneObject, Camera
    from . import sprite_types as editor_sprite_types
    from .ui.windows import SettingsWindow, WindowManager
    from .ui import theme as ui_theme
    from .ui import toolbar as ui_toolbar
    from .ui import statusbar as ui_statusbar
    from .ui import hierarchy as ui_hierarchy
    from .ui import inspector as ui_inspector
    from .ui import viewport as ui_viewport
    from .ui import input_handling as ui_input
except ImportError:
    import sys
    _root = Path(__file__).resolve().parent.parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
    from spritePro.editor.scene import Scene, SceneObject, Camera
    from spritePro.editor import sprite_types as editor_sprite_types
    from spritePro.editor.ui.windows import SettingsWindow, WindowManager
    from spritePro.editor.ui import theme as ui_theme
    from spritePro.editor.ui import toolbar as ui_toolbar
    from spritePro.editor.ui import statusbar as ui_statusbar
    from spritePro.editor.ui import hierarchy as ui_hierarchy
    from spritePro.editor.ui import inspector as ui_inspector
    from spritePro.editor.ui import viewport as ui_viewport
    from spritePro.editor.ui import input_handling as ui_input


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
    grid_labels_visible: bool
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
        
        self.colors = dict(ui_theme.COLORS)
        
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
        self.min_zoom = ui_theme.EDITOR_MIN_ZOOM
        self.max_zoom = ui_theme.EDITOR_MAX_ZOOM
        self.min_grid_size = ui_theme.EDITOR_MIN_GRID_SIZE
        self.max_grid_size = ui_theme.EDITOR_MAX_GRID_SIZE
        self.camera_preview_enabled = True
        self.camera_preview_size = Vector2(800, 600)
        self._camera_preview_copy_rect: Optional[pygame.Rect] = None
        
        # Инструменты
        self.current_tool = ToolType.SELECT
        self.selected_objects: List[SceneObject] = []
        
        self.ui_left_width = ui_theme.UI_LEFT_WIDTH
        self.ui_right_width = ui_theme.UI_RIGHT_WIDTH
        self.ui_top_height = ui_theme.UI_TOP_HEIGHT
        self.ui_bottom_height = ui_theme.UI_BOTTOM_HEIGHT
        self._toolbar_tools_list = [
            (ToolType.SELECT, "V", "Select"),
            (ToolType.MOVE, "G", "Move"),
            (ToolType.ROTATE, "R", "Rotate"),
            (ToolType.SCALE, "T", "Scale"),
        ]
        
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

        self.hierarchy_scroll = 0
        self._hierarchy_visible_capacity = 0
        self.camera_selected = False
        self._last_hierarchy_click_time = 0.0
        self._last_hierarchy_click_obj = None

        # Окна/страницы
        self.window_manager = WindowManager()
        self.settings_window = SettingsWindow(
            pygame.Rect(self.width // 2 - 190, self.height // 2 - 140, 380, 280)
        )
        self.window_manager.register(self.settings_window)

        # Строка состояния
        self.status_message = "Ready"
        self.status_message_timer = 2.0

        # Восстановление последней сцены
        last_path = self._get_last_scene_path()
        if last_path:
            try:
                self._load_scene(last_path)
            except Exception:
                pass

        # Запуск
        self._save_state(mark_modified=False)

    def _get_viewport_rect(self) -> pygame.Rect:
        return ui_viewport.get_viewport_rect(self)

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
        """Синхронизирует параметры камеры редактора в модель сцены (scene_*)."""
        self.scene.camera.scene_x = self.camera.x
        self.scene.camera.scene_y = self.camera.y
        self.scene.camera.scene_zoom = self.zoom

    def _copy_scene_camera_to_game(self) -> None:
        """Копирует текущие параметры камеры сцены в параметры камеры игры."""
        self._sync_scene_camera()
        self.scene.camera.game_x = self.scene.camera.scene_x
        self.scene.camera.game_y = self.scene.camera.scene_y
        self.scene.camera.game_zoom = self.scene.camera.scene_zoom
        self._save_state()
        self._set_status("Game camera set from scene")

    def _frame_selection(self) -> None:
        """Перемещает камеру к выбранному объекту (F или двойной клик по иерархии)."""
        if self.camera_selected or not self.selected_objects:
            return
        viewport = self._get_viewport_rect()
        if not viewport.width or not viewport.height:
            return
        objs = self.selected_objects
        if len(objs) == 1:
            self.camera.x = objs[0].transform.x
            self.camera.y = objs[0].transform.y
        else:
            min_x = min(o.transform.x for o in objs)
            max_x = max(o.transform.x for o in objs)
            min_y = min(o.transform.y for o in objs)
            max_y = max(o.transform.y for o in objs)
            cx = (min_x + max_x) / 2
            cy = (min_y + max_y) / 2
            w = max(max_x - min_x, 50)
            h = max(max_y - min_y, 50)
            zoom_x = (viewport.width * 0.85) / w if w > 0 else self.zoom
            zoom_y = (viewport.height * 0.85) / h if h > 0 else self.zoom
            new_zoom = min(zoom_x, zoom_y, self.max_zoom)
            new_zoom = max(new_zoom, self.min_zoom)
            self.zoom = new_zoom
            self.camera.x = cx
            self.camera.y = cy
        self._sync_scene_camera()
        self._save_state()
        self._set_status("Framed selection")

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
            grid_labels_visible=self.scene.grid_labels_visible,
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
        self.scene.grid_labels_visible = state.grid_labels_visible
        self.scene.snap_to_grid = state.snap_to_grid
        self.selected_objects.clear()

    def add_sprite(self, sprite_path: str, world_pos: Optional[Vector2] = None) -> SceneObject:
        """Добавляет новый спрайт на сцену (изображение)."""
        full_path = os.path.abspath(sprite_path) if os.path.exists(sprite_path) else sprite_path
        obj = SceneObject(
            name=os.path.splitext(os.path.basename(sprite_path))[0],
            sprite_path=full_path,
            sprite_shape=editor_sprite_types.SHAPE_IMAGE,
        )
        if world_pos is not None:
            obj.transform.x = world_pos.x
            obj.transform.y = world_pos.y
        if self.scene.objects:
            obj.z_index = max(o.z_index for o in self.scene.objects) + 1
        self.scene.add_object(obj)
        self._save_state()
        return obj

    def add_primitive(self, shape: str, world_pos: Optional[Vector2] = None) -> SceneObject:
        """Добавляет примитив (Rectangle, Circle, Ellipse) на сцену."""
        label = editor_sprite_types.SHAPE_LABELS.get(shape, shape)
        obj = SceneObject(
            name=label,
            sprite_path="",
            sprite_shape=shape,
            sprite_color=(200, 200, 200),
            custom_data={"width": 100, "height": 100},
        )
        if world_pos is not None:
            obj.transform.x = world_pos.x
            obj.transform.y = world_pos.y
        else:
            obj.transform.x = 400
            obj.transform.y = 300
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
        self.camera_selected = False
        if not add_to_selection:
            self.selected_objects.clear()
        if obj and obj not in self.selected_objects:
            self.selected_objects.append(obj)

    def deselect_all(self) -> None:
        """Снимает выделение со всех объектов"""
        self.selected_objects.clear()
        self.camera_selected = False

    def get_object_at(self, world_pos: Vector2) -> Optional[SceneObject]:
        """Получает объект по мировым координатам (проверка сверху вниз)"""
        for obj in reversed(self.scene.objects):
            if not obj.visible:
                continue
            display_w, display_h = self._get_object_display_size(obj)
            if display_w <= 0 or display_h <= 0:
                continue
            x = obj.transform.x - display_w / 2
            y = obj.transform.y - display_h / 2
            if x <= world_pos.x <= x + display_w and y <= world_pos.y <= y + display_h:
                return obj
        return None

    def _get_sprite_image(self, obj: SceneObject) -> Optional[pygame.Surface]:
        """Получает изображение спрайта: для примитивов — рендер по shape/color/size, иначе из файла."""
        shape = getattr(obj, "sprite_shape", "image")
        if editor_sprite_types.is_primitive(shape):
            w, h = self._get_object_native_size(obj)
            color = getattr(obj, "sprite_color", (255, 255, 255))
            return editor_sprite_types.render_primitive_surface(shape, w, h, color)
        if not obj.sprite_path:
            return None
        
        # Проверяем кэш
        if obj.sprite_path in self.image_cache:
            return self.image_cache[obj.sprite_path]
        
        editor_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(editor_dir))
        scene_dir = os.path.dirname(self.filepath) if self.filepath else None

        search_paths = [
            obj.sprite_path,
            os.path.abspath(obj.sprite_path),
        ]
        if scene_dir:
            search_paths.append(os.path.join(scene_dir, obj.sprite_path))
            search_paths.append(os.path.join(scene_dir, os.path.basename(obj.sprite_path)))
        search_paths.extend([
            os.path.join(self.assets_folder, obj.sprite_path),
            os.path.join(self.assets_folder, "images", obj.sprite_path),
            os.path.join(editor_dir, "assets", obj.sprite_path),
            os.path.join(editor_dir, "assets", "images", obj.sprite_path),
            os.path.join(project_root, "assets", obj.sprite_path),
            os.path.join(project_root, "assets", "images", obj.sprite_path),
            os.path.join("assets", obj.sprite_path),
            os.path.join("assets", "images", obj.sprite_path),
            os.path.join(os.getcwd(), obj.sprite_path),
        ])
        
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
                ui_input.handle_text_input_text(self, event)
            
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
        if ui_input.handle_text_input_keydown(self, event):
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

        # F — фокус камеры на выбранном объекте
        elif event.key == pygame.K_f:
            self._frame_selection()
        
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
            
            if ui_statusbar.handle_click(self, self.mouse_pos):
                return
            
            if self.mouse_pos.y <= self.ui_top_height:
                if ui_toolbar.handle_click(self, self.mouse_pos):
                    return
            
            if self.mouse_pos.x >= self.width - self.ui_right_width:
                if ui_inspector.handle_click(self, self.mouse_pos):
                    return
            
            if self.mouse_pos.x <= self.ui_left_width:
                obj = ui_hierarchy.handle_click(self, self.mouse_pos)
                if obj is not None:
                    now = time.time()
                    is_double = (
                        obj == self._last_hierarchy_click_obj
                        and (now - self._last_hierarchy_click_time) < ui_theme.DOUBLE_CLICK_INTERVAL
                    )
                    self._last_hierarchy_click_time = now
                    self._last_hierarchy_click_obj = obj
                    if is_double and obj != "__camera__":
                        self._frame_selection()
                        return
                    if obj == "__camera__":
                        self.camera_selected = True
                        self.selected_objects.clear()
                    else:
                        keys = pygame.key.get_pressed()
                        self.select_object(obj, add_to_selection=keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])
                    return
            
            # Проверяем клик по объекту в viewport
            viewport = self._get_viewport_rect()
            if viewport.collidepoint(self.mouse_pos):
                if self._camera_preview_copy_rect and self._camera_preview_copy_rect.collidepoint(self.mouse_pos.x, self.mouse_pos.y):
                    self._copy_scene_camera_to_game()
                    return
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

    def _browse_sprite_path_for_selected(self) -> None:
        """Открыть диалог выбора изображения и установить sprite_path выбранному объекту (тип Image)."""
        if not self.selected_objects:
            return
        obj = self.selected_objects[0]
        if getattr(obj, "sprite_shape", "image") != "image":
            return
        if not TKINTER_AVAILABLE:
            return
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            filepath = filedialog.askopenfilename(
                title="Выберите изображение для спрайта",
                filetypes=[
                    ("Images", "*.png *.jpg *.jpeg *.bmp *.gif"),
                    ("All files", "*.*"),
                ],
                initialdir=self.assets_folder,
            )
            root.destroy()
            if filepath:
                obj.sprite_path = filepath
                self._save_state()
        except Exception:
            pass

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
        mouse_pos = Vector2(pygame.mouse.get_pos())
        if ui_hierarchy.handle_wheel(self, event.y):
            return
        viewport_rect = self._get_viewport_rect()
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
        """Обновление масштаба (или width/height у примитивов) при перетаскивании"""
        dx = (self.mouse_world_pos.x - self.drag_start.x) / 100.0
        dy = (self.mouse_world_pos.y - self.drag_start.y) / 100.0
        keys = pygame.key.get_pressed()
        uniform = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        pixel_delta = 80.0
        if uniform:
            delta = (dx + dy) * 0.5 * pixel_delta
            dw = dh = delta
        else:
            dw = dx * pixel_delta
            dh = dy * pixel_delta

        for obj in self.selected_objects:
            if obj.locked:
                continue
            start = self._drag_object_starts.get(obj.id)
            if start is None:
                continue
            if editor_sprite_types.is_primitive(getattr(obj, "sprite_shape", "image")):
                new_w = max(4, start["width"] + dw)
                new_h = max(4, start["height"] + dh)
                if abs(new_w - obj.custom_data.get("width", 100)) > 1e-6 or abs(new_h - obj.custom_data.get("height", 100)) > 1e-6:
                    self._transform_changed_during_drag = True
                obj.custom_data["width"] = int(round(new_w))
                obj.custom_data["height"] = int(round(new_h))
            else:
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
        ui_viewport.render(self)

    def _render_ui(self) -> None:
        ui_toolbar.render(self)
        ui_hierarchy.render(self)
        ui_inspector.render(self)
        ui_statusbar.render(self)

    def _get_object_native_size(self, obj: SceneObject) -> Tuple[int, int]:
        if editor_sprite_types.is_primitive(getattr(obj, "sprite_shape", "image")):
            w = obj.custom_data.get("width", 100)
            h = obj.custom_data.get("height", 100)
            return (max(1, int(w)), max(1, int(h)))
        sprite = self._get_sprite_image(obj)
        if sprite is None:
            return (0, 0)
        return sprite.get_width(), sprite.get_height()

    def _get_object_display_size(self, obj: SceneObject) -> Tuple[float, float]:
        if editor_sprite_types.is_primitive(getattr(obj, "sprite_shape", "image")):
            return self._get_object_native_size(obj)
        native_w, native_h = self._get_object_native_size(obj)
        return native_w * obj.transform.scale_x, native_h * obj.transform.scale_y

    def _adjust_selected_property(self, prop: str, delta: float) -> None:
        if self.camera_selected:
            cam = self.scene.camera
            if prop == "scene_x":
                cam.scene_x += delta
                self.camera.x = cam.scene_x
            elif prop == "scene_y":
                cam.scene_y += delta
                self.camera.y = cam.scene_y
            elif prop == "scene_zoom_pct":
                cam.scene_zoom = max(self.min_zoom, min(self.max_zoom, cam.scene_zoom + delta / 100))
                self.zoom = cam.scene_zoom
            elif prop == "game_x":
                cam.game_x += delta
            elif prop == "game_y":
                cam.game_y += delta
            elif prop == "game_zoom_pct":
                cam.game_zoom = max(self.min_zoom, min(self.max_zoom, cam.game_zoom + delta / 100))
            else:
                return
            self._save_state()
            return
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
                if editor_sprite_types.is_primitive(getattr(obj, "sprite_shape", "image")):
                    w = obj.custom_data.get("width", 100) + (delta if prop == "width" else 0)
                    h = obj.custom_data.get("height", 100) + (delta if prop == "height" else 0)
                    obj.custom_data["width"] = max(1, int(w))
                    obj.custom_data["height"] = max(1, int(h))
                    changed = True
                else:
                    native_w, native_h = self._get_object_native_size(obj)
                    if prop == "width" and native_w > 0:
                        current_w = native_w * obj.transform.scale_x
                        obj.transform.scale_x = max(0.05, (current_w + delta) / native_w)
                        changed = True
                    if prop == "height" and native_h > 0:
                        current_h = native_h * obj.transform.scale_y
                        obj.transform.scale_y = max(0.05, (current_h + delta) / native_h)
                        changed = True
            elif prop == "color_r":
                c = getattr(obj, "sprite_color", (255, 255, 255))
                obj.sprite_color = (max(0, min(255, int(c[0] + delta))), c[1], c[2])
                changed = True
            elif prop == "color_g":
                c = getattr(obj, "sprite_color", (255, 255, 255))
                obj.sprite_color = (c[0], max(0, min(255, int(c[1] + delta))), c[2])
                changed = True
            elif prop == "color_b":
                c = getattr(obj, "sprite_color", (255, 255, 255))
                obj.sprite_color = (c[0], c[1], max(0, min(255, int(c[2] + delta))))
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
        elif prop == "screen_space":
            new_value = not self.selected_objects[0].screen_space
            for obj in self.selected_objects:
                obj.screen_space = new_value
                changed = True
        if changed:
            self._save_state()

    def _cycle_inspector_dropdown(self, prop: str) -> None:
        if prop != "sprite_shape" or not self.selected_objects:
            return
        for obj in self.selected_objects:
            if getattr(obj, "locked", False):
                continue
            current = getattr(obj, "sprite_shape", "image")
            obj.sprite_shape = editor_sprite_types.next_shape(current)
            if editor_sprite_types.is_primitive(obj.sprite_shape):
                if "width" not in obj.custom_data:
                    obj.custom_data["width"] = 100
                if "height" not in obj.custom_data:
                    obj.custom_data["height"] = 100
        self._save_state()

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

    def _apply_text_input_value(self, name: str) -> None:
        if name == "prop_input_name":
            raw = self._text_input_buffers.get(name, "").strip()
            if self.selected_objects:
                self.selected_objects[0].name = raw or "New Object"
                self._save_state()
            return
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
        if self.camera_selected:
            cam = self.scene.camera
            if prop == "scene_x":
                cam.scene_x = value
                self.camera.x = value
            elif prop == "scene_y":
                cam.scene_y = value
                self.camera.y = value
            elif prop == "scene_zoom_pct":
                z = max(self.min_zoom, min(self.max_zoom, value / 100))
                cam.scene_zoom = z
                self.zoom = z
            elif prop == "game_x":
                cam.game_x = value
            elif prop == "game_y":
                cam.game_y = value
            elif prop == "game_zoom_pct":
                cam.game_zoom = max(self.min_zoom, min(self.max_zoom, value / 100))
            else:
                return
            self._save_state()
            return
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
                if editor_sprite_types.is_primitive(getattr(obj, "sprite_shape", "image")):
                    v = max(1, int(value))
                    if prop == "width" and obj.custom_data.get("width") != v:
                        obj.custom_data["width"] = v
                        changed = True
                    if prop == "height" and obj.custom_data.get("height") != v:
                        obj.custom_data["height"] = v
                        changed = True
                else:
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
            elif prop == "color_r":
                c = getattr(obj, "sprite_color", (255, 255, 255))
                v = max(0, min(255, int(round(value))))
                if c[0] != v:
                    obj.sprite_color = (v, c[1], c[2])
                    changed = True
            elif prop == "color_g":
                c = getattr(obj, "sprite_color", (255, 255, 255))
                v = max(0, min(255, int(round(value))))
                if c[1] != v:
                    obj.sprite_color = (c[0], v, c[2])
                    changed = True
            elif prop == "color_b":
                c = getattr(obj, "sprite_color", (255, 255, 255))
                v = max(0, min(255, int(round(value))))
                if c[2] != v:
                    obj.sprite_color = (c[0], c[1], v)
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
            data = {
                "x": obj.transform.x,
                "y": obj.transform.y,
                "rotation": obj.transform.rotation,
                "scale_x": obj.transform.scale_x,
                "scale_y": obj.transform.scale_y,
            }
            if editor_sprite_types.is_primitive(getattr(obj, "sprite_shape", "image")):
                data["width"] = float(obj.custom_data.get("width", 100))
                data["height"] = float(obj.custom_data.get("height", 100))
            self._drag_object_starts[obj.id] = data

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
            scene_grid_labels_visible=self.scene.grid_labels_visible,
            scene_snap_to_grid=self.scene.snap_to_grid,
            on_toggle_grid=self._toggle_grid_visibility,
            on_toggle_grid_labels=self._toggle_grid_labels,
            on_toggle_snap=self._toggle_snap,
            zoom_text=f"{self.zoom * 100:.0f}%",
            grid_text=f"{self.scene.grid_size}px",
        )

    def _toggle_grid_visibility(self) -> None:
        self.scene.grid_visible = not self.scene.grid_visible
        self._save_state()

    def _toggle_grid_labels(self) -> None:
        self.scene.grid_labels_visible = not self.scene.grid_labels_visible
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
        self._save_last_scene_path(filepath)
        self._set_status(f"Saved: {os.path.basename(filepath)}")

    def _last_scene_config_path(self) -> Path:
        """Путь к файлу, в котором хранится путь к последней сцене"""
        return Path.home() / ".spritepro_editor_last_scene.txt"

    def _get_last_scene_path(self) -> Optional[str]:
        """Прочитать путь к последней сцене; если файл есть и существует — вернуть его"""
        p = self._last_scene_config_path()
        if not p.is_file():
            return None
        try:
            path = p.read_text(encoding="utf-8").strip()
            return path if path and Path(path).is_file() else None
        except Exception:
            return None

    def _save_last_scene_path(self, filepath: str) -> None:
        """Сохранить путь к сцене для следующего запуска"""
        try:
            path = str(Path(filepath).expanduser().resolve())
            self._last_scene_config_path().write_text(path, encoding="utf-8")
        except Exception:
            pass

    def _load_scene(self, filepath: Optional[str] = None) -> None:
        """Загрузка сцены"""
        if filepath is None:
            filepath = self._show_open_dialog()
            if not filepath:
                return

        filepath = str(Path(filepath).expanduser().resolve())
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
            self._save_last_scene_path(filepath)
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
