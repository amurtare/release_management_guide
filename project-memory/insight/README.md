# insight/

raw 메모 공간. 비자명한 디버깅 결론, 의외의 동작, 실험 결과 등을 빠르게 기록.

---

## 규칙

- **파일 형식**: `YYYY-MM-DD-<kebab>.md`
- **본문 필수**: `**컨텍스트**:` 줄 포함 (SessionStart hook이 추출)
- **저장 트리거**: 사용자 명시 요청 → 즉시 저장 / 에이전트 감지 → 제안만, 자동 저장 금지
- **graduation 규칙**: 두 번 이상 참조 → 본체(decisions/gotchas/components) 승격 → 원본 삭제
- **정리 시점**: 릴리즈 시 / 6개월 0참조 → 삭제

---

## 예시

```markdown
# 2026-05-19-sync-index-encoding

**컨텍스트**: /sync-index 실행 시 한글이 깨지는 현상 디버깅

PowerShell에서 파이썬 스크립트 실행 시 기본 인코딩이 cp949로 설정되어
한글 포함 파일 읽기/쓰기에서 UnicodeDecodeError 발생.
PYTHONIOENCODING=utf-8 환경변수 또는 open(..., encoding="utf-8") 명시로 해결.
```
