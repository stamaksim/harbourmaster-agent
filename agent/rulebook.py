"""Parse RULEBOOK.md into a {section_id: text} dict.

Structural parser only — no game-rule content (suit names, values, numbers)
is hardcoded here. If RULEBOOK.md is replaced with a revised version, this
file should not need to change.
"""

import re
from pathlib import Path

RULEBOOK_PATH = Path(__file__).resolve().parent.parent / "RULEBOOK.md"

# A section marker is "§N" or "§N.M" at the start of a line, optionally
# preceded by a markdown heading prefix (e.g. "## §1 Components").
SECTION_RE = re.compile(r"^(?:#{1,6}\s+)?§(\d+(?:\.\d+)?)(.*)$")


def _is_heading(line: str) -> bool:
    return line.lstrip().startswith("#")


def _finalize(lines: list[str]) -> str:
    return "\n".join(lines).strip()


def parse_rulebook(text: str) -> dict[str, str]:
    """Parse rulebook markdown text into {"§N" or "§N.M": text}."""
    lines = text.splitlines()
    sections: dict[str, str] = {}
    current_id = None
    current_lines: list[str] = []
    current_title_len = 0  # lines belonging to the marker line itself (0 or 1)

    def _store(section_id: str, section_lines: list[str], title_len: int) -> None:
        if "." not in section_id:
            body_lines = section_lines[title_len:]
            if not any(l.strip() for l in body_lines):
                return  # bare container heading with no body content of its own
        sections[section_id] = _finalize(section_lines)

    i = 0
    while i < len(lines):
        line = lines[i]
        match = SECTION_RE.match(line)
        if match:
            if current_id is not None:
                _store(current_id, current_lines, current_title_len)
            current_id = "§" + match.group(1)
            rest = match.group(2).strip()
            current_lines = [rest] if rest else []
            current_title_len = len(current_lines)
            i += 1
            continue

        if current_id is not None:
            is_blank = line.strip() == ""
            next_line = lines[i + 1] if i + 1 < len(lines) else ""
            if is_blank and _is_heading(next_line) and not SECTION_RE.match(next_line):
                _store(current_id, current_lines, current_title_len)
                current_id = None
                current_lines = []
                i += 1
                continue
            current_lines.append(line)

        i += 1

    if current_id is not None:
        _store(current_id, current_lines, current_title_len)

    return sections


def load_rulebook(path: Path = RULEBOOK_PATH) -> dict[str, str]:
    return parse_rulebook(path.read_text())


if __name__ == "__main__":
    sections = load_rulebook()
    print(f"{len(sections)} sections found")
    for section_id in ("§5.1", "§7.1"):
        print(f"\n{section_id}:")
        print(sections.get(section_id, "<not found>"))
