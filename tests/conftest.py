"""Общие фикстуры: headless-инициализация SpritePro (dummy SDL)."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pytest

import spritePro as s


@pytest.fixture(scope="session")
def game():
    """Инициализированный игровой контекст с dummy-экраном 320x240."""
    s.init()
    s.get_screen((320, 240), "tests")
    return s.get_game()


@pytest.fixture()
def clean_game(game):
    """Контекст с очищенными спрайтами и update-объектами перед тестом."""
    game.all_sprites.empty()
    game.update_objects.clear()
    game._update_object_ids.clear()
    yield game
    game.all_sprites.empty()
    game.update_objects.clear()
    game._update_object_ids.clear()
