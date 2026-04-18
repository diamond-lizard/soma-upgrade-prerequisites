# Ruff Compliance Rules for This Project

This project uses ruff with the following rules enabled: E, F, W, I, N, UP, B, A, C4, SIM, TCH, RUF.
Line length limit is 99 characters. Target Python version is 3.10.
All modules use ```from __future__ import annotations```.

When writing Python code, follow these rules to avoid ruff violations:

## 1. TYPE_CHECKING IMPORTS (TCH rules)

Because ```from __future__ import annotations``` is active, all annotations are strings at
runtime. Any import used ONLY in type annotations (function signatures, variable annotations,
return types) must go inside ```if TYPE_CHECKING:``` blocks. Only imports used as runtime
values (constructors, isinstance, function calls, base classes) stay as regular imports.

**Procedural rule:** For EVERY import you write, immediately ask: is this name used as a
runtime value (constructor call, isinstance, function call, base class) in this file? If not,
it goes in TYPE_CHECKING. Do this check at write time, not as a later pass.

**Most common trap:** `Path` is almost always used only in annotations (e.g., `def foo(p: Path)`)
and must go in TYPE_CHECKING. Only import it at top level if you call `Path(...)` or use it as
a runtime value in that file.

Common examples:
- ```Path``` used only in ```def foo(p: Path)``` -> TYPE_CHECKING
- ```Path``` used in ```Path("/tmp")``` -> regular import
- ```subprocess``` used only in ```-> subprocess.CompletedProcess[str]``` -> TYPE_CHECKING
- Pydantic BaseModel/Field used as base class or field default -> regular import
- App imports used only in annotations -> TYPE_CHECKING (TCH001)
- Stdlib imports used only in annotations -> TYPE_CHECKING (TCH003)

## 2. IMPORT SORTING (I001)

Imports must follow isort ordering:
- ```from __future__``` first
- stdlib imports (alphabetical)
- blank line
- third-party imports (alphabetical)
- blank line
- local/app imports (alphabetical)
- blank line
- ```if TYPE_CHECKING:``` block (with its own internal ordering: stdlib then third-party then local)

Never put regular imports after ```if TYPE_CHECKING:``` blocks.

**Procedural rule:** Before adding any import to an existing file, read the full import
block first. Then determine the correct position: bare ``import`` statements come before
``from`` imports within the same group, and within each form they are alphabetical. Inside
``from X import (a, b, c)`` blocks, names must also be alphabetical. Insert at the correct
position, not at a convenient line.

## 3. LINE LENGTH (E501)

Maximum 99 characters per line.

## 4. MODERN PYTHON (UP rules)

- Import ```Generator```, ```Callable```, etc. from ```collections.abc```, not ```typing```
- Use ```X | Y``` union syntax, not ```Union[X, Y]``` or ```Optional[X]```
- Use ``from datetime import UTC`` and ``tz=UTC`` instead of ``datetime.timezone.utc``
  (UP017, Python 3.11+). Note: ``datetime.UTC`` is a module-level attribute, not accessible
  via ``from datetime import datetime`` -- import ``UTC`` directly.

## 5. BUGBEAR (B rules)

- Never use ```assert False``` -- use ```raise AssertionError()``` instead
- Don't use mutable default arguments

## 6. FLAKE8-COMPREHENSIONS (C4)

- Use ```dict.fromkeys(iterable, value)``` instead of ```{k: value for k in iterable}```
- Use list/dict/set comprehensions instead of ```list(generator)``` where appropriate

## 7. SIMPLIFY (SIM)

Prefer simplified constructs (ternary, merged conditionals, etc.)

## 8. NO UNUSED (F rules)

No unused imports (F401), no unused variables (F841), no redefined-but-unused imports (F811).

**Procedural rule:** Only import what the file uses *right now*. Do not add imports for
functions or types you plan to write later in the same file. Add each import at the moment
you write the code that uses it. When removing or moving a function from a file, immediately
check whether any of its imports are now unused and remove them.


## 9. NO LAMBDA ASSIGNMENTS (E731)

Never assign a lambda expression to a variable. Use a ``def`` statement instead.
Lambda expressions are only acceptable as inline arguments to function calls.

## 10. NO SEMICOLONS (E702)

Never combine multiple statements on one line with semicolons.
Each statement must be on its own line.

## 11. RAW REGEX STRINGS (RUF043)

When passing a regex pattern to ``match=`` (e.g., in ``pytest.raises``), always use a raw
string (``r"..."``) if the pattern contains regex metacharacters like ``.*``, ``\d``, ``[``,
etc. This makes the regex intent explicit and avoids the RUF043 warning.

## 12. PROTOCOL DEFAULTS (mypy strict)

Never use a stdlib or library function directly as a default value for a Protocol-typed
parameter, and never assign one to a Protocol-typed variable. Overloaded signatures, extra
kwargs, and different parameter names in stdlib functions commonly fail to match simpler
Protocol definitions. Instead, default to ``None`` and resolve to a new variable via a
ternary expression (which lets mypy infer the union type rather than checking assignment
compatibility with the Protocol):

```python
def make_checker(which_fn: WhichFn | None = None) -> Callable[[], bool]:
    resolved = which_fn if which_fn is not None else shutil.which
```

More generally: when a fix fails for the same root cause as the original bug, stop and
re-analyze the root cause before attempting another fix.
