import pygame


def round_corners(surface: pygame.Surface, radius: int = 10) -> pygame.Surface:
    """Возвращает новый Surface с тем же изображением, но со скруглёнными углами.

    Args:
        surface (pygame.Surface): Исходное изображение.
        radius (int, optional): Радиус угла. Defaults to 10.

    Returns:
        pygame.Surface: Изображение скруглёнными углами.
    """
    size = surface.get_size()
    # Создаём маску с альфа-каналом
    mask = pygame.Surface(size, pygame.SRCALPHA)
    # Рисуем скруглённый прямоугольник на маске (белый, полностью непрозрачный)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)

    return set_mask(surface, mask)


def set_mask(surface: pygame.Surface, mask: pygame.Surface) -> pygame.Surface:
    """
    Применяем маску к исходному изображению.

    Args:
        surface (pygame.Surface): Исходное изображение
        mask (pygame.Surface): Маска

    Returns:
        pygame.Surface: Изображение с применением маски
    """
    size = surface.get_size()

    # Копируем картинку на маску с учетом альфа-канала
    rounded = pygame.Surface(size, pygame.SRCALPHA)
    rounded.blit(surface, (0, 0))
    rounded.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    return rounded
