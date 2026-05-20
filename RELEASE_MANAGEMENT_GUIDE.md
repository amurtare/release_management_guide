# 릴리즈 관리 구축 가이드

이 프로젝트에서 사용하는 버전 관리 + 업데이트 관리 체계를 다른 프로젝트에 그대로 적용하는 방법을 설명한다.

---

## 구성 요소

| 파일/도구 | 역할 |
|-----------|------|
| `package.json` (또는 언어별 매니페스트) | 버전 번호 단일 소스 |
| `docs/UPDATE_CHECKLIST.md` | 릴리즈 시 순서대로 따르는 체크리스트 |
| `release-notes/v{버전}.md` | 버전별 변경 내역 문서 |
| Git 태그 | 코드베이스에서 버전 지점 고정 |
| `CLAUDE.md` | Claude Code에 체크리스트 자동 실행 트리거 등록 |
| `project-memory/` | 개발 맥락 누적 — 설계 결정·함정·히스토리 |
| `.claude/hooks/` | SessionStart/Stop/PreCompact hook — 세션 시작·종료·압축 전 자동 컨텍스트 주입·회고 |

---

## 1단계 — 버전 번호 관리 방식 정의

### Semver 규칙

`MAJOR.MINOR.PATCH` 형식을 따른다 ([semver.org](https://semver.org)).

| 세그먼트 | 올리는 조건 | 예시 |
|----------|------------|------|
| **MAJOR** | 기존 사용자가 즉시 영향을 받는 호환성 파괴 변경 | API 응답 구조 변경, 필수 설정 파일 포맷 변경 |
| **MINOR** | 하위 호환을 유지하면서 새 기능 추가 | 새 페이지, 새 필터, 새 차트 추가 |
| **PATCH** | 버그 수정, 오탈자 수정, 성능 개선 (기능 추가 없음) | 차트 렌더링 버그, API 응답 누락 수정 |

**판단이 애매할 때 기준:**
- "기존 사용자가 아무것도 바꾸지 않아도 이전처럼 동작하는가?" → YES면 MINOR 이하
- "설정 파일, .env, 실행 명령을 바꿔야 하는가?" → YES면 MAJOR 고려
- 여러 버그를 한 번에 묶어 수정했어도 기능 추가가 없으면 PATCH

**세그먼트 올림 시 하위 세그먼트는 0으로 초기화한다:**
```
0.3.2 → MINOR 추가 → 0.4.0
0.3.2 → MAJOR 변경 → 1.0.0
0.3.2 → PATCH 수정 → 0.3.3
```

### 프리릴리즈 식별자 (선택)

정식 릴리즈 전 테스트가 필요한 경우에만 사용한다.

| 식별자 | 의미 | 예시 |
|--------|------|------|
| `alpha` | 내부 테스트, 기능 불완전 | `0.4.0-alpha.1` |
| `beta` | 외부 테스트 가능, 기능 완성 | `0.4.0-beta.1` |
| `rc` | 릴리즈 후보, 버그 수정만 남음 | `0.4.0-rc.1` |

소규모 프로젝트나 내부 도구는 프리릴리즈 식별자를 생략하고 바로 정식 버전을 올려도 무방하다.

### 버전 소스 관리

**버전 번호는 한 곳에만 정의하고, 나머지는 그 값을 참조한다.**

| 언어/환경 | 버전 소스 파일 | 필드 |
|-----------|--------------|------|
| Node.js / Next.js | `package.json` | `"version"` |
| Rust | `Cargo.toml` | `version` |
| Python | `pyproject.toml` | `version` (또는 `__version__`) |
| Go | `version.go` 또는 Git 태그 직접 사용 | — |

앱 내에서 버전을 읽어야 할 경우:
```ts
// Node.js 예시 — package.json에서 직접 읽기
import { version } from "../package.json";
```

### Git 태그

커밋과 버전을 연결하는 공식 수단이다. 릴리즈 커밋 직후 태그를 생성한다.

```bash
# 태그 생성
git tag v0.3.3

# 원격에 태그 푸시 (커밋 push와 별도로 필요)
git push origin v0.3.3

# 또는 모든 태그 한 번에 푸시
git push origin --tags
```

태그 목록 확인:
```bash
git tag --sort=-version:refname   # 최신순 정렬
```

특정 버전 코드로 이동:
```bash
git checkout v0.3.2
```

---

## 2단계 — 디렉토리 구조 생성

```
project-root/
├── docs/
│   └── UPDATE_CHECKLIST.md
├── release-notes/
│   └── v0.1.0.md
├── project-memory/
│   ├── index.md
│   ├── log.md
│   ├── decisions/
│   ├── gotchas.md
│   ├── components.md
│   ├── open-questions.md
│   └── insight/
│       └── README.md
└── .claude/
    ├── settings.json
    └── hooks/
        ├── session_start_brief.py
        ├── session_stop_review.py
        └── pre_compact_review.py
```

### 설치 체크리스트 (이 가이드를 새 프로젝트에 적용할 때)

- [ ] **버전 필드 존재 확인** — `package.json`(또는 언어별 매니페스트)에 `version` 필드가 있는지 확인
  - 없으면 추가: `"version": "0.1.0"`
  - 이 필드는 업데이트 체크 기능의 비교 대상이 되므로 첫 버전부터 반드시 존재해야 함
- [ ] `docs/UPDATE_CHECKLIST.md` 생성
- [ ] `release-notes/` 디렉토리 생성 + `v{현재버전}.md` 작성
- [ ] `CLAUDE.md`에 트리거 등록 (5단계 참고)
- [ ] 앱 내 업데이트 배너 구현 (6단계 참고)
- [ ] `project-memory/` 디렉토리 구조 생성 (7단계 참고)
- [ ] SessionStart/Stop/PreCompact hook 설정

---

## 3단계 — 업데이트 체크리스트 작성

`docs/UPDATE_CHECKLIST.md`를 생성하고 아래 템플릿을 기반으로 프로젝트에 맞게 조정한다.

```markdown
# 버전 업데이트 체크리스트

메이저/마이너 업데이트 시 아래 항목을 순서대로 확인한다.

## 1. 버전 번호 갱신

- [ ] `package.json` — `version` 필드 업데이트
- [ ] 버전 규칙: `MAJOR.MINOR.PATCH` — docs/RELEASE_MANAGEMENT_GUIDE.md 참고

## 2. 릴리즈 노트 작성

- [ ] `release-notes/v{버전}.md` 신규 생성
- [ ] 포함 항목: 새 기능, 개선, 버그 수정, API 변경, 보안 패치
- [ ] 기존 릴리즈 노트와 동일한 포맷 유지

## 3. README.md 갱신 여부 확인

아래 섹션 중 변경 영향이 있는지 확인한다:

- [ ] 기능 목록 — 새 기능이 추가되었으면 반영
- [ ] 설치/실행 방법 — 명령어나 환경 변수가 바뀌었으면 갱신
- [ ] 버전 표기 — `vX.Y.Z 기준` 문구를 현재 버전으로 갱신

## 4. 보안 점검 (새 API/기능이 추가된 경우)

- [ ] 새 API 엔드포인트에 사용자 입력이 있는가? → Command Injection, Path Traversal 확인
- [ ] 외부 서비스 호출이 추가되었는가? → SSRF, 인증 토큰 노출 확인
- [ ] 클라이언트에서 `dangerouslySetInnerHTML` 사용했는가? → XSS 확인
- [ ] `npm audit` 실행 — 새 취약점이 있으면 패치

## 5. 빌드 & 테스트

- [ ] `npx next build` — 에러/경고 0 확인   ← 빌드 명령은 프로젝트에 맞게 변경
- [ ] `npm run dev` — 실행 후 주요 페이지 동작 확인
- [ ] 새 기능의 정상 동작 수동 확인

## 6. project-memory 갱신 점검

이번 릴리즈에서 다음 중 하나라도 변경됐으면 `project-memory/`도 같이 갱신한다.
**stale한 project-memory는 거짓말 소스가 되므로** 빠뜨리지 말 것.

- [ ] 설계 의도/정책 변경 → `project-memory/decisions/<topic>.md` 추가/수정
- [ ] 반복 가능한 함정 발견 → `project-memory/gotchas.md` 항목 추가
- [ ] 컴포넌트 관계/데이터 흐름 변경 → `project-memory/components.md` 갱신
- [ ] 미해결 이슈 진척/해결 → `project-memory/open-questions.md` 갱신
- [ ] `project-memory/log.md`에 이번 릴리즈 항목 append (1~3줄, 의도 위주)
- [ ] `project-memory/insight/` 정리 — 6개월 이상 참조 0회 항목 삭제
- [ ] staleness 점검: decisions에 superseded 항목 없는지, gotchas에 해결된 항목 없는지,
  components가 현재 구조와 맞는지 확인

## 7. 커밋 & 배포

- [ ] 관련 파일 모두 `git add` (package.json, release-notes, README.md, 소스 파일)
- [ ] 커밋 메시지에 버전 포함: `v0.2.0: 새 기능 설명`
- [ ] `git tag v0.2.0` 후 `git push origin v0.2.0`
- [ ] `git push origin main`
```

> **조정 포인트**
> - 섹션 3은 README 구조에 맞게 항목을 교체한다.
> - 섹션 4는 백엔드가 없는 프로젝트라면 전체 생략해도 된다.
> - 섹션 5의 빌드 명령은 프레임워크에 맞게 바꾼다 (예: `cargo build`, `go build`).
> - 섹션 6은 project-memory 갱신이 필요 없는 순수 문서 수정 릴리즈라면 생략 가능하다.

---

## 4단계 — 릴리즈 노트 형식 정의

`release-notes/v0.1.0.md`를 아래 형식으로 작성한다. 이 형식을 모든 버전에 걸쳐 통일한다.

```markdown
## v0.1.0 — 한 줄 요약

### 새 기능
- **기능명** — 설명

### 개선
- **항목** — 설명

### 버그 수정
- **버그명** — 증상 및 수정 내용

### 보안
- 항목

### 데이터/API 변경
- 항목

### 신규 파일
- `path/to/file.ts` — 역할 설명
```

> 해당 버전에 변경 사항이 없는 섹션은 생략한다.

---

## 5단계 — CLAUDE.md에 트리거 등록

`CLAUDE.md`에 아래 내용을 추가하면 Claude Code가 릴리즈 관련 요청을 받았을 때 체크리스트를 자동으로 실행한다.

```markdown
## 버전 업데이트

메이저/마이너 업데이트 시 반드시 `docs/UPDATE_CHECKLIST.md`의 체크리스트를 따른다.
사용자가 "업데이트 해줘", "버전 올려줘", "배포 준비해줘" 등을 요청하면 체크리스트를 자동으로 실행한다.

## 릴리즈 노트

- 위치: `release-notes/v{버전}.md`
- 버전 배포 시 반드시 릴리즈 노트를 작성한다
- 원격 저장소의 릴리즈 노트는 업데이트 배너에서 사용자에게 표시된다

## 세션 시작 시 project-memory 참조

> **세션 시작 시 가장 먼저**: 비자명한 작업(코드 변경, 설계 논의, 릴리즈 준비, 디버깅)
> 전에 [project-memory/index.md](project-memory/index.md)를 훑고 관련 페이지로 진입할 것.

## 메인테이너 워크플로

언제 project-memory를 갱신하나:
- 설계 결정을 내렸을 때 → `project-memory/decisions/<topic>.md`
- 반복 가능한 함정을 발견했을 때 → `project-memory/gotchas.md`
- 컴포넌트 구조를 바꿨을 때 → `project-memory/components.md`
- 미해결 이슈를 인지했을 때 → `project-memory/open-questions.md`
- 작업 단위를 마쳤을 때 (의도/맥락 보존 필요 시) → `project-memory/log.md`
```

---

## 6단계 — 업데이트 수신 메커니즘 구축

배포된 새 버전을 사용자가 인지하고 받을 수 있도록 하는 단계.

> **⚠ 프로젝트 구조에 맞춰 설계할 것**
>
> 아래는 **한 가지 사례(웹 대시보드 + 앱 내 배너)**일 뿐이다. CLI 도구, 서버, 라이브러리 등 형태에 따라 적절한 방식이 다르므로, 자기 프로젝트의 현재 구조에 맞게 설계한다.
>
> 형태별 예시:
> - **웹 앱** → 앱 내 배너 + 원클릭 업데이트 (아래 사례)
> - **CLI 도구** → `--version` 플래그 + 명령 실행 시 stderr 안내 (`update-notifier` 등)
> - **서버/데몬** → 시작 시 로그에 새 버전 안내
> - **라이브러리/패키지** → 패키지 매니저(npm/pip/cargo)가 자동 처리하므로 별도 구현 불필요

### 사례 — 웹 앱: 앱 내 배너 (Next.js + GitLab Releases API)

```
GitLab Releases API
  → 앱 시작 시 최신 버전 태그 fetch
  → 현재 버전(package.json)과 비교
  → 신규 버전이면 배너 표시 + 릴리즈 노트 내용 렌더링
```

```ts
// lib/update-check.ts
export async function fetchLatestRelease() {
  const res = await fetch(
    "https://gitlab.nexon.com/api/v4/projects/{id}/releases/permalink/latest",
    {
      headers: { "PRIVATE-TOKEN": process.env.GITLAB_TOKEN! },
      next: { revalidate: 3600 },
    }
  );
  const data = await res.json();
  return { version: data.tag_name, body: data.description };
}
```

> 이 기능이 동작하려면 Git 태그가 GitLab Release로 등록되어 있어야 한다.
>
> 비공개 저장소에서는 PAT(Personal Access Token)가 필요하다. 발급 방법은 [GitLab Personal Access Token 발급 가이드](https://www.notion.so/nexoncompany/GitLab-Personal-Access-Token-Mac-Windows-33ddadb56b2f810e83bee7dfe80bf835)를 참고한다. 토큰 부담 없이 구현하고 싶다면 `git fetch` + `git show origin/main:package.json` 같은 Git CLI 기반 방식도 가능 (사용자가 `git clone`으로 설치한 경우에 한해).

---

## 7단계 — project-memory 연동

### 왜 이걸 하는가

릴리즈 관리만으로는 "무엇이 바뀌었나"는 기록되지만 "왜 그렇게 결정했나", "이 함정을 이미 밟았다"는 기록되지 않는다. project-memory는 이 공백을 채우고, 릴리즈 체크리스트가 갱신 트리거 역할을 한다.

| | `release-notes/vX.Y.Z.md` | `project-memory/log.md` |
|--|--|--|
| 대상 | 사용자/소비자 | 메인테이너/다음 세션 에이전트 |
| 내용 | 무엇이 바뀌었나, 영향, breaking | 왜, 무엇을 시도했나, 맥락 |
| 트리거 | 릴리즈마다 | 작업 세션마다 |

### project-memory/ 구조 상세

#### index.md

세션 시작 진입점. 카테고리별 한 줄 요약 + 링크로 구성한다.

#### log.md

개발 로그. append-only. 형식:

```
## [YYYY-MM-DD] <kind> | <한 줄 제목>
본문 1~5줄 (의도·맥락만, 코드 diff 아님)
```

kind 값: `release`, `design`, `debug`, `handoff` 등

**handoff 항목 필수 필드** — 비자명한 작업이 미완인 채 세션을 종료할 때 반드시 포함:

```
## [YYYY-MM-DD] handoff | 한 줄 제목
- **목표**: 이번 세션에서 하려던 것
- **마지막 완료**: 어디까지 됐는지
- **다음 단계**: 이어서 해야 할 것
- **차단 요소**: (있으면) 막힌 것, 조사 중인 것
- **수정 파일**: 변경한 주요 파일 목록
```

#### decisions/

설계 결정. 파일 하나에 결정 하나. "왜 이렇게 했는가" 중심.

- 초기 생성 시 빈 디렉토리이므로 `.gitkeep` 플레이스홀더 파일 생성 필요
- **수명 규칙**: 본문은 immutable(수정 금지). 후속 결정이 기존 결정을 뒤집을 때만 예외:
  - 새 파일 작성 (기존 파일 본문을 조용히 덮어쓰지 않음)
  - 기존 파일 상단에 `> **Superseded by**: [decisions/<new>.md](<new>.md)` 한 줄 추가 (이것만 허용되는 수정)
  - index.md에서 superseded 표시

#### gotchas.md

반복 함정. 항목별 증상 + 원인 + 올바른 해법.

**수명 규칙**: 근본 원인이 코드에서 해결되면 항목에 `~~취소선~~` + `(해결됨: vX.Y.Z)` 추가. 다음 릴리즈 점검에서 제거.

#### components.md

아키텍처/의존 맵. 구조 변경 시 갱신.

**수명 규칙**: 릴리즈 체크리스트에서 현재 구조와 일치 여부 강제 점검.

#### open-questions.md

미해결 이슈. 항목별 형식:

```
상태: 조사중 | 가설 | 부분 해결 | 보류
관찰: ...
가설·시도: ...
다음 단계: ...
```

해결 시 decisions/gotchas로 graduation 후 제거. **수명 규칙**: 6개월 이상 진척 없으면 "보류" 상태 표시 + 릴리즈 시 archive 고려.

#### insight/

raw 메모.

- 파일 형식: `YYYY-MM-DD-<kebab>.md`, 본문에 `**컨텍스트**:` 줄 필수 (SessionStart hook이 추출)
- 저장 트리거: 사용자 명시 요청 → 즉시 저장 / 에이전트 감지 → 제안만, 자동 저장 금지
- graduation 규칙: 두 번 이상 참조 → 본체(decisions/gotchas/components) 승격 → 원본 삭제
- 정리 시점: 릴리즈 시, 6개월 0참조 → 삭제
- `insight/README.md`에 위 규칙을 문서화할 것

### 신뢰도 규칙

project-memory의 기록과 현재 코드/설정/테스트가 모순될 때의 우선순위:

```
현재 코드·테스트·설정 > project-memory 기록
```

- project-memory는 "기록 당시의 맥락"이지 "현재 사실"이 아님
- 에이전트는 project-memory의 주장을 행동 전에 현재 파일로 검증해야 함
- 충돌 발견 시: project-memory를 수정하거나 superseded 마킹 (코드를 memory에 맞추는 것이 아님)
- SessionStart hook이 주입하는 log/insight는 "최근 맥락 힌트"이지 "확인된 현재 상태"가 아님

### SessionStart hook

`.claude/hooks/session_start_brief.py`로 작성. 세션 시작 시 project-memory brief를 stdout으로 출력해 에이전트가 현재 버전·최근 로그·최근 insight를 인지하게 한다.

```python
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

# 버전 소스는 프로젝트에 맞게 조정
VERSION_FILE = REPO_ROOT / "VERSION"           # plain-text
# import json; json.loads((REPO_ROOT / "package.json").read_text())["version"]

# suppress 마커 경로는 프로젝트 전용으로 변경할 것
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


def _cleanup_stale_markers(max_age_days: int = 7) -> None:
    marker_dir = SUPPRESS_MARKER.parent
    if not marker_dir.is_dir():
        return
    cutoff = time.time() - max_age_days * 86400
    for pattern in (".session-stop-reviewed-*", ".session-compact-reviewed-*"):
        try:
            for p in marker_dir.glob(pattern):
                try:
                    if p.stat().st_mtime < cutoff:
                        p.unlink()
                except OSError:
                    continue
        except OSError:
            continue


def main() -> int:
    if SUPPRESS_MARKER.exists():
        return 0
    if not _is_repo_session():
        return 0

    _cleanup_stale_markers()

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
```

**settings.json 등록:**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/session_start_brief.py\""
          }
        ]
      }
    ]
  }
}
```

### Stop hook (회고 리마인더)

`.claude/hooks/session_stop_review.py`로 작성. 에이전트가 세션을 끝내려 할 때 실질적 파일 변경이 있었으면 project-memory 회고 리마인더를 1회 주입한다.

```python
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

# suppress 마커 경로는 프로젝트 전용으로 변경할 것
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
        return True  # 저장소 밖 편집 — 보수적으로 substantial
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
```

**settings.json 등록:**

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/session_stop_review.py\""
          }
        ]
      }
    ]
  }
}
```

### PreCompact hook (압축 전 리마인더)

`.claude/hooks/pre_compact_review.py`로 작성. `/compact` 실행 직전에 실질적 파일 변경이 있었으면 project-memory 회고 리마인더를 주입한다. Stop hook과 달리 **새 편집이 있을 때마다** 발동하며, `auto` 자동 압축 시에는 조용히 통과한다.

```python
"""PreCompact hook — 컨텍스트 압축 전 project-memory 리마인더."""

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

SUPPRESS_MARKER = Path.home() / ".no-pre-compact-review"
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


def _marker_for(session_id: str) -> Path | None:
    sid = SAFE_SESSION_ID.sub("_", session_id or "")
    if not sid:
        return None
    return MARKER_DIR / f".session-compact-reviewed-{sid}"


def _read_marker(marker: Path) -> dict:
    try:
        return json.loads(marker.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_marker(marker: Path, transcript_path: str, line_count: int, mtime: float) -> None:
    try:
        MARKER_DIR.mkdir(parents=True, exist_ok=True)
        marker.write_text(
            json.dumps({"transcript_path": transcript_path, "line_count": line_count, "mtime": mtime}),
            encoding="utf-8",
        )
    except OSError:
        pass


def _resolve_start_line(marker: Path, transcript_path: str) -> int:
    """마커에서 시작 줄을 읽고, 무효화 조건에 해당하면 0 반환."""
    if not marker.exists():
        return 0
    stored = _read_marker(marker)
    if not stored:
        return 0

    stored_path  = stored.get("transcript_path", "")
    stored_lines = stored.get("line_count", 0)
    stored_mtime = stored.get("mtime", 0.0)

    p = Path(transcript_path)
    try:
        current_mtime = p.stat().st_mtime
    except OSError:
        return 0

    if stored_path != transcript_path:
        return 0

    try:
        current_lines = sum(1 for _ in p.open("r", encoding="utf-8", errors="replace"))
    except OSError:
        return 0

    if stored_lines > current_lines:
        return 0
    if stored_mtime != current_mtime:
        return 0

    return stored_lines


def _scan_transcript(transcript_path: str, start_line: int) -> bool:
    if not transcript_path:
        return False
    p = Path(transcript_path)
    if not p.exists():
        return False
    try:
        with p.open("r", encoding="utf-8", errors="replace") as fh:
            for idx, line in enumerate(fh):
                if idx < start_line:
                    continue
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


def _line_count(transcript_path: str) -> int:
    try:
        with Path(transcript_path).open("r", encoding="utf-8", errors="replace") as fh:
            return sum(1 for _ in fh)
    except OSError:
        return 0


REMINDER = (
    "[컨텍스트 압축 전 회고 — 새 편집이 있을 때마다 발동]\n"
    "곧 /compact로 컨텍스트가 압축됩니다. 압축 후에는 이번 세션 전반부의 맥락이 희석됩니다.\n"
    "다음 세션의 에이전트를 위해 project-memory/ 에 흔적을 남길지 검토하세요.\n"
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
    "기록을 마쳤거나 남길 게 없으면 '없음'으로 답한 뒤 /compact를 다시 실행하세요.\n"
)


def main() -> int:
    payload = _read_stdin_payload()

    if payload.get("trigger") == "auto":
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

    start_line = _resolve_start_line(marker, transcript_path)

    if not _scan_transcript(transcript_path, start_line):
        return 0

    lc = _line_count(transcript_path)
    try:
        mtime = Path(transcript_path).stat().st_mtime
    except OSError:
        mtime = 0.0
    _write_marker(marker, transcript_path, lc, mtime)

    sys.stdout.write(json.dumps({"decision": "block", "reason": REMINDER}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**settings.json 등록:**

```json
{
  "hooks": {
    "PreCompact": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/pre_compact_review.py\""
          }
        ]
      }
    ]
  }
}
```

---

### wiki/(llm-wiki-scaffold)와의 공존

llm-wiki-scaffold를 동시에 적용할 경우 `wiki/`와 `project-memory/`는 폴더명이 분리되어 충돌하지 않는다.

| | `project-memory/` | `wiki/` |
|--|--|--|
| 출처 | release_management_guide | llm-wiki-scaffold |
| 목적 | 프로젝트 내부 개발 맥락 | 도메인 지식 베이스 |
| 내용 | 설계 결정, 함정, 컴포넌트 맵, 개발 로그 | 개념, 엔티티, 요약, 소스 인덱싱 |
| 트리거 | 개발 활동 + 릴리즈 | 외부 소스 Ingest |
| 오퍼레이션 | release, debug, design, handoff | ingest, query, lint |

핵심 규칙: **겹치지 않는다.** `project-memory/`는 소프트웨어 자체의 구축 맥락, `wiki/`는 소프트웨어가 다루는 도메인 지식.

---

## 워크플로 요약

```
새 기능 개발 완료
    ↓
버전 번호 결정 (MAJOR / MINOR / PATCH 판단)
    ↓
"버전 올려줘" 요청 (Claude Code 또는 직접)
    ↓
UPDATE_CHECKLIST.md 항목 순서대로 실행
    ├── release-notes/v{버전}.md 신규 작성
    ├── project-memory/log.md append
    ├── project-memory/ 관련 페이지 갱신 점검
    ├── package.json 버전 갱신
    ├── README.md 필요 섹션 갱신
    └── 빌드 & 보안 점검
    ↓
커밋 메시지: "v0.X.Y: 변경 요약"
    ↓
git tag v0.X.Y
    ↓
git push origin main && git push origin v0.X.Y
```

---

## 체크리스트 항목 추가 기준

| 상황 | 추가할 항목 |
|------|-------------|
| DB 마이그레이션이 있는 경우 | 섹션 5에 마이그레이션 실행 확인 추가 |
| 환경 변수가 추가된 경우 | 섹션 3에 `.env.example` 갱신 확인 추가 |
| 공개 API가 있는 경우 | 섹션 3에 API 문서 갱신 확인 추가 |
| CI/CD 파이프라인이 있는 경우 | 섹션 6에 파이프라인 통과 확인 추가 |
| GitLab Release를 사용하는 경우 | 섹션 6에 Release 페이지 생성 확인 추가 |
| project-memory 관련 맥락 변화가 있는 경우 | 커밋 전에 project-memory 갱신 점검 섹션 추가 |
