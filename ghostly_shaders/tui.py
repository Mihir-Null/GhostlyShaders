from __future__ import annotations

import curses
from typing import Callable, List

from .shaders import Shader


def run_tui(
    shaders: List[Shader],
    on_apply: Callable[[Shader], None],
    initial_index: int = 0,
) -> None:
    if not shaders:
        raise ValueError("No shaders available to display")

    initial_index = max(0, min(initial_index, len(shaders) - 1))

    def _main(stdscr: "curses._CursesWindow") -> None:
        curses.curs_set(0)
        stdscr.nodelay(False)
        stdscr.keypad(True)
        highlight = initial_index
        top = 0
        message = ""

        while True:
            stdscr.erase()
            height, width = stdscr.getmaxyx()
            list_height = max(1, height - 2)

            if highlight < top:
                top = highlight
            elif highlight >= top + list_height:
                top = highlight - list_height + 1

            for row, idx in enumerate(range(top, min(len(shaders), top + list_height))):
                shader = shaders[idx]
                label = shader.relative
                truncated = label[: width - 1]
                if idx == highlight:
                    stdscr.attron(curses.A_REVERSE)
                    stdscr.addstr(row, 0, truncated)
                    stdscr.attroff(curses.A_REVERSE)
                else:
                    stdscr.addstr(row, 0, truncated)

            instructions = "↑/↓ or j/k to move • Enter to apply • q to quit"
            stdscr.addstr(height - 2, 0, instructions[: width - 1])
            stdscr.addstr(height - 1, 0, message[: width - 1])
            stdscr.refresh()

            key = stdscr.getch()
            if key in (curses.KEY_UP, ord("k")):
                highlight = max(0, highlight - 1)
            elif key in (curses.KEY_DOWN, ord("j")):
                highlight = min(len(shaders) - 1, highlight + 1)
            elif key in (curses.KEY_ENTER, ord("\n"), ord("\r")):
                try:
                    on_apply(shaders[highlight])
                except Exception as exc:  # pragma: no cover - surfaced via UI
                    message = f"Error: {exc}"
                else:
                    message = f"Applied {shaders[highlight].relative}"
            elif key in (ord("q"), 27):
                break

    curses.wrapper(_main)
