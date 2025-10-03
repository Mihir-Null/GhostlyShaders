from __future__ import annotations

import argparse
import hashlib
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from .config import (
    DEFAULT_CONFIG_PATH,
    DEFAULT_SHADER_PATH,
    read_custom_shader_paths,
    update_custom_shader_paths,
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


def _slugify(value: str) -> str:
    slug = re.sub(r"[^0-9A-Za-z]+", "-", value).strip("-").lower()
    return slug[:48] or "shader"


def _destination_paths(destination: Path, shaders: Sequence[Shader]) -> List[Path]:
    if not shaders:
        return []

    expanded = destination.expanduser()
    if expanded.exists() and expanded.is_dir():
        base_dir = expanded.resolve()
        base_suffix = ".glsl"
        base_path = base_dir / f"shader{base_suffix}"
        base_stem = "shader"
    else:
        resolved = expanded.resolve()
        if expanded.exists() and expanded.is_file():
            base_path = resolved
            base_suffix = resolved.suffix or ".glsl"
            base_stem = base_path.stem
            base_dir = base_path.parent
        elif resolved.suffix:
            base_path = resolved
            base_suffix = resolved.suffix
            base_stem = resolved.stem
            base_dir = base_path.parent
        else:
            base_dir = resolved
            base_suffix = ".glsl"
            base_path = base_dir / f"shader{base_suffix}"
            base_stem = "shader"

    base_dir.mkdir(parents=True, exist_ok=True)

    destinations: List[Path] = []
    for index, shader in enumerate(shaders):
        if index == 0:
            destinations.append(base_path)
            continue

        slug = _slugify(shader.relative)
        filename = f"{base_stem}__{index + 1:02d}_{slug}{base_suffix}"
        destinations.append(base_dir / filename)

    return destinations


def _cleanup_generated(base_path: Path, desired: Sequence[Path]) -> None:
    if not desired:
        return

    base_dir = base_path.parent
    base_suffix = base_path.suffix or ".glsl"
    prefix = f"{base_path.stem}__"
    for existing in base_dir.glob(f"{prefix}*{base_suffix}"):
        if existing not in desired and existing.is_file():
            existing.unlink(missing_ok=True)


def _apply_shaders(
    shaders: Sequence[Shader],
    destination: Path,
    update_config: bool,
    config_path: Path,
) -> None:
    if not shaders:
        return

    destinations = _destination_paths(destination, shaders)
    if not destinations:
        return

    base_path = destinations[0]
    _cleanup_generated(base_path, destinations)

    for shader, target in zip(shaders, destinations):
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(shader.path, target)

    if update_config:
        update_custom_shader_paths(destinations, config_path=config_path)


def _digest_index_map(shaders: Sequence[Shader]) -> Dict[str, int]:
    mapping: Dict[str, int] = {}
    for idx, shader in enumerate(shaders):
        digest = _file_digest(shader.path)
        if digest is not None and digest not in mapping:
            mapping[digest] = idx
    return mapping


def _determine_initial_state(
    shaders: List[Shader],
    configured_paths: Sequence[Path],
) -> Tuple[int, List[int]]:
    digest_map = _digest_index_map(shaders)
    selected: List[int] = []

    for path in configured_paths:
        digest = _file_digest(path)
        if digest is None:
            continue
        idx = digest_map.get(digest)
        if idx is None or idx in selected:
            continue
        selected.append(idx)

    highlight = selected[0] if selected else 0
    return highlight, selected


def main() -> None:
    args = _parse_args()
    config_path = args.config.expanduser()
    shaders = discover_shaders(args.repo)

    configured_shaders = read_custom_shader_paths(config_path=config_path)
    if args.shader_output is not None:
        target_shader_path = args.shader_output
    elif configured_shaders:
        target_shader_path = configured_shaders[0]
    else:
        target_shader_path = DEFAULT_SHADER_PATH

    target_shader_path = target_shader_path.expanduser()
    highlight_index, preselected = _determine_initial_state(
        shaders, configured_shaders
    )
    highlight_index = max(0, min(highlight_index, len(shaders) - 1)) if shaders else 0

    def on_apply(selection: List[Shader]) -> None:
        _apply_shaders(selection, target_shader_path, not args.no_config, config_path)

    run_tui(shaders, on_apply, highlight_index, preselected)


if __name__ == "__main__":
    main()
