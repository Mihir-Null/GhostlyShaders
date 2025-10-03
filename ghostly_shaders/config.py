from __future__ import annotations

from pathlib import Path
from typing import Optional

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "ghostty" / "config"
DEFAULT_SHADER_PATH = Path.home() / ".config" / "ghostty" / "shaders" / "shader.glsl"


def read_custom_shader_path(config_path: Path = DEFAULT_CONFIG_PATH) -> Optional[Path]:
    """Return the value of the ``custom-shader`` directive if present."""
    if not config_path.exists():
        return None

    for raw_line in config_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.split("=", 1)[0].strip() != "custom-shader":
            continue
        _, value = raw_line.split("=", 1)
        return Path(value.strip())

    return None


def update_custom_shader_path(
    shader_path: Path,
    config_path: Path = DEFAULT_CONFIG_PATH,
) -> None:
    """Insert or update the ``custom-shader`` directive in the Ghostty config."""
    shader_path = shader_path.expanduser().resolve()
    config_lines = []
    if config_path.exists():
        config_lines = config_path.read_text(encoding="utf-8").splitlines()

    directive = f"custom-shader = {shader_path}"
    replaced = False
    for idx, line in enumerate(config_lines):
        if line.strip().startswith("custom-shader"):
            config_lines[idx] = directive
            replaced = True
            break

    if not replaced:
        config_lines.append(directive)

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text("\n".join(config_lines) + "\n", encoding="utf-8")
