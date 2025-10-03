# Ghostly Shaders

This repository vendors the [hackr-sh/ghostty-shaders](https://github.com/hackr-sh/ghostty-shaders)
collection and adds a small curses-based TUI for browsing the shaders and
activating one for your local Ghostty installation.

## Layout

- `ghostty_shaders_repo/` – cloned upstream shader collection.
- `ghostly_shaders/` – Python package that exposes the TUI.

## Usage

A quick way to try the tool without installing anything globally is to run:

```sh
python -m ghostly_shaders
```

You can also install the package locally:

```sh
pip install .
# then
ghostly-shaders
```

### Controls

- `↑/↓` or `j/k` to navigate the shader list
- `Enter` to copy the highlighted shader to your Ghostty config
- `q` (or `Esc`) to exit the TUI

### What happens when you apply a shader?

1. The source `.glsl` file is copied to
   `~/.config/ghostty/shaders/shader.glsl` (customisable via
   `--shader-output`).
2. Unless you pass `--no-config`, the tool ensures the Ghostty config file
   (default `~/.config/ghostty/config`) contains
   `custom-shader = ~/.config/ghostty/shaders/shader.glsl`.

Pass `--help` for more CLI options, such as pointing at a different shaders
checkout via `--repo`.

## Updating the shaders

The shaders are stored as a plain git checkout under
`ghostty_shaders_repo/`. To sync with upstream you can run:

```sh
git -C ghostty_shaders_repo pull
```

## License

The TUI helper is released under the MIT license. Shaders retain their
respective upstream licensing.
