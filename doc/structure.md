# System structure

## Emulator (in Python)

Lite `kb` system emulator was first written in Python before the system
implementation in Rust. It was done to prototype some elements used in `kb` to
debug and test language-specific problems out of the whole system run.

`kb.py` emulator does not contain the full system model, but only contains the
alternative and very limited implementation of the `metaL` language core.
