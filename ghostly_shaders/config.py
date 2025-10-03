from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "ghostty" / "config"
DEFAULT_SHADER_PATH = Path.home() / ".config" / "ghostty" / "shaders" / "shader.glsl"


def read_custom_shader_paths(config_path: Path = DEFAULT_CONFIG_PATH) -> List[Path]:
    """Return every ``custom-shader`` directive value in order of appearance."""
    if not config_path.exists():
        return []

    found: List[Path] = []
    for raw_line in config_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.split("=", 1)[0].strip() != "custom-shader":
            continue
        _, value = raw_line.split("=", 1)
        found.append(Path(value.strip()).expanduser())

    return found


def read_custom_shader_path(config_path: Path = DEFAULT_CONFIG_PATH) -> Optional[Path]:
    """Return the first ``custom-shader`` directive if present."""

    paths = read_custom_shader_paths(config_path=config_path)
    return paths[0] if paths else None


def update_custom_shader_paths(
    shader_paths: Iterable[Path],
    config_path: Path = DEFAULT_CONFIG_PATH,
) -> None:
    """Insert or update ``custom-shader`` directives in the Ghostty config."""

    normalized_paths = [Path(path).expanduser().resolve() for path in shader_paths]
    config_lines = []
    if config_path.exists():
        config_lines = config_path.read_text(encoding="utf-8").splitlines()

    filtered = [line for line in config_lines if line.strip().split("=", 1)[0].strip() != "custom-shader"]

    directives = [f"custom-shader = {path}" for path in normalized_paths]
    if directives:
        filtered.extend(directives)

    config_path.parent.mkdir(parents=True, exist_ok=True)
    if filtered:
        config_path.write_text("\n".join(filtered) + "\n", encoding="utf-8")
    else:
        config_path.write_text("", encoding="utf-8")


def update_custom_shader_path(
    shader_path: Path,
    config_path: Path = DEFAULT_CONFIG_PATH,
) -> None:
    """Insert or update a single ``custom-shader`` directive in the Ghostty config."""

    update_custom_shader_paths([shader_path], config_path=config_path)
