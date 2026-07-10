"""Регрессионные тесты компонентов (аудит U3, U8, U9, U10, U12, U13, U18-U20)."""

import pytest

import spritePro as s
from spritePro.components.timer import Timer
from spritePro.components.health import HealthComponent
from spritePro.utils.pool import ObjectPool, PoolManager
from spritePro.utils import color_effects


class TestTimerReset:
    def test_reset_clears_elapsed_in_dt_mode(self, clean_game):
        fired = []
        t = Timer(1.0, callback=lambda: fired.append(1), auto_register=False)
        t.update(0.9)
        t.reset()
        t.update(0.9)
        assert not fired  # после reset прошло только 0.9 из 1.0
        t.update(0.2)
        assert fired

    def test_kill_unregisters(self, clean_game):
        t = Timer(1.0, auto_register=True)
        assert any(getattr(e, "obj", e) is t for e in clean_game.update_objects)
        t.kill()
        assert all(getattr(e, "obj", e) is not t for e in clean_game.update_objects)


class TestHealthBoolComparison:
    def test_eq_true_means_alive(self, clean_game):
        hp = HealthComponent(max_health=100, current_health=50)
        assert (hp == True) is True  # noqa: E712 — проверяем именно bool-ветку
        hp.take_damage(50)
        assert (hp == False) is True  # noqa: E712

    def test_eq_number_compares_hp(self, clean_game):
        hp = HealthComponent(max_health=100, current_health=50)
        assert hp == 50

    def test_hashable(self, clean_game):
        hp = HealthComponent(max_health=10)
        assert hp in {hp}


class TestPoolManager:
    def test_register_without_instance(self):
        PoolManager._instance = None  # симулируем «ещё не создавался»
        pool = ObjectPool(lambda: object())
        PoolManager.register("test_pool_audit", pool)
        assert PoolManager.get("test_pool_audit") is pool


class TestColorEffects:
    def test_temperature_equal_min_max(self):
        color = color_effects.temperature(5, min_temp=5, max_temp=5)
        assert isinstance(color, tuple)

    def test_health_bar_zero_max(self):
        color = color_effects.health_bar(0, max_health=0)
        assert isinstance(color, tuple)


class TestPages:
    def test_bad_page_name_does_not_break_state(self, clean_game):
        from spritePro.components.pages import PageManager

        pm = PageManager()
        with pytest.raises(KeyError):
            pm.set_active_page("nope")
        # get_active_page не должен бросать после неудачной установки
        pm.get_active_page()
