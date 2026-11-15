from __future__ import annotations

from pathlib import Path


class PathForbiddenError(ValueError):
    pass


def ensure_within(root: Path, candidate: Path) -> Path:
    resolved_root = root.expanduser().resolve()
    resolved_candidate = candidate.expanduser().resolve(strict=False)
    if not resolved_candidate.is_relative_to(resolved_root):
        raise PathForbiddenError("路径超出允许的数据根目录")
    return resolved_candidate


def resolve_relative_path(root: Path, relative_path: str | Path) -> Path:
    candidate = Path(relative_path)
    if candidate.is_absolute() or candidate.drive:
        raise PathForbiddenError("数据路径必须是相对路径")
    if ".." in candidate.parts:
        raise PathForbiddenError("数据路径不得包含父目录跳转")
    return ensure_within(root, root / candidate)
