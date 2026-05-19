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

## [2026-05-19] research | 앤트로픽 공식 브랜드 컬러 확인

- 출처: github.com/anthropics/skills/blob/main/skills/brand-guidelines/SKILL.md
- 총 7색 — 기본 4색(Dark #141413, Light #faf9f5, Mid Gray #b0aea5, Light Gray #e8e6dc) + 액센트 3색(Orange #d97757, Blue #6a9bcc, Green #788c5d)
- 폰트: Poppins(헤딩) + Lora(본문)
- 이 저장소 팔레트(OKLCH 5색 커스텀)와 무관, 앤트로픽 브랜드 적용 불필요
