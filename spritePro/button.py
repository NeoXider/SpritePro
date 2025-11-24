import sys
from pathlib import Path
import pygame
from typing import Tuple, Optional, Callable, Union, List, TYPE_CHECKING

if TYPE_CHECKING:
    from spritePro.constants import Anchor


current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from spritePro.sprite import Sprite
from spritePro.components.text import TextSprite
from spritePro.components.mouse_interactor import MouseInteractor
from spritePro.constants import Anchor
import spritePro
import random


class Button(Sprite):
    """Удобная UI кнопка на основе Sprite + TextSprite + MouseInteractor.

    Объединяет функциональность спрайта с отображением текста и взаимодействием с мышью
    для создания интерактивной кнопки с анимациями при наведении и нажатии.

    Attributes:
        text_sprite (TextSprite): Спрайт текста кнопки.
        interactor (MouseInteractor): Компонент для обработки взаимодействия с мышью.
        base_color (Tuple[int, int, int]): Базовый цвет фона кнопки.
        hover_color (Tuple[int, int, int]): Цвет фона при наведении.
        press_color (Tuple[int, int, int]): Цвет фона при нажатии.
        current_color (Tuple[int, int, int]): Текущий цвет фона.
        hover_scale_delta (float): Изменение масштаба при наведении.
        press_scale_delta (float): Изменение масштаба при нажатии.
        anim_speed (float): Множитель скорости анимации.
        animated (bool): Включены ли анимации.
        use_scale_fx (bool): Включен ли эффект масштабирования.
        use_color_fx (bool): Включен ли эффект изменения цвета.
    """

    def __init__(
        self,
        sprite: str = "",
        size: Tuple[int, int] = (250, 70),
        pos: Tuple[int, int] = (300, 200),
        text: str = "Button",
        text_size: int = 24,
        text_color: Tuple[int, int, int] = (0, 0, 0),
        font_name: Optional[Union[str, Path]] = None,
        on_click: Optional[Callable[[], None]] = None,
        hover_scale_delta: float = 0.05,
        press_scale_delta: float = -0.08,
        hover_color: Tuple[int, int, int] = (230, 230, 230),
        press_color: Tuple[int, int, int] = (180, 180, 180),
        base_color: Tuple[int, int, int] = (255, 255, 255),
        anim_speed: float = 0.2,
        animated: bool = True,
        sorting_order: int = 1000,
        use_scale_fx: bool = True,
        use_color_fx: bool = True,
        anchor: Union[str, "Anchor", None] = None,
    ):
        """Инициализирует новую кнопку.

        Args:
            sprite (str, optional): Путь к изображению спрайта. По умолчанию пустая строка.
            size (Tuple[int, int], optional): Размеры кнопки (ширина, высота). По умолчанию (250, 70).
            pos (Tuple[int, int], optional): Позиция кнопки на экране. По умолчанию (300, 200).
            text (str, optional): Текст метки кнопки. По умолчанию "Button".
            text_size (int, optional): Базовый размер шрифта. По умолчанию 24.
            text_color (Tuple[int, int, int], optional): Цвет текста в RGB. По умолчанию (0, 0, 0).
            font_name (Optional[Union[str, Path]], optional): Путь к TTF шрифту или None. По умолчанию None.
            on_click (Optional[Callable[[], None]], optional): Функция обработчик клика. По умолчанию None.
            hover_scale_delta (float, optional): Изменение масштаба при наведении. По умолчанию 0.05.
            press_scale_delta (float, optional): Изменение масштаба при нажатии. По умолчанию -0.08.
            hover_color (Tuple[int, int, int], optional): Цвет фона при наведении. По умолчанию (230, 230, 230).
            press_color (Tuple[int, int, int], optional): Цвет фона при нажатии. По умолчанию (180, 180, 180).
            base_color (Tuple[int, int, int], optional): Базовый цвет фона. По умолчанию (255, 255, 255).
            anim_speed (float, optional): Множитель скорости анимации. По умолчанию 0.2.
            animated (bool, optional): Включены ли анимации. По умолчанию True.
            sorting_order (int, optional): Порядок отрисовки (слой). По умолчанию 1000.
            use_scale_fx (bool, optional): Включен ли эффект масштабирования. По умолчанию True.
            use_color_fx (bool, optional): Включен ли эффект изменения цвета. По умолчанию True.
            anchor (str | Anchor, optional): Якорь для позиционирования. По умолчанию None (используется Anchor.CENTER).
        """
        # Определяем якорь (если не передан, используем CENTER для обратной совместимости)
        if anchor is None:
            anchor = spritePro.Anchor.CENTER
        
        # Инициализируем Sprite с пустым фоном
        super().__init__(sprite, size=size, pos=pos, sorting_order=sorting_order, anchor=anchor)

        # Параметры анимации и цвета
        self.set_color(base_color)
        self.hover_color = hover_color
        self.press_color = press_color
        self.base_color = base_color
        self.current_color = base_color
        self.hover_scale_delta = hover_scale_delta
        self.press_scale_delta = press_scale_delta
        self.start_scale = self.scale
        self._target_scale = self.scale
        self.anim_speed = anim_speed
        self.animated = animated
        self.use_scale_fx = use_scale_fx
        self.use_color_fx = use_color_fx

        # Текст как отдельный спрайт
        self.text_sprite = TextSprite(
            text=text,
            font_size=text_size,
            color=text_color,
            pos=self.rect.center,
            font_name=font_name,
            # TextSprite по умолчанию уже 1000, но позволим синхронно с кнопкой
            sorting_order=sorting_order,
        )
        self.text_sprite.set_parent(self, keep_world_position=True)

        # Логика мыши
        self.interactor = MouseInteractor(sprite=self, on_click=on_click)

    def set_base_color(self, base_color: tuple = (255,255,255)):
        """Устанавливает базовый цвет кнопки.

        Args:
            base_color (tuple, optional): Кортеж из трех целых чисел, представляющий базовый цвет кнопки. По умолчанию (255, 255, 255).
        """
        self.base_color = base_color

    def set_all_colors(self, base_color: tuple, press_color: tuple, hover_color: tuple):
        """Устанавливает все три состояния цвета для кнопки.

        Args:
            base_color (tuple): Кортеж из трех целых чисел, представляющий базовый цвет кнопки.
            press_color (tuple): Кортеж из трех целых чисел, представляющий цвет кнопки при нажатии.
            hover_color (tuple): Кортеж из трех целых чисел, представляющий цвет кнопки при наведении.
        """
        self.base_color = base_color
        self.press_color = press_color
        self.hover_color = hover_color

    def set_all_scales(self, base_scale: float, hover_scale: float, press_scale: float):
        """Устанавливает базовый, ховер и пресс масштабы для кнопки.

        Args:
            base_scale (float): Базовый масштаб кнопки.
            hover_scale (float): Масштаб кнопки при наведении.
            press_scale (float): Масштаб кнопки при нажатии.
        """
        self.set_scale(base_scale, update=True)
        self.hover_scale_delta = hover_scale - base_scale
        self.press_scale_delta = press_scale - base_scale

    def update(self, screen: pygame.Surface = None):
        """Обновляет состояние кнопки и отрисовывает её на экране.

        Этот метод обрабатывает:
        - Обновление взаимодействия с мышью
        - Изменения состояния цвета и масштаба
        - Отрисовку фона, спрайта и текста

        Args:
            screen (pygame.Surface, optional): Поверхность для отрисовки. Если None, используется глобальный экран.
        """
        screen = screen or spritePro.screen

        interactor = self.interactor
        if interactor is not None:
            interactor.update()
            is_pressed = interactor.is_pressed
            is_hovered = interactor.is_hovered
        else:
            is_pressed = False
            is_hovered = False

        # Определяем цвет
        if self.use_color_fx:
            if is_pressed:
                self.current_color = self.press_color
            elif is_hovered:
                self.current_color = self.hover_color
            else:
                self.current_color = self.base_color
        else:
            self.current_color = self.base_color

        # Определяем цель масштаба
        if self.use_scale_fx:
            if is_pressed:
                self._target_scale = self.start_scale + self.press_scale_delta
            elif is_hovered:
                self._target_scale = self.start_scale + self.hover_scale_delta
            else:
                self._target_scale = self.start_scale
        else:
            self._target_scale = self.start_scale

        # Плавная анимация масштаба
        if self.animated:
            delta = (self._target_scale - self.scale) * self.anim_speed
            self.set_scale(self.scale + delta, False)
        else:
            self.set_scale(self._target_scale, False)

        # Рисуем фон (прямоугольник) и спрайт от родителя
        self.set_color(self.current_color)
        super().update(screen)

        # Обновляем и рисуем текст
        label = self.text_sprite
        if label is not None and getattr(label, 'alive', lambda: True)():
            label.rect.center = self.rect.center
            label.update(screen)

    def set_scale(self, scale: float, update: bool = True):
        """Устанавливает масштаб кнопки.

        Args:
            scale (float): Новое значение масштаба.
            update (bool, optional): Обновлять ли базовый масштаб. По умолчанию True.
        """
        if update:
            self.start_scale = scale
        super().set_scale(scale)
        # Keep label visually in sync with button scale
        if getattr(self, "text_sprite", None) is not None:
            try:
                self.text_sprite.set_scale(scale)
            except Exception:
                pass

    def on_click(self, func: Callable):
        """Устанавливает функцию обработчик клика для кнопки.

        Args:
            func (Callable): Функция, которая будет вызвана при клике на кнопку.
        """
        self.interactor.on_click = func

    def on_hover(self, func: Callable):
        """Устанавливает функцию обработчик наведения для кнопки.

        Args:
            func (Callable): Функция, которая будет вызвана при наведении на кнопку.
        """
        self.interactor.on_hover_enter = func

    def kill(self) -> None:
        """Удаляет кнопку из игры и освобождает все связанные ресурсы.
        
        Удаляет текстовый спрайт и интерактор, затем вызывает родительский метод kill().
        """
        text_sprite = getattr(self, "text_sprite", None)
        if text_sprite is not None:
            text_sprite.set_parent(None, keep_world_position=True)
            if hasattr(text_sprite, "kill"):
                text_sprite.kill()
            self.text_sprite = None
        self.interactor = None
        super().kill()



if __name__ == "__main__":
    from spritePro.utils.surface import round_corners

    def get_rundom_color() -> List[int]:
        return [random.randint(0, 255) for _ in range(3)]

    def set_rand_color() -> None:
        global color
        btn.text_sprite.set_color(get_rundom_color())
        btn.set_base_color(get_rundom_color())
        btn.press_color = get_rundom_color()
        btn.text_sprite.set_text(
            f"""=== ({
                random.choice(
                    [
                        "<_>",
                        ">_<",
                        "-_-",
                        "^_^",
                    ]
                )
            }) ==="""
        )
        color = get_rundom_color()

    pygame.init()
    screen = spritePro.get_screen((800, 600), "Button")
    color = (100, 120, 255)

    btn = Button(
        sprite="",
        pos=screen.get_rect().center,
        text="Random color",
        text_size=52,
        base_color=(255, 255, 255),
        on_click=set_rand_color,
    )
    btn.set_image(round_corners(btn.image, 30))

    while True:
        spritePro.update()

        screen.fill(color)
        btn.update(screen)
        btn.rect.x +=random.randint(-1,1)
        btn.rect.y += random.randint(-1,1)
