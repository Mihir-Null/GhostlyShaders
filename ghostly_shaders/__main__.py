from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path
from typing import List, Optional

from .config import (
    DEFAULT_CONFIG_PATH,
    DEFAULT_SHADER_PATH,
    read_custom_shader_path,
    update_custom_shader_path,
)
from .shaders import Shader, discover_shaders
from .tui import run_tui


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pick and activate a Ghostty shader from a local repository.",
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path("ghostty_shaders_repo"),
        help="Path to the cloned ghostty-shaders repository.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Ghostty configuration file to update.",
    )
    parser.add_argument(
        "--shader-output",
        type=Path,
        default=None,
        help=(
            "Location where the selected shader will be copied. "
            "Defaults to the path referenced by the Ghostty config or "
            f"{DEFAULT_SHADER_PATH}."
        ),
    )
    parser.add_argument(
        "--no-config",
        action="store_true",
        help="Skip updating the Ghostty config file.",
    )
    return parser.parse_args()


def _file_digest(path: Path) -> Optional[str]:
    if not path.exists() or not path.is_file():
        return None

    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _apply_shader(shader: Shader, destination: Path, update_config: bool, config_path: Path) -> None:
    destination = destination.expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(shader.path, destination)

    if update_config:
        update_custom_shader_path(destination, config_path=config_path)


def _find_selected_index(shaders: List[Shader], current_digest: Optional[str]) -> int:
    if current_digest is None:
        return 0

    for idx, shader in enumerate(shaders):
        if _file_digest(shader.path) == current_digest:
            return idx
    return 0


def main() -> None:
    args = _parse_args()
    config_path = args.config.expanduser()
    shaders = discover_shaders(args.repo)

    configured_shader = read_custom_shader_path(config_path=config_path)
    if args.shader_output is not None:
        target_shader_path = args.shader_output
    elif configured_shader is not None:
        target_shader_path = configured_shader
    else:
        target_shader_path = DEFAULT_SHADER_PATH

    target_shader_path = target_shader_path.expanduser()
    current_digest = _file_digest(target_shader_path)
    selected_index = _find_selected_index(shaders, current_digest)

    def on_apply(shader: Shader) -> None:
        _apply_shader(shader, target_shader_path, not args.no_config, config_path)

    run_tui(shaders, on_apply, selected_index)


if __name__ == "__main__":
    main()
