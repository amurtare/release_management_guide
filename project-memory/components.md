# Components — 저장소 구조 맵

릴리즈/구조 변경 시 갱신.

---

## 파일 구조

```
release_management_guide/
├── RELEASE_MANAGEMENT_GUIDE.md   ← 가이드 본체 (단일 소스)
├── README.md                     ← 저장소 소개 (간략)
├── CLAUDE.md                     ← Claude Code 프로젝트 지시 (릴리즈 트리거 등)
├── VERSION                       ← 버전 번호 단일 소스 (plain-text)
├── index.html                    ← 웹 뷰 (/sync-index로 동기화)
├── html-design-guide.md          ← index.html 디자인 규칙 참고 문서
├── handoff.md                    ← 세션 간 인계 메모 (임시)
├── docs/
│   └── UPDATE_CHECKLIST.md       ← 릴리즈 체크리스트
├── release-notes/
│   └── v0.1.0.md                 ← 버전별 릴리즈 노트
├── project-memory/               ← 개발 맥락 누적 (이 디렉토리)
└── .claude/
    ├── settings.json             ← hooks 등록
    ├── settings.local.json       ← 로컬 권한 허용 목록
    ├── commands/
    │   └── sync-index.md         ← /sync-index 슬래시 커맨드
    └── hooks/
        ├── session_start_brief.py  ← SessionStart hook
        ├── session_stop_review.py  ← Stop hook
        └── pre_compact_review.py   ← PreCompact hook
```

---

## 핵심 의존 관계

- `index.html` ← (`/sync-index`) ← `RELEASE_MANAGEMENT_GUIDE.md`
- `VERSION` ← SessionStart hook이 읽어 brief 출력
- `project-memory/` ← Stop hook이 회고 리마인더 주입
- `project-memory/` ← PreCompact hook이 압축 전 회고 리마인더 주입
