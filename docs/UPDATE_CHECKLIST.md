# 업데이트 체크리스트

> 이 저장소는 **문서 저장소**다. 버전 소스는 Git 태그를 직접 사용한다.

---

## 버전 올리기 전 확인

### 1. 변경 범위 판단

- [ ] 변경 유형 결정:
  - **PATCH** — 오탈자, 링크, 표현 수정
  - **MINOR** — 섹션 추가, 주요 개정, 새 HTML 파일 추가
  - **MAJOR** — 가이드 방향 전환, 체계 전면 개편

### 2. 콘텐츠 점검

- [ ] `RELEASE_MANAGEMENT_GUIDE.md` 수정 시 `index.html`과 동기화 (`/sync-index` 실행)
- [ ] 링크 유효성 확인 (Notion 링크, GitLab 링크)
- [ ] 코드 블록 내 명령어 실제 동작 확인

### 3. 릴리즈 노트 작성

- [ ] `release-notes/v{새버전}.md` 생성 (기존 파일 포맷 참고)
- [ ] 변경 내용 분류: 신규 / 변경 / 수정 / 제거
- [ ] Semver 해석 섹션 포함

### 4. 커밋 & 태그

- [ ] 변경 파일 스테이징 및 커밋: `v{버전}: {한 줄 요약}`
- [ ] 태그 생성: `git tag v{버전}`
- [ ] 원격 푸시: `git push && git push --tags`

---

## 빠른 참조

```bash
# 현재 태그 확인
git tag --sort=-version:refname | head -5

# 태그 생성
git tag v0.2.0

# 태그 포함 푸시
git push && git push --tags
```
