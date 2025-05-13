# diagnostics.py
from dataclasses import dataclass

@dataclass
class SemanticError:
    kind: str          # p.ej. "TypeError", "UndeclaredVar", …
    msg: str           # mensaje legible para el usuario
    line: int | None   = None
    col: int  | None   = None

    def __str__(self):
        loc = f"[L{self.line},C{self.col}] " if self.line is not None else ""
        return f"❌ {loc}{self.kind}: {self.msg}"
