# release_management_guide — 저장소 유지보수

> 이 파일과 `.claude/` 디렉토리는 이 저장소 자체를 관리하기 위한 설정이다.
> **다른 프로젝트에 복사하지 않는다.** 가이드 본체는 `RELEASE_MANAGEMENT_GUIDE.md` 하나다.

---

## index.html 동기화

`RELEASE_MANAGEMENT_GUIDE.md` 또는 `README.md`를 수정했다면 `/sync-index`를 실행해 `index.html`을 최신 내용과 일치시킨다.

---

## 릴리즈 트리거

사용자가 **"버전 올려줘"**, **"릴리즈해줘"**, **"v{숫자} 태그"** 같은 말을 하면 아래 순서로 진행한다.

1. `docs/UPDATE_CHECKLIST.md`를 열고 각 항목을 순서대로 실행한다.
2. 변경 범위를 확인해 PATCH / MINOR / MAJOR 중 하나를 결정한다.
3. `RELEASE_MANAGEMENT_GUIDE.md` 또는 `index.html`을 수정했다면 `/sync-index`를 실행한다.
4. `release-notes/v{새버전}.md`를 작성한다.
5. 변경 파일을 커밋한다: `v{버전}: {한 줄 요약}`
6. 태그를 생성한다: `git tag v{버전}`
7. 푸시 전 사용자에게 확인을 받는다.
