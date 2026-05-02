# Документация SpritePro

Все статьи лежат в этой папке. Пути в ссылках ниже указаны **относительно `docs/`** (удобно при просмотре на GitHub внутри `docs/`).

## С чего начать

| Документ | Описание |
|----------|----------|
| [GETTING_STARTED.md](GETTING_STARTED.md) | Установка, первая сцена, CLI `--create`, частые вопросы |
| [API_REFERENCE.md](API_REFERENCE.md) | Справочник по классам и функциям |
| [BEST_PRACTICES.md](BEST_PRACTICES.md) | Рекомендации по коду и архитектуре |

Полный оглавление по всем файлам и демо — в корне репозитория: [DOCUMENTATION_INDEX.md](../DOCUMENTATION_INDEX.md).

## Карта разделов

| Папка | Тема |
|-------|------|
| [core/](core/) | Спрайты, анимации, твины, физика, камера, частицы, ресурсы, билдер |
| [ui/](ui/) | Кнопки, текст, слайдеры, лейаут, маски, скролл в UI |
| [systems/](systems/) | Игровой цикл, ввод, события, таймеры, здоровье, сеть |
| [utils/](utils/) | Сохранения, аудио, отладка, поверхности, эффекты |
| [editor/](editor/) | Sprite Editor, типовые проблемы физики в редакторе |
| [builds/](builds/) | Web, Kivy, mobile, сборки |
| [demo_games/](demo_games/) | Каталог демо и готовые сцены |
| [cli_tools/](cli_tools/) | Плагины и CLI |

## Вне папки `docs/`

| Материал | Путь от корня репо |
|----------|-------------------|
| Обзор проекта и установка | [README.md](../README.md) |
| Участие в разработке | [CONTRIBUTING.md](../CONTRIBUTING.md) |
| Планы | [ROADMAP.md](../ROADMAP.md) |
| История версий | [CHANGELOG.md](../CHANGELOG.md) |
| Курс по мультиплееру | [multiplayer_course/README.md](../multiplayer_course/README.md) |
| Демо с `level.json` в корне | [demoGames/README.md](../demoGames/README.md) |

Соглашение: в **корневых** файлах (`README.md`, `DOCUMENTATION_INDEX.md`) ссылки на статьи ведут как `docs/...`. Внутри `docs/*.md` — относительные пути от текущего файла (`../core/sprite.md` из `docs/ui/` и т.д.).
