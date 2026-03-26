# Ready Sprites (Готовые спрайты)

Модуль `readySprites` предоставляет готовые к использованию компоненты.

## Лобби мультиплеера

Готовый экран настройки мультиплеера: имя, выбор «Хост»/«Клиент», порт и IP, подключение, список игроков (roster), кнопки «В игру» и «Готов».

**Использование:**

```python
s.run(
    multiplayer=True,
    multiplayer_entry=your_multiplayer_main,
    multiplayer_use_lobby=True,
)
```

**Ручное использование:**

```python
from spritePro.readyScenes import MultiplayerLobbyScene, ChatScene, ChatStyle

s.scene.add_scene("lobby", MultiplayerLobbyScene())
s.scene.set_scene_by_name("lobby", recreate=True)
```

## ChatScene

Мультиплеерный чат: история сообщений, поле имени, ввод текста, скролл, время в сообщениях.

```python
from spritePro.readyScenes import ChatScene, ChatStyle

chat = ChatScene()
chat.init_chat_scene(
    s.multiplayer_ctx,
    name="Игрок",
    style=ChatStyle()
)
s.scene.add_scene("chat", chat)
```

## Связанное

- [Networking](../systems/networking_guide.md) — сетевое взаимодействие
- [UI](../ui/) — UI компоненты
