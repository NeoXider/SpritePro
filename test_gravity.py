import spritePro as s

class GameScene(s.Scene):
    def __init__(self):
        super().__init__()
        
        # Мир
        w = s.get_physics_world()
        w.set_gravity(100) # медленно падают по умолчанию

        # Спрайт 1: дефолт (100)
        self.s1 = s.Sprite("", (40, 40), (200, 100))
        self.s1.set_color((255, 0, 0))
        s.add_physics(self.s1)

        # Спрайт 2: кастомная гравитация 2000 (очень быстро падает)
        self.s2 = s.Sprite("", (40, 40), (400, 100))
        self.s2.set_color((0, 255, 0))
        cfg = s.PhysicsConfig(gravity=2000)
        s.add_physics(self.s2, cfg)
        
        # Спрайт 3: отрицательная гравитация -500 (летит вверх)
        self.s3 = s.Sprite("", (40, 40), (600, 300))
        self.s3.set_color((0, 0, 255))
        cfg3 = s.PhysicsConfig(gravity=-500)
        s.add_physics(self.s3, cfg3)

    def update(self):
        # Если вылетели за экран, вернем
        for sprite in (self.s1, self.s2, self.s3):
            if sprite.rect.centery > 800:
                s.get_physics(sprite).position = (sprite.rect.centerx, 100)
                s.get_physics(sprite).velocity = s.Vector2(0, 0)
            if sprite.rect.centery < -100:
                s.get_physics(sprite).position = (sprite.rect.centerx, 500)
                s.get_physics(sprite).velocity = s.Vector2(0, 0)

if __name__ == "__main__":
    s.run(scene=GameScene, size=(800, 600))
