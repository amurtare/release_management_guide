# 크로스페이지 링크는 단계명·번호에 종속하지 않는다

## 결정

서브 페이지(gitlab-pat-setup.html, wsl-setup.html)에서 index.html로 돌아가는 복원점 링크는
특정 Quick Start 카드 번호나 단계명을 언급하지 않는다.
대신 `index.html#quickstart` 처럼 섹션 단위의 안정적 앵커를 가리킨다.

## 이유

Quick Start 카드의 순서·제목은 바뀔 수 있다.
특정 단계명을 언급하면 index.html 수정 시 서브 페이지 텍스트도 함께 고쳐야 하는 종속성이 생긴다.

## 적용 범위

- Next Card CTA의 링크 목적지
- Next Card 제목·본문의 "N단계 ○○ 하세요" 식 표현
- 안정적 앵커 후보: `#quickstart`, `#workflow`, `#step1`~`#step6` (메인 섹션, QS와 별개 체계)

## 현재 적용 상태

| 링크 | 목적지 |
|------|--------|
| gitlab-pat-setup.html Next Card | `index.html#quickstart` |
| wsl-setup.html Next Card | `gitlab-pat-setup.html` (서브 페이지 간 이동, 문제 없음) |
