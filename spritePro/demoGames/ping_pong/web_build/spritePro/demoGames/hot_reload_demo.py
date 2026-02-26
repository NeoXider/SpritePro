"""Demo: Hot Reload — перезагрузка текстур при изменении файлов на диске."""
from pathlib import Path
import pygame
import spritePro as sp
from spritePro.asset_watcher import get_hot_reload_manager


def run_demo():
    sp.get_screen((800, 600), "Hot Reload Demo")
    sp.enable_debug()

    assets_dir = Path(__file__).resolve().parent / "demo_assets" / "images"
    assets_dir.mkdir(parents=True, exist_ok=True)

    image_path_holder = [None]
    for ext in (".png", ".jpg", ".jpeg", ".bmp", ".gif"):
        for p in assets_dir.glob(f"*{ext}"):
            image_path_holder[0] = str(p)
            break
        if image_path_holder[0]:
            break

    sprite = sp.Sprite(image_path_holder[0] or "", pos=(400, 300), size=(120, 120))
    if not image_path_holder[0]:
        sprite.set_rect_shape(size=(120, 120), color=(80, 120, 200))
        sp.debug_log_info("[Hot Reload] Put an image in demo_assets/images to see reload")
    else:
        sp.debug_log_info(f"[Hot Reload] Watching: {assets_dir}")

    hint = sp.TextSprite(
        "Edit/save an image in demo_assets/images — texture will reload automatically",
        color=(200, 200, 200),
        pos=(400, 450),
    )
    hint.set_position((400, 450), anchor="center")

    manager = get_hot_reload_manager()

    def refresh_sprite():
        if not image_path_holder[0]:
            for ext in (".png", ".jpg", ".jpeg", ".bmp", ".gif"):
                for p in assets_dir.glob(f"*{ext}"):
                    image_path_holder[0] = str(p)
                    break
                if image_path_holder[0]:
                    break
        if image_path_holder[0]:
            sprite.set_image(image_path_holder[0], sprite.size_vector)
            sp.debug_log_info("[Hot Reload] Texture refreshed")

    def on_reload():
        manager.watcher.reload_textures()
        refresh_sprite()

    manager.watcher.watch(
        str(assets_dir),
        extensions=[".png", ".jpg", ".jpeg", ".bmp", ".gif"],
        on_reload=on_reload,
    )
    manager.start()

    while True:
        sp.update(fill_color=(25, 25, 35))
        for event in sp.pygame_events:
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
        sprite.update()


if __name__ == "__main__":
    run_demo()
