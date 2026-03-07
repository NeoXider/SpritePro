from __future__ import annotations

import logging
import re
import shutil
import subprocess
import sys
from pathlib import Path
from textwrap import dedent


ANDROID_ORIENTATIONS = (
    "landscape",
    "portrait",
    "landscape-reverse",
    "portrait-reverse",
    "all",
)

ANDROID_SPEC_TEMPLATE = dedent(
    """\
    [app]
    title = {title}
    package.name = {package_name}
    package.domain = {package_domain}
    source.dir = .
    source.include_exts = py,png,jpg,jpeg,gif,webp,wav,mp3,ogg,json,ttf,otf,atlas,kv,txt
    source.exclude_dirs = .git,.venv,venv,__pycache__,build,dist,.idea,.cursor,.pytest_cache,.mypy_cache
    version = {version}
    requirements = {requirements}
    orientation = {orientation}
    fullscreen = 1
    {android_permissions_block}

    [buildozer]
    log_level = 2
    warn_on_root = 1
    """
)


def android_project_root_from_target(target: Path) -> Path:
    resolved = target.resolve()
    if resolved.is_file() and resolved.suffix == ".py":
        return resolved.parent
    if resolved.is_dir():
        return resolved
    raise FileNotFoundError(f"Не удалось определить проект для Android build: {target}")


def read_text_if_exists(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def extract_first_match(text: str, pattern: str) -> str | None:
    match = re.search(pattern, text, re.MULTILINE)
    if match:
        return match.group(1)
    return None


def infer_android_title(project_root: Path) -> str:
    config_text = read_text_if_exists(project_root / "config.py")
    title = extract_first_match(config_text, r"""^TITLE\s*=\s*["'](.+?)["']\s*$""")
    if title:
        return title
    return project_root.name.replace("_", " ").strip() or "SpritePro Game"


def infer_android_version(project_root: Path) -> str:
    pyproject_text = read_text_if_exists(project_root / "pyproject.toml")
    version = extract_first_match(pyproject_text, r"""^version\s*=\s*["'](.+?)["']\s*$""")
    if version:
        return version
    return "0.1.0"


def infer_android_orientation(project_root: Path) -> str:
    config_text = read_text_if_exists(project_root / "config.py")
    size_match = re.search(
        r"""^WINDOW_SIZE\s*=\s*\((\d+)\s*,\s*(\d+)\)\s*$""", config_text, re.MULTILINE
    )
    if not size_match:
        return "all"
    width = int(size_match.group(1))
    height = int(size_match.group(2))
    return "landscape" if width >= height else "portrait"


def sanitize_android_package_name(value: str) -> str:
    sanitized = re.sub(r"[^a-z0-9]", "", value.lower())
    return sanitized or "spriteprogame"


def build_android_permissions_block(permissions: list[str]) -> str:
    if not permissions:
        return ""
    unique_permissions: list[str] = []
    for permission in permissions:
        normalized = permission.strip()
        if normalized and normalized not in unique_permissions:
            unique_permissions.append(normalized)
    if not unique_permissions:
        return ""
    return f"android.permissions = {','.join(unique_permissions)}"


def write_android_spec(
    project_root: Path,
    *,
    title: str,
    package_name: str,
    package_domain: str,
    version: str,
    orientation: str,
    requirements: str,
    permissions: list[str],
) -> Path:
    spec_path = project_root / "buildozer.spec"
    spec_path.write_text(
        ANDROID_SPEC_TEMPLATE.format(
            title=title,
            package_name=package_name,
            package_domain=package_domain,
            version=version,
            orientation=orientation,
            requirements=requirements,
            android_permissions_block=build_android_permissions_block(permissions),
        ),
        encoding="utf-8",
    )
    return spec_path


def run_android_build(
    target: Path,
    *,
    mode: str,
    refresh_spec: bool,
    title: str | None,
    package_name: str | None,
    package_domain: str,
    version: str | None,
    orientation: str | None,
    requirements: str | None,
    permissions: list[str],
) -> int:
    project_root = android_project_root_from_target(target)
    main_file = project_root / "main.py"
    if not main_file.is_file():
        raise FileNotFoundError(f"В проекте не найден main.py: {project_root}")

    resolved_title = title or infer_android_title(project_root)
    resolved_package_name = sanitize_android_package_name(package_name or project_root.name)
    resolved_version = version or infer_android_version(project_root)
    resolved_orientation = orientation or infer_android_orientation(project_root)
    resolved_requirements = requirements or "python3,kivy,pygame,pymunk,spritepro"

    spec_path = project_root / "buildozer.spec"
    if refresh_spec or not spec_path.exists():
        spec_path = write_android_spec(
            project_root,
            title=resolved_title,
            package_name=resolved_package_name,
            package_domain=package_domain,
            version=resolved_version,
            orientation=resolved_orientation,
            requirements=resolved_requirements,
            permissions=permissions,
        )
        logging.info("Buildozer spec ready: %s", spec_path)
    else:
        logging.info("Using existing buildozer.spec: %s", spec_path)

    if mode == "spec":
        logging.info(
            "Spec generated only. Next step: run inside Linux/WSL -> buildozer android debug"
        )
        return 0

    if not sys.platform.startswith("linux"):
        raise RuntimeError(
            "Автосборка APK через Buildozer запускается только в Linux/WSL. "
            "Spec уже готов, продолжайте сборку там."
        )

    buildozer_exe = shutil.which("buildozer")
    if buildozer_exe is None:
        raise RuntimeError("Buildozer не найден в PATH. Установите его: pip install buildozer")

    if mode == "debug":
        command = [buildozer_exe, "android", "debug"]
    elif mode == "release":
        command = [buildozer_exe, "android", "release"]
    elif mode == "aab":
        command = [buildozer_exe, "android", "release", "aab"]
    else:
        raise ValueError(f"Неизвестный android mode: {mode}")

    logging.info("Android project: %s", project_root)
    logging.info("Title: %s", resolved_title)
    logging.info("Package: %s.%s", package_domain, resolved_package_name)
    logging.info("Version: %s", resolved_version)
    logging.info("Orientation: %s", resolved_orientation)
    logging.info("Requirements: %s", resolved_requirements)
    if permissions:
        logging.info("Permissions: %s", ", ".join(permissions))
    logging.info("Run: %s", " ".join(command))

    completed = subprocess.run(command, cwd=project_root)
    return completed.returncode
