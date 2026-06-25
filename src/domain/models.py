from dataclasses import dataclass, field


@dataclass
class ParseResult:
    items: list[tuple[str, str, str]] = field(default_factory=list)
    invalid_lines: list[str] = field(default_factory=list)
    duplicate_ids: list[str] = field(default_factory=list)


@dataclass
class AddResult:
    ok: int = 0
    confirmed_skip: int = 0
    already_in_playlist: list[tuple[str, str]] = field(default_factory=list)
    api_errors: list[tuple[str, str, str]] = field(default_factory=list)


@dataclass
class RemoveResult:
    ok: int = 0
    not_found: list[tuple[str, str]] = field(default_factory=list)
    api_errors: list[tuple[str, str, str]] = field(default_factory=list)
