"""Stop hook — project-memory 회고 리마인더 (세션당 1회)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

for _stream_name in ("stdout", "stderr"):
    _stream = getattr(sys, _stream_name, None)
    if _stream is not None and hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MEM_DIR   = REPO_ROOT / "project-memory"

SUPPRESS_MARKER = Path.home() / ".no-session-stop-review"
MARKER_DIR      = SUPPRESS_MARKER.parent

EDIT_TOOLS      = {"Edit", "Write", "NotebookEdit", "MultiEdit"}
SAFE_SESSION_ID = re.compile(r"[^A-Za-z0-9_.-]")


def _is_repo_session() -> bool:
    return MEM_DIR.is_dir()


def _read_stdin_payload() -> dict:
    try:
        raw = sys.stdin.read()
    except Exception:
        return {}
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _is_substantial_edit(file_path: str) -> bool:
    """project-memory/, .claude/ 외부 파일이면 회고할 가치가 있는 변경으로 간주."""
    if not file_path:
        return False
    fp   = file_path.replace("\\", "/")
    repo = str(REPO_ROOT).replace("\\", "/")
    rel  = fp[len(repo):].lstrip("/") if fp.startswith(repo) else None
    if rel is None:
        return True
    return bool(rel) and not (
        rel.startswith("project-memory/") or rel.startswith(".claude/")
    )


def _scan_transcript(transcript_path: str) -> bool:
    if not transcript_path:
        return False
    p = Path(transcript_path)
    if not p.exists():
        return False
    try:
        with p.open("r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                msg = entry.get("message")
                if not isinstance(msg, dict):
                    continue
                for block in (msg.get("content") or []):
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") != "tool_use":
                        continue
                    if block.get("name") not in EDIT_TOOLS:
                        continue
                    inp = block.get("input") or {}
                    fp  = inp.get("file_path") or inp.get("notebook_path") or ""
                    if _is_substantial_edit(fp):
                        return True
    except OSError:
        return False
    return False


def _marker_for(session_id: str) -> Path | None:
    sid = SAFE_SESSION_ID.sub("_", session_id or "")
    if not sid:
        return None
    return MARKER_DIR / f".session-stop-reviewed-{sid}"


REMINDER = (
    "[세션 마무리 회고 — 세션당 1회 발동]\n"
    "이번 세션에서 다음 세션의 에이전트에게 유용할 만한 흔적을 project-memory/ 에 남길지 검토하세요.\n"
    "규칙은 project-memory/index.md, project-memory/insight/README.md, CLAUDE.md '메인테이너 워크플로' 섹션 참고.\n"
    "\n"
    "후보:\n"
    "- 작업 단위 한 줄 흔적(의도/시도/결과) → project-memory/log.md append\n"
    "  형식: ## [YYYY-MM-DD] <kind> | <한 줄 제목> + 본문 1~5줄.\n"
    "- 비자명한 디버깅 결론·의외의 동작 → project-memory/insight/YYYY-MM-DD-<주제>.md + index.md 등록\n"
    "- 반복적으로 부딪힐 함정 → project-memory/gotchas.md 항목 추가\n"
    "- 설계 결정의 의도 → project-memory/decisions/<topic>.md\n"
    "- 미해결 이슈/조사 중 가설 → project-memory/open-questions.md\n"
    "\n"
    "원칙: raw 코드·release-notes·git log에 이미 있는 사실은 다시 적지 않음.\n"
    "남길 게 없으면 '없음' 한 줄로 답하고 턴을 끝내세요.\n"
)


def main() -> int:
    payload = _read_stdin_payload()
    if payload.get("stop_hook_active"):
        return 0
    if SUPPRESS_MARKER.exists():
        return 0
    if not _is_repo_session():
        return 0

    session_id      = str(payload.get("session_id") or "")
    transcript_path = str(payload.get("transcript_path") or "")

    marker = _marker_for(session_id)
    if marker is None:
        return 0
    if marker.exists():
        return 0

    if not _scan_transcript(transcript_path):
        return 0

    try:
        MARKER_DIR.mkdir(parents=True, exist_ok=True)
        marker.touch()
    except OSError:
        return 0

    sys.stdout.write(json.dumps({"decision": "block", "reason": REMINDER}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
