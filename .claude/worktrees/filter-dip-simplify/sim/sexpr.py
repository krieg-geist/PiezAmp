"""Minimal S-expression parser/serializer for KiCad files."""

from __future__ import annotations


class Sym(str):
    """Bare (unquoted) atom."""
    __slots__ = ()


def parse(text: str):
    """Parse S-expression text into nested lists of Sym/str/int/float."""
    i, n = 0, len(text)

    def skip_ws():
        nonlocal i
        while i < n and text[i] in " \t\r\n":
            i += 1

    def parse_expr():
        nonlocal i
        skip_ws()
        if i >= n:
            raise ValueError("unexpected EOF")
        c = text[i]
        if c == "(":
            i += 1
            out = []
            while True:
                skip_ws()
                if i >= n:
                    raise ValueError("unclosed list")
                if text[i] == ")":
                    i += 1
                    return out
                out.append(parse_expr())
        if c == '"':
            i += 1
            buf = []
            while i < n:
                ch = text[i]
                if ch == "\\" and i + 1 < n:
                    nxt = text[i + 1]
                    if nxt == "n":
                        buf.append("\n")
                    elif nxt == "t":
                        buf.append("\t")
                    elif nxt in ('"', "\\"):
                        buf.append(nxt)
                    else:
                        buf.append("\\")
                        buf.append(nxt)
                    i += 2
                    continue
                if ch == '"':
                    i += 1
                    return "".join(buf)
                buf.append(ch)
                i += 1
            raise ValueError("unclosed string")
        # bare atom
        j = i
        while i < n and text[i] not in ' \t\r\n()"':
            i += 1
        return Sym(text[j:i])

    expr = parse_expr()
    skip_ws()
    return expr


def _atom_str(a) -> str:
    if isinstance(a, Sym):
        return str(a)
    if isinstance(a, str):
        s = a.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        return f'"{s}"'
    if isinstance(a, float):
        # match KiCad's trimmed float style
        s = f"{a:.6f}".rstrip("0").rstrip(".")
        return s if s not in ("-0", "") else "0"
    return str(a)


def dumps(expr, indent: int = 0) -> str:
    """Serialize with KiCad-style tab indentation."""
    if not isinstance(expr, list):
        return _atom_str(expr)
    # short lists with no sublists stay on one line
    if not any(isinstance(e, list) for e in expr):
        return "(" + " ".join(_atom_str(e) for e in expr) + ")"
    tab = "\t" * (indent + 1)
    parts = []
    head = []
    idx = 0
    # leading atoms stay on the opening line
    while idx < len(expr) and not isinstance(expr[idx], list):
        head.append(_atom_str(expr[idx]))
        idx += 1
    open_line = "(" + " ".join(head)
    for e in expr[idx:]:
        parts.append(tab + dumps(e, indent + 1))
    return open_line + "\n" + "\n".join(parts) + "\n" + "\t" * indent + ")"


def find(expr, name: str):
    """First child list whose head is `name`."""
    for e in expr:
        if isinstance(e, list) and e and e[0] == name:
            return e
    return None


def find_all(expr, name: str):
    return [e for e in expr if isinstance(e, list) and e and e[0] == name]
