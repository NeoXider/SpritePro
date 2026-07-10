"""Unity-семантика активности: activeSelf ребёнка переживает выключение родителя."""

import spritePro as s


def _pair(clean_game):
    parent = s.Sprite("", (50, 50), (100, 100))
    child = s.Sprite("", (20, 20), (100, 100))
    child.set_parent(parent)
    return parent, child


class TestActiveHierarchy:
    def test_disabled_child_stays_disabled_after_parent_toggle(self, clean_game):
        parent, child = _pair(clean_game)
        child.active = False
        parent.active = False
        parent.active = True
        assert parent.active is True
        assert child.active is False

    def test_child_follows_parent_disable_enable(self, clean_game):
        parent, child = _pair(clean_game)
        parent.active = False
        assert child.active is False
        parent.active = True
        assert child.active is True

    def test_enabling_child_under_disabled_parent_defers(self, clean_game):
        parent, child = _pair(clean_game)
        parent.active = False
        child.active = True
        assert child.active is False, "эффективная активность ждёт включения родителя"
        parent.active = True
        assert child.active is True

    def test_deep_hierarchy(self, clean_game):
        a = s.Sprite("", (50, 50), (0, 0))
        b = s.Sprite("", (30, 30), (0, 0))
        c = s.Sprite("", (10, 10), (0, 0))
        b.set_parent(a)
        c.set_parent(b)
        c.active = False
        a.active = False
        a.active = True
        assert b.active is True
        assert c.active is False
