# release_management_guide — 저장소 유지보수

> 이 파일과 `.claude/` 디렉토리는 이 저장소 자체를 관리하기 위한 설정이다.
> **다른 프로젝트에 복사하지 않는다.** 가이드 본체는 `RELEASE_MANAGEMENT_GUIDE.md` 하나다.

---

## index.html 동기화

`RELEASE_MANAGEMENT_GUIDE.md` 또는 `README.md`를 수정했다면 `/sync-index`를 실행해 `index.html`을 최신 내용과 일치시킨다.

---

## iShare 배포

사용자가 **"iShare 배포해줘"**, **"배포 업데이트해줘"** 같은 말을 하면 아래 명령을 실행한다.

```bash
cp "D:/Git/release_management_guide/RELEASE_MANAGEMENT_GUIDE.md" "D:/Git/release_management_guide/RELEASE_MANAGEMENT_GUIDE.txt" && node "C:/Users/amurtare/.claude-enterprise/plugins/cache/isharepub/ishare-hosting/0.2.0/cli/index.js" upload 1237 "D:/Git/release_management_guide/index.html" "D:/Git/release_management_guide/wsl-setup.html" "D:/Git/release_management_guide/gitlab-pat-setup.html" "D:/Git/release_management_guide/RELEASE_MANAGEMENT_GUIDE.txt" --entry-file index.html && rm "D:/Git/release_management_guide/RELEASE_MANAGEMENT_GUIDE.txt"
```

- `RELEASE_MANAGEMENT_GUIDE.txt`는 배포용 임시 파일이며 `.gitignore`에 등록되어 있다. 배포 후 자동 삭제된다.
- `ISHARE_TOKEN`이 현재 프로세스 환경에 없으면 배포가 실패한다. 실패 시 handoff.md에 재시도 명령을 남긴다.
- 배포 성공 시 `project-memory/log.md`에 `ops | iShare 재배포` 항목을 추가한다.

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
