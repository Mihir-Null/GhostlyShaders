from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class Shader:
    """Metadata describing a shader file sourced from the upstream repo."""

    name: str
    path: Path
    relative: str

    @property
    def display_name(self) -> str:
        return self.name


def discover_shaders(repo_path: Path) -> List[Shader]:
    repo_path = repo_path.expanduser().resolve()
    if not repo_path.exists():
        raise FileNotFoundError(f"Shader repository not found: {repo_path}")

    shader_paths: Iterable[Path] = repo_path.rglob("*.glsl")
    shaders: List[Shader] = []
    for path in shader_paths:
        if path.is_dir():
            continue
        relative = path.relative_to(repo_path)
        shaders.append(
            Shader(
                name=relative.stem.replace("_", " "),
                path=path,
                relative=str(relative),
            )
        )

    shaders.sort(key=lambda shader: shader.relative.lower())
    return shaders
