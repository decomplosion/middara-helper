"""Strict, non-mutating validation for Middara game text."""

from __future__ import annotations

import re
from typing import Any, Mapping

DEFAULT_COMBAT_TOKENS = ("MELEE", "RANGED")


def _location_at(text: str, offset: int) -> tuple[int, int]:
    """Return 1-based line and column for a character offset."""
    line = text.count("\n", 0, offset) + 1
    previous_newline = text.rfind("\n", 0, offset)
    column = offset + 1 if previous_newline == -1 else offset - previous_newline
    return line, column


def _make_error(
    text: str, offset: int, token: str, code: str, message: str
) -> dict[str, Any]:
    line, column = _location_at(text, offset)
    lines = text.splitlines() or [""]
    context = lines[line - 1].strip() if line <= len(lines) else ""
    return {
        "code": code,
        "token": token,
        "message": message,
        "line": line,
        "column": column,
        "context": context,
    }


def _levenshtein_distance(left: str, right: str) -> int:
    """Compute edit distance using O(min(len(left), len(right))) memory."""
    if len(left) < len(right):
        left, right = right, left
    previous = list(range(len(right) + 1))
    for i, left_char in enumerate(left, 1):
        current = [i]
        for j, right_char in enumerate(right, 1):
            current.append(min(
                current[-1] + 1,
                previous[j] + 1,
                previous[j - 1] + (left_char != right_char),
            ))
        previous = current
    return previous[-1]


def validate_game_text(
    text: str, *, combat_tokens: tuple[str, ...] | list[str] | None = None
) -> dict[str, Any]:
    """Validate one string and return a validity flag and error list.

    The source is never rewritten. Configure combat_tokens with the project's
    known stance/action vocabulary to enable exact checks and typo suggestions.
    """
    if not isinstance(text, str):
        raise TypeError("validate_game_text expects a string")

    tokens = tuple(token.upper() for token in (
        DEFAULT_COMBAT_TOKENS if combat_tokens is None else combat_tokens
    ))
    errors: list[dict[str, Any]] = []

    # Recognized tokens must appear exactly as [TOKEN], uppercase.
    for token in tokens:
        pattern = re.compile(r"\[?\b" + re.escape(token) + r"\b\]?", re.IGNORECASE)
        for match in pattern.finditer(text):
            if match.group(0) != f"[{token}]":
                errors.append(_make_error(
                    text,
                    match.start(),
                    match.group(0),
                    "MALFORMED_COMBAT_TOKEN",
                    f"Combat token must be exactly [{token}] (uppercase and enclosed in square brackets).",
                ))

    # Detect likely one-edit misspellings when written in bracket-token form.
    bracket_pattern = re.compile(r"\[([A-Za-z]+)\]?|\b([A-Za-z]+)\]")
    for match in bracket_pattern.finditer(text):
        candidate = (match.group(1) or match.group(2) or "").upper()
        if not candidate or candidate in tokens:
            continue
        closest = next(
            (known for known in tokens if _levenshtein_distance(candidate, known) == 1),
            None,
        )
        if closest:
            errors.append(_make_error(
                text,
                match.start(),
                match.group(0),
                "POSSIBLE_COMBAT_TOKEN_TYPO",
                f"Possible typo of [{closest}]; found {match.group(0)!r}.",
            ))

    # SP must be uppercase and separated from numeric amounts by whitespace.
    resource_pattern = re.compile(r"(?<![A-Za-z])(?:\d+)?sp(?![A-Za-z])", re.IGNORECASE)
    for match in resource_pattern.finditer(text):
        found = match.group(0)
        if found != "SP":
            has_number = found[0].isdigit()
            errors.append(_make_error(
                text,
                match.start(),
                found,
                "MALFORMED_RESOURCE_TOKEN",
                (
                    'Numeric resource amounts must be separated from "SP" by a space (for example, "3 SP").'
                    if has_number
                    else 'Resource token must be uppercase "SP".'
                ),
            ))

    errors.sort(key=lambda error: (error["line"], error["column"]))
    return {"valid": not errors, "errors": errors}


def validate_text_files(
    files: Mapping[str, str], *, combat_tokens: tuple[str, ...] | list[str] | None = None
) -> dict[str, dict[str, Any]]:
    """Validate multiple named text files independently, without modifying them."""
    return {
        path: validate_game_text(text, combat_tokens=combat_tokens)
        for path, text in files.items()
    }
