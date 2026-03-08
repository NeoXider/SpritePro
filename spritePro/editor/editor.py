"""
Главный модуль редактора спрайтов
"""

import os
import importlib.util
from pathlib import Path
import pygame
from pygame.math import Vector2
from typing import Optional, List, Tuple, Dict, Callable
from enum import Enum, auto

# Файловый диалог через tkinter
TKINTER_AVAILABLE = importlib.util.find_spec("tkinter") is not None

try:
    from .path_utils import resolve_sprite_path
    from .scene import Scene, SceneObject
    from . import sprite_types as editor_sprite_types
    from . import (
        file_actions,
        object_actions,
        property_actions,
        editor_actions,
        settings_actions,
        event_actions,
        transform_actions,
        history_actions,
    )
    from .history_actions import EditorState
    from .ui.windows import SettingsWindow, WindowManager
    from .ui import theme as ui_theme
    from .ui import toolbar as ui_toolbar
    from .ui import statusbar as ui_statusbar
    from .ui import hierarchy as ui_hierarchy
    from .ui import inspector as ui_inspector
    from .ui import viewport as ui_viewport
except ImportError:
    import sys

    _root = Path(__file__).resolve().parent.parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
    from spritePro.editor.path_utils import resolve_sprite_path
    from spritePro.editor.scene import Scene, SceneObject
    from spritePro.editor import sprite_types as editor_sprite_types
    from spritePro.editor import (
        file_actions,
        object_actions,
        property_actions,
        editor_actions,
        settings_actions,
        event_actions,
        transform_actions,
        history_actions,
    )
    from spritePro.editor.history_actions import EditorState
    from spritePro.editor.ui.windows import SettingsWindow, WindowManager
    from spritePro.editor.ui import theme as ui_theme
    from spritePro.editor.ui import toolbar as ui_toolbar
    from spritePro.editor.ui import statusbar as ui_statusbar
    from spritePro.editor.ui import hierarchy as ui_hierarchy
    from spritePro.editor.ui import inspector as ui_inspector
    from spritePro.editor.ui import viewport as ui_viewport


class ToolType(Enum):
    SELECT = auto()
    MOVE = auto()
    ROTATE = auto()
    SCALE = auto()

class SpriteEditor:
    """Главный класс редактора спрайтов"""

    def __init__(self, size: Tuple[int, int] = (1280, 720)):
        pygame.init()
        self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)
        pygame.display.set_caption("Sprite Editor")

        self.width, self.height = size
        self.clock = pygame.time.Clock()
        self.running = True
        self.TKINTER_AVAILABLE = TKINTER_AVAILABLE

        self.editor_settings = settings_actions.normalize_settings({})
        self.colors = dict(ui_theme.COLORS)

        # Сцена
        self.scene = Scene(name="New Scene")
        self.scene.grid_size = 10
        self.filepath: Optional[str] = None
        self.modified = False

        # Папка с ассетами -_relative to project root
        editor_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(editor_dir))
        self.project_root = project_root
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
        self.hierarchy_previews_enabled = True
        self.viewport_tool_badge_enabled = True
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
        self._toolbar_buttons: Dict[str, Dict[str, object]] = {}
        self._toolbar_menu = None
        self._inspector_actions: List[Tuple[pygame.Rect, Callable[[], None]]] = []
        self._statusbar_controls: Dict[str, pygame.Rect] = {}
        self._active_slider: Optional[str] = None
        self._active_text_input: Optional[str] = None
        self._active_text_input_type: str = "text"
        self._active_text_input_min: Optional[float] = None
        self._active_text_input_max: Optional[float] = None
        self._text_input_buffers: Dict[str, str] = {"zoom_input": "", "grid_input": ""}
        self._property_input_rects: Dict[str, pygame.Rect] = {}

        self.hierarchy_scroll = 0
        self._hierarchy_visible_capacity = 0
        self.camera_selected = False
        self._last_hierarchy_click_time = 0.0
        self._last_hierarchy_click_obj = None
        self._hierarchy_context_menu = None

        # Окна/страницы
        self.window_manager = WindowManager()
        self.settings_window = SettingsWindow(
            pygame.Rect(self.width // 2 - 260, self.height // 2 - 220, 520, 440)
        )
        self.window_manager.register(self.settings_window)

        settings_actions.load_into_editor(self)

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
        editor_actions.copy_scene_camera_to_game(self)

    def _frame_selection(self) -> None:
        editor_actions.frame_selection(self)

    def _set_status(self, message: str, ttl: float = 2.0) -> None:
        editor_actions.set_status(self, message, ttl)

    def _resolve_run_script_path(self) -> Optional[Path]:
        return editor_actions.resolve_run_script_path(self)

    def _run_project(self) -> None:
        editor_actions.run_project(self)

    def _save_state(self, mark_modified: bool = True) -> None:
        history_actions.save_state(self, mark_modified)

    def undo(self) -> None:
        history_actions.undo(self)

    def redo(self) -> None:
        history_actions.redo(self)

    def _restore_state(self, state: EditorState) -> None:
        history_actions.restore_state(self, state)

    def add_sprite(self, sprite_path: str, world_pos: Optional[Vector2] = None) -> SceneObject:
        """Добавляет новый спрайт на сцену (изображение)."""
        return object_actions.add_sprite(self, sprite_path, world_pos)

    def add_primitive(self, shape: str, world_pos: Optional[Vector2] = None) -> SceneObject:
        """Добавляет примитив (Rectangle, Circle, Ellipse) на сцену."""
        return object_actions.add_primitive(self, shape, world_pos)

    def add_text(self, text: str = "New Text", world_pos: Optional[Vector2] = None) -> SceneObject:
        """Добавляет текстовый объект на сцену."""
        return object_actions.add_text(self, text, world_pos)

    def delete_selected(self) -> None:
        """Удаляет выделенные объекты"""
        object_actions.delete_selected(self)

    def copy_selected(self) -> List[SceneObject]:
        """Копирует выделенные объекты"""
        return object_actions.copy_selected(self)

    def _get_clone_base_name(self, name: str) -> str:
        return object_actions.get_clone_base_name(name)

    def _make_next_clone_name(self, base_name: str, used_names: set[str]) -> str:
        return object_actions.make_next_clone_name(base_name, used_names)

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
            if not obj.active:
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
        if shape == editor_sprite_types.SHAPE_TEXT:
            cd = getattr(obj, "custom_data", None) or {}
            text = str(cd.get("text") or "New Text")
            font_size = max(8, int(cd.get("font_size") or 28))
            color = getattr(obj, "sprite_color", (255, 255, 255))
            return editor_sprite_types.render_text_surface(text, font_size, color)
        if not obj.sprite_path:
            return None

        resolved_path = resolve_sprite_path(
            obj.sprite_path,
            scene_path=self.filepath,
            project_root=self.project_root,
            assets_folder=self.assets_folder,
        )
        cache_key = str(resolved_path) if resolved_path is not None else obj.sprite_path

        if cache_key in self.image_cache:
            return self.image_cache[cache_key]

        if resolved_path is not None:
            try:
                img = pygame.image.load(str(resolved_path)).convert_alpha()
                self.image_cache[cache_key] = img
                return img
            except Exception:
                pass

        cd = getattr(obj, "custom_data", None) or {}
        w = max(1, int(cd.get("width") or cd.get("w") or 64))
        h = max(1, int(cd.get("height") or cd.get("h") or 64))
        fallback = editor_sprite_types.render_primitive_surface(
            editor_sprite_types.SHAPE_RECTANGLE, w, h, (255, 255, 255)
        )
        return fallback

    def _snap_to_grid(self, value: float) -> float:
        return transform_actions.snap_to_grid(self, value)

    def handle_events(self) -> None:
        event_actions.handle_events(self)

    def _handle_keydown(self, event: pygame.event.Event) -> None:
        event_actions.handle_keydown(self, event)

    def _handle_mousedown(self, event: pygame.event.Event) -> None:
        event_actions.handle_mousedown(self, event)

    def _new_scene(self) -> None:
        editor_actions.new_scene(self)

    def _add_sprite_dialog(self) -> None:
        editor_actions.add_sprite_dialog(self)

    def _browse_sprite_path_for_selected(self) -> None:
        editor_actions.browse_sprite_path_for_selected(self)

    def _handle_mouseup(self, event: pygame.event.Event) -> None:
        event_actions.handle_mouseup(self, event)

    def _handle_mousewheel(self, event: pygame.event.Event) -> None:
        event_actions.handle_mousewheel(self, event)

    def _handle_dropfile(self, event: pygame.event.Event) -> None:
        event_actions.handle_dropfile(self, event)

    def update(self) -> None:
        transform_actions.update(self)

    def _update_move(self) -> None:
        transform_actions.update_move(self)

    def _update_rotate(self) -> None:
        transform_actions.update_rotate(self)

    def _update_scale(self) -> None:
        transform_actions.update_scale(self)

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
        ui_toolbar.render_overlay(self)

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
        property_actions.adjust_selected_property(self, prop, delta)

    def _toggle_selected_property(self, prop: str) -> None:
        property_actions.toggle_selected_property(self, prop)

    def _cycle_inspector_dropdown(self, prop: str) -> None:
        property_actions.cycle_inspector_dropdown(self, prop)

    def _click_in_status_input(self, pos: tuple[int, int]) -> bool:
        return property_actions.click_in_status_input(self, pos)

    def _click_in_property_input(self, pos: tuple[int, int]) -> bool:
        return property_actions.click_in_property_input(self, pos)

    def _click_in_any_text_input(self, pos: tuple[int, int]) -> bool:
        return property_actions.click_in_any_text_input(self, pos)

    def _activate_text_input(
        self,
        name: str,
        initial_value: str = "",
        input_type: str = "text",
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
    ) -> None:
        property_actions.activate_text_input(self, name, initial_value, input_type, min_val, max_val)

    def _deactivate_text_input(self, apply: bool) -> None:
        property_actions.deactivate_text_input(self, apply)

    def _apply_text_input_value(self, name: str) -> None:
        property_actions.apply_text_input_value(self, name)

    def _set_selected_property_value(self, prop: str, value: float) -> None:
        property_actions.set_selected_property_value(self, prop, value)

    def _update_active_slider(self, mouse_x: float) -> None:
        transform_actions.update_active_slider(self, mouse_x)

    def _capture_drag_state(self) -> None:
        transform_actions.capture_drag_state(self)

    def _set_zoom(self, new_zoom: float, mouse_pos: Optional[Vector2] = None) -> None:
        transform_actions.set_zoom(self, new_zoom, mouse_pos)

    def _set_grid_size(self, new_size: int) -> None:
        transform_actions.set_grid_size(self, new_size)

    def _render_windows(self) -> None:
        editor_actions.render_windows(self)

    def _toggle_grid_visibility(self) -> None:
        editor_actions.toggle_grid_visibility(self)

    def _toggle_grid_labels(self) -> None:
        editor_actions.toggle_grid_labels(self)

    def _toggle_snap(self) -> None:
        editor_actions.toggle_snap(self)

    def _save_scene(self, filepath: Optional[str] = None) -> None:
        """Сохранение сцены"""
        file_actions.save_scene(self, filepath)

    def _save_editor_settings(self) -> None:
        settings_actions.save_now(self)

    def _reload_editor_settings(self) -> None:
        settings_actions.reload_from_disk(self)

    def _reset_editor_settings(self) -> None:
        settings_actions.reset_to_defaults(self)

    def _export_editor_settings(self) -> None:
        settings_actions.export_settings(self)

    def _import_editor_settings(self) -> None:
        settings_actions.import_settings(self)

    def _toggle_scene_setting(self, key: str) -> None:
        settings_actions.toggle_scene_setting(self, key)

    def _adjust_scene_setting(self, key: str, delta: int) -> None:
        settings_actions.adjust_scene_setting(self, key, delta)

    def _toggle_view_setting(self, key: str) -> None:
        settings_actions.toggle_view_setting(self, key)

    def _adjust_view_setting(self, key: str, delta: int) -> None:
        settings_actions.adjust_view_setting(self, key, delta)

    def _adjust_theme_setting(self, key: str, delta: int) -> None:
        settings_actions.adjust_theme_setting(self, key, delta)

    def _adjust_theme_color(self, color_key: str, channel: int, delta: int) -> None:
        settings_actions.adjust_theme_color(self, color_key, channel, delta)

    def _save_scene_as(self) -> None:
        """Сохраняет сцену в новый файл JSON."""
        file_actions.save_scene_as(self)

    def _last_scene_config_path(self) -> Path:
        """Путь к файлу, в котором хранится путь к последней сцене"""
        return file_actions.last_scene_config_path()

    def _get_last_scene_path(self) -> Optional[str]:
        """Прочитать путь к последней сцене; если файл есть и существует — вернуть его"""
        return file_actions.get_last_scene_path()

    def _save_last_scene_path(self, filepath: str) -> None:
        """Сохранить путь к сцене для следующего запуска"""
        file_actions.save_last_scene_path(filepath)

    def _load_scene(self, filepath: Optional[str] = None) -> None:
        """Загрузка сцены"""
        file_actions.load_scene(self, filepath)

    def _show_save_dialog(self) -> Optional[str]:
        """Показать диалог сохранения"""
        return file_actions.show_save_dialog(self)

    def _show_open_dialog(self) -> Optional[str]:
        """Показать диалог открытия"""
        return file_actions.show_open_dialog(self)

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
