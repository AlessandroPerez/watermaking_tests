"""Registry of all codes in the suite (k = 512 message bits each)."""

from __future__ import annotations

import importlib

from .base import Code, DecodeResult, HardInput, simulate_awgn  # noqa: F401

MODULES = ("simple", "bch", "rs", "conv", "ldpc", "polar", "turbo", "concat")


def all_codes(k: int = 512, modules: tuple[str, ...] = MODULES) -> list[Code]:
    out: list[Code] = []
    for m in modules:
        out.extend(importlib.import_module(f"{__name__}.{m}").codes(k))
    names = [c.name for c in out]
    dup = {n for n in names if names.count(n) > 1}
    assert not dup, f"duplicate code names: {dup}"
    return out


def get_codes(names: list[str] | None = None, k: int = 512,
              modules: tuple[str, ...] = MODULES) -> list[Code]:
    codes = all_codes(k, modules)
    if names is None:
        return codes
    by = {c.name: c for c in codes}
    missing = [n for n in names if n not in by]
    if missing:
        raise KeyError(f"unknown codes {missing}; available: {sorted(by)}")
    return [by[n] for n in names]
