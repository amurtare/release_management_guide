# HTML Design System — 생성 규칙

> 이 문서는 `ref/index.html`의 디자인 언어를 기반으로 새 HTML 페이지를 생성할 때 따르는 규칙과 컴포넌트 CSS를 정리한다.
> **Part 1–2(섹션 1–9)** 가 생성 규칙이고, **Part 3(섹션 10–11)** 와 부록은 참조 자료다.

---

## Part 1 — Foundation

### 1. 디자인 토큰

모든 페이지의 `<style>` 첫 줄에 아래 `:root` 블록을 그대로 포함한다.

```css
/* Google Fonts — <head>에 추가 */
/* Newsreader:ital,opsz,wght@0,6..72,400..700;1,6..72,400 */
/* IBM+Plex+Sans:wght@300;400;500;600;700                  */
/* JetBrains+Mono:wght@400;500                              */

:root {
  /* Surfaces */
  --bg:           oklch(0.95 0.02 85);
  --bg-deep:      oklch(0.91 0.025 80);
  --surface:      oklch(0.985 0.012 88);
  --surface-alt:  oklch(0.97 0.018 85);
  --surface-glass:oklch(0.99 0.008 90 / 0.62);

  /* Ink */
  --ink:          oklch(0.18 0.03 245);
  --ink-soft:     oklch(0.36 0.025 245);
  --ink-muted:    oklch(0.55 0.02 245);
  --ink-line:     oklch(0.85 0.02 80);

  /* Phase palette — hue 회전 48°→85°→148°→200°→320° */
  --p1: oklch(0.62 0.14 48);    /* terracotta */
  --p2: oklch(0.56 0.13 148);   /* moss       */
  --p3: oklch(0.66 0.16 85);    /* saffron    */
  --p4: oklch(0.48 0.14 320);   /* mulberry   */
  --p5: oklch(0.50 0.09 200);   /* verdigris  */

  --p1-soft: oklch(0.93 0.05 50);
  --p2-soft: oklch(0.93 0.04 148);
  --p3-soft: oklch(0.94 0.06 85);
  --p4-soft: oklch(0.92 0.04 320);
  --p5-soft: oklch(0.93 0.03 200);

  /* Phase palette — dark variants (L−0.18, C×0.7) */
  --p1-dark: oklch(0.44 0.10 48);
  --p2-dark: oklch(0.38 0.09 148);
  --p3-dark: oklch(0.48 0.11 85);
  --p4-dark: oklch(0.30 0.10 320);
  --p5-dark: oklch(0.32 0.06 200);

  /* Phase palette — muted variants (L+0.08, C×0.5) */
  --p1-muted: oklch(0.70 0.07 48);
  --p2-muted: oklch(0.64 0.07 148);
  --p3-muted: oklch(0.74 0.08 85);
  --p4-muted: oklch(0.56 0.07 320);
  --p5-muted: oklch(0.58 0.05 200);

  /* Role accents (역할 스위처 사용 시) */
  --role-undergrad: var(--p1);
  --role-grad:      var(--p2);
  --role-staff:     var(--p4);
  --role-pi:        var(--p5);

  /* Geometry */
  --r-lg:   18px;
  --r-md:   12px;
  --r-sm:   6px;
  --r-pill: 999px;

  /* Elevation 1–5 */
  --e1: 0 1px 2px oklch(0.20 0.03 245 / 0.05), 0 1px 3px oklch(0.20 0.03 245 / 0.04);
  --e2: 0 2px 4px oklch(0.20 0.03 245 / 0.05), 0 4px 12px oklch(0.20 0.03 245 / 0.06);
  --e3: 0 4px 8px oklch(0.20 0.03 245 / 0.06), 0 12px 28px oklch(0.20 0.03 245 / 0.08);
  --e4: 0 6px 14px oklch(0.20 0.03 245 / 0.08), 0 24px 48px oklch(0.20 0.03 245 / 0.10);
  --e5: 0 12px 24px oklch(0.20 0.03 245 / 0.12), 0 40px 80px oklch(0.20 0.03 245 / 0.14);

  /* Type */
  --f-display: "Newsreader", ui-serif, Georgia, serif;
  --f-body:    "IBM Plex Sans", ui-sans-serif, system-ui, sans-serif;
  --f-mono:    "JetBrains Mono", ui-monospace, "SF Mono", Menlo, monospace;

  /* Motion */
  --ease-out:    cubic-bezier(0.22, 1, 0.36, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

**Elevation 사용 티어**:

| 레벨 | 용도 |
|------|------|
| `--e1` | 기본 카드 정적 상태 |
| `--e2` | hover 경량 (light lift), 스티키 요소 |
| `--e3` | hover 중량 (medium/full lift) |
| `--e4`–`--e5` | 모달, 드롭다운 등 플로팅 레이어 |

#### 1.1 팔레트 확장 규칙

6번째 이상의 색이 필요할 때 **새 hue를 추가하지 않는다**. 기본 5색의 변형 변수를 사용한다.

| 변형 | 공식 | 변수 패턴 | 용도 |
|------|------|-----------|------|
| soft  | L+0.31, C×0.34 | `--pN-soft`  | 카드 배경, 하이라이트 영역 |
| dark  | L−0.18, C×0.7  | `--pN-dark`  | 완료·최종 단계, 강한 강조 |
| muted | L+0.08, C×0.5  | `--pN-muted` | 비활성·보조 상태 |

**hue 선택**: 필요한 색과 hue 각도 거리가 가장 가까운 `--pN`을 기준으로 삼는다. `--ink` 계열(245°)이 필요한 경우 가장 가까운 `--p5`(200°)의 dark 변형으로 대체한다.

```css
/* 6번째 이상 필요 시 — dark 티어로 사이클 재시작 */
.node-6 { --c: var(--p1-dark); --c-soft: var(--p1-soft); }
.node-7 { --c: var(--p2-dark); --c-soft: var(--p2-soft); }
/* ... */
```

---

### 2. 타이포그래피 규칙

| 패밀리 | 변수 | 사용처 | 특이사항 |
|--------|------|--------|---------|
| Newsreader | `--f-display` | 헤딩, 카드 타이틀, 번호, 인용문, `<em>` 강조 | `font-weight: 500`, 장식적 사용 시 `font-style: italic` |
| IBM Plex Sans | `--f-body` | 본문 기본값 | `font-feature-settings: "ss01","cv11"` body에 전역 적용 |
| JetBrains Mono | `--f-mono` | eyebrow, 라벨, 코드, 태그, 통계 | 항상 `0.68–0.78rem`, `text-transform: uppercase`, `letter-spacing: 0.08–0.12em` |

**헤딩 스케일**:
```css
.h-display  { font-size: clamp(1.85rem, 4.2vw, 3.4rem); font-weight: 600; letter-spacing: -0.022em; }
.sec-title  { font-size: clamp(1.75rem, 3.5vw, 2.6rem); font-weight: 500; letter-spacing: -0.02em; }
```

---

### 3. 재사용 패턴 프리미티브

아래 7개 패턴이 여러 컴포넌트에서 공유된다. 컴포넌트 카탈로그에서 "프리미티브 3.N 사용"으로 참조한다.

#### 3.1 섹션 헤더

모든 `<section>` 상단에 사용하는 일관된 헤더 구조.

```css
section { padding: 5rem 0 4rem; position: relative; }

.sec-head { margin-bottom: 2.5rem; max-width: 44rem; }

.sec-eyebrow {
  font-family: var(--f-mono);
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--ink-muted);
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.85rem;
}
.sec-eyebrow .num { font-weight: 500; color: var(--accent, var(--p2)); }

.sec-title {
  font-family: var(--f-display);
  font-weight: 500;
  font-size: clamp(1.75rem, 3.5vw, 2.6rem);
  line-height: 1.1;
  letter-spacing: -0.02em;
  margin-bottom: 0.85rem;
  color: var(--ink);
}
.sec-title em { font-style: italic; font-weight: 400; color: var(--accent, var(--p2)); }

.sec-sub { font-size: 1rem; color: var(--ink-soft); line-height: 1.6; max-width: 38rem; }
```

```html
<section id="example" style="--accent: var(--p2)">
  <div class="wrap">
    <div class="sec-head">
      <div class="sec-eyebrow"><span class="num">01</span> Section Label</div>
      <h2 class="sec-title">제목 <em>강조</em></h2>
      <p class="sec-sub">섹션 설명 문장.</p>
    </div>
    <!-- 컴포넌트 -->
  </div>
</section>
```

#### 3.2 상단 컬러 바

카드 상단에 `var(--c)` 색상 4–6px 바를 올리는 패턴. `overflow: hidden`이 `border-radius` 클리핑을 담당한다.

```css
/* 부모 카드에 반드시 필요 */
.card {
  position: relative;
  overflow: hidden;       /* 이 두 줄이 바의 모서리를 깎아줌 */
  border-radius: var(--r-lg);
}

/* 상단 바 */
.card::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;            /* 변형: 5px (phase-stage), 6px (primer-card) */
  background: var(--c);
}
```

하단 바 변형 (phase-tab 활성 상태):
```css
.phase-tab::after {
  content: "";
  position: absolute;
  left: 0; right: 0; bottom: 0;
  height: 3px;
  background: var(--c);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.4s var(--ease-out);
}
.phase-tab[aria-pressed="true"]::after { transform: scaleX(1); }
```

좌측 바 변형 (playbook-head):
```css
.playbook-head::before {
  content: "";
  position: absolute;
  top: 0; left: 0;
  width: 4px; height: 100%;
  background: var(--c);
}
```

#### 3.3 코너 글로우

카드 우상단에 `var(--c-soft)` 방사형 글로우를 추가. hover 시 강도 상승.

```css
.card {
  position: relative;
  overflow: hidden;
}
.card::after {
  content: "";
  position: absolute;
  top: -60px; right: -60px;        /* 오프셋: -50px ~ -100px */
  width: 200px; height: 200px;     /* 크기: 160px ~ 300px */
  background: radial-gradient(circle, var(--c-soft) 0%, transparent 70%);
  filter: blur(20px);
  opacity: 0.5;                    /* hover 전 */
  pointer-events: none;
  transition: opacity 0.4s;
}
.card:hover::after { opacity: 1; }
```

| 컴포넌트 | 크기 | 오프셋 |
|----------|------|--------|
| `.primer-card` | 200×200 | -60px |
| `.phase-stage` | 300×300 | -100px |
| `.eco-card-ext` | 160×160 | -50px |
| `.wf-card` | 180×180 | -50px |

#### 3.4 프롬프트/인용

자연어 프롬프트나 인용문에 좌측 컬러 바 + 겹따옴표 curly quote 패턴.

```css
.prompt {
  padding: 0.85rem 1rem;
  background: oklch(0.97 0.02 85);
  border-left: 3px solid var(--c, var(--p2));
  border-radius: 0 var(--r-sm) var(--r-sm) 0;
  font-family: var(--f-display);
  font-size: 1rem;
  font-style: italic;
  color: var(--ink);
  line-height: 1.5;
}
.prompt::before {
  content: '\201C';             /* " */
  font-size: 1.6rem;
  color: var(--c, var(--p2));
  margin-right: 0.15rem;
  vertical-align: -0.18em;
}
.prompt::after {
  content: '\201D';             /* " */
  font-size: 1.6rem;
  color: var(--c, var(--p2));
  margin-left: 0.15rem;
  vertical-align: -0.18em;
}
```

코드 프롬프트 변형 (`.qs-prompt` — mono 폰트, curly quote 없음):
```css
.qs-prompt {
  font-family: var(--f-mono);
  font-size: 0.88rem;
  /* ::before / ::after 동일하게 사용 */
}
```

팁 변형 (`.fh-tip` — 따옴표 없음, saffron 컬러):
```css
.fh-tip {
  padding: 0.85rem 1rem;
  background: oklch(0.96 0.04 85);
  border-left: 3px solid var(--p3);
  border-radius: 0 var(--r-sm) var(--r-sm) 0;
  font-size: 0.88rem;
  color: var(--ink);
  line-height: 1.6;
}
```

#### 3.5 다크 코드 블록

터미널/코드 스냅샷에 쓰이는 어두운 배경 블록. 문맥에 따라 클래스 이름만 다르고 패턴은 동일하다.

```css
.code-dark {
  background: oklch(0.16 0.02 245);
  color: oklch(0.86 0.012 90);
  border-radius: var(--r-md);
  padding: 1.2rem 1.35rem;
  font-family: var(--f-mono);
  font-size: 0.78rem;
  line-height: 1.7;
  white-space: pre-wrap;
  overflow-x: auto;
}

/* 문법 강조 클래스 */
.code-dark .dim  { color: oklch(0.55 0.012 90); }   /* 주석, 흐린 텍스트 */
.code-dark .key  { color: oklch(0.78 0.14 145); }   /* 키워드 (green) */
.code-dark .new  { color: oklch(0.78 0.14 145); }   /* 새 항목 */
.code-dark .hi   { color: oklch(0.80 0.16 75); }    /* 강조 (amber) */
.code-dark .h2   { color: oklch(0.80 0.16 75); font-weight: 600; }
.code-dark .link { color: oklch(0.72 0.14 200); }   /* 링크 (teal) */
```

사용처: `.fh-md-block`, `.phase-snap`, `.gist-box` 내부 모두 이 패턴.

#### 3.6 호버 엘리베이션

카드 hover 시 위로 떠오르며 그림자가 강해지는 패턴. 3단계 티어.

```css
/* Light lift — eco-card, fh-card, phase-tab, adapt-card */
.card-light {
  transition: transform 0.3s var(--ease-out), box-shadow 0.3s var(--ease-out);
}
.card-light:hover { transform: translateY(-2px); box-shadow: var(--e2); }

/* Medium lift — qs-card, playbook, wf-card */
.card-medium {
  transition: transform 0.3s var(--ease-out), box-shadow 0.3s var(--ease-out);
}
.card-medium:hover { transform: translateY(-3px); box-shadow: var(--e3); }

/* Full lift — primer-card, loop-card */
.card-full {
  transition: transform 0.4s var(--ease-out), box-shadow 0.4s var(--ease-out);
}
.card-full:hover { transform: translateY(-4px); box-shadow: var(--e3); }
```

spring 변형: `var(--ease-out)` → `var(--ease-spring)` (탄성감 필요 시)

#### 3.7 진입 애니메이션 (스크롤 리빌)

카드·섹션이 뷰포트에 진입할 때 아래에서 위로 페이드인. 그리드 카드에는 stagger delay를 적용해 순차 등장감을 준다.

```css
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}

.reveal { opacity: 0; }
.reveal.visible {
  animation: fadeUp 0.6s var(--ease-out) both;
}

/* 카드 그리드 stagger (5개까지 CSS, 이상은 JS inline style) */
.reveal.visible:nth-child(1) { animation-delay: 0ms; }
.reveal.visible:nth-child(2) { animation-delay: 80ms; }
.reveal.visible:nth-child(3) { animation-delay: 160ms; }
.reveal.visible:nth-child(4) { animation-delay: 240ms; }
.reveal.visible:nth-child(5) { animation-delay: 320ms; }
```

```js
// IntersectionObserver 기본 패턴 (threshold: 15% 진입 시 트리거)
const io = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('visible'); io.unobserve(e.target); }
  });
}, { threshold: 0.15 });
document.querySelectorAll('.reveal').forEach(el => io.observe(el));
```

> `prefers-reduced-motion` 연동: 섹션 4.4의 전역 규칙(`animation-duration: 0.01ms`)이 자동 적용되므로 별도 처리 불필요.

**HTML 적용**: 카드 그리드의 각 카드에 `.reveal` 추가.
```html
<div class="qs-card reveal" style="--c:var(--p1);--c-soft:var(--p1-soft)">...</div>
```

---

### 4. 레이아웃 & 반응형

#### 4.1 페이지 셸

```css
* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  background: var(--bg);
  color: var(--ink);
  font-family: var(--f-body);
  font-feature-settings: "ss01", "cv11";
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
  position: relative;
}

.shell { position: relative; z-index: 2; }
.wrap  { max-width: 1180px; margin: 0 auto; padding: 0 1.5rem; }
@media (min-width: 1280px) { .wrap { padding: 0 2rem; } }

/* 텍스트 선택 브랜드 컬러 */
::selection { background: oklch(0.56 0.13 148 / 0.25); color: var(--ink); }
```

**최대 가로 폭: 1180px** — 모든 생성 HTML에 동일하게 적용한다.

#### 4.2 카드 균등 폭 규칙 (필수)

같은 그룹에 묶인 카드는 화면 크기와 관계없이 **항상 동일한 가로 폭**을 유지해야 한다. 행 수가 바뀌는 건 허용하지만, 마지막 행 카드만 늘어나는 것은 금지다.

**금지**: `repeat(auto-fit, minmax(Npx, 1fr))` — 아이템 수가 열 수의 배수가 아닐 때 마지막 행이 넓어진다.

**사용**: `repeat(N, minmax(0, 1fr))` + 미디어쿼리로 열 수를 명시 전환한다.

> `1fr`은 내부적으로 `minmax(auto, 1fr)`이다. `auto` 최솟값은 콘텐츠의 고유 너비(intrinsic minimum)를 허용하므로, `<pre>` 같은 줄바꿈 없는 콘텐츠가 있으면 열 폭이 달라진다. `minmax(0, 1fr)`로 최솟값을 0으로 고정해야 진짜 균등 폭이 보장된다.

```css
/* ✅ 올바른 패턴 — 3카드 그리드 */
.card-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));  /* 0: 콘텐츠가 열 폭을 늘리지 않음 */
  gap: 1.25rem;
}
@media (max-width: 900px) { .card-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 560px) { .card-grid { grid-template-columns: 1fr; } }

/* ❌ 금지 패턴 */
.card-grid { grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
```

#### 4.3 그리드별 브레이크포인트 참조표

| 그리드 | 카드 수 | 기본 | 중단점 |
|--------|---------|------|--------|
| `.quickstart` | 3 | `repeat(3, minmax(0,1fr))` | @900px → `1fr` |
| `.primer-grid` | 3 | `repeat(3, minmax(0,1fr))` | @900px → `1fr` |
| `.eco-grid-core` | 3 | `repeat(3, minmax(0,1fr))` | @700px → `1fr` |
| `.eco-grid-ext` | 5 | `repeat(3, minmax(0,1fr))` | @700px → `1fr` |
| `.fh-grid` | 5 | `repeat(2, minmax(0,1fr))` | @800px → `1fr` |
| `.playbook-grid` | 4 | `repeat(2, minmax(0,1fr))` | @600px → `1fr` |
| `.phase-rail` | 5 | `repeat(5, minmax(0,1fr))` | @720px → `repeat(2,1fr)` |
| `.eco-grid-ops` | 7 | `repeat(4, minmax(0,1fr))` | @800px → `repeat(2,1fr)` · @560px → `1fr` |
| `.adapt-grid` | 8 | `repeat(4, minmax(0,1fr))` | @900px → `repeat(2,1fr)` · @560px → `1fr` |
| `.loops-grid` | 5 | `repeat(3, minmax(0,1fr))` | @800px → `repeat(2,1fr)` · @560px → `1fr` |
| `.workflows` | 5 | `repeat(3, minmax(0,1fr))` | @800px → `repeat(2,1fr)` · @560px → `1fr` |

> `.eco-grid-ops`, `.loops-grid`, `.playbook-grid`, `.adapt-grid`, `.workflows`는 `ref/index.html`에서 `auto-fit + minmax`를 사용하지만, 카드 균등 폭 규칙에 따라 위 `repeat(N, 1fr)` 패턴으로 교정한다.

#### 4.4 접근성

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}

/* 키보드 포커스 링 — 마우스 클릭 시에는 숨김 */
:focus-visible {
  outline: 2px solid var(--accent, var(--p2));
  outline-offset: 2px;
}
:focus:not(:focus-visible) { outline: none; }
```

> `.role-pill`, `.phase-tab`, Gist 복사 버튼 등 인터랙티브 요소에 키보드 탐색 시 브랜드 컬러 아웃라인이 표시된다.

---

### 5. 배경 & 텍스처

#### 5.1 페이퍼 그레인

두 개의 `body` 가상 요소로 종이 질감을 구현한다. `z-index: 0/1`, `.shell`은 `z-index: 2`로 콘텐츠가 위에 올라온다.

```css
/* 앰비언트 그라디언트 */
body::before {
  content: "";
  position: fixed; inset: 0;
  pointer-events: none; z-index: 0;
  background:
    radial-gradient(ellipse 80% 60% at 20% 0%,   oklch(0.66 0.16 85 / 0.10) 0%, transparent 60%),
    radial-gradient(ellipse 70% 50% at 100% 30%,  oklch(0.50 0.09 200 / 0.07) 0%, transparent 60%),
    radial-gradient(ellipse 80% 70% at 0% 100%,   oklch(0.48 0.14 320 / 0.06) 0%, transparent 60%);
  mix-blend-mode: multiply;
}

/* SVG 노이즈 텍스처 */
body::after {
  content: "";
  position: fixed; inset: 0;
  pointer-events: none; z-index: 1;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'><filter id='n'><feTurbulence baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0.2 0 0 0 0 0.18 0 0 0 0 0.18 0 0 0 0.05 0'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>");
  opacity: 0.55;
  mix-blend-mode: multiply;
}
```

#### 5.2 글라스모피즘 (스티키 요소)

```css
.sticky-bar {
  position: sticky; top: 0; z-index: 50;
  background: oklch(0.95 0.02 85 / 0.78);
  backdrop-filter: blur(20px) saturate(1.4);
  -webkit-backdrop-filter: blur(20px) saturate(1.4);
  border-bottom: 1px solid oklch(0.85 0.02 80 / 0.5);
}
```

---

## Part 2 — Component Catalog

각 항목 구조: **용도** → **그리드 CSS** → **카드 CSS** → **서브 요소** → **HTML 스켈레톤**

### 6. 컴포넌트 카탈로그

---

#### 6.1 `.qs-card` — Quick Start 카드

순서가 있는 단계 안내 (3개). 프리미티브: 3.2(상단 바), 3.6 medium lift.

```css
.quickstart {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  margin: 2rem 0 1.5rem;
}
@media (max-width: 900px) { .quickstart { grid-template-columns: 1fr; } }

.qs-card {
  background: var(--surface);
  border: 1px solid oklch(0.88 0.018 80);
  border-radius: var(--r-lg);
  padding: 1.5rem 1.5rem 1.4rem;
  position: relative; overflow: hidden;
  box-shadow: var(--e1);
  transition: transform 0.3s var(--ease-out), box-shadow 0.3s var(--ease-out);
}
.qs-card:hover { transform: translateY(-3px); box-shadow: var(--e3); }
.qs-card::before { content:""; position:absolute; top:0;left:0;right:0; height:4px; background:var(--c); }

.qs-num {
  display: inline-flex; align-items: baseline; gap: 0.4rem;
  font-family: var(--f-display); font-size: 2.1rem; font-weight: 500;
  font-style: italic; color: var(--c); letter-spacing: -0.03em; line-height: 1;
  margin-bottom: 0.25rem;
}
.qs-num small {
  font-family: var(--f-mono); font-size: 0.7rem; font-style: normal;
  color: var(--ink-muted); letter-spacing: 0.1em; text-transform: uppercase; font-weight: 600;
}
.qs-title { font-family: var(--f-display); font-size: 1.25rem; font-weight: 500; letter-spacing: -0.01em; color: var(--ink); margin-bottom: 0.85rem; line-height: 1.25; }
.qs-body  { font-size: 0.92rem; line-height: 1.7; color: var(--ink); }
.qs-body strong { color: var(--c); font-weight: 600; }
.qs-bullet { display: flex; align-items: baseline; gap: 0.55rem; padding: 0.2rem 0; font-size: 0.88rem; }
.qs-bullet::before { content:"·"; color:var(--c); font-weight:700; font-size:1.1rem; line-height:1; }
```

```html
<div class="quickstart">
  <div class="qs-card" style="--c:var(--p1);--c-soft:var(--p1-soft)">
    <div class="qs-num">01<small>STEP</small></div>
    <div class="qs-title">제목</div>
    <div class="qs-body">
      <div class="qs-bullet">항목</div>
    </div>
  </div>
</div>
```

---

#### 6.2 `.fh-card` — FAQ 카드

Q&A 형식 (5개, 2열). 프리미티브: 3.4(프롬프트), 3.5(다크 코드), 3.6 light lift.

```css
.fh-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1.25rem;
}
@media (max-width: 800px) { .fh-grid { grid-template-columns: 1fr; } }

.fh-card {
  background: var(--surface);
  border: 1px solid oklch(0.88 0.018 80);
  border-radius: var(--r-lg);
  padding: 1.6rem 1.7rem 1.5rem;
  position: relative; overflow: hidden;
  box-shadow: var(--e1);
  border-top: 4px solid var(--c, var(--p2));
  transition: transform 0.3s var(--ease-out), box-shadow 0.3s var(--ease-out);
}
.fh-card:hover { transform: translateY(-2px); box-shadow: var(--e2); }
.fh-card.span-2 { grid-column: span 2; }
@media (max-width: 800px) { .fh-card.span-2 { grid-column: span 1; } }

.fh-num { font-family:var(--f-mono); font-size:0.7rem; letter-spacing:0.1em; color:var(--c); font-weight:600; text-transform:uppercase; margin-bottom:0.5rem; }
.fh-q   { font-family:var(--f-display); font-size:1.3rem; font-weight:500; letter-spacing:-0.01em; line-height:1.25; color:var(--ink); margin-bottom:0.85rem; }
.fh-q em { font-style:italic; color:var(--c); font-weight:400; }
.fh-a   { font-size:0.92rem; line-height:1.7; color:var(--ink); margin-bottom:0.85rem; }
.fh-a strong { color:var(--c); font-weight:600; }
.fh-a-emph { font-family:var(--f-display); font-size:1.1rem; font-weight:500; line-height:1.3; color:var(--c); margin:0.4rem 0 1rem; }

/* 인라인 프롬프트 (프리미티브 3.4 변형) */
.fh-prompt-inline {
  display:block; margin:0.7rem 0 0.85rem; padding:0.75rem 1rem;
  background:oklch(0.97 0.02 85); border-left:3px solid var(--c);
  border-radius:0 var(--r-sm) var(--r-sm) 0;
  font-family:var(--f-display); font-size:1rem; font-style:italic; color:var(--ink); line-height:1.45;
}
.fh-prompt-inline::before { content:'\201C'; color:var(--c); margin-right:0.15rem; font-size:1.3rem; vertical-align:-0.18em; }
.fh-prompt-inline::after  { content:'\201D'; color:var(--c); margin-left:0.15rem;  font-size:1.3rem; vertical-align:-0.18em; }

/* 마크다운 예시 블록 (프리미티브 3.5) */
.fh-md-block {
  background:oklch(0.16 0.02 245); color:oklch(0.86 0.012 90);
  border-radius:var(--r-md); padding:1.2rem 1.35rem;
  font-family:var(--f-mono); font-size:0.78rem; line-height:1.7;
  white-space:pre-wrap; overflow-x:auto; margin:0.75rem 0;
}
.fh-md-block .fm   { color:oklch(0.55 0.012 90); }
.fh-md-block .key  { color:oklch(0.78 0.14 145); }
.fh-md-block .h2   { color:oklch(0.80 0.16 75); font-weight:600; }
.fh-md-block .link { color:oklch(0.72 0.14 200); }
```

```html
<div class="fh-grid">
  <div class="fh-card" style="--c:var(--p1)">
    <div class="fh-num">Q 01</div>
    <div class="fh-q">질문 제목?</div>
    <p class="fh-a">답변 본문.</p>
  </div>
  <div class="fh-card span-2" style="--c:var(--p2)"><!-- 전체 너비 카드 --></div>
</div>
```

---

#### 6.3 `.primer-card` — 개념 카드

핵심 개념 소개 (3개). 프리미티브: 3.2(6px 상단 바), 3.3(코너 글로우), 3.6 full lift.

```css
.primer-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.25rem;
  margin-bottom: 4rem;
}
@media (max-width: 900px) { .primer-grid { grid-template-columns: 1fr; } }

.primer-card {
  background: var(--surface);
  border: 1px solid oklch(0.88 0.018 80);
  border-radius: var(--r-lg);
  padding: 1.75rem 1.65rem 1.5rem;
  position: relative; overflow: hidden;
  box-shadow: var(--e1);
  transition: all 0.4s var(--ease-out);
}
.primer-card::before { content:""; position:absolute; top:0;left:0;right:0; height:6px; background:var(--c); }
.primer-card::after  {
  content:""; position:absolute; top:-60px; right:-60px;
  width:200px; height:200px;
  background:radial-gradient(circle, var(--c-soft) 0%, transparent 70%);
  filter:blur(20px); opacity:0.6; pointer-events:none; transition:opacity 0.4s;
}
.primer-card:hover { transform: translateY(-4px); box-shadow: var(--e3); }
.primer-card:hover::after { opacity: 1; }

.primer-num  { font-family:var(--f-mono); font-size:0.7rem; letter-spacing:0.1em; color:var(--c); font-weight:600; margin-bottom:0.4rem; }
.primer-name { font-family:var(--f-display); font-size:1.85rem; font-weight:500; letter-spacing:-0.02em; line-height:1.05; color:var(--ink); margin-bottom:0.3rem; }
.primer-tag  { display:inline-block; padding:0.2rem 0.65rem; background:var(--c-soft); color:oklch(from var(--c) calc(l - 0.15) c h); font-family:var(--f-mono); font-size:0.7rem; border-radius:var(--r-pill); margin-bottom:1rem; }
.primer-body { font-size:0.92rem; line-height:1.65; color:var(--ink); margin-bottom:1rem; }
.primer-body strong { color:var(--c); font-weight:600; }
.primer-stat { font-family:var(--f-mono); font-size:0.75rem; color:var(--ink-muted); padding-top:0.85rem; border-top:1px solid oklch(0.88 0.018 80); }
```

```html
<div class="primer-grid">
  <div class="primer-card" style="--c:var(--p1);--c-soft:var(--p1-soft)">
    <div class="primer-num">001</div>
    <div class="primer-name">개념명</div>
    <span class="primer-tag">태그</span>
    <p class="primer-body">설명 본문.</p>
    <div class="primer-stat">통계 정보</div>
  </div>
</div>
```

---

#### 6.4 `.eco-card` / `.eco-card-ext` — 에코시스템 카드

폴더/시스템 아키텍처 계층 표시. Core(3개 3열), Ops(7개 4열), Ext(5개 3열).

```css
/* Core — 3열 */
.eco-grid-core {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.85rem;
}
@media (max-width: 700px) { .eco-grid-core { grid-template-columns: 1fr; } }

/* Operations — 4열 */
.eco-grid-ops {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.65rem;
}
@media (max-width: 800px) { .eco-grid-ops { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 560px) { .eco-grid-ops { grid-template-columns: 1fr; } }

/* External — 3열 */
.eco-grid-ext {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}
@media (max-width: 700px) { .eco-grid-ext { grid-template-columns: 1fr; } }

/* 기본 에코 카드 — 좌측 3px 바 */
.eco-card {
  padding: 1rem 1.15rem;
  background: var(--surface);
  border: 1px solid oklch(0.88 0.018 80);
  border-radius: var(--r-md);
  border-left: 3px solid var(--c, var(--p2));
  transition: all 0.25s var(--ease-out);
}
.eco-card:hover { transform: translateY(-2px); box-shadow: var(--e2); }
.eco-folder { font-family:var(--f-mono); font-size:0.78rem; color:var(--c,var(--p2)); font-weight:500; margin-bottom:0.3rem; }
.eco-name   { font-family:var(--f-display); font-size:1.05rem; font-weight:500; margin-bottom:0.35rem; color:var(--ink); }
.eco-body   { font-size:0.82rem; color:var(--ink-soft); line-height:1.5; }

/* 외부 시스템 카드 — 상단 4px 바 + 코너 글로우 (프리미티브 3.3) */
.eco-card-ext {
  padding: 1.4rem 1.35rem;
  background: var(--surface);
  border-radius: var(--r-md);
  border: 1px solid oklch(0.88 0.018 80);
  border-top: 4px solid var(--c, var(--p4));
  position: relative; overflow: hidden;
  transition: all 0.3s var(--ease-out);
}
.eco-card-ext::after {
  content:""; position:absolute; top:-50px; right:-50px;
  width:160px; height:160px;
  background:radial-gradient(circle, var(--c-soft, var(--p4-soft)) 0%, transparent 70%);
  filter:blur(20px); opacity:0.5; pointer-events:none; transition:opacity 0.3s;
}
.eco-card-ext:hover { transform: translateY(-3px); box-shadow: var(--e3); }
.eco-card-ext:hover::after { opacity: 1; }
.eco-ext-icon {
  width:36px; height:36px; border-radius:10px;
  background:var(--c-soft, var(--p4-soft));
  display:flex; align-items:center; justify-content:center;
  margin-bottom:0.85rem;
  font-family:var(--f-mono); font-size:1.05rem; font-weight:600;
  color:var(--c, var(--p4));
}

/* 계층 구분선 */
.eco-bridge {
  text-align:center; font-family:var(--f-mono); font-size:0.72rem;
  color:var(--ink-muted); letter-spacing:0.12em; margin:1.75rem 0 1.5rem;
}
.eco-bridge::before, .eco-bridge::after {
  content:""; display:inline-block; width:60px; height:1px;
  background:var(--ink-line); vertical-align:middle; margin:0 1rem;
}
```

---

#### 6.5 `.loop-card` — 반복 루프 카드

주기적 운영 루프 (5개, 3열). SVG 오빗 애니메이션 포함.

```css
.loops-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.25rem;
}
@media (max-width: 800px) { .loops-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 560px) { .loops-grid { grid-template-columns: 1fr; } }

.loop-card {
  background: var(--surface);
  border: 1px solid oklch(0.88 0.018 80);
  border-radius: var(--r-lg);
  padding: 1.5rem;
  position: relative; overflow: hidden;
  box-shadow: var(--e1);
  transition: transform 0.4s var(--ease-out), box-shadow 0.4s var(--ease-out);
}
.loop-card:hover { transform: translateY(-4px); box-shadow: var(--e3); }

/* SVG 오빗 */
.loop-orbit { width:80px; height:80px; margin-bottom:1rem; }
.loop-orbit .ring { fill:none; stroke:var(--c-soft); stroke-width:4; }
.loop-orbit .arc  { fill:none; stroke:var(--c); stroke-width:4; stroke-linecap:round; stroke-dasharray:100; animation:spin 4s linear infinite; }
.loop-orbit .dot  { fill:var(--c); }
@keyframes spin { from { stroke-dashoffset:100; } to { stroke-dashoffset:0; } }

.loop-cad  { font-family:var(--f-mono); font-size:0.68rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--c); font-weight:600; margin-bottom:0.4rem; }
.loop-name { font-family:var(--f-display); font-size:1.2rem; font-weight:500; margin-bottom:0.6rem; color:var(--ink); }
.loop-flow { font-family:var(--f-mono); font-size:0.78rem; color:var(--ink-soft); background:var(--surface-alt); padding:0.7rem 0.85rem; border-radius:var(--r-sm); line-height:1.65; margin-bottom:0.85rem; }
.loop-out  { font-size:0.85rem; color:var(--ink-soft); }
```

```html
<div class="loop-card" style="--c:var(--p1);--c-soft:var(--p1-soft)">
  <div class="loop-orbit">
    <svg viewBox="0 0 80 80">
      <circle class="ring" cx="40" cy="40" r="34"/>
      <circle class="arc"  cx="40" cy="40" r="34"/>
      <circle class="dot"  cx="40" cy="6"  r="4"/>
    </svg>
  </div>
  <div class="loop-cad">DAILY</div>
  <div class="loop-name">루프 이름</div>
  <div class="loop-flow">흐름 설명</div>
  <div class="loop-out">아웃풋</div>
</div>
```

---

#### 6.6 `.phase-tab` + `.phase-stage` — 페이즈 탐색기

탭 클릭 → 스테이지 패널 교체 (5탭). 프리미티브: 3.2(하단 바 변형), 3.2(상단 바), 3.3(코너 글로우).

```css
/* 탭 레일 */
.phase-rail {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 0.75rem; margin-bottom: 2rem;
}
@media (max-width: 720px) { .phase-rail { grid-template-columns: repeat(2, minmax(0, 1fr)); } }

.phase-tab {
  padding: 1.1rem 1rem;
  background: var(--surface); border: 1px solid oklch(0.88 0.018 80);
  border-radius: var(--r-md); cursor: pointer;
  transition: all 0.3s var(--ease-out); text-align: left;
  position: relative; overflow: hidden;
}
.phase-tab::after { content:""; position:absolute; left:0;right:0;bottom:0; height:3px; background:var(--c); transform:scaleX(0); transform-origin:left; transition:transform 0.4s var(--ease-out); }
.phase-tab:hover { transform: translateY(-2px); box-shadow: var(--e2); }
.phase-tab[aria-pressed="true"] { box-shadow: var(--e2); border-color: var(--c); }
.phase-tab[aria-pressed="true"]::after { transform: scaleX(1); }

.pt-num   { font-family:var(--f-mono); font-size:0.68rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--c); font-weight:600; }
.pt-name  { font-family:var(--f-display); font-size:1.15rem; font-weight:500; margin:0.3rem 0 0.15rem; color:var(--ink); }
.pt-dates { font-family:var(--f-mono); font-size:0.72rem; color:var(--ink-muted); }

/* 스테이지 패널 */
.phase-stage {
  background: var(--surface); border: 1px solid oklch(0.88 0.018 80);
  border-radius: var(--r-lg); padding: 2.25rem;
  position: relative; overflow: hidden; min-height: 380px; box-shadow: var(--e2);
}
.phase-stage::before { content:""; position:absolute; top:0;left:0;right:0; height:5px; background:var(--c); }
.phase-stage::after  { content:""; position:absolute; top:-100px;right:-100px; width:300px;height:300px; background:radial-gradient(circle, var(--c-soft) 0%, transparent 70%); opacity:0.7; pointer-events:none; filter:blur(20px); }

.phase-content { position:relative; z-index:1; display:grid; grid-template-columns:1.3fr 1fr; gap:2.5rem; }
@media (max-width: 800px) { .phase-content { grid-template-columns: 1fr; } }

.phase-tagline { font-family:var(--f-display); font-size:clamp(1.4rem,2.2vw,1.8rem); font-weight:500; color:var(--c); margin-bottom:0.5rem; }
.phase-summary { font-size:0.95rem; color:var(--ink-soft); line-height:1.65; margin-bottom:1.5rem; }

/* 폴더 스냅샷 (프리미티브 3.5) */
.phase-snap { background:oklch(0.16 0.02 245); color:oklch(0.86 0.012 90); border-radius:var(--r-md); padding:1.25rem; font-family:var(--f-mono); font-size:0.78rem; line-height:1.7; white-space:pre; overflow-x:auto; }
.phase-snap .dim { color:oklch(0.55 0.012 90); }
.phase-snap .new { color:oklch(0.78 0.14 145); }
.phase-snap .hi  { color:oklch(0.80 0.16 75); }
```

---

#### 6.7 `.playbook` — 역할 플레이북 카드

역할별 단계 안내 (4개, 2열). 프리미티브: 3.2(좌측 바 변형), 3.6 medium lift.

```css
.playbook-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1.25rem;
}
@media (max-width: 600px) { .playbook-grid { grid-template-columns: 1fr; } }

.playbook {
  background: var(--surface); border: 1px solid oklch(0.88 0.018 80);
  border-radius: var(--r-lg); overflow: hidden; position: relative;
  box-shadow: var(--e1);
  transition: transform 0.3s var(--ease-out), box-shadow 0.3s var(--ease-out);
}
.playbook:hover { transform: translateY(-3px); box-shadow: var(--e3); }

/* 헤더 영역 */
.playbook-head {
  padding: 1.5rem 1.5rem 1rem;
  background: linear-gradient(135deg, var(--c-soft) 0%, transparent 100%);
  border-bottom: 1px solid oklch(0.92 0.018 80);
  position: relative;
}
.playbook-head::before { content:""; position:absolute; top:0;left:0; width:4px;height:100%; background:var(--c); }

.pb-role  { font-family:var(--f-mono); font-size:0.7rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--c); font-weight:600; margin-bottom:0.4rem; }
.pb-title { font-family:var(--f-display); font-size:1.4rem; font-weight:500; letter-spacing:-0.015em; color:var(--ink); line-height:1.15; }
.pb-sub   { font-size:0.85rem; color:var(--ink-soft); margin-top:0.4rem; line-height:1.5; }

/* 단계 목록 */
.playbook-body { padding: 1.25rem 1.5rem 1.5rem; }
.pb-step { display:grid; grid-template-columns:28px 1fr; gap:0.75rem; padding:0.65rem 0; border-bottom:1px dashed oklch(0.90 0.02 80); }
.pb-step:last-child { border-bottom: 0; }
.pb-step-num  { width:24px;height:24px; border-radius:50%; background:var(--c); color:oklch(0.99 0.005 90); display:flex;align-items:center;justify-content:center; font-family:var(--f-mono); font-size:0.72rem; font-weight:600; }
.pb-step-text { font-size:0.85rem; color:var(--ink); line-height:1.55; }
.pb-step-text strong { color:var(--c); font-weight:600; }
```

---

#### 6.8 `.adapt-card` — 원칙 카드

간결한 원칙 목록 (8개, 4열). 컨테이너 `.adapt`에 대형 배경 글로우 포함.

```css
.adapt {
  background: linear-gradient(180deg, var(--surface) 0%, var(--bg-deep) 100%);
  border-radius: var(--r-lg); padding: 3rem;
  position: relative; overflow: hidden; box-shadow: var(--e3);
}
.adapt::before {
  content:""; position:absolute; top:-100px;left:-100px; width:400px;height:400px;
  background:radial-gradient(circle, var(--p2-soft) 0%, transparent 60%);
  filter:blur(40px); pointer-events:none;
}

.adapt-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
  position: relative; z-index: 1;
}
@media (max-width: 900px) { .adapt-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 560px) { .adapt-grid { grid-template-columns: 1fr; } }

.adapt-card {
  padding: 1.25rem; background: var(--surface);
  border-radius: var(--r-md); border: 1px solid oklch(0.88 0.018 80);
  transition: all 0.3s var(--ease-out);
}
.adapt-card:hover { border-color: var(--p2); transform: translateY(-2px); box-shadow: var(--e2); }

.adapt-num   { font-family:var(--f-display); font-size:1.6rem; font-weight:500; color:var(--p2); letter-spacing:-0.02em; margin-bottom:0.4rem; }
.adapt-title { font-size:0.95rem; font-weight:600; margin-bottom:0.5rem; color:var(--ink); line-height:1.3; }
.adapt-body  { font-size:0.83rem; color:var(--ink-soft); line-height:1.55; }
```

---

#### 6.9 `.wf-card` — 워크플로 시나리오 카드

실제 사용 사례 (5개, 3열). 프리미티브: 3.3(코너 글로우), 3.4(프롬프트), 3.6 medium lift.

```css
.workflows {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.25rem;
}
@media (max-width: 800px) { .workflows { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 560px) { .workflows { grid-template-columns: 1fr; } }

.wf-card {
  background: var(--surface); border: 1px solid oklch(0.88 0.018 80);
  border-radius: var(--r-lg); padding: 1.5rem 1.65rem 1.4rem;
  position: relative; overflow: hidden; box-shadow: var(--e1);
  border-left: 4px solid var(--c, var(--p2));
  transition: transform 0.3s var(--ease-out), box-shadow 0.3s var(--ease-out);
}
.wf-card:hover { transform: translateY(-3px); box-shadow: var(--e3); }
.wf-card::after {
  content:""; position:absolute; top:-50px;right:-50px; width:180px;height:180px;
  background:radial-gradient(circle, var(--c-soft,var(--p2-soft)) 0%, transparent 70%);
  filter:blur(20px); opacity:0.55; pointer-events:none;
}

.wf-role {
  display:inline-flex; align-items:center; gap:0.4rem;
  padding:0.22rem 0.65rem; background:var(--c-soft,var(--p2-soft));
  color:oklch(from var(--c,var(--p2)) calc(l - 0.18) c h);
  border-radius:var(--r-pill); font-family:var(--f-mono); font-size:0.7rem;
  font-weight:600; text-transform:uppercase; margin-bottom:0.7rem;
}
.wf-role::before { content:""; width:7px;height:7px; border-radius:50%; background:var(--c,var(--p2)); }
.wf-situation { font-family:var(--f-display); font-size:1.18rem; font-weight:500; line-height:1.25; color:var(--ink); margin-bottom:0.85rem; }
.wf-context   { font-size:0.85rem; color:var(--ink-soft); line-height:1.55; margin-bottom:0.85rem; }

/* 시스템 칩 */
.wf-systems { display:flex; flex-wrap:wrap; gap:0.4rem; margin-bottom:0.95rem; }
.wf-chip { display:inline-flex; align-items:center; gap:0.3rem; padding:0.2rem 0.55rem; background:var(--surface-alt); border:1px solid oklch(0.88 0.018 80); border-radius:var(--r-sm); font-family:var(--f-mono); font-size:0.72rem; color:var(--ink); }

/* 프롬프트 인용 (프리미티브 3.4) */
.wf-prompt-label { font-family:var(--f-mono); font-size:0.68rem; letter-spacing:0.1em; color:var(--ink-muted); text-transform:uppercase; font-weight:600; margin-bottom:0.35rem; }
.wf-prompt {
  padding:0.85rem 1rem; background:oklch(0.97 0.02 85);
  border-left:3px solid var(--c,var(--p2)); border-radius:0 var(--r-sm) var(--r-sm) 0;
  font-family:var(--f-display); font-size:1rem; color:var(--ink); line-height:1.5; font-style:italic;
}
.wf-prompt::before { content:'\201C'; font-size:1.6rem; color:var(--c,var(--p2)); margin-right:0.15rem; vertical-align:-0.18em; }
.wf-prompt::after  { content:'\201D'; font-size:1.6rem; color:var(--c,var(--p2)); margin-left:0.15rem;  vertical-align:-0.18em; }

.wf-out { margin-top:0.85rem; font-size:0.83rem; color:var(--ink-soft); line-height:1.55; }
.wf-out strong { display:block; font-family:var(--f-mono); font-size:0.68rem; letter-spacing:0.1em; text-transform:uppercase; color:var(--c,var(--p2)); margin-bottom:0.25rem; font-weight:600; }
```

---

#### 6.10 `.role-callout` — 섹션 역할 콜아웃

주요 섹션 하단에 붙는 역할별 코멘트 블록.

```css
.role-callout {
  margin-top: 1.75rem; padding: 1.25rem 1.5rem;
  background: linear-gradient(135deg, var(--accent-soft, oklch(0.96 0.02 80)) 0%, var(--surface) 100%);
  border-left: 4px solid var(--accent, var(--p2));
  border-radius: 0 var(--r-md) var(--r-md) 0;
  box-shadow: var(--e1);
}
.role-callout-head {
  display:flex; align-items:center; gap:0.5rem;
  font-family:var(--f-mono); font-size:0.7rem; text-transform:uppercase; letter-spacing:0.1em;
  color:var(--accent,var(--p2)); font-weight:600; margin-bottom:0.5rem;
}
.role-callout-head::before { content:""; width:8px;height:8px; background:var(--accent,var(--p2)); border-radius:50%; }
.role-callout-body { font-size:0.92rem; line-height:1.6; color:var(--ink); }
.role-callout-body strong { color:var(--accent,var(--p2)); font-weight:600; }

/* 역할 가시성 제어 */
[data-show-role] { display: none; }
body[data-role="undergrad"] [data-show-role="undergrad"],
body[data-role="grad"]      [data-show-role="grad"],
body[data-role="staff"]     [data-show-role="staff"],
body[data-role="pi"]        [data-show-role="pi"] { display: block; }
```

```html
<div class="role-callout">
  <div class="role-callout-head">역할 관련 노트</div>
  <div class="role-callout-body" data-show-role="grad">대학원생 전용 설명.</div>
  <div class="role-callout-body" data-show-role="pi">PI 전용 설명.</div>
</div>
```

---

#### 6.11 Hero 영역

페이지 최상단. 제목·리드·통계 카운터로 구성.

```css
.hero {
  padding: 5rem 0 3rem;
  position: relative;
}

/* 상단 eyebrow (섹션 헤더 변형 — 대시 선 선행) */
.eyebrow {
  display: inline-flex; align-items: center; gap: 0.5rem;
  font-family: var(--f-mono); font-size: 0.72rem; text-transform: uppercase;
  letter-spacing: 0.12em; color: var(--ink-muted); margin-bottom: 1.25rem;
}
.eyebrow::before { content: ""; width: 24px; height: 1px; background: var(--ink-muted); }

.h-display {
  font-family: var(--f-display); font-weight: 600;
  font-size: clamp(1.85rem, 4.2vw, 3.4rem);
  line-height: 1.08; letter-spacing: -0.022em; color: var(--ink);
  margin-bottom: 1.5rem; max-width: 26ch;
}
.h-display em { font-style: italic; font-weight: 400; color: var(--p2); }

.lede {
  font-size: clamp(1rem, 1.4vw, 1.18rem);
  color: var(--ink-soft); max-width: 38rem; margin-bottom: 2.5rem; line-height: 1.6;
}

/* 통계 행 — wave 스타일, 카드 아님 */
.hero-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));  /* 통계는 균등 폭 예외 허용 */
  gap: 0;
  border-top: 1px solid var(--ink-line); border-bottom: 1px solid var(--ink-line);
  padding: 1.5rem 0; margin-top: 3rem;
}
.h-stat { padding: 0.25rem 1.5rem 0.25rem 0; border-right: 1px solid var(--ink-line); }
.h-stat:last-child { border-right: 0; }
.h-stat-num {
  font-family: var(--f-display); font-weight: 500;
  font-size: clamp(1.75rem, 3vw, 2.4rem); letter-spacing: -0.02em;
  line-height: 1; color: var(--ink);
}
.h-stat-num small { font-family: var(--f-body); font-size: 0.75rem; font-weight: 500; color: var(--ink-muted); letter-spacing: 0; margin-left: 0.25rem; }
.h-stat-lab { font-family: var(--f-mono); font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--ink-muted); margin-top: 0.4rem; }
```

```html
<div class="hero">
  <div class="wrap">
    <div class="eyebrow">카테고리 레이블</div>
    <h1 class="h-display">제목 <em>강조</em></h1>
    <p class="lede">리드 문단.</p>
    <div class="hero-stats">
      <div class="h-stat">
        <div class="h-stat-num" data-count="42">0<small>개</small></div>
        <div class="h-stat-lab">통계 레이블</div>
      </div>
    </div>
  </div>
</div>
```

> `data-count` 속성이 있으면 JS 카운트업 애니메이션이 적용된다 (Section 8 참조).

---

#### 6.12 `.role-bar` — 역할 스위처 (스티키)

스크롤에 따라 상단에 고정되는 역할 선택 바. 프리미티브 5.2(글라스모피즘) 적용.

```css
.role-bar {
  position: sticky; top: 0; z-index: 50;
  padding: 0.75rem 0;
  background: oklch(0.95 0.02 85 / 0.78);
  backdrop-filter: blur(20px) saturate(1.4);
  -webkit-backdrop-filter: blur(20px) saturate(1.4);
  border-bottom: 1px solid oklch(0.85 0.02 80 / 0.5);
}
.role-inner {
  display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap;
}
.role-label {
  font-family: var(--f-mono); font-size: 0.7rem; text-transform: uppercase;
  letter-spacing: 0.1em; color: var(--ink-muted); margin-right: 0.25rem;
}
.role-pills { display: flex; gap: 0.4rem; flex-wrap: wrap; }

.role-pill {
  padding: 0.45rem 0.95rem;
  border: 1px solid oklch(0.85 0.02 80);
  background: var(--surface); border-radius: var(--r-pill);
  font-family: var(--f-body); font-weight: 500; font-size: 0.83rem;
  color: var(--ink-soft); cursor: pointer;
  transition: all 0.25s var(--ease-out);
  position: relative; overflow: hidden;
}
.role-pill:hover { color: var(--ink); border-color: var(--accent, var(--ink-soft)); transform: translateY(-1px); }
.role-pill[aria-pressed="true"] { background: var(--accent); color: oklch(0.99 0.005 90); border-color: transparent; box-shadow: var(--e2); }
.role-pill .glyph { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: var(--accent); margin-right: 0.4rem; vertical-align: middle; transition: all 0.25s; }
.role-pill[aria-pressed="true"] .glyph { background: oklch(0.99 0.005 90); }
```

```html
<div class="role-bar">
  <div class="wrap role-inner">
    <span class="role-label">읽는 사람</span>
    <div class="role-pills" id="rolePills">
      <button class="role-pill" data-role="grad" style="--accent: var(--role-grad);" aria-pressed="true">
        <span class="glyph"></span>대학원생
      </button>
      <button class="role-pill" data-role="pi" style="--accent: var(--role-pi);" aria-pressed="false">
        <span class="glyph"></span>PI
      </button>
    </div>
  </div>
</div>
```

> JS에서 `document.body.dataset.role = role`로 설정하면 `[data-show-role]` 패턴(6.10 참조)이 연동된다.

---

### 7. 데이터 시각화 컴포넌트

> JS로 생성되는 SVG 컴포넌트. CSS 컨테이너만 문서화한다.

| 유형 | 컨테이너 클래스 | 비고 |
|------|----------------|------|
| Knowledge Chain SVG | `.chain`, `.chain-svg-wrap`, `.chain-svg` | 6노드 클릭 가능 SVG |
| 스택 에리어 차트 | `.flow-card`, `.flow-svg-wrap` | 31일 × 5레이어, hover 툴팁 |
| 데일리 렛저 | `.ledger`, `.ledger-strip`, `.day-cell` | 31개 바, 로그 스케일 |
| Trellis 바 차트 | `.trellis-chart`, `.trellis-bars`, `.tbar` | 스크롤 트리거 애니메이션 |
| 루프 오빗 | `.loop-orbit` (6.5 참조) | CSS 애니메이션 SVG |
| 카운터 | `[data-count]` on `.h-stat-num` | `requestAnimationFrame` 카운트업 |

---

### 8. 인터랙티브 요소 참조

> DOM 컨테이너가 올바른 클래스명으로 존재하면 JS 구현은 어떤 프레임워크에서도 동일하게 적용 가능하다.

| # | 이름 | 트리거 | 핵심 패턴 |
|---|------|--------|-----------|
| 1 | Hero 카운터 | 페이지 로드 | `data-count` → `requestAnimationFrame` cubic ease-out |
| 2 | Gist 복사 버튼 | 클릭 | `navigator.clipboard.writeText()` + 1.8초 피드백 |
| 3 | Knowledge Chain | 노드 클릭/hover | JS SVG 렌더 → `#chainDetail` 패널 주입 |
| 4 | 스택 에리어 차트 | mousemove | Catmull-Rom 스무딩, 범례 토글 |
| 5 | 데일리 렛저 | 클릭 / ←→ 키 | 로그 스케일 바 높이, 상세 패널 |
| 6 | Phase 탭 탐색기 | 탭 클릭 | `renderPhase(n)` → `.phase-stage` 주입 |
| 7 | Trellis 아코디언 | 클릭 | `.t-rule` → `.open` 토글 |
| 8 | Trellis 바 애니메이션 | 스크롤 진입 | `IntersectionObserver` threshold 0.3 |

---

### 9. `--c` / `--c-soft` 컬러 주입 패턴

카드마다 인라인 스타일로 색상을 주입해 CSS 규칙은 `var(--c)`를 참조한다. 이 패턴이 이 디자인 시스템의 가장 핵심적인 메커니즘이다.

```html
<!-- HTML: 카드에 색상 주입 -->
<div class="qs-card" style="--c: var(--p1); --c-soft: var(--p1-soft)">...</div>
<div class="qs-card" style="--c: var(--p3); --c-soft: var(--p3-soft)">...</div>
<div class="qs-card" style="--c: var(--p2); --c-soft: var(--p2-soft)">...</div>
```

```css
/* CSS: var(--c)를 참조하는 위치들 */
.qs-card::before     { background: var(--c); }   /* 상단 바 */
.qs-num              { color: var(--c); }         /* 번호 */
.qs-body strong      { color: var(--c); }         /* 강조 텍스트 */
.qs-tab              { background: var(--c-soft); } /* 배경 tint */
.qs-bullet::before   { color: var(--c); }         /* 불릿 */
```

**파생 색상** (OKLCH relative color):
```css
/* --c보다 15% 어두운 텍스트 (배경 tint 위) */
color: oklch(from var(--c) calc(l - 0.15) c h);
```

**카드 색상 배정 전략**:

| 상황 | 전략 |
|------|------|
| 순서가 있는 카드 (Quick-Start, 개념 등) | hue 회전 순서: p1 → p3 → p2 → p5 → p4 |
| 병렬 선택지 (역할별 카드 등) | 섹션 accent 단색 또는 2색 교차 |
| 조건-결과형 | 섹션 accent 단색 통일 |

---

## Part 3 — Reference

### 10. 섹션 타입 & 비주얼 패턴

> `ref/index.html` 기준 참조 맵. 생성 규칙이 아닌 구조 이해용.

| # | 블록 타입 | CSS 클래스 | 역할 |
|---|-----------|------------|------|
| 1 | **Hero + Quick-Start** | `.hero`, `.quickstart`, `.qs-card` | 메인 랜딩 + 3단계 카드 + 스탯 카운터 |
| 2 | **First Hour FAQ** | `.fh-section`, `.fh-grid`, `.fh-card` | 5문 5답 + 인라인 프롬프트 + 코드 예시 |
| 3 | **Role Bar** | `.role-bar`, `.role-pills`, `.role-pill` | 스티키 역할 스위처 |
| 4 | **Concept Primer** | `.primer-section`, `.primer-grid`, `.primer-card` | 개념 카드 + SVG 체인 다이어그램 |
| 5 | **Ecosystem** | `.eco-section`, `.eco-tier`, `.eco-card`, `.eco-card-ext` | 3계층 아키텍처 |
| 6 | **Compounding Flow** | `.flow-section`, `.flow-card` | 에리어 차트 + 데일리 렛저 |
| 7 | **Phase Explorer** | `.phase-rail`, `.phase-tab`, `.phase-stage` | 탭 기반 5단계 타임라인 |
| 8 | **Governance Trellis** | `.trellis-chart`, `.tbar`, `.t-rule` | 성장 바 차트 + 아코디언 |
| 9 | **Recurring Loops** | `.loops-grid`, `.loop-card` | SVG 오빗 애니메이션 루프 |
| 10 | **Backlog Anatomy** | `.anatomy`, `.an-row` | 6행 키-값 템플릿 |
| 11 | **Role Playbooks** | `.playbook-grid`, `.playbook` | 역할별 6단계 플레이북 |
| 12 | **Adapt Principles** | `.adapt`, `.adapt-grid`, `.adapt-card` | 8개 원칙 그리드 |
| 13 | **Real Workflows** | `.workflows`, `.wf-card` | 워크플로 시나리오 5개 |
| 14 | **Footer** | `footer`, `.footer-grid` | 3컬럼 정보 푸터 |

> **role-callout 패턴**: Ecosystem·Flow·Phases·Trellis·Loops·Anatomy 이후 6회 반복.

---

### 11. HTML 스켈레톤 템플릿

새 페이지 생성 시 이 보일러플레이트로 시작한다.

```html
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>페이지 제목</title>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;0,6..72,700;1,6..72,400&family=IBM+Plex+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
/* 1. 디자인 토큰 (:root) */
/* 2. 배경 텍스처 (body::before, body::after) */
/* 3. 레이아웃 (.shell, .wrap) */
/* 4. 섹션 헤더 (프리미티브 3.1) */
/* 5. 재사용 패턴 프리미티브 (3.2–3.6) */
/* 6. 컴포넌트 CSS (사용하는 것만) */
/* 7. 반응형 미디어쿼리 */
/* 8. prefers-reduced-motion */
</style>
</head>
<body data-role="grad"><!-- 기본 역할 설정 (역할 스위처 사용 시) -->
<div class="shell">

  <!-- Sticky Nav / Role Bar (선택) -->

  <!-- Hero -->
  <div class="hero">
    <div class="wrap">
      <div class="eyebrow">카테고리</div>
      <h1 class="h-display">제목 <em>강조</em></h1>
      <p class="lede">리드 문단.</p>
    </div>
  </div>

  <!-- Section 예시 -->
  <section id="section-id" style="--accent: var(--p2)">
    <div class="wrap">
      <div class="sec-head">
        <div class="sec-eyebrow"><span class="num">01</span> 레이블</div>
        <h2 class="sec-title">섹션 제목 <em>강조</em></h2>
        <p class="sec-sub">설명 문장.</p>
      </div>
      <!-- 컴포넌트 삽입 -->
    </div>
  </section>

  <footer>
    <div class="wrap">
      <!-- 푸터 콘텐츠 -->
    </div>
  </footer>

</div><!-- /.shell -->
<script>
// 인터랙티브 요소 JS
</script>
</body>
</html>
```

---

### 12. 문체 규칙

모든 HTML 페이지의 사용자 노출 텍스트(eyebrow, 제목, 본문, 버튼 라벨, callout, 툴팁 등)는 **존댓말**로 작성한다.

| 구분 | 잘못된 예 | 올바른 예 |
|------|-----------|-----------|
| 본문 설명 | `순서대로 확인한다.` | `순서대로 확인합니다.` |
| 안내 문구 | `클론한 경로를 메모해둔다.` | `클론한 경로를 메모해 두세요.` |
| 결과 안내 | `생략해도 된다.` | `생략할 수 있습니다.` |
| 조건 설명 | `페이지를 벗어나면 다시 볼 수 없음.` | `페이지를 벗어나면 다시 볼 수 없습니다.` |

**예외**: 코드 블록(`<pre>`, `<code>`) 안의 명령어·주석·파일 경로는 예외로 한다.

---

## Appendix

> 아래 부록은 `ref/index.html` 원본 페이지에 특화된 참조 자료다. 생성 규칙이 아니다.

### A. 내러티브 아크 (원본 페이지 스토리 흐름)

```
접근성 → 온보딩 → 정체성 → 이론 → 범위 → 증거 → 구조 → 거버넌스 → 운영 → 템플릿 → 실행 → 일반화 → 증명
```

**아크 요약**: "너도 할 수 있다" → "이렇게 된다" → "이렇게 복제한다"

### B. 섹션 ID 순서 (원본 페이지)

`#first-hour` → `#primer` → `#ecosystem` → `#flow` → `#phases` → `#trellis` → `#loops` → `#anatomy` → `#playbooks` → `#adapt` → `#workflows`

### C. 구조적 특이사항 (원본 페이지)

- `<body data-role="grad">` — 기본 역할 대학원생
- 모든 SVG(체인·플로우·루프 오빗)는 JS로 완전 생성 — HTML에 빈 컨테이너만 존재
- 데이터(`dailyLog`, `flowData`)는 HTML 인라인 하드코딩 — 외부 의존성 없음
- `IntersectionObserver` 사용처: Trellis 바 진입 애니메이션
