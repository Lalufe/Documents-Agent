from __future__ import annotations

import shutil
import sys
from dataclasses import dataclass
from typing import Literal

OfficeStatusValue = Literal[
    "available",
    "unavailable",
    "unsupported_platform",
    "unknown",
]


@dataclass(frozen=True, slots=True)
class OfficeDependencyStatus:
    status: OfficeStatusValue
    detail: str | None


def _word_is_registered() -> bool:
    try:
        import winreg
    except ImportError:
        return False

    for root in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        try:
            with winreg.OpenKey(root, r"SOFTWARE\Classes\Word.Application"):
                return True
        except OSError:
            continue
    return False


def detect_office_status() -> OfficeDependencyStatus:
    if sys.platform != "win32":
        return OfficeDependencyStatus(
            status="unsupported_platform",
            detail="Office COM is only supported on Windows",
        )
    if _word_is_registered():
        return OfficeDependencyStatus(status="available", detail="com_registration")
    if shutil.which("WINWORD.EXE") is not None:
        return OfficeDependencyStatus(status="available", detail="executable")
    return OfficeDependencyStatus(status="unavailable", detail="word_not_found")
