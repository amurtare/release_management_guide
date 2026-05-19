# 개발 로그

<!-- append-only. 형식: ## [YYYY-MM-DD] <kind> | <한 줄 제목> -->

## [2026-05-19] release | v0.1.0 — 릴리즈 관리 체계 이 저장소에 적용 완료

- GitLab 전용으로 전환 (GitHub 레퍼런스 전면 제거)
- index.html UI 재설계 (html-design-guide 기반)
- GitLab PAT 발급 가이드 Notion 링크 추가

## [2026-05-19] design | 선택 항목(project-memory + hooks) 사후 적용

- v0.1.0 적용 시 선택 항목이 누락되었음을 사용자가 발견, 이번 세션에서 추가
- VERSION, project-memory/ 전체 구조, .claude/hooks/ 2개, .claude/settings.json 신규 생성
- Stop hook 동작 확인됨 (세션 종료 시 회고 리마인더 정상 발동)

## [2026-05-19] design | CSS Grid 카드 폭 불균등 버그 수정 및 가이드 반영

- Quick Start 카드 4개가 서로 다른 폭으로 렌더링됨 (Card 03의 `<pre>` URL이 열을 확장)
- 원인: `1fr = minmax(auto, 1fr)` — 콘텐츠 intrinsic min width가 열 최솟값으로 작용
- index.html 전체 그리드 + html-design-guide.md Section 4.2/4.3/6.x 일괄 수정
- 올바른 패턴: `repeat(N, minmax(0, 1fr))`

## [2026-05-19] design | 팔레트 확장 규칙 수립 및 적용

- 6번째 이상 색이 필요할 때 새 hue 추가 금지, `--pN-dark` / `--pN-muted` 변형 사용
- `--p1~p5` 각각 dark(L−0.18, C×0.7), muted(L+0.08, C×0.5) 변수 신설 (총 10개)
- index.html SVG/JS 하드코딩 `oklch(0.30 0.04 245)` → `--p5-dark` 로 통일
- html-design-guide.md 섹션 1.1 팔레트 확장 규칙 신설

## [2026-05-19] design | hero + Quick Start 섹션 통합

- hero `<div>`와 별도 `<section id="quickstart">` 두 개로 나뉘어 있던 구조를 하나로 합침
- `ref/index.html` 패턴 참고 — 소개 lede 바로 아래에 카드 그리드가 이어지는 방식
- `sec-head` / `sec-eyebrow` / `sec-title` / `sec-sub` 헤딩 블록 제거, nav anchor `#quickstart`는 hero div에 id로 유지

## [2026-05-19] design | gitlab-pat-setup.html 디자인 가이드 정합성 리팩토링

- html-design-guide.md 확정 전에 만들어진 파일을 가이드 기준으로 전면 정합
- 20개 클래스 리네이밍: `.part-*`→`.sec-*`, `.faq-*`→`.fh-*`, `.os-*`→`.role-*`, `.codeblock*`→`.code-block*`
- 누락 패턴 추가: 스크롤 리빌, 히어로 fadeUp, 호버 translateY, `::selection`, `prefers-reduced-motion`, `:focus-visible`
- 모놀리식 `.wrap` → 섹션별 `.wrap`, `role-bar` sticky화, `.wrap` max-width 860px→1180px (사용자 선택)
- `:root` 토큰 완전화: `--pN-dark/muted` 10개, `--e4/e5` 추가, 전역 `--accent` 제거

## [2026-05-19] design | gitlab-pat-setup.html + wsl-setup.html 신규 생성

- Notion MD 파일 2개를 html-design-guide.md 기준 독립 HTML 페이지로 변환
- `gitlab-pat-setup.html`: OS switcher (body[data-os] + role-bar sticky), Part 1 공통 + Part 2-A Mac + Part 2-B Windows, FAQ 4항목
- `wsl-setup.html`: Windows 전용, 8단계 (MD의 중복 Step 7 → Step 8 정정), 인증서 섹션 pre.scrollable 적용
- 양 페이지 간 상호 cross-link (next-card, hero lede, sec-sub)
- callout.tip / callout.note / callout.warning 3종 모두 사용

## [2026-05-19] design | index.html Quick Start 카드 구조 정비 + 크로스페이지 링크 정비

- index.html Quick Start "Git 확인" 카드 삭제 (gitlab-pat-setup.html이 이미 담당)
- 카드 번호 재정렬: 01 PAT / 02 클론 / 03 적용, 그리드 4→3칸
- gitlab-pat-setup.html Next Card CTA: `index.html#step3` → `index.html#quickstart` (단계명 비종속)
- 설계 원칙 → decisions/cross-page-link-stability.md 참고

## [2026-05-19] release | v0.3.0 — UI 구조 간소화 및 콘텐츠 정확도 개선

- 네비게이션 바 3개 파일 전체 제거
- index.html: Quick Start 3카드 재구성, 워크플로 순서 수정 (요청→결정), hero lede 재작성
- gitlab-pat-setup.html: Next Card CTA 단계명 비종속화 (→ index.html#quickstart)
- wsl-setup.html 신규 커밋 포함
- sec-title em 강조 단어 핵심 명사로 재배치

## [2026-05-19] research | 앤트로픽 공식 브랜드 컬러 확인

- 출처: github.com/anthropics/skills/blob/main/skills/brand-guidelines/SKILL.md
- 총 7색 — 기본 4색(Dark #141413, Light #faf9f5, Mid Gray #b0aea5, Light Gray #e8e6dc) + 액센트 3색(Orange #d97757, Blue #6a9bcc, Green #788c5d)
- 폰트: Poppins(헤딩) + Lora(본문)
- 이 저장소 팔레트(OKLCH 5색 커스텀)와 무관, 앤트로픽 브랜드 적용 불필요
