from __future__ import annotations

import curses
from typing import Callable, List, Optional, Set

from .shaders import Shader


def run_tui(
    shaders: List[Shader],
    on_apply: Callable[[List[Shader]], None],
    initial_index: int = 0,
    initial_selected: Optional[List[int]] = None,
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
        selected_order: List[int] = []
        selected_set: Set[int] = set()

        if initial_selected:
            filtered = [idx for idx in initial_selected if 0 <= idx < len(shaders)]
            selected_order.extend(filtered)
            selected_set.update(filtered)

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
                prefix = "* " if idx in selected_set else "  "
                label = f"{prefix}{shader.relative}"
                truncated = label[: width - 1]
                if idx == highlight:
                    stdscr.attron(curses.A_REVERSE)
                    stdscr.addstr(row, 0, truncated)
                    stdscr.attroff(curses.A_REVERSE)
                else:
                    stdscr.addstr(row, 0, truncated)

            selection_hint = (
                f"selected: {len(selected_order)}" if selected_order else "no selection"
            )
            instructions = (
                "↑/↓ or j/k move • Space toggle • Enter apply • c clear • q quit | "
                f"{selection_hint}"
            )
            stdscr.addstr(height - 2, 0, instructions[: width - 1])
            stdscr.addstr(height - 1, 0, message[: width - 1])
            stdscr.refresh()

            key = stdscr.getch()
            if key in (curses.KEY_UP, ord("k")):
                highlight = max(0, highlight - 1)
            elif key in (curses.KEY_DOWN, ord("j")):
                highlight = min(len(shaders) - 1, highlight + 1)
            elif key == ord(" "):
                if highlight in selected_set:
                    selected_set.remove(highlight)
                    selected_order = [idx for idx in selected_order if idx != highlight]
                else:
                    selected_set.add(highlight)
                    selected_order.append(highlight)
            elif key in (ord("c"), ord("C")):
                selected_set.clear()
                selected_order.clear()
            elif key in (curses.KEY_ENTER, ord("\n"), ord("\r")):
                targets: List[Shader]
                if selected_order:
                    targets = [shaders[idx] for idx in selected_order]
                else:
                    targets = [shaders[highlight]]

                try:
                    on_apply(targets)
                except Exception as exc:  # pragma: no cover - surfaced via UI
                    message = f"Error: {exc}"
                else:
                    applied = ", ".join(shader.relative for shader in targets)
                    message = f"Applied {applied}"
            elif key in (ord("q"), 27):
                break

    curses.wrapper(_main)
