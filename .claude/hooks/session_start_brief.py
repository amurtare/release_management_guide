"""SessionStart hook — project-memory brief 출력."""

from __future__ import annotations

import sys
import time
from pathlib import Path

for _stream_name in ("stdout", "stderr"):
    _stream = getattr(sys, _stream_name, None)
    if _stream is not None and hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

REPO_ROOT    = Path(__file__).resolve().parent.parent.parent
MEM_DIR      = REPO_ROOT / "project-memory"
LOG_FILE     = MEM_DIR / "log.md"
INSIGHT_DIR  = MEM_DIR / "insight"

VERSION_FILE = REPO_ROOT / "VERSION"           # plain-text

SUPPRESS_MARKER = Path.home() / ".no-session-brief"

LOG_TAIL     = 3
INSIGHT_TAIL = 3


def _is_repo_session() -> bool:
    return MEM_DIR.is_dir()


def _read_version() -> str:
    try:
        return VERSION_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        return "?"


def _log_tail() -> list[str]:
    if not LOG_FILE.exists():
        return []
    try:
        text = LOG_FILE.read_text(encoding="utf-8")
    except OSError:
        return []
    return [l for l in text.splitlines() if l.startswith("## [")][-LOG_TAIL:]


def _insight_tail() -> list[tuple[str, str]]:
    if not INSIGHT_DIR.is_dir():
        return []
    files = sorted(
        (p for p in INSIGHT_DIR.glob("*.md") if p.name != "README.md"),
        key=lambda p: p.name,
        reverse=True,
    )[:INSIGHT_TAIL]
    out: list[tuple[str, str]] = []
    for p in files:
        first = ""
        try:
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("**컨텍스트**"):
                    first = line.strip()
                    break
        except OSError:
            pass
        out.append((p.name, first))
    return out


def _cleanup_stale_stop_markers(max_age_days: int = 7) -> None:
    marker_dir = SUPPRESS_MARKER.parent
    if not marker_dir.is_dir():
        return
    cutoff = time.time() - max_age_days * 86400
    try:
        for p in marker_dir.glob(".session-stop-reviewed-*"):
            try:
                if p.stat().st_mtime < cutoff:
                    p.unlink()
            except OSError:
                continue
    except OSError:
        return


def main() -> int:
    if SUPPRESS_MARKER.exists():
        return 0
    if not _is_repo_session():
        return 0

    _cleanup_stale_stop_markers()

    version   = _read_version()
    log_lines = _log_tail()
    insights  = _insight_tail()

    parts: list[str] = []
    parts.append("=== project-memory brief ===")
    parts.append(f"VERSION: {version}")
    parts.append("")
    parts.append(
        "이 저장소에는 project-memory/index.md 에 누적된 컨텍스트(설계 결정·gotcha·"
        "미해결 이슈·insight)가 있습니다. 비자명한 작업(코드 변경, 설계 논의, 릴리즈 "
        "준비, 디버깅) 전에 project-memory/index.md를 먼저 훑고 관련 페이지로 진입하세요."
    )
    parts.append("")

    if log_lines:
        parts.append(f"최근 log ({len(log_lines)}건):")
        for line in log_lines:
            parts.append(f"  {line}")
        parts.append("")

    if insights:
        parts.append(f"최근 insight ({len(insights)}건):")
        for name, ctx in insights:
            parts.append(f"  - {name}  // {ctx}" if ctx else f"  - {name}")
        parts.append("")

    parts.append(f"brief를 끄려면: `{SUPPRESS_MARKER}` 빈 파일 생성. 다시 켜려면 삭제.")
    parts.append("=== end brief ===")

    sys.stdout.write("\n".join(parts) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
