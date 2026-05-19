# Gotchas

반복적으로 밟기 쉬운 함정. 증상 + 원인 + 올바른 해법 형식.

<!-- 항목 수명 규칙: 근본 원인이 해결되면 ~~취소선~~ + (해결됨: vX.Y.Z) 추가, 다음 릴리즈 점검에서 제거 -->

## CSS Grid `repeat(N, 1fr)` 사용 시 카드 폭이 불균등해짐

- **증상**: 그리드 카드들의 폭이 제각각 — 특정 카드가 눈에 띄게 넓음
- **원인**: `1fr = minmax(auto, 1fr)`. `auto` 최솟값은 콘텐츠 intrinsic min width를 허용하므로, `<pre>` 코드블록이나 긴 URL이 있는 카드가 해당 열 전체를 확장함
- **해법**: `repeat(N, minmax(0, 1fr))` 사용. `0`으로 최솟값을 고정해 콘텐츠가 열 폭에 영향을 주지 못하게 함
- **관련 규칙**: html-design-guide.md 섹션 4.2

## `/sync-index` 실행 없이 `RELEASE_MANAGEMENT_GUIDE.md`만 수정하면 index.html이 뒤처짐

- **증상**: index.html의 내용이 가이드 본체와 달라 보임
- **원인**: index.html은 자동 동기화되지 않고 `/sync-index` 실행 시에만 갱신됨
- **해법**: `RELEASE_MANAGEMENT_GUIDE.md` 또는 `README.md` 수정 후 반드시 `/sync-index` 실행
