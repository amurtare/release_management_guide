# 릴리즈 관리 구축 가이드

이 프로젝트에서 사용하는 버전 관리 + 업데이트 관리 체계를 다른 프로젝트에 그대로 적용하는 방법을 설명한다.

> **용어 — 기본 브랜치**: 이 가이드가 "기본 브랜치"라고 쓰는 것은 적용 대상 저장소의 기본 브랜치(`origin/HEAD`가 가리키는 브랜치. 원격이 없으면 `main` 또는 `master`)다. 이 가이드의 명령 예시에서는 `<기본 브랜치>`로 적는다. 저장소가 `main`을 쓰면 `main`으로, `master`나 `develop`을 쓰면 그 이름으로 바꿔 읽는다.

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
| `handoff.md` | 세션 이월 — 미완료 작업의 다음 세션 전달용 |
| `.claude/hooks/` | SessionStart/PostToolUse(Bash)/PreCompact/PreToolUse(ExitPlanMode) hook — 세션 시작 컨텍스트 주입·커밋 성사 후 회고·압축 전 회고·플랜 검수 게이트 |
| `dev/` · `templates/dev/` | (선택) 구현 중심 프로젝트 확장 — 계획·설계·구현을 사이클 단위로 진행·검수하는 문서 구조와 그 골격 템플릿 (8단계) |

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
├── handoff.md
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
        ├── post_commit_review.py
        ├── pre_compact_review.py
        └── pre_plan_exit_review.py
```

기능·시스템을 여러 번 추가하는 구현 중심 프로젝트라면 위 구조에 `dev/`(사이클 진입점·`dev/global/`·사이클 폴더)가 더해진다 — 8단계 참고.

### 설치 체크리스트 (이 가이드를 새 프로젝트에 적용할 때)

- [ ] **버전 필드 존재 확인** — `package.json`(또는 언어별 매니페스트)에 `version` 필드가 있는지 확인
  - 없으면 추가: `"version": "0.1.0"`
  - 이 필드는 업데이트 체크 기능의 비교 대상이 되므로 첫 버전부터 반드시 존재해야 함
- [ ] `docs/UPDATE_CHECKLIST.md` 생성
- [ ] `release-notes/` 디렉토리 생성 + `v{현재버전}.md` 작성
- [ ] `CLAUDE.md`에 트리거 등록 (5단계 참고)
- [ ] 앱 내 업데이트 배너 구현 (6단계 참고)
- [ ] `project-memory/` 디렉토리 구조 생성 (7단계 참고)
- [ ] `handoff.md` 생성 + `.gitignore`에 추가 (세션 이월용, 로컬 전용 — 7단계 "세션 이월" 참고)
- [ ] **8단계(구현 중심 확장) 적용 여부를 사용자에게 묻고 결정 파일에 기록** — 적용 계획을 세울 때 에이전트가 아래 기준을 보고 사용자에게 **묻는다**(혼자 정하지 않는다). 답은 적용·미적용 모두 `project-memory/decisions/<토픽>.md`에 남긴다(미적용도 기록해야 다음 에이전트가 다시 묻지 않는다). 나중에 도입하기로 하면 새 결정 파일을 만든다.
  - 묻는 기준: ① 기능을 여러 번 추가해 나갈 계획인가 ② 여러 세션에 걸치는 설계·구현 작업이 이어지는가 ③ 중간에 접거나 되돌릴 수 있는 작업이 생기는가
  - 적용으로 정해지면 8단계의 "적용 체크리스트"를 수행한다. 미적용이면 8단계는 건너뛴다 — 훅은 `dev/README.md` 첫 줄 표식(8단계 템플릿에 들어 있다)이 없으면 8단계 동작을 하지 않는다.
- [ ] hook **파일**을 `.claude/hooks/`에 복사하고, 각 파일 상단 "설정값" 블록을 프로젝트에 맞게 조정 — 버전 소스(`VERSION_FILE`), 기본 브랜치(`BASE_BRANCH` — 빈 값이면 자동 판단하고, 8단계를 쓰는데 판단하지 못하면 지정), 검수 모델(`REVIEW_MODEL`), 커밋 회고 면제(`EXEMPT_PATTERNS`·`EXEMPT_SUBJECT_PREFIXES`)
- [ ] **Python 실행 명령 확인** — 훅은 Python 3(표준 라이브러리만 사용)와 `git`이 필요하다. 터미널에서 `python --version`을 실행해 보고, 안 되면 Windows는 `py`, macOS·Linux는 `python3`를 쓴다. 아래 등록 예시의 `command`에 있는 `python`을 그 명령으로 바꾼다.
- [ ] hook을 `settings.json`(또는 `settings.local.json`)의 `hooks` 객체에 **등록** — 아래 "hooks 등록" 절의 통합 예시를 쓰고, 이미 있는 키는 보존한다. ⚠️ 파일 복사만으로는 발동하지 않는다. 등록이 없으면 훅은 침묵한다.
- [ ] 등록 검증 — 아래 "hooks 등록" 절의 **이벤트별 발동 확인표**를 순서대로 수행
  - 플랜 검수: plan 모드 → ExitPlanMode 시도 → "플랜 검수 게이트" 차단 메시지 확인. Codex·Copilot가 없어도 통과하지 않는다 — 대체 검수자(맥락 없는 서브에이전트) → 사용자 승인 예외 안내가 나오는 것이 정상
  - 커밋 회고: 저장소에서 두 번 커밋 → "커밋 회고" 리마인더 확인 (설치 후 이 머신의 첫 커밋은 baseline 설정이라 안 뜨는 게 정상, 두 번째 커밋부터 발동)
- [ ] 검수자 우선순위와 모델을 `CLAUDE.md`의 "플랜 검수" 절에 기록(5단계 템플릿 참고)하고, 모델이 정해져 있다면 `pre_plan_exit_review.py` 상단 `REVIEW_MODEL`에 **같은 값**을 지정 (공용 기본은 빈 값 = 모델 미지정)

### hooks 등록 — 통합 `settings.json` 예시

훅 4종을 한꺼번에 등록하는 예시다. 7단계의 각 훅 절에도 그 훅의 등록 조각이 있고, 모두 같은 `hooks` 객체에 병합한다.

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          { "type": "command", "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/session_start_brief.py\"" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/post_commit_review.py\"" }
        ]
      }
    ],
    "PreCompact": [
      {
        "hooks": [
          { "type": "command", "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/pre_compact_review.py\"" }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "ExitPlanMode",
        "hooks": [
          { "type": "command", "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/pre_plan_exit_review.py\"" }
        ]
      }
    ]
  }
}
```

- **기존 `settings.json`이 있으면 덮어쓰지 않는다.** `permissions`·`env` 같은 다른 키는 그대로 두고, `hooks` 객체가 있으면 그 안에서 합친다. 같은 이벤트 키(예: `PostToolUse`)가 이미 있으면 그 배열에 위 항목을 **추가**한다(기존 항목을 지우지 않는다).
- `python`은 위 체크리스트에서 확인한 실행 명령으로 바꾼다(`py`·`python3`).
- **PostToolUse의 `matcher`는 셸 도구 이름과 일치해야 한다.** 이 예시는 `Bash`이지만, 환경에 따라 셸 도구 이름이 다를 수 있다(예: Windows의 PowerShell 도구). 커밋한 뒤 회고 리마인더가 뜨지 않으면 그 환경의 셸 도구 이름을 `matcher`에 추가한다(여러 개는 `|`로 잇는다 — 예: `"Bash|PowerShell"`).

**이벤트별 발동 확인표** — 등록한 뒤 이 순서로 확인한다.

| 이벤트 (훅) | 확인 방법 | 정상 결과 |
|---|---|---|
| SessionStart (`session_start_brief.py`) | 새 세션을 시작한다 | 첫 화면에 `=== project-memory brief ===` 출력 |
| PreToolUse·ExitPlanMode (`pre_plan_exit_review.py`) | plan 모드에서 ExitPlanMode를 호출한다. 이어서 ① **다시 호출** ② 플랜 마지막 줄에 안내된 해시로 검수 기록 줄을 쓰고 호출 ③ 본문을 한 줄 고치고 호출 | ① 두 번째 호출도 계속 차단(이전 방식은 한 번 차단하고 자동 통과했다) ② 통과 ③ 해시가 어긋나 다시 차단. 차단 메시지에는 현재 본문 해시가 있다 |
| PostToolUse·Bash (`post_commit_review.py`) | 코드나 문서 파일을 바꿔 **두 번** 커밋한다(첫 커밋은 baseline 설정) | 두 번째 커밋 뒤 `[커밋 회고` 리마인더 — `project-memory/`·`.claude/`만 바꾼 커밋은 면제라 안 뜬다 |
| PreCompact (`pre_compact_review.py`) | 파일을 편집한 뒤 `/compact`를 실행한다(자동 압축은 조용히 통과) | `[컨텍스트 압축 전 회고` 차단 메시지 |

### 이미 적용한 프로젝트에 다시 적용할 때

이 가이드는 플러그인이 아니라서 자동 업데이트가 없다. 이미 적용한 프로젝트가 새 가이드 내용을 반영하려면 에이전트가 다시 적용해야 하고, 이 절은 그 경우만 다룬다.

**순서**

1. 프로젝트의 현재 `.claude/hooks/*.py`와 이 가이드의 훅 코드블록(7단계)을 비교해 바뀐 부분만 파악한다. 바뀐 훅만 교체한다.
2. 교체하기 전에 아래 "보존할 설정값"을 적어 둔다 → 새 코드로 교체 → 같은 값으로 되돌린다. 각 훅 상단에 `── 설정값 ──` 주석으로 감싼 블록이 있다.
3. `settings.json`의 등록을 위 통합 예시와 비교한다. 이전 가이드가 만든 등록 중 새 가이드에 없는 것(예: 이전 설계의 Stop 훅)만 지운다. 프로젝트 고유의 훅 항목은 그대로 둔다.
4. 위 "이벤트별 발동 확인표"를 다시 수행한다.
5. 8단계를 쓰는 프로젝트라면 `dev/README.md` 첫 줄에 표식이 있는지, 프로젝트 문서의 줄 형식이 8단계 "훅이 읽는 줄 형식" 표와 같은지 확인한다.
6. 무엇을 바꿨는지 `project-memory/log.md`에 한 줄 남긴다.

**보존할 설정값** — 훅을 덮어쓸 때 프로젝트의 값을 유지한다.

| 훅 | 설정값 |
|---|---|
| `session_start_brief.py` | `VERSION_FILE`, `SUPPRESS_MARKER`, `BASE_BRANCH` |
| `post_commit_review.py` | `SUPPRESS_MARKER`, `EXEMPT_PATTERNS`, `EXEMPT_SUBJECT_PREFIXES` |
| `pre_plan_exit_review.py` | `REVIEW_MODEL`, `PROJECT_SUPPRESS_MARKER`, `SUPPRESS_MARKER` |
| `pre_compact_review.py` | `SUPPRESS_MARKER` |

**현재 버전에서 동작이 크게 달라지는 점** — 이전에 적용한 훅과 비교할 때 가장 크게 다른 곳이다.

- **플랜 검수 게이트가 엄격해졌다.** 이전에는 검수자가 없으면 통과했고 플랜당 한 번 차단한 뒤 자동 통과했다. 지금은 플랜 파일의 **마지막 줄**에 `플랜 검수: GO — <검수자·회차> — 본문 <해시8>` 기록이 있고 해시가 현재 본문과 같을 때만 통과한다. 검수자가 없어도, 플랜 파일을 찾지 못하거나 읽지 못해도 통과시키지 않고 차단한다.
- **커밋 회고가 merge 커밋을 면제하지 않는다**(부모가 둘 이상인 커밋은 늘 회고 대상). `dev/` 진행 기록 면제(`dev/README.md`·`dev/*/README.md`·`dev/*/*/progress.md`)는 `dev/README.md` 첫 줄 표식 `<!-- rmg: dev-cycles -->`이 있을 때만 적용된다.
- **Stop 이벤트 등록은 없다.** 이전 설계의 Stop 훅(세션 종료 회고)을 등록해 두었다면 `settings.json`에서 지운다. 커밋 회고(PostToolUse)와 압축 전 회고(PreCompact)가 대신한다.

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

- [ ] 설계 의도/정책 변경 → `project-memory/decisions/<topic>.md` 추가 (기존 결정을 뒤집으면 본문은 수정하지 않고 새 파일 + 옛 파일 맨 위 `Superseded by` 한 줄)
- [ ] 반복 가능한 함정 발견 → `project-memory/gotchas.md` 항목 추가
- [ ] 구조 변경 → `project-memory/components.md` 갱신 (파일·폴더·도구·상태 파일 위치·빌드/배포 의존, `dev/global/`이 없는 프로젝트는 컴포넌트 관계·데이터 흐름까지)
  - `dev/global/`이 있는 프로젝트(8단계)는 컴포넌트 관계·데이터 흐름 같은 논리 설계 변경을 `dev/global/`에 적고, `components.md`에는 물리 구조만 둔다 — 7단계 "components.md" 경계
- [ ] 미해결 이슈 진척/해결 → `project-memory/open-questions.md` 갱신
  (구현 중심 확장을 쓰는 프로젝트면 진행 중 사이클 단계의 `dev/<코드>/<단계>/open-questions.md`도)
- [ ] `project-memory/log.md`에 이번 릴리즈 항목 append (1~3줄, 의도 위주)
- [ ] `project-memory/insight/` 정리 — 6개월 이상 참조 0회 항목 삭제
- [ ] staleness 점검: decisions에 superseded 항목 없는지, gotchas에 해결된 항목 없는지,
  components가 현재 구조와 맞는지 확인

## 7. 커밋 & 배포

기본 브랜치에 대한 커밋·푸시는 사용자 허락 후에만 한다.

- [ ] **커밋·푸시 전 사용자에게 확인을 받는다**
- [ ] 관련 파일 모두 `git add` (package.json, release-notes, README.md, 소스 파일)
- [ ] 커밋 메시지에 버전 포함: `v0.2.0: 새 기능 설명`
- [ ] `git tag v0.2.0` 후 `git push origin v0.2.0`
- [ ] `git push origin <기본 브랜치>`
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

## 커밋 / 푸시

- 기본 브랜치에 대한 커밋·푸시는 사용자 허락 후에만 한다. 릴리즈할 때도 커밋·푸시 전에 사용자에게 확인을 받는다.

## 플랜 검수

- 플랜 모드를 끝내기(ExitPlanMode) 전에 독립 검수자의 GO(P0·P1 없음)를 받는다. 검수 기록은 플랜 파일의 마지막 줄에 남긴다
  (`.claude/hooks/pre_plan_exit_review.py`가 확인한다 — RMG 7단계 "PreToolUse hook" 참고).
- 검수자 우선순위: Codex → Copilot → 맥락을 물려받지 않는 Claude 서브에이전트(독립성이 약하므로 그 사실을 기록) → 사용자 승인 예외.
- 검수 모델: `<모델 이름 — 없으면 "지정 없음">` (훅 `pre_plan_exit_review.py` 상단 `REVIEW_MODEL`과 같은 값). 지정했다면 Codex에 요청할 때 요청 맨 앞에 `--model <모델>`을 넣는다.
- 산출물(코드·문서) 검수의 기록은 `project-memory/log.md` 작업 항목의 `검수:` 줄에 남긴다(검수자·회차·판정). 8단계(사이클) 안의 검수 기록은 8단계 규칙을 따른다.

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
> 비공개 저장소에서는 PAT(Personal Access Token)가 필요하다. 발급 방법은 [GitLab Personal Access Token 발급 가이드](https://www.notion.so/nexoncompany/GitLab-Personal-Access-Token-Mac-Windows-33ddadb56b2f810e83bee7dfe80bf835)를 참고한다. 토큰 부담 없이 구현하고 싶다면 `git fetch` + `git show origin/<기본 브랜치>:package.json` 같은 Git CLI 기반 방식도 가능 (사용자가 `git clone`으로 설치한 경우에 한해).

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

**구현 중심 확장(`dev/global/`)을 쓰는 프로젝트의 경계**: `dev/global/`이 있는 프로젝트에서는 단위 ID로 인용할 수 있는 것(단위·책임·인터페이스·정책·소유 경계)은 `dev/global/`에, 그 밖의 물리 구조(파일·폴더 트리, 도구, 상태 파일 위치, 빌드·배포 의존)는 `components.md`에 둔다. `components.md`는 논리 설계를 다시 적지 않고 `dev/global/overview.md`로 링크한다. 확장을 쓰지 않으면 `dev/global/`이 없으므로 `components.md`가 지금처럼 전체 맵이다.

#### open-questions.md

미해결 이슈. 항목별 형식:

```
상태: 조사중 | 가설 | 부분 해결 | 보류
관찰: ...
가설·시도: ...
다음 단계: ...
```

해결 시 decisions/gotchas로 graduation 후 제거. **수명 규칙**: 6개월 이상 진척 없으면 "보류" 상태 표시 + 릴리즈 시 archive 고려.

**구현 중심 확장을 쓰는 프로젝트의 경계 규칙**: 특정 단계의 단위·항목 ID로 인용할 수 있으면 그 단계의 `dev/<코드>/<단계>/open-questions.md`에, 아니면(특정 사이클·단계에 묶이지 않는 프로젝트 차원의 이슈·가설, 사이클 밖 작업에서 생긴 것) 이 `project-memory/open-questions.md`에 적는다. 단계 전환 때 남은 항목은 다음 단계 장부로 이관한다.

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

구현 중심 확장(8단계)을 쓰는 프로젝트에서는 사이클 상황도 함께 출력한다. **8단계를 쓰는 프로젝트인지는 `dev/README.md`의 첫 줄이 정확히 `<!-- rmg: dev-cycles -->`인지로 판단한다**(UTF-8 BOM·CRLF·줄 앞뒤 공백은 무시. 빈 줄 뒤나 본문 중간의 표식은 무효). 그 표식이 있으면: **브랜치가 `cycle/<코드>`이면** 사이클 README의 "현재 단계"와 그 단계 `progress.md`의 "다음 착수 지점"을, **브랜치가 기본 브랜치이면** `dev/README.md` 표의 `진행 중` 사이클과 브랜치를 안내한다. 그 밖의 브랜치·detached HEAD·파일이 없거나 깨진 경우는 조용히 생략한다. 표식이 없는 프로젝트(`dev/`가 없거나 무관한 `dev/README.md`만 있음)의 출력은 달라지지 않는다.

기본 브랜치는 설정값 `BASE_BRANCH`가 있으면 그것이고, 빈 값이면 ① `origin/HEAD`가 가리키는 이름(로컬 브랜치 또는 `origin/<이름>`으로 실제 있을 때) ② 로컬 `main`·`master` 중 **하나만** 있을 때 그것으로 자동 판단한다. 판단하지 못하면(예: 둘 다 있거나 둘 다 없음) 사이클 안내 대신 "기본 브랜치를 판단할 수 없다"는 경고 한 줄을 출력한다(`cycle/<코드>` 브랜치가 아닌 어느 브랜치에서든 나온다) — `BASE_BRANCH`를 지정하면 된다.

```python
"""SessionStart hook — project-memory brief 출력."""

from __future__ import annotations

import re
import subprocess
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
HANDOFF_FILE = REPO_ROOT / "handoff.md"
DEV_DIR      = REPO_ROOT / "dev"                # 구현 중심 확장(사이클)을 쓰는 프로젝트에만 있다

# ── 설정값 — 이 훅을 다시 적용(덮어쓰기)할 때 보존할 프로젝트별 값 ──
# 버전 소스는 프로젝트에 맞게 조정
VERSION_FILE = REPO_ROOT / "VERSION"           # plain-text
# import json; json.loads((REPO_ROOT / "package.json").read_text())["version"]
# import tomllib; tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
# suppress 마커 경로는 프로젝트 전용으로 변경할 것
SUPPRESS_MARKER = Path.home() / ".no-session-brief"
# 기본 브랜치 이름. 빈 값이면 자동 판단(origin/HEAD → 로컬 main·master 중 하나만 있을 때 그것).
BASE_BRANCH = ""
# ── 설정값 끝 ──

# dev/README.md 첫 줄이 이 표식일 때만 8단계(사이클)를 쓰는 프로젝트로 본다.
DEV_MARKER = "<!-- rmg: dev-cycles -->"

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


def _handoff_pending() -> list[str]:
    if not HANDOFF_FILE.exists():
        return []
    try:
        text = HANDOFF_FILE.read_text(encoding="utf-8")
    except OSError:
        return []
    in_remaining = False
    lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("## 남은 작업"):
            in_remaining = True
            continue
        if in_remaining and line.startswith("## "):
            break
        if in_remaining:
            stripped = line.strip()
            if stripped and stripped not in {"(현재 없음)", "---"}:
                lines.append(stripped)
    return lines


_CYCLE_CODE_RE = re.compile(r"^[A-Z0-9]{2,8}$")
_STAGES = {"plan": "plan", "design": "design", "impl": "impl"}


def _git(args: list[str]) -> str | None:
    """git 명령을 REPO_ROOT에서 실행. 실패하면 None."""
    try:
        out = subprocess.run(
            ["git", *args],
            cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=5,
        )
    except Exception:
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def _current_branch() -> str | None:
    """현재 브랜치 이름. detached HEAD이거나 git을 못 쓰면 None."""
    return _git(["symbolic-ref", "-q", "--short", "HEAD"]) or None


def _ref_exists(ref: str) -> bool:
    return _git(["show-ref", "--verify", "--quiet", ref]) is not None


def _base_branch() -> str | None:
    """기본 브랜치 이름. BASE_BRANCH가 있으면 그것, 없으면 자동 판단, 판단 불가면 None.

    자동 판단: ① origin/HEAD가 가리키는 이름(로컬 브랜치 또는 origin/<이름>으로 실제 있을 때)
    ② 로컬 main·master 중 정확히 하나만 있을 때 그것.
    """
    if BASE_BRANCH:
        return BASE_BRANCH
    head = _git(["symbolic-ref", "--short", "refs/remotes/origin/HEAD"])
    if head and head.startswith("origin/"):
        name = head[len("origin/"):]
        if name and (_ref_exists(f"refs/heads/{name}") or _ref_exists(f"refs/remotes/origin/{name}")):
            return name
    found = [b for b in ("main", "master") if _ref_exists(f"refs/heads/{b}")]
    return found[0] if len(found) == 1 else None


def _dev_cycles_enabled() -> bool:
    """dev/README.md의 첫 줄이 DEV_MARKER일 때만 참(UTF-8 BOM·CRLF·앞뒤 공백은 무시).

    빈 줄 뒤나 본문 중간의 표식은 무효다. post_commit_review.py도 같은 판정을 쓴다.
    """
    try:
        with (DEV_DIR / "README.md").open(encoding="utf-8-sig") as f:
            first = f.readline()
    except (OSError, UnicodeDecodeError):
        return False
    return first.strip() == DEV_MARKER


def _read_lines(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []


def _next_start_point(progress: Path) -> list[str]:
    """progress.md의 '## 다음 착수 지점' 절 본문(다음 '## ' 전까지). HTML 주석(형식 안내)은 건너뛴다."""
    lines: list[str] = []
    inside = in_comment = False
    for line in _read_lines(progress):
        if line.startswith("## 다음 착수 지점"):
            inside = True
            continue
        if inside and line.startswith("## "):
            break
        if not inside:
            continue
        s = line.strip()
        if in_comment or s.startswith("<!--"):
            in_comment = "-->" not in s
            continue
        if s:
            lines.append(s)
    return lines


def _in_progress_rows(dev_readme: Path) -> list[tuple[str, str, str]]:
    """dev/README.md 사이클 표에서 상태가 '진행 중'인 행 (코드, 이름, 브랜치).

    코드블록·HTML 주석 안의 줄(예시)은 무시한다.
    """
    rows: list[tuple[str, str, str]] = []
    in_fence = in_comment = False
    for line in _read_lines(dev_readme):
        s = line.strip()
        if s.startswith("`" * 3) or s.startswith("~" * 3):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if "<!--" in s:
            in_comment = True
        if in_comment:
            if "-->" in s:
                in_comment = False
            continue
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) >= 4 and cells[2] == "진행 중":
            rows.append((cells[0], cells[1], cells[3]))
    return rows


def _dev_cycle_section() -> list[str]:
    """8단계(dev/README.md 첫 줄 표식)를 쓰는 프로젝트에서 사이클 상황을 출력한다.

    cycle/<코드> 브랜치: 사이클 README의 현재 단계 + 그 단계 progress.md '다음 착수 지점'.
    기본 브랜치: 진행 중 사이클 안내(기본 브랜치를 판단할 수 없으면 경고 한 줄).
    그 밖의 브랜치·detached HEAD·파일이 없거나 깨진 경우는 조용히 생략.
    """
    if not _dev_cycles_enabled():
        return []
    dev_readme = DEV_DIR / "README.md"
    branch = _current_branch()
    if branch is None:
        return []

    if branch.startswith("cycle/"):
        code = branch[len("cycle/"):]
        if not _CYCLE_CODE_RE.match(code):
            return []
        cycle_readme = DEV_DIR / code / "README.md"
        stage = None
        for line in _read_lines(cycle_readme):
            m = re.search(r"현재 단계:\s*\**\s*(Plan|Design|Impl)\b", line)
            if m:
                stage = m.group(1)
                break
        if stage is None:
            return []
        out = [f"[DEV] 사이클 {code} (브랜치 {branch}) — 현재 단계: {stage}"]
        progress = DEV_DIR / code / _STAGES[stage.lower()] / "progress.md"
        start = _next_start_point(progress)
        if start:
            out.append(f"다음 착수 지점 (dev/{code}/{stage.lower()}/progress.md):")
            out.extend(f"  {ln}" for ln in start)
        out.append(f"시작: dev/{code}/{stage.lower()}/README.md를 읽고 플랜 모드부터 들어가세요.")
        out.append("")
        return out

    base = _base_branch()
    if base is None:
        return ["[DEV] 기본 브랜치를 판단할 수 없어 사이클 안내를 생략했습니다 — session_start_brief.py의 BASE_BRANCH를 지정하세요.", ""]

    if branch == base:
        rows = _in_progress_rows(dev_readme)
        if not rows:
            return ["[DEV] 진행 중인 사이클 없음 (dev/README.md 사이클 표)", ""]
        out = []
        for code, name, br in rows:
            out.append(f"[DEV] 진행 중 사이클: {code} ({name}) — 브랜치 {br}. 이어서 하려면 그 브랜치로 옮겨 가세요.")
        out.append("")
        return out

    return []


def _cleanup_stale_markers(max_age_days: int = 7) -> None:
    cutoff = time.time() - max_age_days * 86400

    def _sweep(marker_dir: Path, patterns: tuple[str, ...]) -> None:
        if not marker_dir.is_dir():
            return
        for pattern in patterns:
            try:
                for p in marker_dir.glob(pattern):
                    try:
                        if p.stat().st_mtime < cutoff:
                            p.unlink()
                    except OSError:
                        continue
            except OSError:
                continue

    _sweep(SUPPRESS_MARKER.parent, (".session-stop-reviewed-*", ".session-compact-reviewed-*"))
    # 플랜 리뷰 마커는 세션이 아닌 플랜 파일 기준이라 전용 하위 디렉터리에 보관된다.
    _sweep(Path.home() / ".claude" / "plan-review-markers", (".plan-reviewed-*",))


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

    parts.extend(_dev_cycle_section())

    handoff = _handoff_pending()
    if handoff:
        parts.append("[HANDOFF] 미완료 작업:")
        for line in handoff:
            parts.append(f"  {line}")
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

### PostToolUse hook (커밋 성사 후 회고)

`.claude/hooks/post_commit_review.py`로 작성. Bash tool이 끝날 때마다 실행되어 **HEAD sha가 직전 처리값보다 전진했는지**로 커밋 성사를 감지하고, 새 커밋이 얹혔으면 project-memory 회고 리마인더를 주입한다.

이전 설계는 "세션 종료 시 1회"였으나, Stop 이벤트는 세션 종료가 아니라 **매 턴 종료마다** 발동해 사용자 선택지(AskUserQuestion) 대기나 평범한 턴 종료에서도 오발동했고, 애초에 "세션 종료"를 훅 시점에 감지할 방법이 없었다. 그래서 회고를 **작업 한 단위가 완료되는 실제 체크포인트 = 커밋**에 묶는다. 커밋 여부를 명령 문자열로 추측하지 않고 **실제 HEAD 변화**로만 판정하므로, 문서 안 `git commit` 문자열 오탐·재실행 루프·마커 누적이 원천적으로 없다.

> **v0.8.0에서 추가**: HEAD 전진만으로는 "누가 커밋했는지" 구분하지 못해, 이 가이드 세팅을 복사한 저장소에서 스케줄러(cron/BAT 등) 자동 커밋이 "에이전트가 방금 한 작업"으로 오인되어 회고가 오발동하는 문제가 있었다. 상태를 **session_id 기준**으로 구간을 나누고, 커밋 subject 접두로 **자동커밋을 면제**해 해결한다.

동작 요약:
- HEAD가 직전 처리값과 같으면(읽기전용 명령 등) 조용히 통과.
- **세션이 바뀌면**(PostToolUse payload의 `session_id`가 상태 파일에 저장된 값과 다르면) baseline만 재설정하고 통과한다 — 지난 세션 이후(다른 세션·스케줄러 등) 쌓인 커밋은 "이번 세션 작업"으로 오판하지 않는다.
- `merge-base --is-ancestor`로 **직전 값 위에 새 커밋이 얹힌 경우만** 회고. `--amend`·`reset`·`checkout`·`rebase` 등 HEAD가 옆으로 이동한 경우는 새 작업 커밋이 아니므로 발동하지 않는다.
- 범위의 커밋이 전부 다음 중 하나면 발동하지 않는다: (1) 변경 파일이 전부 `EXEMPT_PATTERNS`에 해당 — `project-memory/**`·`.claude/**`(회고 결과·설정)와 구현 중심 확장의 진행 기록(`dev/README.md`, `dev/*/README.md`, `dev/*/*/progress.md`). **`dev/...` 패턴은 `dev/README.md` 첫 줄에 8단계 표식 `<!-- rmg: dev-cycles -->`이 있을 때만 적용한다**(표식 판정은 SessionStart 훅과 같다 — 8단계를 쓰지 않는 프로젝트의 무관한 `dev/` 폴더가 면제되지 않게), (2) 커밋 subject가 `EXEMPT_SUBJECT_PREFIXES`(기본 `"chore: auto "`)로 시작(스케줄러 자동 커밋). 경로는 `/`로 정규화한 뒤 세그먼트 단위로 비교한다(`*`는 한 세그먼트, 끝의 `**`는 그 아래 전부). **merge 커밋(부모 2개 이상)은 맨 먼저 판정해 무조건 면제하지 않는다**(사이클 승격 merge처럼 코드·설계가 한꺼번에 들어오는 커밋). 파일 목록을 판단할 수 없는 경우(빈 diff 등)도 **fail-closed**로 면제하지 않는다.
- 상태 파일(`~/.claude/commit-review-state/<repo-hash>`)에 `{"session_id", "head"}` JSON을 원자적으로(temp 파일 + `os.replace`) 저장 — 저장소당 파일 하나라 누적이 없다. 구버전 bare-sha 상태 파일은 자동으로 신포맷에 마이그레이션된다. `session_id`가 없는 환경(구버전 CC 등)에서는 세션 구분 없이 기존 head-only 동작으로 degrade한다.
- **한계**:
  - 커밋이 전혀 없는 세션(조사·설계 논의 등)은 트리거가 없다. 이런 세션의 회고는 `/compact` 시 PreCompact hook과 `handoff.md`가 담당한다.
  - **세션의 첫 Bash 호출이 곧 커밋인 경우, 그 커밋은 1회 놓친다** — 매 세션 baseline이 재설정되기 때문. "매 호출 재발동 루프"보다 "가끔 놓침"을 택한 트레이드오프.
  - 동시에 같은 저장소에서 두 Claude 세션이 커밋하면 단일 상태 슬롯을 공유해 서로 baseline을 재설정할 수 있다(오발동이 아닌 누락 방향이라 안전 쪽으로 수용).

```python
"""PostToolUse hook — 커밋 성사(HEAD 전진) 직후 project-memory 회고 유도.

Bash tool이 끝날 때마다 실행되어 HEAD sha가 직전 처리값보다 전진했는지 확인한다.
새 커밋이 얹혔으면(merge-base --is-ancestor) 회고 리마인더를 주입한다.
명령 문자열을 파싱해 "커밋인지" 추측하지 않고 실제 HEAD 변화로만 판정하므로,
문서 안 'git commit' 문자열 오탐·재실행 루프·마커 누적이 원천적으로 없다.

상태는 session_id 기준으로 구간을 나눈다(세션이 바뀌면 baseline만 재설정하고
통과) — 그래야 스케줄러 등 세션 밖에서 쌓인 커밋이 "이번 세션 작업"으로
오판되지 않는다. 또한 커밋 subject가 EXEMPT_SUBJECT_PREFIXES로 시작하면
(예: 스케줄러 자동 커밋) 면제한다. 이 훅은 강제 게이트가 아니라 리마인더이므로
접두 우회 자체를 막지는 못한다 — 더 엄격히 하려면 스케줄러 전용
author/커밋 트레일러 기준으로 좁힐 것. 저장소별로 EXEMPT_SUBJECT_PREFIXES를 조정.

한계:
- 세션의 첫 Bash 호출이 곧 커밋인 경우, 그 커밋은 baseline 설정에 흡수되어
  1회 놓친다(리마인더 훅이라 "매 호출 재발동 루프"보다 "가끔 놓침"을 택함).
  이런 세션의 회고는 PreCompact hook·handoff.md가 보조한다.
- 동시에 같은 저장소에서 두 Claude 세션이 커밋하면 단일 상태 슬롯을 공유해
  서로 baseline을 재설정할 수 있다(오발동이 아닌 누락 방향이라 안전 쪽으로 수용).
- sideways(amend/rebase/reset 등으로 얹힌 새 작업)는 의도적으로 비발동.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
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

STATE_DIR = Path.home() / ".claude" / "commit-review-state"

# ── 설정값 — 이 훅을 다시 적용(덮어쓰기)할 때 보존할 프로젝트별 값 ──
SUPPRESS_MARKER = Path.home() / ".no-commit-review"

# 회고 대상에서 면제할 경로(회고 결과·설정·진행 기록만 담긴 커밋은 재발동 안 함).
# 경로는 `/`로 정규화한 뒤 세그먼트 단위로 비교한다: `*`는 정확히 한 세그먼트,
# 끝의 `**`는 그 접두 이하 전부. (fnmatch의 `*`는 `/`도 매칭하므로 쓰지 않는다.)
# `dev/...` 패턴은 8단계(dev/README.md 첫 줄이 DEV_MARKER)를 쓰는 프로젝트에서만 적용된다.
EXEMPT_PATTERNS = (
    "project-memory/**",
    ".claude/**",
    "dev/README.md",
    "dev/*/README.md",
    "dev/*/*/progress.md",
)

# 회고 대상에서 면제할 커밋 subject 접두 — 스케줄러/봇 자동 커밋.
# trailing space로 "chore: automobile" 같은 오매치를 막는다. 저장소별로 조정.
EXEMPT_SUBJECT_PREFIXES = ("chore: auto ",)
# ── 설정값 끝 ──

# dev/README.md 첫 줄이 이 표식일 때만 8단계(사이클)를 쓰는 프로젝트로 본다.
DEV_MARKER = "<!-- rmg: dev-cycles -->"

_HEX40_RE = re.compile(r"^[0-9a-f]{40}$")


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


def _git(args: list[str]) -> str | None:
    """git 명령을 REPO_ROOT에서 실행. 실패 시 None."""
    try:
        out = subprocess.run(
            ["git", *args],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return None
    if out.returncode != 0:
        return None
    return out.stdout.strip()


def _git_ok(args: list[str]) -> bool:
    """종료코드만 필요한 git 명령(예: merge-base --is-ancestor). 성공 시 True."""
    try:
        out = subprocess.run(
            ["git", *args],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return False
    return out.returncode == 0


def _state_file() -> Path:
    repo_key = hashlib.sha1(str(REPO_ROOT).encode("utf-8")).hexdigest()[:8]
    return STATE_DIR / repo_key


def _read_state() -> dict | None:
    """상태 파일을 읽어 종류를 판정한다.

    반환: None(콜드스타트/판단불가) |
          {"kind": "legacy", "head": sha} |
          {"kind": "session", "session_id": sid, "head": sha}
    """
    try:
        raw = _state_file().read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        if _HEX40_RE.match(raw):  # 구버전 bare-sha 상태 파일
            return {"kind": "legacy", "head": raw}
        return None  # 잘림/손상 — 재설정
    if isinstance(data, dict):
        sid = data.get("session_id")
        head = data.get("head")
        if isinstance(sid, str) and isinstance(head, str) and head:
            return {"kind": "session", "session_id": sid, "head": head}
    return None


def _write_state(session_id: str, head: str) -> None:
    """상태 파일을 원자적으로 교체(임시 파일 + os.replace) — 병렬 Bash 호출로 인한
    잘린 JSON을 방지한다."""
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(dir=str(STATE_DIR))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump({"session_id": session_id, "head": head}, f)
            os.replace(tmp_path, str(_state_file()))
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
    except OSError:
        pass


def _dev_cycles_enabled() -> bool:
    """dev/README.md의 첫 줄이 DEV_MARKER일 때만 참(UTF-8 BOM·CRLF·앞뒤 공백은 무시).

    빈 줄 뒤나 본문 중간의 표식은 무효다. session_start_brief.py도 같은 판정을 쓴다.
    """
    try:
        with (REPO_ROOT / "dev" / "README.md").open(encoding="utf-8-sig") as f:
            first = f.readline()
    except (OSError, UnicodeDecodeError):
        return False
    return first.strip() == DEV_MARKER


def _path_is_exempt(path: str) -> bool:
    """경로 하나가 EXEMPT_PATTERNS 중 하나와 세그먼트 단위로 일치하는지.

    `dev/`로 시작하는 패턴은 8단계 표식이 있을 때만 적용한다."""
    segs = path.replace("\\", "/").strip("/").split("/")
    for pattern in EXEMPT_PATTERNS:
        if pattern.startswith("dev/") and not _dev_cycles_enabled():
            continue
        psegs = pattern.split("/")
        if psegs[-1] == "**":
            prefix = psegs[:-1]
            if len(segs) > len(prefix) and all(
                p == "*" or p == s for p, s in zip(prefix, segs)
            ):
                return True
        elif len(psegs) == len(segs) and all(
            p == "*" or p == s for p, s in zip(psegs, segs)
        ):
            return True
    return False


def _is_merge_commit(sha: str) -> bool | None:
    """부모가 둘 이상이면 True. 판단 불가면 None."""
    out = _git(["rev-list", "--parents", "-n", "1", sha])
    if out is None:
        return None
    return len(out.split()) > 2  # <sha> <parent1> <parent2> ...


def _commit_is_exempt(sha: str) -> bool:
    """커밋 하나가 회고 면제 대상인지: subject 접두 매치 또는 변경 파일이 전부
    EXEMPT_PATTERNS. merge 커밋(부모 2개 이상)은 맨 먼저 판정해 무조건 면제하지 않는다
    (subject·경로 면제보다 앞 — 사이클 승격 merge처럼 코드·설계가 한꺼번에 들어오는 커밋).
    파일 목록을 판단할 수 없으면(빈 diff 등) fail-closed로 면제하지 않는다."""
    merge = _is_merge_commit(sha)
    if merge is None or merge:
        return False  # 판단 불가이거나 merge → 면제 아님(회고 쪽)
    subject = _git(["log", "-1", "--format=%s", sha])
    if subject is not None and subject.startswith(EXEMPT_SUBJECT_PREFIXES):
        return True

    out = _git(["show", "--first-parent", "--format=", "--name-only", sha])
    if out is None:
        return False  # 판단 불가 → 면제 아님(회고 쪽)
    files = [ln.strip() for ln in out.splitlines() if ln.strip()]
    if not files:
        return False  # 빈 diff(merge 등) → 면제 아님(회고 쪽)
    return all(_path_is_exempt(f) for f in files)


def _range_is_exempt(last: str, current: str) -> bool:
    """last..current 의 커밋이 전부 면제 대상이면 True."""
    out = _git(["rev-list", f"{last}..{current}"])
    if out is None:
        return False  # 판단 불가 → 회고 유도 쪽으로
    shas = [ln.strip() for ln in out.splitlines() if ln.strip()]
    if not shas:
        return False
    return all(_commit_is_exempt(sha) for sha in shas)


REMINDER = (
    "[커밋 회고 — 방금 만든 커밋 단위]\n"
    "방금 커밋된 작업 단위에서 다음 세션의 에이전트에게 유용할 흔적을 project-memory/ 에 남길지 검토하세요.\n"
    "규칙은 project-memory/index.md, project-memory/insight/README.md, CLAUDE.md '메인테이너 워크플로' 섹션 참고.\n"
    "\n"
    "후보:\n"
    "- 작업 단위 한 줄 흔적(의도/시도/결과) → project-memory/log.md append\n"
    "  형식: ## [YYYY-MM-DD] <kind> | <한 줄 제목> + 본문 1~5줄.\n"
    "- 비자명한 디버깅 결론·의외의 동작 → project-memory/insight/YYYY-MM-DD-<주제>.md + index.md 등록\n"
    "- 반복적으로 부딪힐 함정 → project-memory/gotchas.md 항목 추가\n"
    "- 설계 결정의 의도 → project-memory/decisions/<topic>.md\n"
    "- 미해결 이슈/조사 중 가설 → project-memory/open-questions.md\n"
    "  (dev/ 폴더를 쓰는 프로젝트: 단위·항목 ID로 인용할 수 있으면 dev/<코드>/<단계>/open-questions.md, 아니면 project-memory/open-questions.md)\n"
    "- 미완료 작업이 남아 있으면 → handoff.md '남은 작업' 섹션에 기록\n"
    "  (dev/ 사이클 항목을 GO 뒤 커밋한 경우: 다음 착수 지점은 그 단계 progress.md가 공식 기록이고 handoff.md는 GO 전 중간 상태 전용 — 비운다)\n"
    "\n"
    "원칙: raw 코드·release-notes·git log에 이미 있는 사실은 다시 적지 않음.\n"
    "기록할 내용은 지금 작성하면 되고(다음 커밋에 함께 포함하면 됨), 남길 게 없으면 '없음' 한 줄로 답하고 진행하세요.\n"
)


def main() -> int:
    payload = _read_stdin_payload()  # 명령 문자열은 감지에 쓰지 않음 — HEAD로만 판정
    raw_sid = payload.get("session_id")
    session_id = raw_sid if isinstance(raw_sid, str) and raw_sid else None

    if SUPPRESS_MARKER.exists():
        return 0
    if not _is_repo_session():
        return 0

    current = _git(["rev-parse", "HEAD"])
    if current is None:  # 비-git / 커밋 없음
        return 0

    state = _read_state()

    if state is None:  # 콜드스타트/판단불가 — baseline만 세우고 통과
        _write_state(session_id or "", current)
        return 0

    if state["kind"] == "legacy":
        # 구버전 bare-sha 상태 — 세션 개념이 없던 값이므로 신포맷으로
        # 마이그레이션만 하고(head 일치 여부와 무관) 조용히 통과.
        _write_state(session_id or "", current)
        return 0

    stored_session_id = state["session_id"]
    last = state["head"]

    if current == last:  # HEAD 불변 — 커밋 아님
        return 0

    if session_id and stored_session_id and stored_session_id != session_id:
        # 새 세션 — 지난 세션 이후 쌓인 커밋은 회고 대상 아님. baseline만 재설정.
        _write_state(session_id, current)
        return 0

    # HEAD 변함: last 위에 새 커밋이 얹혔을 때만 회고
    if not _git_ok(["merge-base", "--is-ancestor", last, current]):
        # sideways(checkout/reset/rebase/amend 등) — 새 작업 커밋 아님
        _write_state(session_id or stored_session_id, current)
        return 0

    _write_state(session_id or stored_session_id, current)

    if _range_is_exempt(last, current):  # 회고·설정 파일·자동커밋만 담긴 범위 → 재발동 안 함
        return 0

    sys.stdout.write(json.dumps({"decision": "block", "reason": REMINDER}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**settings.json 등록** (matcher `"Bash"`로 Bash tool 호출마다 실행):

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/post_commit_review.py\""
          }
        ]
      }
    ]
  }
}
```

### PreCompact hook (압축 전 리마인더)

`.claude/hooks/pre_compact_review.py`로 작성. `/compact` 실행 직전에 실질적 파일 변경이 있었으면 project-memory 회고 리마인더를 주입한다. 커밋 회고 hook이 커밋 성사 시점을 잡는 것과 달리, 이 hook은 **커밋 없이 컨텍스트가 압축되는 경우**를 커버하며 새 편집이 있을 때마다 발동하고, `auto` 자동 압축 시에는 조용히 통과한다.

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

# ── 설정값 — 이 훅을 다시 적용(덮어쓰기)할 때 보존할 프로젝트별 값 ──
SUPPRESS_MARKER = Path.home() / ".no-pre-compact-review"
# ── 설정값 끝 ──
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
    "  (dev/ 폴더를 쓰는 프로젝트: 단위·항목 ID로 인용할 수 있으면 dev/<코드>/<단계>/open-questions.md, 아니면 project-memory/open-questions.md)\n"
    "- 미완료 작업이 남아 있으면 → handoff.md '남은 작업' 섹션에 기록 (다음 세션 SessionStart에서 자동 표시됨)\n"
    "  (dev/ 사이클 항목을 진행 중이면 handoff.md는 GO 전 중간 상태 — 구현 중·검수 대기·NO-GO 수정 중 — 전용이다. 이미 GO·커밋한 항목의 다음 착수 지점은 그 단계 progress.md에 있다)\n"
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

### PreToolUse hook — ExitPlanMode 플랜 검수 게이트

`.claude/hooks/pre_plan_exit_review.py`로 작성. 플랜 모드를 종료하려 할 때 **플랜이 독립 검수자의 GO를 받았는지**를 확인하고, 받지 않았으면 차단한다. 검수 규칙(아래)은 이 가이드를 적용한 **모든 프로젝트**에 적용되며, 구현 중심 확장(8단계)은 이 규칙을 그대로 인용한다.

**통과 조건은 하나다**: 플랜 파일의 **마지막 비어 있지 않은 줄**이 유효한 검수 기록이고, 그 줄의 본문 해시가 현재 플랜 본문(마지막 줄 제외)의 해시와 같을 것.

```
플랜 검수: GO — <검수자·회차> — 본문 <해시8>
플랜 검수: 예외(<사유>) — 사용자 승인 — 본문 <해시8>
```

- **본문 해시**: 마지막 줄을 뺀 플랜 전체를 줄바꿈 정규화(CRLF→LF)·줄 끝 공백 제거·끝 빈 줄 제거 후 SHA-1 앞 8자. 훅이 **차단할 때마다 현재 해시를 안내**한다. 그래서 GO를 받은 뒤 플랜 본문을 고치면 기록의 해시가 어긋나 다시 차단된다 — 재검수 후 해시를 새 값으로 갱신해야 한다. 흐름: 차단(해시 안내) → 검수 → (고치면 재검수) → 마지막 줄에 기록 → 재호출 통과.
- 파일 **중간**의 `플랜 검수:` 줄은 코드블록 안이든 밖이든 모두 일반 본문이다(기록으로 인정도, 해시 제외도 하지 않는다). 인용(`>`)·취소선·`GO 아님`·해시 없는 줄·`(대기)` 자리표시는 무효다. 기록 줄 아래에 내용을 덧붙이면 마지막 줄이 기록이 아니게 되어 차단된다.
- 훅은 마크다운 중 **코드블록 펜스 상태 하나**만 확인한다. 닫히지 않은 코드블록 안에 기록 줄을 쓰는 실수를 막기 위해서다(여는 줄: 앞 공백 0~3칸 + 같은 문자(`` ` `` 또는 `~`) 3개 이상, 닫는 줄: 같은 문자를 열 때 길이 이상 + 공백·탭만).
- **목표와 한계**: 목표는 *실수로* 검수 없이, 또는 낡은 GO로 통과하는 것을 막는 것이다. 올바른 해시를 가진 유효 줄을 **고의로** 쓰는 위조, 검수가 실제로 있었는지의 확인은 훅이 하지 못한다 — 그것은 에이전트와 사용자의 책임이다.
- 마커(`~/.claude/plan-review-markers/`)는 안내 문구 선택(첫 차단 = 검수 안내 전문 / 이후 = 짧은 안내)에만 쓴다. 통과 판정과 무관하므로 마커 생성 실패·7일 정리가 통과로 이어지지 않는다. 대상 플랜은 ExitPlanMode payload의 플랜 경로를 우선 쓰고, payload에 경로가 없을 때만 `~/.claude/plans/`의 최신 파일을 쓴다. payload가 지정한 파일이 없으면 다른 플랜으로 대체하지 않고 차단한다(이전 플랜의 GO로 통과하는 실수 방지).
- **플랜 파일을 확인할 수 없으면 통과시키지 않고 차단한다**: payload에도 경로가 없고 `~/.claude/plans/`에도 플랜이 없을 때, 플랜 파일을 읽지 못할 때(디렉터리 경로·잘못된 UTF-8·권한 등 모든 읽기 오류)가 그렇다. 차단 메시지가 찾아본 위치와 게이트를 끄는 방법을 알려 준다. (이 가이드를 적용하지 않은 저장소 — `project-memory/`가 없는 곳 — 에서는 게이트가 동작하지 않는다.)
- **게이트를 끄는 방법**(둘 다 의도된 방법이다): 이 저장소만 끄려면 `.claude/no-plan-exit-review` 빈 파일, 모든 저장소에서 끄려면 `~/.no-plan-exit-review` 빈 파일을 만든다. 게이트를 끄는 것은 검수를 건너뛰는 결정이므로 **이유를 `project-memory/decisions/`의 결정 파일로 남긴다**.
- **훅이 동작하지 않는 환경**(Claude Code가 아닌 다른 에이전트 도구 등): 플랜을 끝내기 전에 이 절의 검수 규칙대로 검수받고, 플랜 파일 마지막 줄에 위와 같은 기록 줄을 **직접** 남긴다. 해시는 위 "본문 해시" 정의대로 계산한다(훅이 있는 환경의 차단 메시지가 알려 주는 값과 같다). 훅이 없어도 검수 규칙(독립 검수자·GO·재검수 범위)은 그대로 적용된다.

**검수 규칙** (플랜 검수·산출물 검수·승격 검수·사이클 밖 작업 검수에 모두 적용):

- 산출물(플랜, 코드·테스트·설계 문서)을 **독립 검수자**에게 넘겨 리뷰받는다. 통과 없이 다음으로 가지 않는다.
- **심각도**: P0 = 데이터 손상·보안·되돌릴 수 없는 부작용 / P1 = 명세 위반·잘못된 동작·문서 간 모순으로 진행이 막힘 / P2 = 개선 권고(가독성·테스트 보강 등).
- **통과 = 검수자가 GO**(P0·P1 없음). NO-GO면 지적을 코드·문서로 확인해 반영 → 같은 절차로 재검수를 GO까지 반복한다. P2만 남은 GO는 반영하거나 반영하지 않는 이유를 기록한다.
- **재검수 범위는 직전 지적의 해소 확인으로 좁힌다**: 직전 지적 목록과 수정 위치를 넘기고, 판정 대상은 ① 지적이 해소됐는가 ② 그 수정이 같은 지점에 만든 회귀뿐이다. 범위 밖에서 새로 보인 결함은 GO/NO-GO에 넣지 않고 보고만 받아 미결 장부에 기록한다. 단 범위 밖 결함이 P0이고 **코드로 재현·확인된 경우에만** 새 지적으로 받아 수정한 뒤 재검수한다.
- 검수자의 지적도 **코드·실행 경로로 확인한 뒤** 반영한다(검수자 오탐 방지). 반영하지 않으면 이유를 기록한다.
- 검수 대상 변경(코드, 설계 문서, 플랜)은 **GO 전에는 커밋하지 않는다.** GO 전 중간 상태는 `handoff.md`에 남긴다.
- **검수자 우선순위**: ① **Codex** — 지정 모델이 있으면 요청 맨 앞에 `--model <모델>`을 붙이고, 실행 기록(Codex 세션 기록의 `"model"`)으로 실제 모델을 확인해 검수 기록에 남긴다 → ② **Copilot** (Codex가 없거나 사용량 한도 등으로 못 할 때) → ③ **맥락을 물려받지 않는 Claude 서브에이전트** (작성자와 같은 계열이라 독립성이 약하다 — 그 사실을 기록) → ④ **사용자 승인 예외** (위 셋이 모두 불가하면 사용자에게 알리고, 승인받으면 `플랜 검수: 예외(<사유>) — 사용자 승인 — 본문 <해시8>`).
  같은 검수자에게 다시 요청해도 장애가 계속될 때만 다음 순위로 내려간다.
- **`REVIEW_MODEL`**: 훅 상단의 설정값. 공용 기본은 빈 값(모델 미지정)이다. 값이 있으면 안내문이 검수 요청에 `--model <값>`을 넣고 실행 기록으로 확인하라고 안내한다. 모델 선택은 사용자·프로젝트의 몫이므로 가이드는 특정 모델을 기본으로 두지 않는다. 검수자 우선순위와 모델은 프로젝트 `CLAUDE.md`의 "플랜 검수" 절에 **한 번** 적고(5단계 템플릿), `REVIEW_MODEL`에는 그 절과 같은 값을 둔다. 다른 문서(8단계의 단계 README 등)는 값을 복사하지 않고 그 절을 가리킨다.

리뷰어 감지 규칙(안내 문구 선택용 — 감지 여부가 통과 여부를 바꾸지 않는다):
- 빌트인 **Codex** 플러그인 설치 → `codex:codex-rescue` (Copilot과 동시 설치 시 Codex 우선)
- **Copilot** 플러그인(`ghcopilot_plugin_for_claude`) 설치 → `copilot:copilot-rescue`
- **둘 다 없음** → 맥락 없는 Claude 서브에이전트 → 사용자 승인 예외 순으로 안내

```python
"""PreToolUse hook — ExitPlanMode 호출 시 플랜 검수 게이트.

통과 조건은 하나다: 플랜 파일의 **마지막 비어 있지 않은 줄**이 유효한 검수 기록이고,
그 줄의 본문 해시가 현재 플랜 본문(마지막 줄 제외)의 해시와 같다.

  플랜 검수: GO — <검수자·회차> — 본문 <해시8>
  플랜 검수: 예외(<사유>) — 사용자 승인 — 본문 <해시8>

- 파일 중간의 `플랜 검수:` 줄은 어디에 있든(코드블록 안이든 밖이든) 일반 본문이다.
- 마크다운은 코드블록 펜스 상태(닫히지 않은 블록 안에 기록 줄을 쓰는 실수)만 확인한다.
- 목표: 실수로 검수 없이, 또는 낡은 GO(검수 뒤 본문이 바뀜)로 통과하는 것을 막는다.
  비목표: 올바른 해시를 가진 유효 줄을 고의로 쓰는 위조, 검수가 실제로 있었는지의 확인.
"""

from __future__ import annotations

import hashlib
import json
import os
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

# ── 설정값 — 이 훅을 다시 적용(덮어쓰기)할 때 보존할 프로젝트별 값 ──
# 검수 요청에 `--model <값>`을 붙일 모델. 빈 값이면 모델을 지정하지 않는다.
# CLAUDE.md '플랜 검수' 절에 적은 모델과 같은 값으로 둔다.
REVIEW_MODEL = ""
# 게이트를 끄는 마커 — 이 저장소만(프로젝트별) / 모든 저장소(전역). 끌 때는 이유를 결정 파일(project-memory/decisions/)에 남긴다.
PROJECT_SUPPRESS_MARKER = REPO_ROOT / ".claude" / "no-plan-exit-review"
SUPPRESS_MARKER = Path.home() / ".no-plan-exit-review"
# ── 설정값 끝 ──

MARKER_DIR      = Path.home() / ".claude" / "plan-review-markers"
PLANS_DIR       = Path.home() / ".claude" / "plans"

# 플러그인 매니페스트 경로 (계정마다 codex는 .claude, copilot은 .claude-enterprise에 분리)
_PLUGIN_MANIFESTS = [
    Path.home() / ".claude" / "plugins" / "installed_plugins.json",
    Path.home() / ".claude-enterprise" / "plugins" / "installed_plugins.json",
]

# 리뷰어별 subagent_type
_REVIEWER_SUBAGENT = {
    "codex":   "codex:codex-rescue",
    "copilot": "copilot:copilot-rescue",
}

SAFE_KEY = re.compile(r"[^A-Za-z0-9_.-]")

RECORD_PREFIX = "플랜 검수:"
RECORD_RE = re.compile(
    r"^(?:- )?플랜 검수: (?:GO — \S.*?|예외\(.+\) — 사용자 승인) — 본문 (?P<hash>[0-9a-f]{8})\s*$"
)
_FENCE_OPEN_RE = re.compile(r"^ {0,3}(?P<run>`{3,}|~{3,})(?P<info>.*)$")


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


def _marker_for(plan_path: Path) -> Path:
    key = SAFE_KEY.sub("_", plan_path.stem)
    if not key:  # ".md" 등 빈 stem → 경로 해시 폴백 (충돌/공통키 방지)
        key = hashlib.sha1(str(plan_path).encode("utf-8")).hexdigest()[:16]
    return MARKER_DIR / f".plan-reviewed-{key}"


def _find_latest_plan() -> Path | None:
    if not PLANS_DIR.is_dir():
        return None
    plans = sorted(
        (p for p in PLANS_DIR.glob("*.md") if p.is_file()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return plans[0] if plans else None


def _plan_from_payload(payload: dict) -> Path | None:
    """payload의 tool_input이 지정한 플랜 파일 경로(없으면 None).

    경로가 지정됐는데 파일이 없어도 그 경로를 그대로 돌려준다 — 호출부가 다른 플랜(최신 파일)으로
    대체하지 않고 차단해야 하기 때문이다(현재 플랜이 이동·삭제됐을 때 이전 플랜의 GO로 통과하는 실수 방지).
    """
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return None
    for key in ("planFilePath", "plan_file_path", "planPath"):
        if key not in tool_input:
            continue
        value = tool_input[key]
        if isinstance(value, str) and value.strip():
            return Path(value)
        # 키는 있는데 값이 비었거나 문자열이 아님 — "경로 없음"이 아니라 잘못된 지정이므로 차단 대상으로 돌려준다.
        return Path(f"(잘못된 {key} 값: {value!r})")
    return None


def _detect_reviewer() -> str | None:
    """설치된 리뷰어를 감지한다. Codex 우선, 없으면 Copilot, 둘 다 없으면 None.

    두 매니페스트 경로를 모두 스캔하며, 파일/JSON 파싱 오류는 조용히 무시한다.
    키 형식 'name@marketplace' 에서 '@' 앞 이름만으로 판정해 marketplace 변동에 강하다.
    """
    found: set[str] = set()

    for manifest_path in _PLUGIN_MANIFESTS:
        try:
            raw = manifest_path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except Exception:
            continue

        plugins = data.get("plugins") if isinstance(data, dict) else None
        if not isinstance(plugins, dict):
            continue

        for key in plugins:
            if not isinstance(key, str):
                continue
            name = key.split("@", 1)[0].lower()
            if name in _REVIEWER_SUBAGENT:
                found.add(name)

    # Codex 우선 (Copilot은 Codex 미사용 환경의 대체제)
    if "codex" in found:
        return "codex"
    if "copilot" in found:
        return "copilot"
    return None


def _strip_trailing_blank(lines: list[str]) -> list[str]:
    out = list(lines)
    while out and not out[-1]:
        out.pop()
    return out


def _split_plan(text: str) -> tuple[list[str], str | None]:
    """플랜 텍스트를 (전체 줄들, 마지막 비어 있지 않은 줄)로 나눈다.

    줄바꿈은 LF로 정규화하고 줄 끝 공백을 제거하며, 파일 끝의 빈 줄은 버린다.
    해시 대상 본문은 `_hash_body`가 정한다.
    """
    lines = _strip_trailing_blank(
        [ln.rstrip() for ln in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    )
    if not lines:
        return [], None
    return lines, lines[-1]


def _hash_body(lines: list[str], last_is_record: bool) -> list[str]:
    """해시 대상 본문: 마지막 줄이 검수 기록이면 그 줄을 뺀 나머지, 아니면 전체.

    어느 경우든 끝의 빈 줄만 제거한다(중간의 빈 줄은 그대로) — 그래야 기록이 없을 때 안내한
    해시와, 그 아래에 빈 줄 + 기록 줄을 덧붙인 뒤의 해시가 같다.
    """
    return _strip_trailing_blank(lines[:-1] if last_is_record else lines)


def _body_hash(body: list[str]) -> str:
    return hashlib.sha1("\n".join(body).encode("utf-8")).hexdigest()[:8]


def _fence_left_open(body: list[str]) -> bool:
    """본문을 위에서 아래로 읽어 마지막에 열린 코드블록 펜스가 남아 있는지 본다.

    여는 줄: 앞 공백 0~3칸 + 같은 문자(` 또는 ~) 3개 이상. 백틱 펜스는 info에 백틱이 있으면 여는 줄이 아니다.
    닫는 줄: 앞 공백 0~3칸 + 같은 문자를 열 때 길이 이상 + 뒤에는 공백·탭만.
    그 밖의 마크다운 문맥(들여쓴 코드블록, HTML 블록 등)은 해석하지 않는다.
    """
    open_char = ""
    open_len = 0
    for line in body:
        if not open_char:
            m = _FENCE_OPEN_RE.match(line)
            if not m:
                continue
            run = m.group("run")
            if run[0] == "`" and "`" in m.group("info"):
                continue
            open_char, open_len = run[0], len(run)
        else:
            stripped = line.lstrip(" ")
            if len(line) - len(stripped) > 3:
                continue
            run = stripped.rstrip(" \t")
            if run and set(run) == {open_char} and len(run) >= open_len:
                open_char, open_len = "", 0
    return bool(open_char)


RECORD_FORMAT = (
    "   플랜 검수: GO — <검수자·회차> — 본문 {h}\n"
    "   (사용자가 검수 예외를 승인한 경우) 플랜 검수: 예외(<사유>) — 사용자 승인 — 본문 {h}"
)

REVIEW_INSTRUCTION = (
    "[플랜 검수 게이트]\n"
    "ExitPlanMode가 차단되었습니다. {reason}\n"
    "\n"
    "플랜 파일: {plan_path}\n"
    "현재 본문 해시: {h}\n"
    "\n"
    "1. {reviewer_line}\n"
    "   검수자·모델은 CLAUDE.md '플랜 검수' 절에 적힌 것을 따르세요.\n"
    "2. prompt에 플랜 파일의 내용을 포함해 검수를 요청하세요.{model_line}\n"
    "   판정: P0 = 데이터 손상·보안·되돌릴 수 없는 부작용 / P1 = 명세 위반·잘못된 동작·문서 간 모순으로 진행이 막힘 / P2 = 개선 권고.\n"
    "   P0·P1이 없으면 GO, 있으면 NO-GO. 검수자의 지적도 코드·문서로 확인한 뒤 반영하세요.\n"
    "3. NO-GO면 반영 후 같은 검수자에게 재검수를 요청하세요. 재검수 범위는 직전 지적의 해소와 그 수정이 만든 회귀로 좁힙니다\n"
    "   (범위 밖에서 새로 보인 결함은 판정에 넣지 말고 보고만 받습니다).\n"
    "4. GO를 받으면 플랜 파일의 **마지막 줄**에 아래 형식의 검수 기록을 쓰세요(해시는 플랜 본문이 바뀌면 달라집니다. 본문을 고쳤다면 재검수 후 해시를 갱신).\n"
    "{record_format}\n"
    "5. ExitPlanMode를 다시 호출하세요. 마지막 줄이 유효한 기록이고 해시가 현재 본문과 같을 때만 통과합니다.\n"
    "\n"
    "검수자 우선순위: Codex → Copilot → 맥락을 물려받지 않는 Claude 서브에이전트(독립성이 약하므로 그 사실을 기록) → 사용자 승인 예외.\n"
)


def _reviewer_line(reviewer: str | None) -> str:
    if reviewer is not None:
        return f'Agent 도구를 subagent_type "{_REVIEWER_SUBAGENT[reviewer]}"으로 호출하세요.'
    return (
        "Codex·Copilot 플러그인이 감지되지 않았습니다. 맥락을 물려받지 않는 Claude 서브에이전트(Agent 도구)로 검수하고 "
        "그 사실을 기록하세요. 그것도 불가하면 사용자에게 알리고 승인받아 예외 기록을 쓰세요."
    )


def _model_line() -> str:
    if not REVIEW_MODEL:
        return ""
    return (
        f"\n   Codex에 요청할 때는 prompt 맨 앞에 `--model {REVIEW_MODEL}`을 넣고, 검수 뒤 "
        "`~/.codex/sessions/<날짜>/` 세션 기록의 \"model\"로 실제 실행 모델을 확인해 검수 기록에 남기세요."
    )


def _block(reason: str, plan_path: Path, body_hash: str, reviewer: str | None) -> None:
    message = REVIEW_INSTRUCTION.format(
        reason=reason,
        plan_path=plan_path,
        h=body_hash,
        reviewer_line=_reviewer_line(reviewer),
        model_line=_model_line(),
        record_format=RECORD_FORMAT.format(h=body_hash),
    )
    sys.stdout.write(json.dumps({"decision": "block", "reason": message}, ensure_ascii=False))


def _first_block_for(plan_path: Path) -> bool:
    """이 플랜에 대한 첫 차단인지(안내 문구 선택용). 통과 여부와는 무관하다."""
    marker = _marker_for(plan_path)
    try:
        MARKER_DIR.mkdir(parents=True, exist_ok=True)
        os.close(os.open(str(marker), os.O_CREAT | os.O_EXCL | os.O_WRONLY))
    except OSError:
        return False
    return True


def _block_plain(message: str) -> None:
    """플랜 파일을 확인할 수 없어 검수 안내(해시 등)를 줄 수 없을 때의 차단 응답."""
    sys.stdout.write(json.dumps({
        "decision": "block",
        "reason": "[플랜 검수 게이트]\n" + message + "\n"
                  f"이 게이트를 끄려면(결정 파일에 이유를 남길 것): `{PROJECT_SUPPRESS_MARKER}`(이 저장소만) 또는 "
                  f"`{SUPPRESS_MARKER}`(전역) 빈 파일을 만드세요.",
    }, ensure_ascii=False))


def main() -> int:
    payload = _read_stdin_payload()

    if SUPPRESS_MARKER.exists() or PROJECT_SUPPRESS_MARKER.exists():
        return 0
    if not _is_repo_session():
        return 0

    plan_path = _plan_from_payload(payload)
    if plan_path is not None and not plan_path.is_file():
        # payload가 지정한 플랜 파일이 없다 — 다른 플랜으로 대체하지 않고 차단한다.
        _block_plain(f"ExitPlanMode가 지정한 플랜 파일을 찾을 수 없습니다: {plan_path}\n"
                     "다른 플랜으로 대체하지 않습니다. 플랜 파일이 이동·삭제되지 않았는지 확인하고 다시 호출하세요.")
        return 0
    if plan_path is None:
        plan_path = _find_latest_plan()  # payload에 경로가 없을 때만 최신 플랜을 쓴다
    if plan_path is None:
        _block_plain(f"플랜 파일을 찾을 수 없습니다 — ExitPlanMode가 경로를 알려주지 않았고 {PLANS_DIR}에도 플랜(.md)이 없습니다.\n"
                     "플랜을 파일로 쓴 뒤 검수를 받고 다시 호출하세요.")
        return 0
    try:
        text = plan_path.read_text(encoding="utf-8")
    except Exception as e:  # OSError뿐 아니라 UnicodeDecodeError 등 — 못 읽으면 통과시키지 않는다
        _block_plain(f"플랜 파일을 읽을 수 없습니다: {plan_path} ({type(e).__name__}: {e})\n"
                     "UTF-8 텍스트 파일인지, 다른 프로그램이 잠그고 있지 않은지 확인하고 다시 호출하세요.")
        return 0

    reviewer = _detect_reviewer()  # 안내 문구 선택에만 쓴다(없어도 통과하지 않는다)
    lines, last = _split_plan(text)

    if last is None:
        _block("플랜 파일이 비어 있습니다. 플랜을 쓰고 검수를 받으세요.", plan_path, _body_hash([]), reviewer)
        return 0

    # 마지막 줄이 검수 기록 형태가 아니면 그 줄도 본문이다 — 기록 줄이 그 아래에 덧붙으면
    # 지금 안내하는 해시가 그대로 유효해야 한다.
    body = _hash_body(lines, last.lstrip("- ").startswith(RECORD_PREFIX))
    h = _body_hash(body)

    if _fence_left_open(body):
        _block("플랜 본문에 닫히지 않은 코드블록이 있습니다 — 블록을 닫고, 검수 기록은 코드블록 밖(파일의 마지막 줄)에 쓰세요.",
               plan_path, h, reviewer)
        return 0

    m = RECORD_RE.match(last)
    if m:
        if m.group("hash") == h:
            return 0
        _block("검수 기록 이후 플랜 본문이 바뀌었습니다(기록의 해시가 현재 본문과 다릅니다). 재검수 후 기록의 해시를 현재 값으로 갱신하세요.",
               plan_path, h, reviewer)
        return 0

    if last.lstrip("- ").startswith(RECORD_PREFIX):
        _block("마지막 줄의 검수 기록이 형식 오류입니다(자리표시·`GO 아님`·해시 누락 등).", plan_path, h, reviewer)
        return 0

    if _first_block_for(plan_path):
        reason = "이 플랜은 아직 검수 기록이 없습니다. 플랜을 검수받아야 합니다."
    else:
        reason = "플랜 파일의 마지막 줄이 유효한 검수 기록이 아닙니다(GO를 받은 뒤 기록을 마지막 줄에 쓰세요. 그 아래에 내용을 덧붙이면 안 됩니다)."
    _block(reason, plan_path, h, reviewer)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**settings.json 등록:**

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "ExitPlanMode",
        "hooks": [
          {
            "type": "command",
            "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/pre_plan_exit_review.py\""
          }
        ]
      }
    ]
  }
}
```

위 설정을 기존 SessionStart/PostToolUse/PreCompact hook과 같은 `settings.json`의 `hooks` 객체에 병합한다.

> **⚠️ 등록 후 검증 필수**: plan 모드에서 ExitPlanMode를 호출했을 때 "플랜 검수 게이트" 차단 메시지(현재 본문 해시 포함)가 뜨는지 확인한다. 뜨지 않을 경우 아래 원인을 순서대로 점검:
> 1. `settings.json`에 `hooks` 등록 누락 — 파일 복사만으로는 발동하지 않는다
> 2. `hooks` 키 자체가 없거나 JSON 구조 오류
> 3. `matcher` 값이 `ExitPlanMode`와 정확히 불일치
> 4. `.claude/no-plan-exit-review`(이 저장소) 또는 `~/.no-plan-exit-review`(전역) 파일이 있음 — 게이트를 끄는 마커다
> 5. `python` 명령이 PATH에 없는 경우 (Windows에서 `py`만 있으면 `py`로, macOS·Linux에서는 보통 `python3`로 `command`의 `python`을 교체)
>
> Codex·Copilot가 없어도 게이트는 통과하지 않는다 — 대체 검수자 안내가 나오는 것이 정상이다.

---

### 세션 이월 (Handoff)

project-memory는 **영구 지식**(설계 결정, 함정, 아키텍처)을 보관한다. 반면 handoff는 **세션 간 이월** 전용으로, "지금 하던 일을 다음 세션이 이어받을 수 있게" 하는 데 초점을 맞춘다.

| | `project-memory/` | `handoff.md` |
|--|--|--|
| 수명 | 영구 (릴리즈 주기로 정리) | 임시 (이월 완료 후 초기화) |
| 내용 | 왜 그렇게 결정했나, 어떤 함정이 있나 | 어디까지 했나, 다음에 뭘 해야 하나 |
| 트리거 | 작업 세션마다 회고 | 미완료 작업이 있을 때만 |

#### 로컬/공유 정책

`handoff.md`는 **개인 세션 이월용**이므로 기본적으로 `.gitignore`에 추가해 로컬 전용으로 운영한다. 팀 전체가 공유할 사실은 `project-memory/`에 기록하고, handoff는 "나의 다음 세션"에만 전달하는 매체로 구분한다. 단일 파일이므로 **최신 이월 상태 1개만 유지**한다.

#### 구현 중심 확장(사이클)과의 경계

구현 중심 확장(8단계)의 **사이클 항목을 진행하는 동안**에는 handoff의 역할이 좁아진다:

| | 사이클 항목 진행 중 | 그 밖 (사이클 밖 작업, 확장을 쓰지 않는 프로젝트) |
|--|--|--|
| `handoff.md` | **GO 전 중간 상태 전용** — 구현 중·검수 대기·NO-GO 수정 중. 항목이 GO를 받고 커밋되면 비운다 | 이 절의 정의 그대로 — 미완료 작업 이월 |
| 다음 착수 지점 | 그 단계 `progress.md`(GO 뒤 커밋된 공식 핸드오프)가 가진다 | `handoff.md` "남은 작업" |
| 아래 트리거 ① (커밋 시점의 미완료 작업) | `progress.md` 갱신이 대신한다 | 그대로 적용 |

경계는 "사이클 브랜치(`cycle/<코드>`)에서 항목을 진행 중인가"로 기계적으로 판단한다. `/compact` 전(트리거 ②)과 되돌릴 수 없는 작업의 실패(트리거 ③)는 어느 경우에나 적용된다.

#### handoff.md 형식

프로젝트 루트에 `handoff.md`를 생성한다. `log.md`의 `handoff` kind와 동일한 5필드를 사용한다.

```markdown
# Handoff

> 미완료 작업을 다음 세션에 전달한다.

---

## 남은 작업

(현재 없음)

---

## 완료된 작업 (참고)

(이전 이월 항목의 완료 기록)
```

"남은 작업" 섹션에 내용을 기록할 때:

```markdown
## 남은 작업

### 1. 작업 제목
- **목표**: 이번 세션에서 하려던 것
- **마지막 완료**: 어디까지 됐는지
- **다음 단계**: 이어서 해야 할 것
- **차단 요소**: (있으면) 막힌 것, 조사 중인 것
- **수정 파일**: 변경한 주요 파일 목록
```

#### handoff 생성 트리거

다음 3가지 시점에 handoff.md를 갱신한다.

1. **커밋 시점에 미완료 작업이 남아 있을 때** — 커밋 회고 hook 리마인더가 project-memory 기록과 함께 handoff 갱신을 안내
2. **`/compact` 실행 전** — 컨텍스트 압축으로 전반부 맥락이 희석되므로, 압축 전에 현재 상태를 기록
3. **되돌릴 수 없는 작업 실패 시** — force push, 외부 API 배포, DB 마이그레이션 등이 실패했을 때 재시도 정보를 보존

#### Resume 프로토콜

SessionStart hook이 세션 시작 시 `handoff.md`를 자동 읽어 brief에 포함한다.

```
=== project-memory brief ===
VERSION: 0.3.7
...
[HANDOFF] 미완료 작업:
  ### 1. iShare 배포 재시도
  - **목표**: index.html 배포
  - **차단 요소**: ISHARE_TOKEN 만료
...
=== end brief ===
```

에이전트는 이 내용을 보고:
- 이월된 작업을 이어서 진행하거나
- 사용자에게 확인 후 새 작업을 시작한다

#### 완료 후 정리

이월된 작업이 완료되면 "남은 작업" 섹션을 `(현재 없음)`으로 초기화하고, 필요 시 "완료된 작업" 섹션에 요약을 옮긴다.

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

## 8단계 — 구현 중심 프로젝트 확장 (선택)

기능·시스템·콘텐츠를 **여러 번 추가하는** 구현 중심 프로젝트에서, LLM 코딩 에이전트와 **여러 세션·여러 주에 걸쳐** 계획 → 설계 → 구현을 진행할 때 쓰는 문서 구조와 절차다. 추가 하나하나를 "사이클"로 돌린다. 버전·릴리즈·project-memory·훅(1~7단계)은 그대로 쓰고, 그 위에 이 단계를 얹는다. **구현 중심이 아닌 프로젝트(문서 저장소 등)는 이 단계를 건너뛴다.**

**적용 여부는 사용자가 정한다.** 적용 계획을 세울 때(2단계 설치 체크리스트) 에이전트가 아래 기준을 보고 사용자에게 묻고, 답(적용·미적용 모두)을 `project-memory/decisions/`의 결정 파일로 남긴다. 나중에 도입하기로 하면 새 결정 파일을 만든다.
- 기능을 여러 번 추가해 나갈 계획인가
- 여러 세션에 걸치는 설계·구현 작업이 이어지는가
- 중간에 접거나 되돌릴 수 있는 작업이 생기는가

> **이 프로세스가 푸는 문제**: 수십 항목짜리 작업을 에이전트와 여러 세션에 걸쳐 진행하면
> ① 세션이 끊길 때마다 맥락이 사라지고 ② 설계가 구현 편의로 슬그머니 바뀌고 ③ 확인하지 못한 것이 흩어져 묻히고
> ④ 검수 없이 다음으로 넘어가 결함이 쌓인다. 기능을 여러 번 추가하는 프로젝트에서는 여기에
> ⑤ 진행 중인 추가 작업과 이미 완성된 시스템이 섞여, 중간에 접으면 흔적이 남는 문제가 더해진다.
> 이 단계는 이 다섯 가지를 **문서 구조 + 단계 게이트 + 사이클 격리**로 막는다.

**템플릿**: 이 단계가 만들어 넣는 문서 골격은 [`templates/dev/`](https://github.com/amurtare/release_management_guide/tree/main/templates/dev)에 있다(가져오는 방법은 아래 "템플릿 가져오기"). 이 단계의 본문은 **규칙**이고, 템플릿은 그 규칙을 따르는 빈 문서다. 대상 프로젝트에는 이 가이드 전문을 복사하지 않고, 아래 "적용 체크리스트"로 산출물만 만든다.

**전제 도구**: 본문은 Claude Code 기준이다. 다른 에이전트를 쓴다면 아래처럼 바꿔 읽는다.

| 본문 표기 | 의미 | 다른 도구라면 |
|---|---|---|
| 플랜 모드 | 코드를 쓰지 않고 조사·계획만 하고, 사용자 승인을 받아야 빠져나오는 모드 | "계획만 작성하고 승인 전 파일 수정 금지" 지시 |
| 서브에이전트 | 현재 대화 맥락을 물려받지 않는 새 에이전트(맥락을 물려받는 fork류는 핸드오프 점검·대체 검수에 쓰면 무효) | 새 세션/새 대화 |
| `CLAUDE.md` | 에이전트가 매 세션 자동으로 읽는 프로젝트 지침 | `AGENTS.md` 등 해당 도구의 지침 파일 |
| 독립 검수자 | 작성자와 다른 모델·에이전트(또는 사람) 리뷰어 | 그대로 |

### 용어

용어의 위계: **사이클 > 단계 > Phase > 항목**. 설계 대상은 **단위**라고 부른다.

| 용어 | 뜻 |
|---|---|
| **사이클(cycle)** | 기능·시스템·콘텐츠 하나를 추가하는 작업 한 벌. `dev/<개발 코드>/` 폴더 하나 + `cycle/<개발 코드>` 브랜치 하나. 시작해서 **승격** 또는 **폐기**로 끝난다 |
| **개발 코드** | 사이클의 유일한 식별자. 영문 대문자 약어 2~8자, 허용 문자 `A-Z0-9`(예: `AUTH`, 같은 시스템 재방문은 `AUTH2`). `global`은 예약어(대소문자 무관). 폐기된 코드도 재사용하지 않는다(재시도는 숫자 접미) |
| **단계(stage)** | 사이클 안의 Plan(계획)·Design(기획·설계)·Impl(구현) 셋만 가리킨다. 각 단계는 같은 구조의 폴더를 가진다 |
| **Phase** | 한 단계의 백로그(`checklist.md`)를 묶는 구간. 주로 Impl에서 쓴다 |
| **항목(item)** | 체크리스트 한 줄. 플랜 → (명세 고정) → 작업 → 검수 → 커밋을 한 바퀴 도는 작업 묶음. Design에서는 단위 하나의 상세 설계, Impl에서는 구현 백로그 한 줄 |
| **단위(unit)** | 설계·구현을 나누는 대상. 워크플로라면 실행 노드, 앱이라면 기능·모듈, 라이브러리라면 API 묶음 |
| **단위 ID** | `<개발 코드>-<ID>`(예: `AUTH-U3`). 문서끼리 서로 인용하는 키. 안정 식별자라 재번호화하지 않는다. 사이클 밖에서 생긴 단위(초기 global 포함)는 `GLOBAL-U<n>`으로, global map에서 이어 번호를 매긴다 |
| **global** | `dev/global/` — **구현이 완료된 것까지 반영한**(기본 브랜치에 들어간: 승격된 사이클 + 사이클 밖 작업) 시스템의 현재 설계. 코드 쪽 global은 기본 브랜치 |
| **승격** | 끝난 사이클의 설계를 `dev/global/`에, 코드를 기본 브랜치에 한 시점에 합치는 것 |
| **폐기** | 사이클을 접는 것. 브랜치를 병합하지 않으므로 기본 브랜치·`dev/global/`에 흔적이 남지 않는다 |
| **사이클 밖 작업** | **사용자가 사이클로 하지 않기로 고른** 작업. 기본 브랜치에 직접 한다(원인이 분명한 국소 수정은 묻지 않고 여기에 속한다) |
| **설계 지도** | 한 범위의 모든 단위를 한 표에 늘어놓은 문서 `map.md`. 사이클 것(`design/map.md`, 바뀔 모습)과 global 것(`dev/global/map.md`, 현재 모습)이 있다 |
| **GO / NO-GO**, **P0·P1·P2** | 검수 결과와 심각도 — 7단계 "PreToolUse hook — ExitPlanMode 플랜 검수 게이트"의 검수 규칙 |
| **승격 검수** | 승격 직전, 기본 브랜치를 받은 결과와 global 반영분을 검수하는 것 |
| **외부 리뷰 보강** | Plan·Design 단계에서 독립 검수자가 낸 지적 중 아직 설계에 반영하지 않은 것의 목록(`design/checklist.md`). 누락 없이 반영해야 Design 완료 |
| **구획** | 미결 장부(`open-questions.md`)를 성격별로 나눈 묶음. 문자 하나(A, B, …)가 장부 ID의 접두사가 된다(`B3`) |
| **스모크** | 실제 환경에서 짧게 돌려 보는 확인. 부작용이 있으면 원상복구까지 한 세트 |
| **preflight** | 부작용 때문에 미리 검증하지 못하고 "첫 실사용 때 확인"으로 넘긴 항목 |
| **역전파** | 하위 문서를 바꾼 뒤 그 내용을 요약·인용하는 상위 문서에 되돌려 반영하는 것 |
| **핸드오프** | 다음 세션이 이 세션의 맥락 없이 이어받을 수 있게 남기는 상태 기록 |
| **공용 참조** | 독립 단위로 두지 않고 여러 단위가 함께 인용하는 규칙·모듈 |
| **확정 전제** | 구현 시작 시점에 고정하는 프로젝트 조건 — 절대 규칙·언어/런타임·외부 시스템·실행 환경 제약·스모크 표준 대상·검수자. `dev/<코드>/impl/README.md`에 둔다 |
| **구현 준비 상태 점검** | Design → Impl 전환 직전에 한 번 하는 세션 |

### 사이클 구조와 폴더

```
 기본 브랜치 (= 코드 global — 완료된 것만: 승격된 사이클 + 사이클 밖 작업)
 ├─ dev/README.md        진입점 · 사이클 표 · "승격 완료" 목록
 ├─ dev/global/          현재 설계(as-is) — 완료된 것까지
 ├─ dev/_CODE_/          사이클 폴더 템플릿(적용 때 가져와 보관)
 └─ 코드
        │  사이클 시작: 기본 브랜치에 표 행 등록 → 브랜치 생성
        ▼
 cycle/AUTH 브랜치
 └─ dev/AUTH/
    ├─ README.md          현재 단계 · 사이클 개요
    ├─ plan/   ─→  design/   ─→  impl/        (같은 구조의 단계 폴더)
    │   무엇·왜      바뀔 설계(to-be)    항목별 구현·검수
        │
        ├─ 승격: 기본 브랜치를 받아 재검증 → 기본 브랜치 병합 + dev/global/ 반영 → (릴리즈 여부 확인)
        └─ 폐기: 병합하지 않음 → 기본 브랜치·global 무영향 → archive/AUTH 태그
```

- **사이클은 한 번에 하나만 진행한다.** 동시에 둘이 돌지 않으므로 사이클끼리의 설계 충돌·병합 충돌이 생기지 않는다. 새 사이클은 진행 중인 사이클이 승격되거나 폐기된 뒤에만 시작한다(판정: `dev/README.md` 사이클 표).
- **보류는 없다.** 사이클의 끝은 승격(완료) 또는 폐기 둘뿐이다.
- **global은 "구현이 완료된 내용 중 최신"이다.** 진행 중인 사이클의 설계는 사이클 폴더에만 있고, 승격 때 한 번에 global로 들어간다(사이클 밖 작업이 설계 서술을 바꿨다면 그 커밋에서 global도 고친다). 완료된 사이클의 문서는 **당시의 기록**으로 동결된다.
- **코드도 같은 구조다.** 기본 브랜치가 코드 global(완료된 것만 — 승격된 사이클과 사이클 밖 작업)이고, 사이클 코드는 `cycle/<코드>` 브랜치에만 있다. 그래서 폐기는 "그 브랜치를 병합하지 않는 것"으로 끝나고, 사이클 도중의 릴리즈에 미완성 코드가 실리지 않는다.
- **사이클 브랜치는 global 병합(승격)·폐기의 단위다. 검수·커밋 규칙을 완화하는 수단이 아니다** — 브랜치 안에서도 검수 GO 전에는 커밋하지 않는다.

구현만 잘 굴려도 **앞단이 흔들리면 구현 중에 설계가 계속 뒤집힌다.** 그래서 사이클 안의 Plan·Design도 Impl과 같은 원리(저장소 안 문서가 기억 · 확정과 미결의 분리 · 단계 게이트)로 굴린다. 구현 중 설계와 어긋나면 design을 고치고 plan까지 역전파한다.

**세 단계 폴더는 같은 레벨이고 같은 구조를 가진다.** 모든 단계가 한 세션에 끝난다는 보장이 없으므로, 각 단계가 자기 진입점·백로그·미결 장부·핸드오프 로그를 따로 갖는다.

| 위치 | 성격 | 고유 문서 | 무엇의 단일 소스인가 |
|---|---|---|---|
| `dev/README.md` | `dev/` 전체 진입점 | 사이클 표, "승격 완료" 목록 | 어떤 사이클이 있고 어디서 진행 중인가 |
| `dev/global/` | 현재 설계(as-is) | `overview` · `map` · `<개념>-design` | **구현 완료분의 설계** |
| `dev/<코드>/README.md` | 사이클 진입점 | 현재 단계 필드, 사이클 개요 | 이 사이클의 현재 단계 |
| `dev/<코드>/plan/` | 무엇을·왜·경계 | `overview` | 이 사이클의 목적·확정 결정 |
| `dev/<코드>/design/` | 바뀔 설계(to-be) | `map` · `<개념>-design` | **이 사이클 구현의 기준 설계** |
| `dev/<코드>/impl/` | 구현 실행 관리 | — | "어디까지 만들었나" |
| `dev/<코드>/evidence/` | 증거·실측 | 스크린샷·전사·실측 절차 | 근거 보관 |
| `project-memory/` | 팀 공용 기록(1~7단계 구조) | `decisions/` · `gotchas` · `log` · `open-questions` 등 | 왜 그렇게 정했나·반복 함정 |

각 단계 폴더(plan·design·impl)의 **공통 4문서**:

| 문서 | 역할 |
|---|---|
| `README.md` | 그 단계 새 세션의 **유일한 진입점**. 읽는 순서·전제·진행 방식 |
| `checklist.md` | 그 단계의 백로그(Phase·항목 체크박스) + 항목별 승인된 명세 |
| `open-questions.md` | 그 단계의 미결·미검증 장부 |
| `progress.md` | "다음 착수 지점" + 날짜별 완료 로그. **GO 뒤 커밋된 시점의 공식 핸드오프** |

- **`plan/`에는 설계 문서를 만들지 않는다.** 설계는 `design/`, `plan/`은 개요·진행관리만 둔다 — 섞이면 어느 쪽이 설계의 소스인지 흐려진다.
- **단위 ID와 파일 번호는 안정 식별자다.** 단위를 합치거나 지워 번호에 구멍이 생겨도 재번호화하지 않는다. 다른 문서가 ID로 인용하므로 재번호화는 무관한 대규모 참조 수정을 부른다. 파일명은 번호보다 의미 이름을 권장한다.
- **외부 조망도(화이트보드 사진·위키 흐름도)는 비규범**이다. 설계 지도와 달라도 되지만, 그 차이로 무엇이 달라지는지(어느 단위가 책임을 넘겨받는지, 단위 사이 흐름이 어떻게 바뀌는지, 중단 후 다시 시작할 때 영향)를 적은 경우에만 허용한다. **외부에 부작용을 내거나, 안전 검사·사람 확인·대기를 맡은 단위를 합치거나 지우는 것은 별도 결정 없이 금지**(순수 계산 단위끼리 합치는 것만 허용).
- 문서를 HTML 등으로 시각화했다면 그것은 **파생물**이다. 원천 md가 바뀌면 시각화를 맞춘다(반대 아님).

**저장소의 폴더 구조**

```
<project>/
├─ CLAUDE.md                 # 에이전트 지침 — 이 프로세스를 가리키기만 한다 (아래 스니펫)
├─ src/ …                    # 코드 (기본 브랜치 = 완료된 것만)
├─ project-memory/           # decisions/ · gotchas · log · open-questions · components …
├─ handoff.md                # 로컬 전용(.gitignore) — GO 전 중간 상태 (세션 이월 절의 경계 참고)
└─ dev/
   ├─ README.md              # dev/ 진입점: 사이클 표 + "승격 완료" 목록
   ├─ global/                # 현재 설계(as-is) — 완료된 것까지: 승격된 사이클 + 사이클 밖 작업 (overview · map · <개념>-design · retired/)
   ├─ _CODE_/                # 사이클 폴더 템플릿 — 사이클 시작 때 <코드>/로 복사 (사이클 코드가 아님)
   └─ <코드>/                # 사이클 하나 (cycle/<코드> 브랜치에서만 존재·변경, 승격 후 동결)
      ├─ README.md · plan/ · design/ · impl/ · evidence/
```

**우선순위 규칙**
- 저장소의 현재 상태(설계 문서·코드)가 항상 진행 기록(`progress`·`open-questions`)·`project-memory/` 기록보다 우선한다. 기록이 현재 상태와 충돌하면 기록을 갱신한다.
- **설계 문서와 코드가 서로 어긋나면 설계 문서가 기준**이다(사이클 안에서는 사이클 설계, 사이클 밖에서는 `dev/global/`). 코드를 설계에 맞추거나, 설계를 바꿔야 한다면 사용자와 의논해 확정한 뒤 설계 문서를 고치고 상위 계획으로 역전파한다. 어느 쪽이든 진행 기록만 고쳐 맞추지 않는다.
- **`project-memory/components.md`와 `dev/global/`의 경계**: 7단계 "components.md"의 경계 문구를 따른다(논리 설계는 `dev/global/`, 물리 구조는 `components.md`).

### Plan 단계 — "무엇을 만들고 무엇을 모르는가"를 고정한다

**목적**: 이 사이클의 큰 흐름을 확정하고, 확정된 것과 미결을 갈라 놓아 이후 세션이 단위별로 이어받게 한다. 한 세션에 완성하려 하지 않는다 — `plan/`의 4문서가 핸드오프 역할을 한다.

**산출물**: `plan/README.md`(진입점·원천 자료 목록·실측 근거 요약·**폐기된 초기 가설 목록**) · `plan/overview.md`(목적 · 아키텍처(구성요소·소유 경계, `dev/global/`의 어디를 바꾸나) · **배치 기준** · 운영 모델 · 확정 결정·사실) · `plan/checklist.md`(① 역전파 체크리스트 ② **확정**(재논의 불필요) ③ 남은 일) · `plan/open-questions.md`(① 확보할 자료·실측 ② 남은 결정 논점) · `plan/progress.md`.

**절차**
1. **원천 자료 수집** — 규칙 문서·위키·흐름도·기존 가이드를 저장소에 모으고 경로를 README에 적는다. `dev/global/`의 현재 설계도 원천이다.
2. **구성요소 분해와 배치 기준 확정** — 무엇을 독립 구성요소로 두고 무엇을 공용 모듈·인라인으로 둘지의 기준을 **문장으로** 남긴다. 그래야 나중 판단이 흔들리지 않는다.
3. **확정과 미결 분리** — 사용자와 합의한 것만 "확정"에 넣는다. 에이전트의 추론은 확정이 아니다.
4. **실측이 필요한 가정을 뽑아 `open-questions`로** — 외부 시스템 접근·권한·데이터 포맷처럼 "된다고 들은 것"은 실측 대상이다.
5. **폐기된 초기 가설을 취소선으로 명시** — "이 문서는 최종 결정만 담는다. 아래는 되살리지 말 것".
6. **설계할 단위 목록을 `design/checklist.md`로 넘긴다** — 단위별 "결정할 것"을 적어 Design 단계의 백로그로 만든다.
7. **종료 조건**: 확정 목록, `design/checklist.md`의 단위별 상세화 대기 목록, 실측 계획, 진입점 README.

### Design 단계 — 단위별로 플랜 모드를 다시 켜서 상세 설계를 만든다

**원칙**: 단위 하나(= Design의 항목 하나)당 플랜 모드를 새로 켜고, `design/checklist.md`의 해당 항목을 근거로 **그 단위의 상세 설계를 `design/<개념>-design.md`로** 작성한다(번호 없는 개념명). 설계 문서는 **개념 하나당 하나**다 — 서로 맞물린 단위 여러 개는 한 문서에 함께 담고, 설계 지도의 "참조" 칸이 모두 그 문서를 가리킨다. 기존 시스템을 바꾸는 단위라면 `dev/global/`의 해당 개념 문서를 출발점으로 삼고, 바뀔 모습을 사이클 문서에 쓴다. 플랜 모드에서는 파일을 쓰지 않으므로, 플랜에 설계 내용(초안)을 담아 승인받은 뒤 플랜 모드를 나와 설계 문서로 옮겨 쓴다.

**한 항목(단위 설계)의 절차**
1. `design/checklist.md`에서 단위 하나 선택(의존 순서 — 앞 결정이 뒤의 전제를 바꾸는 것부터).
2. 읽기·조사 + 필요한 **실측**. 사용자가 정할 것은 텍스트로 단계적으로 묻는다(설계 수호 규칙).
3. 설계 문서 작성(템플릿 `design/_concept_-design.md`).
4. **독립 검수**(GO까지 반복) → 지적을 문서·코드로 확인해 반영, 반영하지 않으면 이유를 기록.
5. **역전파 체크리스트** 수행 — 설계 지도·overview·open-questions에 반영.
6. `design/checklist.md` 항목을 `[x]`로 하고 **한 단락 요약 + 설계 문서 링크**를 남긴다. `design/progress.md`에 로그·다음 착수 지점.
7. 비자명한 결정·함정은 `project-memory/`에(사이클 브랜치에 기록된다).
8. **커밋·푸시**(사이클 브랜치) — 설계 문서·역전파한 문서·checklist 요약·progress·`project-memory/` 기록을 **한 커밋**으로. **검수 GO 전에는 커밋하지 않는다.** 그 뒤 핸드오프 점검.

**설계 지도(`design/map.md`)는 이 사이클 설계의 단일 소스**다. 단위마다 한 행: ID · 단위 · 참조(상세 설계 문서 경로) · 처리(한 줄 요지) · global 관계(신규 / `dev/global/`의 어느 단위·문서를 바꾸나 / `제거: <global 단위 ID>` / `대체: <옛 ID> → <새 ID>` — 제거·대체는 승격 때 퇴역으로 처리된다) · **구현 구분** · *(워크플로형)* 순서·분기 · *(워크플로형)* 담당. **"구현 구분" 열이 Design → Impl 계약**이다 — `impl/checklist.md`는 이 열을 Phase로 편성한 것이며, 이 칸에는 "만들 모듈·API와 그 입출력 계약"을 적는다.

**종료 조건**: `design/checklist.md`의 단위 항목 전부 `[x]`, 외부 리뷰 보강 전건 반영, `design/open-questions.md` 전건 해소 또는 preflight로 명시 이관.

### 실측(Evidence) 규칙 — 설계 가정을 사실로 만든다

- **사용자 진술·간접 증거는 검증이 아니다.** 설계가 기대는 외부 시스템(인증·API·메시징·권한)은 직접 호출해 확인한다. "검증됨"이라 적힌 문구의 실체가 진술뿐인 경우가 구현 직전 점검에서 흔히 드러난다.
- **읽기 전용 실측 먼저.** 부작용이 있는 쓰기(알림 발송·리소스 생성)는 **의도적으로 미검증으로 남기고** preflight로 넘긴다 — 그 사실과 이유를 문서에 적는다.
- **가설을 반증한 실측도 기록한다.**
- 증거는 `dev/<코드>/evidence/`에 파일로 남긴다. 나중에 방식이 바뀌어도 **당시 기록 보관용**이라고 머리에 적고 지우지 않는다. 외부 서버·문서는 시간이 지나면 바뀌므로 실측 결과에는 날짜를 적는다.
- 실측 결과가 확정 결정을 뒤집으면 관련 문서(역전파 grep)를 고치고, 결정 기록은 **새 결정 파일** `project-memory/decisions/<주제>.md`로 남긴다. 뒤집힌 옛 결정 파일에는 맨 위에 `> **Superseded by**: [새 파일](…)` 한 줄만 단다(7단계 decisions 규칙).

### 역전파 — 문서가 서로 어긋나지 않게

**역전파 체크리스트**(템플릿 `plan/checklist.md` 맨 위) — 단위를 상세화할 때뿐 아니라 확정 항목의 상태·성격을 바꿀 때도 매번 복사해 체크한다.

- [ ] 이 변경으로 바뀐 결정이 있는가? (없으면 종료)
- [ ] **★ 식별자 grep 역전파** — 바꾼 단위·항목의 ID와 관련 파일명을 `dev/<코드>/`·`project-memory/` 전체에서 grep해 **인용처를 빠짐없이 갱신**한다. 가장 잘 빠지는 곳: 다른 설계 문서의 상호 참조, ID를 나열한 요약 표
- [ ] 사이클 설계 지도의 해당 행 한 줄 요지 갱신(또는 "변경 없음" 확인)
- [ ] `plan/overview.md`의 확정 사실·전제에 영향이 있는가
- [ ] 해당 단계 `open-questions.md`의 해소·신규 발생 반영(건수 표기 포함)
- [ ] 설계 지도의 "참조" 칸이 실제 문서를 정확히 가리키는가

**대체 표식 (`dev/` 문서 본문 전용)**: `dev/` 문서(plan·design·global)의 본문에서 결정이 뒤집히면 옛 서술을 지우지 말고 `~~옛 서술~~ [대체됨 YYYY-MM-DD: 새 내용 — 링크]`로 남긴다. 본문은 현재 서술 위주로 둔다. **`project-memory/decisions/`에는 대체 표식을 쓰지 않는다** — 결정 파일 본문은 수정하지 않고, 뒤집히면 새 결정 파일 + `Superseded by` 연결.

**global의 예외**: global에서 **제거·대체된 단위**는 대체 표식 대신 `dev/global/retired/`로 이동한다(승격 절차 2번). 이동하는 것은 그 단위의 map 행과 그 단위에 대한 서술뿐이고, 같은 개념 문서의 **현역 단위 서술은 그대로** 둔다. 현역 단위의 결정이 뒤집힐 때는 이 예외가 아니라 위 규칙 그대로(global 본문도 대체 표식).

### 단계 전환 게이트

| 전환 | 통과 조건 |
|---|---|
| Plan → Design | 확정 목록 · `design/checklist.md`의 단위별 상세화 대기 목록 · 폐기 가설 명시 · 진입점 README |
| Design → Impl | **설계 완료 범위**(기본 A: 모든 단위 / 선택지 B: 첫 슬라이스에 속한 단위)의 `design/checklist.md` 항목 `[x]` · 그 범위의 외부 리뷰 보강 반영 · 그 범위의 `design/open-questions.md` 해소 또는 preflight 이관 · 역전파 grep 잔존 0, 그리고 **"구현 준비 상태 점검" 세션** 완료: ① 가정 실측 ② 문서 간 어긋남(취소선 누락·옛 서술 혼재) 0 ③ `impl/README.md`의 확정 전제 작성 ④ `impl/checklist.md`가 설계 지도의 "구현 구분" 열을 Phase로 편성 |
| Impl 중 설계 충돌 | 구현이 설계와 어긋나면 `impl/`이 아니라 **design을 고치고** plan까지 역전파 — 단, 사용자와 의논한 뒤에만 |

- **단계 전환 때 미해소 미결은 다음 단계 장부로 이관한다.** 옮긴 항목은 새 장부에 그대로 적고, 원래 장부의 그 항목에는 `[이관 YYYY-MM-DD → <단계>/open-questions.md <ID>]`를 남긴다. 전환할 때마다 사이클 README의 "현재 단계"를 갱신한다.
- **설계 완료 범위 — 기본(A)과 선택지(B)**: **A(기본)** 그 사이클의 모든 단위 설계를 끝낸 뒤 구현에 들어간다. 구현 중 설계가 뒤집힐 위험이 가장 적다. "수직 슬라이스 우선"은 이 경우 구현 순서에만 적용된다. **B(선택지)** 첫 슬라이스에 속한 단위만 설계를 끝내면 구현에 들어간다. 빨리 시작할 수 있지만 **검증되지 않은 방식**이다 — 나머지 단위의 설계가 이미 만든 구현을 바꿀 수 있으므로 그런 변경은 그 항목 플랜에서 사용자와 정하며, 다음 슬라이스로 넘어갈 때마다 같은 조건을 다시 적용한다. 채택 여부는 사용자가 정한다.

### 사이클 생애 — 시작 · 진행 · 승격 · 폐기

**기본 브랜치에 대한 커밋·푸시는 모두 사용자 허락 후에 한다**(시작 등록·승격·폐기 기록 포함). 사이클 브랜치 안의 커밋·푸시는 항목 루프 흐름대로 검수 GO 뒤에 진행한다.

**시작**
1. 진행 중인 사이클이 없는지 `dev/README.md` 사이클 표로 확인한다(있으면 시작하지 않는다).
2. 개발 코드를 정한다: 형식 확인, 예약어 `global` 금지(대소문자 무관), 표(승격·폐기 포함)·기존 `dev/` 폴더·`archive/*` 태그와 중복 금지. (`_CODE_`는 템플릿 폴더 이름이라 코드 형식에도 맞지 않는다.)
3. **기본 브랜치에 등록 커밋**(사용자 허락): `dev/README.md` 표에 행 추가 — 코드·이름·상태 `진행 중`·브랜치 `cycle/<코드>`·시작일.
4. `cycle/<코드>` 브랜치를 만들고 `dev/_CODE_/`(적용 때 가져와 보관한 템플릿)를 복사해 `dev/<코드>/`를 만든다. 사이클 README의 현재 단계 = Plan.

**진행**
- 사이클의 문서·코드·`project-memory/` 기록은 모두 사이클 브랜치에 커밋한다. 커밋 회고 훅도 그대로 쓴다.
- 사이클 도중 기본 브랜치의 변경(사이클 밖 작업)을 받아 올 의무는 없다. 사이클이 그 수정을 직접 필요로 할 때만 받는다. 받을 때는 승격 1번과 같은 방식(`--no-commit` merge → 테스트 + merge로 바뀐 부분 검수 → GO 뒤 커밋)을 쓴다. *(푸시된 사이클 브랜치를 rebase하면 강제 푸시가 필요하므로 merge를 권한다.)*
- "현재 단계"는 사이클 README가 가진다. 기본 브랜치의 표는 시작·종료 때만 바뀐다.

**승격** — Impl의 마지막 항목이 GO를 받고 커밋된 뒤
0. **완료 확인**(설계 완료 범위가 A든 B든 맨 먼저): `design/map.md`의 **모든 행**이 `design/checklist.md`·`impl/checklist.md`에서 `[x]`이거나, 사용자 결정으로 이 사이클의 범위에서 뺀 것(map 행에 대체 표식 + 근거)인지 확인한다. 남은 행이 있으면 승격하지 않는다.
1. 기본 브랜치를 사이클 브랜치로 **커밋하지 않고** merge한다(`git merge --no-commit --no-ff <기본 브랜치>`, 기본 브랜치 변경이 없으면 생략). 충돌은 이 작업 트리에서 해소한다. merge 커밋은 아직 만들지 않는다 — 검수 GO 전 커밋 금지.
2. **global 반영**(같은 작업 트리에서): 사이클의 `overview`·`map`·`<개념>-design.md` 내용을 `dev/global/`의 해당 문서에 병합한다(global에 없는 개념이면 새 문서). global map의 행을 사이클 map 기준으로 갱신한다. 사이클 폴더의 설계 문서 맨 위에 `> 승격됨 YYYY-MM-DD → dev/global/…`을 달고 이후 수정하지 않는다(동결).
   - **퇴역**: 사이클 map의 "global 관계"가 `제거: <ID>`·`대체: <옛 ID> → <새 ID>`인 global 단위는 행을 갱신하는 대신 퇴역시킨다. 그 단위의 global map 행과 그 단위에 대한 개념 서술**만** `dev/global/retired/YYYY-MM-DD-<개발 코드>.md`로 옮기고(머리에 제거일·사유·대체 단위·사이클 링크), global map 아래 "퇴역 단위" 목록에 그 파일 링크를 추가한다. 같은 개념 문서의 현역 단위 서술은 그대로 둔다.
   - 퇴역한 단위 ID를 `dev/`·`project-memory/` 전체에서 grep해 인용처를 갱신한다(역전파). **퇴역한 ID는 다시 쓰지 않는다**(재사용 금지).
3. **전체 테스트 + 승격 검수**: 검수 범위는 ① 기본 브랜치 merge로 바뀐 부분 ② global 반영분이다(재검수 범위 한정 규칙 준용). 기본 브랜치 변경이 없었다면 ①은 비고, 사이클 마지막 항목의 GO가 그대로 유효하다. GO까지 반복한다.
4. **GO 뒤에** 1~2번 결과를 사이클 브랜치에 한 커밋으로 남긴다(기본 브랜치를 받았다면 이 커밋이 merge 커밋이 된다).
5. **사용자 허락** 후 기본 브랜치에 병합한다. 같은 시점에 `dev/README.md` 표의 상태를 `승격 완료`·완료일로 바꾸고 "승격 완료" 목록에 코드를 추가한다.
6. **릴리즈 여부를 사용자에게 묻는다.** 릴리즈는 사이클과 독립이다 — 지금 하지 않으면 다음 승격·사이클 밖 작업 때 묶어서 한다. 릴리즈 절차는 3단계 업데이트 체크리스트를 따른다.

**폐기** — 폐기 기록은 기본 브랜치 커밋이므로 사용자 허락이 필요하다
1. **기본 브랜치에 폐기 기록**(사용자 허락): `dev/README.md` 표의 상태를 `폐기`로, 완료일 칸에 폐기일과 사유 한 줄.
2. 사이클 브랜치의 `project-memory/` 기록 중 **사이클과 무관하게 유효한 것**(외부 시스템·환경 함정, 교훈)을 기본 브랜치의 `gotchas.md` 등으로 옮긴다. 폐기 사유는 `project-memory/decisions/`에 결정 파일 1건으로 남긴다.
3. 사이클 브랜치 끝에 `archive/<코드>` 태그를 달고(원격에도 push), 브랜치를 지운다. 옮기지 못한 기록·시도한 설계와 코드는 이 태그에서 다시 꺼낼 수 있다.
4. 폐기된 개발 코드는 재사용하지 않는다. 같은 기능을 다시 시도하면 숫자를 붙인 새 코드로 시작한다(예: `AUTH2`).

### 사이클 밖 작업 — 사용자가 사이클로 하지 않기로 고른 작업

**사이클 밖 작업은 사용자가 사이클로 하지 않기로 고른 작업이다.** 작업의 크기·종류(버그 수정이든 작은 기능이든)로 정하지 않는다 — 구현 중심 프로젝트에서도 곁가지 구현이나 급한 수정은 사이클 없이 하는 편이 맞을 수 있다. 사이클은 한 번에 하나이고 보류가 없으므로, 사이클 진행 중에 생긴 일도 사이클 밖에서 처리할 수 있다. (이 구분은 SemVer의 MAJOR·MINOR·PATCH와 무관하다 — 버전 번호는 1단계 규칙대로 정한다.)

- **작업을 시작할 때(플랜 모드) 에이전트가 사이클로 할지 묻는다.** 묻는 기준: ① 여러 세션에 걸치는가 ② 설계 지도의 단위를 새로 만들거나 구성을 바꾸는가 ③ 중간에 접을 수 있는 작업인가. 사용자의 선택과 이유는 플랜에 적고, 작업을 마칠 때 `project-memory/log.md`에 남긴다.
- **묻지 않는 경우**: 원인이 분명한 국소 수정(오탈자, 한 곳의 명백한 결함)은 묻지 않고 사이클 밖에서 한다. 이때는 플랜 모드를 생략할 수 있다(아래). 검수는 아래 표를 따른다 — 코드·설계 판단이 없는 오탈자·문서 한 줄만 검수 불필요이고, 결함 수정은 커밋 전 검수 GO가 필요하다.
- 기본 브랜치에 직접 커밋한다. 그 수정이 `dev/global/`의 설계 서술(동작·인터페이스)을 바꾸면 **같은 커밋에서 `dev/global/`도 고친다.** 사이클 밖에서 생긴 설계 단위는 global map에 `GLOBAL-U<n>`으로 등록한다(용어 표 "단위 ID"). 처음 `dev/global/`을 채우는 일도 사이클 밖 작업이다.
- **커밋 전 독립 검수 GO는 필수다**(아래 표의 코드·설계 판단 없는 오탈자·문서 한 줄은 제외). 기본 브랜치는 완료분이고 사이클의 승격 검수 같은 완충 지점이 없으므로, 커밋 전 검수가 유일한 관문이다.
- **플랜 모드**: 사이클 밖으로 하기로 한 작업도 코드 판단이 필요하면(원인 분석이 필요하거나, 여러 파일·모듈에 걸치거나, 동작을 어떻게 바꿀지 판단이 필요한 수정) 플랜 모드부터 들어간다. 원인이 분명한 국소 수정만 플랜 모드 없이 수정 → 검수 GO → 커밋한다.
- **커밋·푸시는 사용자 허락 후에 한다.**
- 기록은 `project-memory/`에 한다(사이클 ID로 인용할 수 없으므로 — 미결 장부 경계 규칙). 산출물 검수 기록은 `log.md` 작업 항목의 `검수:` 줄에 남긴다.
- 사이클 밖 작업이 진행 중인 사이클이 고치는 코드와 겹치면, 그 충돌은 승격 절차 1번(기본 브랜치 merge)에서 해소한다.

**기본 브랜치 커밋의 검수 필요 여부**

| 커밋 | 검수 | 사용자 허락 |
|---|---|---|
| 8단계 골격 도입(템플릿 그대로) | 불필요(템플릿 수정·global 채움부터 검수 대상) | 필요 |
| 사이클 밖 작업(코드·설계 서술) | 필요 | 필요 |
| 승격(기본 브랜치 병합) | 필요(승격 검수, 브랜치에서 GO) | 필요 |
| 사이클 시작 등록 · 폐기 기록 | 불필요(진행관리 기록) | 필요 |
| 릴리즈(버전·릴리즈 노트·태그) | 불필요(포함된 변경은 이미 검수됨) | 필요 |
| 오탈자·문서 한 줄(코드·설계 판단 없음) | 불필요 | 필요 |

### 핵심 원칙 (한 장 요약)

| # | 원칙 | 한 줄 이유 |
|---|---|---|
| 1 | **저장소 안 문서가 유일한 기억이다** | 대화·PC·저장소 밖 플랜 파일은 다음 세션이 보장받지 못한다 |
| 2 | **모든 항목은 산출물 전에 플랜 모드부터** | 플랜 검수가 작업 전에 설계 구멍을 잡는다(오탈자와 사이클 밖의 원인이 분명한 국소 수정만 예외) |
| 3 | **승인된 상세 명세는 작업 전에 저장소에 고정한다** | 한 줄 요약만 있으면 새 세션이 결정을 놓친다 |
| 4 | **검수는 커밋 게이트, 통과 = GO까지 반복** | 1회 검수로 끝내면 결함이 다음 항목으로 샌다 |
| 5 | **미결은 단계마다 장부에 적고 해소되면 지운다** | 흩어지면 코드 결함까지 묻힌다 |
| 6 | **추론은 확인받고, 설계는 의논 없이 바꾸지 않는다** | 편의로 바꾼 설계는 승인까지 받고도 틀린다 |
| 7 | **범위는 빼지 말고 분할한다** | 승인된 명세를 조용히 줄이면 약속이 사라진다 |
| 8 | **커밋 뒤 "맥락 없는 독자"로 핸드오프를 점검한다** | 다음 세션이 한 줄 지시로 이어지는지 사람이 매번 확인하지 않게 |
| 9 | **사이클은 한 번에 하나, 기본 브랜치·global은 완료된 것만** | 진행 중인 변경과 완성된 시스템이 섞이지 않아야 폐기에 여파가 없다 |

### 새 세션 진입 순서

1. 세션 시작 brief(`session_start_brief` 훅) — 진행 중 사이클·현재 단계·다음 착수 지점·`handoff.md`를 보여 준다
2. `project-memory/index.md` — 배경 지식(결정·함정)
3. `dev/README.md` — 진행 중 사이클과 그 브랜치. **현재 브랜치가 그 사이클 브랜치인지 확인**한다
4. `dev/<코드>/README.md` — 현재 단계
5. 해당 단계 `README.md` — 진행 방식 + 전제
6. 해당 단계 `progress.md` — 끝난 것과 **"다음 착수 지점"** / `open-questions.md` — 착수할 항목에 걸린 미결 / `handoff.md` — GO 전 중간 상태가 남아 있는지
7. 해당 단계 `checklist.md` — 해당 항목의 승인된 명세, 설계 지도와 관련 설계 문서
8. **→ 곧장 산출물을 만들지 않고 플랜 모드부터 들어간다**

> 사용자의 한 줄 지시 `"dev/<코드>/<단계>/README.md를 읽고 다음 항목 진행해줘"`만으로 위 순서가 성립해야 한다
> (예: `"dev/AUTH/impl/README.md를 읽고 다음 항목 진행해줘"`). 성립하는지를 매 항목 끝에 핸드오프 점검으로 확인한다.

### 항목 루프 — 한 항목의 생애

```
 ┌───────────────────── 한 항목(= <단계>/checklist.md 한 줄) ─────────────────────────┐
 │ 1. 맥락 잡기      brief → dev/README → 사이클 README → 단계 README → progress …   │
 │ 2. 플랜 모드      조사 → 플랜 작성 → [플랜 검수] → 사용자 승인                    │
 │ 3. 명세 고정      승인된 상세 명세를 <단계>/checklist.md에 반영 (승인 ↔ 작업 사이) │
 │ 4. 작업           (Impl) 구현 / (Design) 설계 문서 / (Plan) 개요·확정               │
 │ 5. 테스트         (Impl) 단위 테스트 + 전체 스위트 결과 기록                        │
 │ 6. 검수           독립 검수자 → NO-GO면 수정 → 재검수, GO까지 반복                  │
 │ 7. 미결 정리      <단계>/open-questions.md 추가·해소                                 │
 │ 8. 로그           <단계>/progress.md에 날짜·완료분·다음 착수 지점                    │
 │ 9. 커밋·푸시      사이클 브랜치에. 산출물 + 문서 + 로그를 한 커밋. GO 전에는 하지 않는다 │
 │10. 핸드오프 점검  맥락 없는 서브에이전트로 확인 → 결과 기록을 추가 커밋·푸시        │
 └───────────────────────────────────────────────────────────────────────────────────┘
```

**플랜 모드 (산출물 전 필수)**
- "다음 항목 진행해줘" 류 요청을 받으면 **읽기·조사 후 바로 작업하지 않고** 플랜 모드로 들어간다. 새 항목을 시작하는 요청이면 사용자에게 묻지 말고 곧바로 들어간다.
- 순서: **조사 → 플랜 작성 → 플랜 검수 → 사용자 승인**. 플랜 검수 결과는 **플랜 파일의 마지막 줄**에 검수 기록(`플랜 검수: GO — <검수자·회차> — 본문 <해시8>`)으로 남긴다 — 훅이 이 줄과 본문 해시를 확인한다(7단계 "플랜 검수 게이트").
- 플랜에 사용자가 정할 것이 있으면 설계 수호 규칙의 방식으로 묻고, 확정되면 날짜·사용자 원문과 함께 플랜에 적는다.
- **예외는 둘뿐**: ① 오탈자·문서 한 줄처럼 코드·설계 판단이 없는 사소한 변경 ② 사용자가 "승인된 플랜 그대로 진행"이라고 지시한 경우. ②도 **작업 전에 `<단계>/checklist.md`의 상세 명세를 먼저 읽는다.** 저장소에 상세 명세가 없으면(저장소 밖 플랜 파일은 다음 세션이 보장받지 못한다) 예외를 쓰지 말고 플랜 모드부터 들어간다. 사이클 밖 작업의 플랜 모드 기준은 "사이클 밖 작업" 절(원인이 분명한 국소 수정만 플랜 모드를 생략할 수 있다).

**승인 직후 명세 고정**: 플랜 승인 → 작업 착수 **사이**에 `<단계>/checklist.md` 해당 항목에 입출력 스키마, 상태·분기 규칙, 플랜 검수에서 나온 결정, 사용자 결정, 테스트 케이스, 스모크 기준을 반영한다. `progress.md`의 "다음 착수 지점"에는 **한 줄 요약 + 명세 위치**만 둔다(상세 복사 금지 — 두 곳에 두면 어긋난다).

**구현·테스트**
- **계약 우선**: 모듈이 내보내는 출력(스키마)을 먼저 고정하고, 소비하는 쪽은 그 계약만 본다.
- **수직 슬라이스 우선**: 가장 작은 흐름 하나를 처음부터 끝까지 먼저 구현해 계약(워크플로형이면 상태 저장·재개 포함)을 일찍 검증한 뒤 넓힌다(구현 순서의 원칙이다 — 설계를 어디까지 끝내고 들어오는지는 설계 완료 범위 A/B).
- 테스트 필수. 전체 스위트 결과(개수, 무작위 순서·시드를 쓰면 그 값)를 로그와 검수 요청에 남긴다.
- 실환경 부작용이 있는 스모크는 **사전 상태 기록 → 승인된 스모크 → `finally`로 정리 → 원상복구 확인**을 한 세트로 한다. 원상복구 확인 항목은 대상에 맞게 정한다(예: 파일이면 사전 해시 일치, 서버 자원이면 이번에 만든 임시 리소스가 남지 않음, 서비스면 테스트 계정 상태 복원). 스모크 표준 대상을 정해 두고, 바꿀 때는 사용자가 정한다.
- **되돌릴 수 없는 외부 쓰기**(메시지 게시·알림 발송 등)는 원상복구가 안 되므로 실환경 스모크를 하지 않는다. preflight로 미뤄 미결 장부에 올린다.

**검수** — 규칙 전체(P0·P1·P2, GO까지 반복, 재검수 범위 한정, 검수자 우선순위, `REVIEW_MODEL`, 기록 줄)는 7단계 "PreToolUse hook — ExitPlanMode 플랜 검수 게이트"의 **검수 규칙**이다. 플랜 검수·구현(산출물) 검수·승격 검수·사이클 밖 작업 검수에 모두 적용한다. 이 단계에서 덧붙이는 것:
- 검수 대상 = 코드, `design/`·`dev/global/` 설계 문서, Plan·Design 항목 산출물, 승격 결과(merge 포함). 검수가 필요 없는 커밋(진행 기록·시작 등록·폐기 기록·릴리즈·골격 도입·코드·설계 판단 없는 오탈자)은 위 "기본 브랜치 커밋의 검수 필요 여부" 표와 핸드오프 점검의 기록 커밋 규칙을 따른다.
- 수정분을 재검수 없이 회귀 테스트로만 고정하지 않는다. 검수자가 테스트를 직접 못 돌리면 내 쪽 전체 스위트 결과를 요청에 넣는다.
- **검수자·모델의 위치**: 검수자 우선순위와 지정 모델은 프로젝트 `CLAUDE.md`의 "플랜 검수" 절에 **한 번** 적혀 있다(5단계 템플릿, 훅 `REVIEW_MODEL`과 같은 값). 단계 README와 `impl/README.md`는 그 절을 가리키고 값을 복사하지 않는다. 사이클마다 검수자가 달라야 할 때만 그 사이클 `impl/README.md` 확정 전제에 적는다.
- **검수 기록**: 플랜 검수는 플랜 파일의 마지막 줄, 사이클 안의 산출물 검수는 `<단계>/progress.md` 로그의 "검수" 줄에 회차별 결과·검수자·모델을 남긴다. 사이클 밖 작업의 산출물 검수는 `project-memory/log.md` 작업 항목의 `검수:` 줄에 남긴다.

**미결 정리 (커밋 전)** — 미결 장부는 넷(`project-memory/open-questions.md` + 단계별 셋)이고 무엇을 어디에 적을지는 **경계 규칙** 하나로 정한다:

> **경계 규칙**: 특정 단계의 단위·항목 ID로 인용할 수 있으면 그 단계의 `dev/<코드>/<단계>/open-questions.md`, 아니면(특정 사이클·단계에 묶이지 않는 프로젝트 차원의 이슈·가설, 사이클 밖 작업에서 생긴 것) `project-memory/open-questions.md`.

해당 장부에 아래를 정리한다. **이번 항목으로 해소된 항목은 지우고** 확인 결과를 `gotchas.md`(사실·함정) 또는 `decisions/`의 새 결정 파일(정책 변경)로 옮긴다. `progress.md`에는 항목을 복사하지 않고 추가·해소한 **ID만** 적는다. 대상: ① 실환경에서 못 본 경로(모킹·임시·합성 데이터로만 확인) ② 검수의 빈틈(검수자가 테스트를 못 돌림, 대체 검수자·사용자 승인 예외로 넘어간 검수) ③ 외부 규칙 의존 가정(서버 정책·권한·조직 규칙) ④ 부작용 때문에 미룬 실행(preflight) ⑤ 미이행.

**로그·핸드오프·커밋** — 핸드오프 기록은 셋이고 역할이 다르다:

| 기록 | 담는 것 | 커밋 | 언제 |
|---|---|---|---|
| `<단계>/progress.md` | GO 뒤 커밋된 시점의 공식 핸드오프 — "다음 착수 지점" + 날짜별 로그 | 항목 커밋에 포함 | 항목 완료 시 |
| `handoff.md`(루트, 로컬 전용) | **GO 전 중간 상태** — 구현 중·검수 대기·NO-GO 수정 중. 최신 1개만 | 안 함(.gitignore) | GO 전에 세션이 끝나거나 `/compact` 전. 항목이 GO·커밋되면 비운다 |
| `project-memory/log.md` | 항목 완료의 의도 1~3줄 + progress 링크(상세는 progress에만) | 항목 커밋에 포함 | 항목 완료 시 |

- **커밋 전에** `progress.md` 맨 위에 새 로그를 추가하고 "다음 착수 지점"을 갱신한다. 로그는 산출물과 **같은 커밋**에 넣는다(커밋 해시는 아직 모르므로 로그 제목에는 다음 커밋 때 채워 넣는다).
- 세션 종료는 훅으로 감지할 수 없다. **GO 전에 세션을 끝낼 때는 `handoff.md`를 직접 갱신한다**(`/compact` 전에는 PreCompact 훅이 안내한다). 사이클 밖에서의 handoff 정의는 7단계 "세션 이월"의 경계 표를 따른다.
- 커밋 단위는 **항목 단위**를 권장한다. 한 항목은 보통 커밋 1개 + 핸드오프 점검 결과 커밋 1개(점검에서 문서를 고쳤다면 그 수정 커밋)로 끝난다.
- 사이클 안의 커밋·푸시는 사이클 브랜치에 한다. 기본 브랜치에 대한 커밋·푸시는 사용자 허락 후.

### 설계 수호 규칙 (모든 단계 공통)

- **추론은 확인받는다.** 문서·코드에 명시되지 않은 값·정책을 추론했다면 플랜·명세·코드·문서에 반영하기 **전에** 사용자에게 확인한다. 플랜의 "가정" 절에 적어 두는 것으로 갈음하지 않는다.
- **설계(단위 구성·의존, 워크플로형이면 분기·사람 개입 지점·순서)는 사용자와 의논해 확정한 뒤에만 바꾼다.** 에이전트의 추론만으로는 근거가 안 된다.
- **설계 변경의 근거는 둘뿐**: 기존 설계의 구조적 문제, 또는 변경으로 생기는 구조적 개선. **설계·구현 편의는 근거가 아니다.** 편의로 단위를 합치거나 빼거나 비워 두지 않는다.
- **아직 구현되지 않은 단위는 건너뛰지 않고 그 앞에서 멈추게 만든다.** 일부만 구현된 상태의 시스템이 미구현 단위에 이르면, 빈 통과 처리(아무것도 안 하고 다음으로 넘기는 stub)로 지나가지 말고 "미구현"을 알리며 명시적으로 멈추게 한다. 개발 순서도 같다 — 막혔다고 그 단위를 비워 둔 채 뒤 단위로 넘어가지 않는다. (작업을 여러 항목으로 나누는 것은 설계 변경이 아니다.)
- **범위는 빼지 말고 분할한다.** 플랜의 문서·부수 작업은 하나하나 "이번 항목에 꼭 필요한가"를 판정한다. ① 산출물과 같은 커밋이어야 하는 것만 이번에 넣고 ② 나머지는 **다음 항목으로 분할**해 `<단계>/checklist.md`에 옮겨 적고 ③ 승인된 명세의 항목을 사용자 결정 없이 장부 한 줄로 대체하지 않는다.
- **정책·설계 질문은 선택지 UI로 한꺼번에 묻지 않고 텍스트로 단계적으로** 묻는다 — 한 번에 한두 개, 의존 순서대로. 질문마다 ① 확인한 사실(근거 `파일:줄`) ② 왜 정해야 하나 ③ 가능한 방법과 장단점 ④ 권장과 근거. 사용자가 되물으면 답부터 하고, 질문에 대한 답을 결정으로 바꾸지 않으며, 사용자 답의 적용 범위를 넓히지 않는다.
- **"절대 규칙"은 구두로만 두지 않는다.** 말로만 지시된 규칙은 기록되지 않아 사라진다 → `CLAUDE.md` + `project-memory/decisions/`의 결정 파일(+ 해당 명세)에 날짜와 함께 적고, 만든 계기(위반 사례)도 한 줄 남긴다.

### 핸드오프 점검 (커밋·푸시 뒤 매 항목 마지막)

Plan·Design·Impl **세 단계 모두 같은 규칙**으로 점검한다.

**목적**: 새 세션에서 `"dev/<코드>/<단계>/README.md를 읽고, 다음 항목 진행해줘."` 한 줄만으로 올바른 다음 항목에 착수할 수 있는지 확인한다. 단계 전환 직후라면 새 단계의 README로 같은 점검을 한다.

**방법**: 현재 대화의 맥락을 **물려받지 않는** 서브에이전트에게 읽기 전용으로 위 문장을 그대로 주고, "실행하지 말고 ▸ 무엇을 읽고 ▸ 어떤 항목을 어떤 절차(플랜 모드 여부 포함)로 시작할지 ▸ 먼저 읽을 문서 ▸ 막히거나 모호한 점"만 보고하게 한다.

**판정 기준 (전부 만족해야 통과)**
1. 다음 항목을 그 단계 `progress.md`의 "다음 착수 지점"과 같게 짚는다
2. 플랜 모드부터 들어간다고 답한다
3. 먼저 읽을 문서·명세(`checklist.md` 항목, `open-questions.md` ID)를 찾아낸다
4. 이미 끝난 항목·지운 ID·옛 명령을 **현재 할 일로 읽지 않는다**
5. 커밋·푸시 누락이 없다 — ① 작업 트리가 깨끗하다(`git status`에 변경 없음, **항상 필수**) ② 원격이 있고 push가 허락된 프로젝트라면 원격과 같다 ③ 원격이 없으면 push 자체가 없으므로 확인 대상이 아니다(기록도 필요 없다) ④ 사용자가 push를 보류했다면 그 사실(이유·push 시점)이 `progress.md` 또는 `handoff.md`에 적혀 있으면 통과한다
6. 현재 브랜치가 `dev/README.md` 표의 진행 중 사이클 브랜치와 같고, 사이클 README의 "현재 단계"가 점검한 단계와 같다

어긋나면 **원인 문서를 고쳐 커밋·푸시한 뒤 같은 점검을 다시** 한다(코드·설계 판단이 없는 문서 수정이라 플랜 모드·검수 없이 진행). 통과하면 결과(통과·고친 곳)를 그 단계 `progress.md`의 그 항목 로그에 한 줄로 남기고 **추가 커밋·푸시**한다 — 이 기록 커밋은 점검 대상이 아니므로 다시 점검하지 않는다.

> 흔한 어긋남: 완료 전 상태를 서술한 구절이 남아 있음 / "다음 착수 지점"이 아직 정하지 않은 결정을 단정함 / 옛 명령·지운 ID가 현재 지침처럼 읽힘 / 사이클 README의 현재 단계를 갱신하지 않음 → 대체 표식을 달거나 갱신한다.

### 항목 루프를 Plan·Design 단계에도 쓰기

항목 루프는 Impl 전용이 아니다. Plan·Design의 항목도 같은 모양으로 굴린다. 차이만 적는다.

| Impl 항목 | Plan·Design 항목의 대응 |
|---|---|
| 플랜 모드 + 플랜 검수 | 같다 (Design은 단위 하나당 플랜 모드) |
| 명세 고정(`impl/checklist.md`) | Design: 설계 문서(`design/<개념>-design.md`) + `design/checklist.md` 요약 / Plan: `plan/overview.md`·`plan/checklist.md` 확정 |
| 구현·테스트 | 문서 작성 + 실측 |
| 구현 검수 | 설계 문서 독립 검수(같은 규칙) |
| 미결 정리 | 그 단계 `open-questions.md`의 실측·결정 논점 |
| 문서 역전파 | 역전파 체크리스트 |
| 로그·커밋·푸시(GO 뒤, 한 커밋) | 같은 규칙 — 그 단계 `progress.md`에 로그 |
| 핸드오프 점검 | 같은 규칙 |

### 템플릿과 적용 체크리스트

**템플릿 [`templates/dev/`](https://github.com/amurtare/release_management_guide/tree/main/templates/dev)**

```
templates/dev/
├─ README.md                      dev/ 진입점 (프로젝트에 한 번) — 첫 줄 표식 포함
├─ global/overview.md · map.md · _concept_-design.md · retired/README.md
└─ _CODE_/                        적용 때 dev/_CODE_/로 보관, 사이클 시작 때 dev/<코드>/로 복사·이름 변경
   ├─ README.md
   ├─ plan/    README · checklist · open-questions · progress · overview
   ├─ design/  README · checklist · open-questions · progress · map · _concept_-design
   ├─ impl/    README · checklist · open-questions · progress
   └─ evidence/README.md
```

**템플릿 가져오기** — 대상 프로젝트 **밖의** 임시 폴더로 받아서 `dev/`에 복사한다(이 가이드의 GitHub 저장소는 `RELEASE_MANAGEMENT_GUIDE.md`와 `templates/dev/`만 공개한다). 대상 프로젝트 루트에서:

1. `git clone --depth 1 --filter=blob:none --sparse https://github.com/amurtare/release_management_guide.git <임시 폴더>`
2. `git -C <임시 폴더> sparse-checkout set templates/dev`
3. `<임시 폴더>/templates/dev/` 아래의 `README.md`·`global/`·`_CODE_/` 셋을 대상 프로젝트의 `dev/`로 복사한다. 결과는 `dev/README.md`, `dev/global/`, `dev/_CODE_/`이다. **이미 `dev/`가 있으면 덮어쓰지 말고 사용자에게 알린다.**
4. `<임시 폴더>`를 지운다.

git을 쓸 수 없으면 GitHub 저장소 페이지에서 zip을 받아 풀고 같은 세 항목을 복사한다. 복사한 `dev/README.md`의 첫 줄 표식은 지우지 않는다(훅이 8단계 프로젝트로 알아보는 신호다).

**훅이 읽는 줄 형식** — 아래 형식이 어긋나면 훅은 오류 없이 그 출력을 생략한다(형식을 바꾸지 말 것). **줄 형식의 한국어 문구(`진행 중`, `현재 단계:`, `## 다음 착수 지점`, `플랜 검수:` 등)를 번역하면 훅이 그 줄을 알아보지 못한다** — brief는 그 출력을 생략하고, 플랜 게이트는 기록을 인정하지 않아 통과시키지 않는다. 영어로 쓰는 프로젝트도 이 줄들은 한국어 그대로 둔다.

| 파일 | 훅 | 형식 |
|---|---|---|
| `dev/README.md` 첫 줄 | `session_start_brief` · `post_commit_review` | `<!-- rmg: dev-cycles -->` — 이 줄이 있을 때만 훅이 8단계 프로젝트로 본다(brief의 사이클 출력, 커밋 회고의 `dev/` 진행 기록 면제). **파일의 첫 줄**이어야 한다(UTF-8 BOM·CRLF·줄 앞뒤 공백은 무시, 빈 줄 뒤나 본문 중간은 무효) |
| `dev/README.md` | `session_start_brief` | 사이클 표의 행 `\| <코드> \| <이름> \| 진행 중 \| cycle/<코드> \| …` — 셋째 칸이 정확히 `진행 중`. 코드블록·HTML 주석 안의 행(예시)은 읽지 않는다 |
| `dev/<코드>/README.md` | `session_start_brief` | `현재 단계: Plan` / `Design` / `Impl` (줄 전체나 단계 이름을 `**` 굵게로 감싸는 것은 허용) |
| `dev/<코드>/<단계>/progress.md` | `session_start_brief` | `## 다음 착수 지점` 제목 아래, 다음 `## ` 제목 전까지(HTML 주석은 건너뜀) |
| 브랜치 이름 | `session_start_brief` | `cycle/<코드>` — 코드는 `A-Z0-9` 2~8자. 기본 브랜치는 훅 설정값 `BASE_BRANCH` 또는 자동 판단(7단계 SessionStart hook) |
| 플랜 파일 마지막 줄 | `pre_plan_exit_review` | `플랜 검수: GO — <검수자·회차> — 본문 <해시8>` (7단계 플랜 검수 게이트) |

`_CODE_`·`_concept_`는 자리표시다(밑줄은 개발 코드 허용 문자가 아니라 실제 코드와 겹치지 않는다 — `dev/_CODE_/`는 사이클이 아니라 템플릿 보관 폴더다). 각 단계 파일에는 그 단계에 해당하는 절만 들어 있다.
**템플릿과 이 단계 본문의 어긋남 관리**: 같은 규칙을 두 곳에서 따로 고치지 않는다 — 규칙은 이 단계 본문이 원천이고 템플릿은 그 규칙의 빈 문서다. 규칙을 바꾸면 같은 변경에서 템플릿(`README` 진행 방식, 줄 형식, 폴더 구조)을 함께 고치고, 릴리즈 체크리스트가 둘의 일치를 확인한다.

**적용 체크리스트** (대상 프로젝트에 만들 산출물)
- [ ] 8단계 적용 여부를 사용자에게 묻고 결정 파일로 남겼다(2단계 설치 체크리스트, 이 단계 도입부의 기준)
- [ ] 1~7단계 기본 구조가 있는지 확인 — `project-memory/`(decisions·gotchas·log·open-questions 등), `handoff.md`, 훅 4종(등록 포함)
- [ ] 위 "템플릿 가져오기"로 `dev/README.md`·`dev/global/`·`dev/_CODE_/`를 만든다 — 사이클 표는 비어 있고, `dev/_CODE_/`는 그대로 보관한다(사이클 시작 때 `dev/<코드>/`로 복사)
  - 골격을 **템플릿 그대로** 넣는 커밋은 검수 없이 사용자 허락만 받는다. 템플릿을 고치거나 `dev/global/`을 채우는 것부터는 검수 대상이다 — 기존 코드가 있으면 현재 구조를 `dev/global/`의 첫 내용으로 채우는데, 이 작업은 사이클 밖 작업이다(사이클로 할지 사용자에게 묻는다)
- [ ] 단위의 정의를 정한다 — 워크플로 노드? 기능? 모듈? (용어 표)
- [ ] 독립 검수자와 호출 방법·모델 지정을 정해 **`CLAUDE.md`의 "플랜 검수" 절에 기록**한다(검수 규칙의 우선순위; 5단계 템플릿). 사이클마다 달라야 할 때만 그 사이클 `impl/README.md` 확정 전제에 적는다. 모델을 고정하려면 훅의 `REVIEW_MODEL`도 같은 값으로 지정
- [ ] 실환경 스모크 표준 대상과 **원상복구 확인 절차** 확정
- [ ] `CLAUDE.md`에 아래 스니펫 추가
- [ ] 훅 4종이 이 가이드 7단계의 최신 코드인지 확인 (플랜 검수 게이트의 GO 줄 확인, 커밋 회고의 `dev/` 진행 기록 면제 — `dev/README.md` 첫 줄 표식 필요, brief의 사이클 출력 — 기본 브랜치 판단(`BASE_BRANCH`))

**`CLAUDE.md` 스니펫**

```markdown
## 계획·설계·구현 작업 원칙 (상세: 각 단계 README "진행 방식")

- **사이클**: 기능·시스템 추가를 사이클로 할지는 작업을 시작할 때(플랜 모드) 사용자에게 묻는다. 사이클로 하기로 한 작업은 `dev/README.md`가 진입점이고, 한 번에 한 사이클만 진행한다.
  사이클은 `dev/<코드>/`(plan·design·impl)와 `cycle/<코드>` 브랜치에서 진행하고, 끝나면 승격(기본 브랜치 병합 + `dev/global/` 반영) 또는 폐기한다.
  `dev/global/`은 기본 브랜치에 반영된 완료분(승격된 사이클 + 사이클 밖 작업)의 현재 설계다.
- **항목은 산출물 전에 반드시 플랜 모드부터 거친다.** 항목 순서(플랜 검수·작업·테스트·검수·미결 정리·커밋·핸드오프 점검)는
  각 단계 `README.md` "진행 방식" 한 곳에만 둔다. 새 항목을 시작하는 요청이면 묻지 말고 곧바로 플랜 모드로 들어간다
  (예외: 사소한 문서 수정, 사용자가 "승인된 플랜 그대로 진행"이라고 지시한 경우 — 이때도 해당 `checklist.md`의 상세 명세를 먼저 읽는다,
  그리고 사이클 밖 작업 중 원인이 분명한 국소 수정 — 이때도 결함 수정은 커밋 전 검수 GO가 필수, 코드·설계 판단 없는 오탈자·문서 한 줄만 검수 불필요).
- **검수**: 플랜·산출물 모두 독립 검수 GO(P0·P1 없음)까지 반복한다. 검수자·모델·기록 형식은 이 파일의 "플랜 검수" 절을 따른다.
- **검수 대상 변경(코드, `design/`·`dev/global/` 설계 문서, Plan·Design 항목 산출물, 승격 결과)은 GO 전에는 커밋하지 않는다**(브랜치 무관). GO 전 중간 상태는 `handoff.md`에 남긴다.
  진행 기록·사이클 등록·폐기 기록·릴리즈 커밋은 검수 대상이 아니다.
- **기본 브랜치에 대한 커밋·푸시는 사용자 허락 후에만 한다**(사이클 밖 작업·릴리즈·사이클 시작 등록·폐기 기록·승격).
  사이클 브랜치 안의 커밋·푸시는 항목 흐름대로 GO 뒤에 진행한다.
- **사이클 밖 작업은 사용자가 사이클로 하지 않기로 고른 작업이다.** 작업을 시작할 때(플랜 모드) 사이클로 할지 사용자에게 묻는다
  (원인이 분명한 국소 수정은 묻지 않고 사이클 밖에서 한다). 기본 브랜치에 직접 하고, 커밋 전 검수 GO 필수(코드·설계 판단 없는 오탈자·문서 한 줄 제외),
  `dev/global/`의 설계 서술을 바꾸면 같은 커밋에서 고친다.
- **★ 절대 규칙 — 추론은 확인받고, 설계는 의논 없이 바꾸지 않는다.** 명시되지 않은 값·정책을 추론했으면 반영 전에
  사용자에게 확인한다. 설계 변경의 근거는 구조적 문제·구조적 개선뿐이며 설계·구현 편의는 근거가 아니다.
  아직 구현되지 않은 단위 앞에서는 멈추고 건너뛰지 않는다.
- 외부 시스템 동작에 기대는 설계 가정은 사용자 진술이 아니라 직접 실측으로 확인하고, 부작용 있는 쓰기는 미검증으로 명시해 preflight로 넘긴다.
- 항목 완료 시(커밋 전) 미결을 경계 규칙대로(단위·항목 ID로 인용 가능 → 그 단계 `open-questions.md`, 아니면 `project-memory/open-questions.md`) 정리하고
  `progress.md` 로그와 함께 항목 커밋에 넣는다. 커밋·푸시 뒤에는 핸드오프 점검을 하고, 결과를 추가 커밋·푸시한다.
- 저장소의 현재 상태(설계 문서·코드)가 항상 진행 기록·`project-memory/` 기록보다 우선한다 — 충돌하면 기록을 갱신한다.
  설계 문서와 코드가 어긋나면 설계 문서가 기준이다.
```

**그대로 둘 것 / 바꿀 것**

| 구분 | 내용 |
|---|---|
| **그대로 둔다** | 단일 사이클·사이클 브랜치·승격/폐기 규칙, `dev/global/`(완료분만), 세 단계 폴더의 같은 구조(4문서), 확정/미결 분리, 역전파 체크리스트, 실측 규칙, 항목 루프, 검수 게이트·GO 반복·재검수 범위 한정·검수자 우선순위, 미결 장부 경계 규칙, 핸드오프 점검, 설계 수호 규칙, 기본 브랜치 커밋·푸시 사용자 허락 |
| **바꾼다** | 단위의 정의, 확정 전제(언어·외부 시스템·절대 규칙), 스모크 표준 대상·원상복구 항목, 검수자 모델 지정, 미결 구획 이름, 기간 한정 예외(사용자가 정한 것만 — 정하면 `impl/README.md` 확정 전제에 적는다) |
| **판단한다** | 설계 완료 범위(기본 A = 사이클의 전건 완료 후 구현 / B = 첫 슬라이스 단위만 설계 후 구현 — B는 검증되지 않음), 검수 회차(플랜 n회 + 산출물 n회), 커밋 단위(항목 vs Phase) |

> **이 단계가 다루지 않는 것**: CI·환경 분리·운영 모니터링 같은 출시 이후 절차. 이 프로세스의 원본이 그 시기까지 운영되지 않아 검증된 절차가 없다. 버전·릴리즈는 1~3단계가 다룬다(승격 뒤 릴리즈 여부 확인).

### 흔한 실패와 대응

| 실패 | 증상 | 대응 |
|---|---|---|
| 플랜 없이 작업 진입 | 사용자 지적으로 되돌림 | 플랜 모드 필수 — 단계 README 맨 위 ⚠️ + `CLAUDE.md` 한 줄 |
| 명세가 한 줄 요약뿐 | 새 세션이 핵심 결정을 놓치고 어긋나게 구현 | 승인 직후 `checklist.md`에 상세 명세 고정 |
| 플랜 범위 과대 | 줄이려다 승인된 명세를 결정 없이 지우려 함 | 빼지 말고 항목 분할 |
| 재검수 범위 확대 | 회차마다 새 결함을 찾아 끝나지 않음, 재현 안 되는 가장자리 사례만 반복 | 직전 지적 해소 + 회귀로 한정(코드로 재현된 범위 밖 P0만 예외) |
| 검수 1회로 통과 | NO-GO인데 두 번째 시도에서 플랜 모드를 빠져나옴 | 플랜 파일 마지막 줄의 검수 기록·본문 해시를 훅이 확인 |
| 검수자 부재 시 무검수 통과 | 리뷰어 플러그인이 없어 검수 없이 진행 | 대체 검수자 → 사용자 승인 예외 기록(훅은 리뷰어가 없어도 통과시키지 않는다) |
| 미결이 흩어짐 | 대화 요약·로그·함정 문서에 분산, 수십 건이 쌓여 코드 결함까지 묻힘 | 경계 규칙으로 장부 일원화, 단계 전환 시 이관 |
| 구두 규칙 소실 | 말로만 지시한 규칙이 사라지고 그 사이 위반 구현 | `CLAUDE.md` + 결정 파일에 날짜와 함께 |
| 편의로 설계 변경 | 단위 합치기·비우기를 승인까지 받음 | 추론 확인, 의논 후 변경 |
| 핸드오프 문서 낡음 | 완료된 항목을 현재 할 일로 읽음, 엉뚱한 브랜치에서 이어 감 | 맥락 없는 서브에이전트로 점검(브랜치·현재 단계 포함) |
| GO 전 상태 유실 | 검수 대기 중 세션이 끊겨 어디까지 했는지 모름 | GO 전 중간 상태는 `handoff.md` |
| 검수 도구 장애 | 검수가 진행되지 않거나 사용량 한도 초과 | 같은 설정으로 다시 요청하고 실행 기록으로 실제 설정 확인. 끝내 안 되면 다음 검수자 → 사용자 승인 예외 |
| 하위 문서만 고치고 상위 미갱신 | 설계 지도 요지가 사라진 채 방치, 인용처 누락 | 식별자 grep 역전파를 체크리스트로 강제 |
| "검증됨"의 실체가 진술 | 실측 없이 설계가 외부 시스템 동작에 기댐 | 직접 호출 실측, 쓰기는 preflight로 명시 |
| 폐기된 가설이 되살아남 | 옛 서술이 남아 옛 방식으로 구현 | 취소선 + `[대체됨 날짜]`, overview에 폐기 목록 |
| ID 재번호화 | 인용처 대량 깨짐 | ID는 안정 식별자, 구멍 허용 |
| 설계 문서를 plan/에 추가 | 개요와 설계가 섞여 소스가 불명확 | 설계는 `design/`만 |
| 사이클 동시 진행 | 두 사이클이 같은 단위를 바꿔 설계·병합 충돌 | 한 번에 한 사이클, `dev/README.md` 표로 판정 |
| 승격 누락 | 구현은 기본 브랜치에 있는데 global이 옛 설계 | 기본 브랜치 병합과 global 반영을 한 시점에, 승격 검수 범위에 global 반영분 포함 |
| 큰 작업을 사이클 밖으로 진행 | 사이클 밖으로 골랐는데 설계 단위가 새로 생기거나 여러 세션으로 길어짐, 설계 문서·global과 코드가 어긋남 | 작업 시작 때 묻는 기준(여러 세션 · 설계 지도 단위 변경 · 중간에 접을 수 있음)에 다시 해당하는지 보고, 해당하면 사이클로 옮길지 사용자에게 묻는다 |
| 퇴역 단위가 global에 남음 | 제거·대체된 단위의 행·서술이 global map·개념 문서에 그대로 있어 옛 설계가 현재 설계처럼 읽힘 | 승격 2번에서 그 단위만 `dev/global/retired/`로 이동 + 퇴역 목록 링크 + 인용처 grep |
| 8단계 완료 전 승격 | 설계 지도에 구현되지 않은 행이 남은 채 승격 | 승격 0번 완료 확인 — map 모든 행이 `[x]`이거나 사용자 결정으로 범위에서 뺀 것(근거 있음) |
| 폐기 기록 누락 | 접은 이유·교훈이 사라져 같은 시도를 반복 | 폐기 사유 결정 파일 + gotchas 이관 + `archive/<코드>` 태그 |

> 이 단계는 perforce-ax-template 저장소 `reference/cl-workflow/`(plan·design·impl)를 운영하며 정리한 절차를 프로젝트 중립적으로 일반화한 뒤, 이 가이드의 버전·project-memory·훅 체계와 결합하고 다중 사이클 구조로 개정한 것이다. 결정 근거는 `project-memory/decisions/impl-extension-process.md`와 `impl-extension-split.md`, 작업 원고 `ref/LONG_TERM_DEV_PROCESS.md`(동결)의 부록 A에 있다.

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
커밋·푸시 전 사용자 확인
    ↓
커밋 메시지: "v0.X.Y: 변경 요약"
    ↓
git tag v0.X.Y
    ↓
git push origin <기본 브랜치> && git push origin v0.X.Y
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
