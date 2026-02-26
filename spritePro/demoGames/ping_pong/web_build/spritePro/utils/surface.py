"""Утилиты для работы с поверхностями pygame.

Этот модуль предоставляет функции для обработки и модификации поверхностей pygame,
такие как скругление углов и применение масок.
"""

import pygame


def round_corners(surface: pygame.Surface, radius: int = 10) -> pygame.Surface:
    """Возвращает новый Surface с тем же изображением, но со скруглёнными углами.

    Создает копию исходной поверхности с применением маски для скругления углов.
    Прозрачные области сохраняются благодаря использованию альфа-канала.

    Args:
        surface (pygame.Surface): Исходное изображение.
        radius (int, optional): Радиус скругления углов в пикселях. По умолчанию 10.

    Returns:
        pygame.Surface: Новое изображение со скруглёнными углами.
    """
    size = surface.get_size()
    # Создаём маску с альфа-каналом
    mask = pygame.Surface(size, pygame.SRCALPHA)
    # Рисуем скруглённый прямоугольник на маске (белый, полностью непрозрачный)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)

    return set_mask(surface, mask)


def set_mask(surface: pygame.Surface, mask: pygame.Surface) -> pygame.Surface:
    """Применяет маску к исходному изображению.

    Создает новую поверхность с применением маски к исходному изображению.
    Маска должна иметь альфа-канал для корректной работы. Используется
    режим смешивания BLEND_RGBA_MULT для применения маски.

    Args:
        surface (pygame.Surface): Исходное изображение.
        mask (pygame.Surface): Маска с альфа-каналом для применения.

    Returns:
        pygame.Surface: Новое изображение с примененной маской.
    """
    size = surface.get_size()

    # Копируем картинку на маску с учетом альфа-канала
    rounded = pygame.Surface(size, pygame.SRCALPHA)
    rounded.blit(surface, (0, 0))
    rounded.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    return rounded
