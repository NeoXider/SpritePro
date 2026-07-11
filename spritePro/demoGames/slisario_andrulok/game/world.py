import pygame
import spritePro as s
from .config import WORLD_WIDTH, WORLD_HEIGHT, BG_IMAGE


def _make_tiled_bg(image_path: str, area: tuple[int, int], scale: float = 0.6) -> pygame.Surface:
    tile = pygame.image.load(image_path).convert()
    tw, th = tile.get_size()
    tile = pygame.transform.scale(tile, (int(tw * scale), int(th * scale)))
    surf = pygame.Surface(area)
    tw, th = tile.get_size()
    w, h = area
    for y in range(0, h, th):
        for x in range(0, w, tw):
            surf.blit(tile, (x, y))
    return surf


class World:
    def __init__(self, scene: s.Scene):
        self.scene = scene

        bg_surf = _make_tiled_bg(str(BG_IMAGE), (WORLD_WIDTH, WORLD_HEIGHT))
        self.bg = s.Sprite(
            bg_surf, (WORLD_WIDTH, WORLD_HEIGHT), (WORLD_WIDTH // 2, WORLD_HEIGHT // 2),
            scene=scene,
        )
        self.bg.set_sorting_order(0)

        border_color = (40, 40, 60)
        border_width = 20
        walls_data = [
            ((WORLD_WIDTH // 2, 10), (WORLD_WIDTH, border_width), "wall_top"),
            ((WORLD_WIDTH // 2, WORLD_HEIGHT - 10), (WORLD_WIDTH, border_width), "wall_bottom"),
            ((10, WORLD_HEIGHT // 2), (border_width, WORLD_HEIGHT), "wall_left"),
            ((WORLD_WIDTH - 10, WORLD_HEIGHT // 2), (border_width, WORLD_HEIGHT), "wall_right"),
        ]
        self.walls: list[s.Sprite] = []
        for pos, size, _ in walls_data:
            wall = s.Sprite("", size, pos, scene=scene)
            wall.set_rect_shape(size=size, color=border_color)
            wall.set_sorting_order(2)
            self.walls.append(wall)
