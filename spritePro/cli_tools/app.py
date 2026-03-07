from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .android import ANDROID_ORIENTATIONS, run_android_build
from .create_project import create_project
from .preview import SCREEN_PRESETS, run_preview


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SpritePro tools")
    parser.add_argument(
        "--create",
        metavar="PATH",
        nargs="?",
        const="main.py",
        help="Create a new project template with two scenes: --create [path]",
    )
    parser.add_argument(
        "--editor",
        "-e",
        action="store_true",
        help="Launch the Sprite Editor",
    )
    parser.add_argument(
        "--webgl",
        metavar="PATH",
        nargs="?",
        const=".",
        help="Prepare web build (Pygbag): --webgl [path to project dir or main.py]",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="DIR",
        default=None,
        help="Output directory for --webgl (default: <project>/web_build)",
    )
    parser.add_argument(
        "--archive",
        action="store_true",
        help="With --webgl: also run pygbag --build --archive and show path to ZIP (for Yandex Games, itch.io)",
    )
    parser.add_argument(
        "--preview",
        metavar="PATH",
        help="Quick preview for a project or main.py with screen/platform overrides",
    )
    parser.add_argument(
        "--screen",
        choices=sorted(SCREEN_PRESETS.keys()),
        help="Screen preset for --preview",
    )
    parser.add_argument(
        "--size",
        metavar="WIDTHxHEIGHT",
        help="Custom screen size for --preview, for example 360x640",
    )
    parser.add_argument(
        "--platform",
        choices=("pygame", "kivy"),
        default="pygame",
        help="Platform for --preview (default: pygame)",
    )
    parser.add_argument(
        "--list-screen-presets",
        action="store_true",
        help="Show available screen presets for --preview",
    )
    parser.add_argument(
        "--android",
        metavar="PATH",
        help="Generate buildozer.spec and optionally build Android package for a project or main.py",
    )
    parser.add_argument(
        "--android-mode",
        choices=("debug", "release", "aab", "spec"),
        default="debug",
        help="Android action for --android: debug/release/aab/spec (default: debug)",
    )
    parser.add_argument(
        "--android-refresh-spec",
        action="store_true",
        help="Rewrite buildozer.spec for --android using SpritePro defaults",
    )
    parser.add_argument(
        "--android-title",
        metavar="TITLE",
        default=None,
        help="App title for generated buildozer.spec",
    )
    parser.add_argument(
        "--android-package-name",
        metavar="NAME",
        default=None,
        help="Android package name, for example mygame",
    )
    parser.add_argument(
        "--android-package-domain",
        metavar="DOMAIN",
        default="org.example",
        help="Android package domain for generated buildozer.spec",
    )
    parser.add_argument(
        "--android-version",
        metavar="VERSION",
        default=None,
        help="App version for generated buildozer.spec",
    )
    parser.add_argument(
        "--android-orientation",
        choices=ANDROID_ORIENTATIONS,
        default=None,
        help="Orientation for generated buildozer.spec",
    )
    parser.add_argument(
        "--android-requirements",
        metavar="REQS",
        default=None,
        help="Override buildozer requirements, comma-separated",
    )
    parser.add_argument(
        "--android-permission",
        action="append",
        default=[],
        help="Android permission for generated buildozer.spec, repeatable",
    )
    return parser


def _configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")


def _handle_editor() -> None:
    import spritePro as s

    s.editor.launch_editor()


def _handle_webgl(args) -> None:
    from spritePro.web_build import build_web, build_web_archive

    path = Path(args.webgl).resolve()
    if path.is_file() and path.suffix == ".py":
        project_dir = path.parent
    else:
        project_dir = path
    if not project_dir.is_dir():
        sys.stderr.write(f"Ошибка: папка не найдена: {project_dir}\n")
        sys.exit(1)
    out = Path(args.output).resolve() if args.output else None
    _configure_logging()
    if args.archive:
        try:
            zip_path = build_web_archive(project_dir, output_dir=out)
            build_dir = out or (project_dir / "web_build")
            logging.info("Готово. Папка сборки: %s", build_dir)
            logging.info("Архив для загрузки (Яндекс Игры, itch.io): %s", zip_path)
        except (FileNotFoundError, RuntimeError) as exc:
            sys.stderr.write(f"Ошибка сборки архива: {exc}\n")
            sys.exit(1)
    else:
        result = build_web(project_dir, output_dir=out)
        logging.info("Готово: %s", result)
        logging.info("Запуск: python -m pygbag %s", result)


def _handle_preview(args, extra_args: list[str]) -> None:
    _configure_logging()
    try:
        exit_code = run_preview(
            Path(args.preview),
            platform=args.platform,
            preset=args.screen,
            size=args.size,
            extra_args=extra_args,
        )
    except (FileNotFoundError, ValueError) as exc:
        sys.stderr.write(f"Ошибка preview: {exc}\n")
        sys.exit(1)
    if exit_code != 0:
        sys.exit(exit_code)


def _handle_android(args) -> None:
    _configure_logging()
    try:
        exit_code = run_android_build(
            Path(args.android),
            mode=args.android_mode,
            refresh_spec=args.android_refresh_spec,
            title=args.android_title,
            package_name=args.android_package_name,
            package_domain=args.android_package_domain,
            version=args.android_version,
            orientation=args.android_orientation,
            requirements=args.android_requirements,
            permissions=args.android_permission,
        )
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        sys.stderr.write(f"Ошибка android build: {exc}\n")
        sys.exit(1)
    if exit_code != 0:
        sys.exit(exit_code)


def _handle_create(args) -> None:
    _configure_logging()
    project_root = create_project(Path(args.create))
    logging.info("Project created at: %s", project_root.resolve())


def run_cli(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args, extra_args = parser.parse_known_args(argv)

    if extra_args and not args.preview:
        parser.error(f"Неизвестные аргументы: {' '.join(extra_args)}")

    if args.list_screen_presets:
        _configure_logging()
        for name, (width, height) in SCREEN_PRESETS.items():
            logging.info("%s = %sx%s", name, width, height)
        return

    if args.editor:
        _handle_editor()
        return

    if args.webgl is not None:
        _handle_webgl(args)
        return

    if args.preview is not None:
        _handle_preview(args, extra_args)
        return

    if args.android is not None:
        _handle_android(args)
        return

    if not args.create:
        parser.print_help()
        return

    _handle_create(args)
