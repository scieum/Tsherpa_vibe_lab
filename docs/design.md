# T셀파 중등 과학 바이브코딩 디자인 시스템 (design.md)

> 이 문서는 모든 단원 페이지가 따르는 **규칙의 원본(SSOT)** 이다.
> 사람은 1~6장을 읽고, 판정 스크립트는 7장의 YAML 블록만 읽는다.
>
> **기준 자료 (절대 기준, 2026-11-12 반영)**
> - 공식 템플릿 2종: `ref/T_Fixed_260909.html`, `ref/T_Floating_260909.html` → 그대로 복사해 `templates/unit/T_Fixed.html`, `templates/unit/T_Floating.html`로 둔다. 템플릿 파일은 레퍼런스와 **바이트 단위로 같아야** 한다 (고치지 않는다).
> - 제작 안내: `ref/바이브코딩 콘텐츠 제작 관련 안내.pdf` (템플릿 유형·필수 유지·변경 가능·작업 폴더·상대경로·검수 기준)
> - 이 문서와 레퍼런스가 다르면 **레퍼런스가 맞다.** 이 문서를 고친다.

---

## 1. 핵심 원칙

1. **템플릿은 2종 중 하나를 고른다** (`01_spec.json`의 `template`).
   | 유형 | 모양 | 고르는 경우 |
   |---|---|---|
   | `T_Fixed` | 제어 패널이 **오른쪽에 고정** (캔버스 3 : 패널 1) | 변인 조작·데이터 확인이 중심인 단원 (기본값) |
   | `T_Floating` | 제어 패널이 **캔버스 안에 떠 있음**. 위쪽 막대를 눌러 닫기·열기, 끌어서 이동 | 캔버스를 넓게 써야 하는 단원. **제어 패널이 필요 없으면** 이 유형을 고르고 패널을 삭제 |
   - 과학은 학습 가이드가 **헤더의 ? 버튼(팝업)** 으로 있고, 이너탭이 없는 버전을 쓴다 (두 템플릿 모두 이 형태).
2. **필수 유지 5가지는 지우거나 바꾸지 않는다** (제작 안내 1-2):
   ① 전체 레이아웃 구조(헤더 / 메인 워크스페이스 / 푸터) ② 로고·제목 구역(로고 클릭 시 T셀파 이동) ③ 학습 가이드 버튼·팝업 ④ 전체화면 버튼 ⑤ 캔버스 안 초기화 버튼
3. **필요 없는 기능만 통째로 지울 수 있다** (제작 안내 1-3). 쓰는 기능은 **템플릿 디자인 그대로** 둔다. 지운 기능은 `01_spec.json`의 `removed_features`에 적는다 (2장 표).
4. **그 밖의 🚫 영역은 한 글자도 바꾸지 않는다.** 꼭 바꿔야 하면 `01_spec.json`의 `locked_zone_exceptions`에 `{zone, reason}`을 적고 G4에서 사람이 승인한다 (엄격 + 신고제).
5. **글은 `CONTENT_CONFIG`에만 쓴다.** 제목, 학습 가이드, 개념 정리, 퀴즈는 HTML에 직접 쓰지 않고 JS 설정값으로 주입한다.
6. **색과 글꼴은 토큰으로만 쓴다.** `:root` 변수와 Tailwind 테마 값은 모든 단원에서 같다 (⚙️ 선택 수정 영역이지만 이 하네스에서는 고정).

---

## 2. 템플릿 영역 지도

### 지울 수 있는 기능 (`removed_features` 값)
| 값 | 지우는 것 | 언제 | 함께 지울 코드 |
|---|---|---|---|
| `sound` | 헤더 음량 버튼(`#sound-toggle-btn`)·음량 팝업(`#volume-popup`) | 효과음 등 음량을 쓰지 않을 때 | ZONE E 전체 + **모든 `uiSound.…` 호출** (템플릿 주석: "삭제시 uiSound 관련 코드 모두 삭제") |
| `env_canvas` | 캔버스 위 변수/조건 안내 막대의 글자(`#env-label-canvas`) | 변수/조건 안내를 패널에만 둘 때, 또는 안내가 필요 없을 때 | `#environment-info` 묶음 |
| `env_panel` | 제어 패널 맨 위 변수/조건 안내(`#env-label-panel` 블록) | 안내를 캔버스에만 둘 때, 또는 필요 없을 때 | 그 `.panel-block` |
| `concept` | 개념 정리 버튼·팝업(`#conceptBtn`, `#conceptBox`) | 개념 정리가 필요 없을 때 | `CONTENT_CONFIG.concept`는 `[]` |
| `quiz` | 확인 퀴즈 버튼·팝업(`#quizBtn`, `#quizBox`) | 확인 퀴즈가 필요 없을 때 | `CONTENT_CONFIG.quizzes`는 `[]` |
| `zoom` | 확대/축소 버튼(`#zoomInBtn`, `#zoomOutBtn`)과 기능 | 확대/축소가 필요 없을 때 | ZONE J 줌 이벤트, 휠·핀치 확대 |
| `drag` | 캔버스 콘텐츠 이동(드래그 앤 드롭) | 끌어서 옮길 것이 없을 때 | ZONE J `/* 캔버스 드래그 */` 블록 |
| `panel` | 플로팅 제어 패널 전체(`#floating-control-panel`) | **T_Floating만**. 제어 패널이 필요 없을 때 | `concept`·`quiz`·`env_panel`도 함께 적는다. 시작 버튼이 없어지면 ZONE G가 안내 문구를 갱신하지 않아 캔버스 위 안내 pill(`#helperText` 묶음)이 "로딩 중..."에 멈추므로 그 묶음도 지운다 (2026-11-12 캡처 확인) |

- **변수/조건 안내는 한 곳만** 쓴다: 필요하면 캔버스(2-1) 또는 패널(2-2) 중 콘텐츠에 맞는 쪽 하나, 필요 없으면 둘 다 지운다. 그래서 `env_canvas`·`env_panel` 중 하나 이상은 항상 `removed_features`에 있다.
- 지우기는 **줄·코드를 빼기만** 한다. 남은 줄을 고치거나 새 줄을 끼워 넣으면 G3에서 🚫 위반이다.

### HTML (두 유형 공통, 차이는 ★)
| 영역 | 표시 | 단원마다 |
|---|---|---|
| `<head>` 라이브러리 (KaTeX, Tailwind, Noto Sans KR) | 🚫 | 그대로 |
| Tailwind 테마, `:root` CSS 변수, 디자인 클래스 | ⚙️ | **그대로** (이 하네스에서는 고정) |
| 헤더 (로고 링크 + 제목 + 음량·학습 가이드·전체화면 버튼, 모바일 ⋮ 더보기 메뉴) | 🚫 | 그대로 (음량만 `sound`로 삭제 가능) |
| 메인 워크스페이스 `#workspace` / 캔버스 영역 `#content-area` (안내 막대, 상태 표시, 줌, 초기화) | 🚫 | 그대로 (`env_canvas`, `zoom` 삭제 가능) |
| ★ T_Fixed: 오른쪽 제어 패널 `<aside id="settings-area">` | ✏️ EDIT ZONE (`입력 폼 영역 시작`~`끝`) | 단원마다 새로 작성 |
| ★ T_Floating: 플로팅 패널 `#floating-control-panel` (토글 버튼 `#controlToggleBtn` 🚫) | ✏️ EDIT ZONE (`입력 폼 영역 시작`~`끝`) | 단원마다 새로 작성 (`panel` 삭제 가능) |
| 하단 동작 버튼 (시작 / 개념 정리 / 확인 퀴즈) | 🚫 (텍스트만 변경 가능) | 그대로 (`concept`, `quiz` 삭제 가능) |
| 모달 (학습 가이드 / 개념 정리 / 확인 퀴즈) | 🚫 | 그대로 (내용은 JS 주입) |
| 전체화면 딤 UI, 푸터 (저작권) | 🚫 | 그대로 |

### JS
| 영역 | 표시 | 내용 |
|---|---|---|
| ZONE A — CONTENT CONFIG | ✏️ | 제목, 안내 라벨, 가이드, 개념, 퀴즈 |
| ZONE B — SIM CONFIG | ✏️ | 슬라이더 범위·단위, 객체 크기 등 수치 |
| ZONE C — SIM STATE | ✏️ | `simData`, `tabStates` |
| ZONE D — CORE ENGINE | 🚫 | 캔버스·`sysState`·DOM 캐시·콘텐츠 주입 |
| ZONE E — SOUND MANAGER | 🚫 | `uiSound` (WebAudio 효과음. `sound` 삭제 시 전체 삭제) |
| ZONE F — SIMULATION LOGIC | ✏️ | 계산·그리기. 코어가 부르는 함수 이름 유지: `initSimulation()`, `draw()`, `updatePhysics()` |
| ZONE G — LOOP & TAB STATE | 🚫 | `startLoop`·`stopLoop`·`updateUIState` (시작 버튼·안내 문구·입력 잠금) |
| ZONE H — CANVAS RESIZE | 🚫 | 크기 맞춤, 전체화면, iOS 전체화면 안내, 토스트 |
| ZONE I — INPUT EVENT HANDLERS | ✏️ | `bindInputEvents()` — 제어 패널 입력 연결 |
| ZONE J — CORE EVENT BINDING | 🚫 | 모달·퀴즈·줌·캔버스 드래그·모바일 메뉴 |
| ★ T_Floating ZONE K — FLOATING PANEL LOGIC | 🚫 | `initFloatingPanel()` (패널 이동·열고 닫기) |
| 초기 실행 (T_Fixed ZONE K / T_Floating ZONE L) | 🚫 | `bindCoreEvents → bindInputEvents → (initFloatingPanel) → initSimulation` |

### 코어가 주는 것 (ZONE F에서 씀)
- `ctx`, `canvas`, `sysState.canvasLogicalWidth/Height`, `sysState.isStarted/isPaused/isDragging`
- 줌을 쓰면 `draw()`에서 템플릿처럼 `sysState.zoomLevel`, `sysState.offsetX/Y`를 적용한다.
- 드래그를 쓰면 코어가 `simData.x/y`(배율 1 이하일 때)를 옮긴다. 다른 방식의 캔버스 조작이 필요하면 ZONE J를 `locked_zone_exceptions`로 신고한다.
- 시작 버튼 글자(`▶ 시작`/`|| 일시정지`/`▶ 계속하기`)와 캔버스 위 안내 문구는 ZONE G가 정한다. 단원에서 바꾸지 않는다.

---

## 3. 디자인 토큰

### 글꼴
- 본문·UI: `Noto Sans KR` (400 / 500 / 600 / 700), 대체 `sans-serif`
- 수식: KaTeX 0.16.9 (`$...$` 인라인)

### 글자 크기
| 토큰 | 값 | 쓰는 곳 |
|---|---|---|
| `--font-size-title` | 1.275rem | 헤더 제목 |
| `--font-size-modal` | 1.15rem | 모달 제목, 퀴즈 질문 |
| `--font-size-guide` | 1.025rem | 가이드 소제목, 퀴즈 정답 |
| `--font-size-desc` | 1rem | 본문, 개념 설명 |
| `--font-size-small` | 0.9rem | 버튼, 패널 라벨 |
| `--font-size-tiny` | 0.75rem | 보조 라벨, 슬라이더 최소·최대, 안내 막대 |

### 색상
| 토큰 | 값 | 역할 |
|---|---|---|
| `--color-text-main` | `#334155` | 본문 |
| `--color-text-sub` | `#475569` | 보조 텍스트 |
| `--color-text-light` | `#64748b` | 약한 텍스트 |
| `--color-primary` | `#4f46e5` | 포인트 (인디고) |
| `--color-primary-bg` | `#e0e7ff` | 포인트 배경 |
| `--color-tab-bg` | `#d8e0ff80` | 탭 배경 |
| `--color-action` | `#059669` | 시작 버튼 (초록) |
| `--color-action-hover` | `#047857` | 시작 버튼 hover |
| `--color-pause` | `#e11d48` | 일시정지·초기화 hover (빨강) |
| `--color-pause-bg` | `#fff1f2` | |
| `--color-pause-border` | `#fecdd3` | |
| `--color-obs1` | `#ea580c` | 관찰 변수 1 (주황) |

- 페이지 배경 `slate-100`, 카드(`.ui-box`) 배경 `#fff` + 테두리 `#e2e8f0`
- **새 색상(hex)은 ZONE F(캔버스 그리기) 안에서만** 쓴다. UI 요소에는 위 토큰과 Tailwind slate/indigo 계열만 쓴다.

### 개념 정리 카드 색
`CONTENT_CONFIG.concept[].color`는 `orange` / `green` / `blue` / `purple` 중 하나. 카드는 최대 4장.

### 모서리·그림자
템플릿에 있는 클래스만 쓴다: `rounded`, `rounded-md`, `rounded-lg`, `rounded-xl`, `rounded-2xl`, `rounded-full` (+ 템플릿의 `rounded-t/r/b-…`). 모달 `shadow-2xl`, 떠 있는 버튼 `shadow-sm`.

---

## 4. 컴포넌트 (제어 패널에서 쓰는 것 — 템플릿 예시 폼 그대로)

| 템플릿 폼 | 클래스·구조 | 용도 |
|---|---|---|
| 묶음 | `.panel-block` + `.var-label-control`(제목) | 입력 묶음 1개 |
| 폼 1 드롭다운 | `#customSelectTrigger` + `#customSelectList`(`li[data-value]`) 커스텀 셀렉트 | 여러 선택지 중 하나. `<select>`를 새로 쓰지 않는다 |
| 폼 2 라디오 | `.radio-label` + `input[type=radio]` | 2~4개 선택지 |
| 폼 3·4 숫자 입력 | `.ratio-number-field` + `.input-text` + `.ratio-number-stepper`(▲▼ `.ratio-step-btn`) | 숫자 1개 / 비율 |
| 폼 5 슬라이더 | `input[type=range]` `accent-indigo-600` + `.var-unit-display`(현재 값) + `.slider-limit-label`(최소·최대) | 연속 값 |
| 폼 6 관찰 게이지 | `.var-label-obs1/2` + `.var-label-var` + `.bar-track` > `.bar-fill` | 관찰 값 표시 |

- 쓰지 않는 예시 폼은 지운다 (EDIT ZONE 안). 단원 폼은 위 예시를 복사해 id·글자만 바꿔 만든다. 새 CSS 클래스를 `<style>`에 추가하지 않는다.
- 동작 중에는 ZONE G가 `varSlider1`·`directInputSingle`·`ratioInputA/B`·`customSelectTrigger`·`simOption` 라디오를 잠근다. 다른 id를 쓰면 ZONE I에서 `sysState.isStarted && !sysState.isPaused`일 때 무시하도록 처리한다.

### 선택지 행 (라디오·체크박스, 2026-10-18)
- 한 묶음의 선택지는 **모두 같은 너비**로 둔다: `grid grid-cols-N gap-2` + 각 라벨 `min-w-0`, 글자는 `whitespace-nowrap`. 글자 길이에 따라 너비가 달라지는 배치를 쓰지 않는다.
- 열 수: 2개 → 2열, 4개 → 2열×2줄, 3개 → 짧으면 3열, 길면 1열. 마지막 하나만 넓게 펼치는 `col-span`은 쓰지 않는다.
- T_Fixed 패널 폭(1440 화면 약 280px), T_Floating 패널 폭(`w-72` = 288px)에서 글자가 잘리지 않는지 V 단계 캡처로 확인한다.

### 캔버스 크기 비례 (확대 규칙, 2026-10-18)
캔버스가 커지면(넓은 화면·전체화면) 캔버스 안의 모든 것이 같은 비율로 커진다.
- 배율 1개(`ui`)를 캔버스 크기에서 구한다. 기준은 1440×900 화면의 캔버스, 범위 0.75~1.5. 예: `ui = clamp(min(w/1080, h/700), 0.75, 1.5)`
- 글자, 라벨, 안내 상자·범례(테두리·여백 포함), 입자·마커, 선 굵기, 간격을 모두 `기준값 × ui`로 그린다. 고정 px 글꼴을 쓰지 않는다.
- 기구·그래프·라벨은 한 묶음으로 캔버스 가운데에 둔다. T_Floating은 열린 패널(오른쪽 위 약 288px)에 가려지지 않게 묶음을 둔다.
- 제어 패널·안내 문구·버튼 같은 DOM 요소는 템플릿 크기를 따른다.

---

## 5. 콘텐츠 작성 규칙 (`CONTENT_CONFIG`)

```js
const CONTENT_CONFIG = {
  title: "단원명",                      // 탭 제목 + 헤더 제목
  envLabel: "🌍 ○○ 조건",               // 캔버스 안내 막대 (env_canvas를 지우면 비워도 됨)
  envLabelpanel: "🌍 ○○ 조건",          // 패널 안내 (env_panel을 지우면 비워도 됨)
  guide: {
    intro: "~을 확인할 수 있다.",        // 1문장
    steps: ["~한다.", "~한다."]          // 3~5개. 4개 이상이면 데스크톱에서 2열로 나뉜다
  },
  concept: [                             // 1~4장 (concept 삭제 시 [])
    { color: "orange", title: "개념명", desc: "~입니다." }
  ],
  quizzes: [                             // 3문항 이상 (quiz 삭제 시 [])
    { q: "질문\n\n① …   ② …   ③ …   ④ …", a: "정답: ① … 해설: …" }
  ]
};
```

- 가이드: `'~다' / '~한다'` 체. 개념 설명: `'~입니다'` 체.
- 수식은 KaTeX `$...$` (예: `$n_1 \\sin\\theta_1 = n_2 \\sin\\theta_2$`).
- 퀴즈 질문(`q`)은 템플릿이 `innerText`로 넣어 **줄바꿈이 보인다**: 질문 뒤 빈 줄(`\n\n`) 다음에 보기. 짧은 보기는 한 줄에 `   `(공백 3칸)으로, 문장형 보기만 한 줄에 하나씩.
- 퀴즈 정답(`a`)은 템플릿이 `textContent`로 넣어 **줄바꿈이 보이지 않는다**: `정답: ② ○○. 해설: …`처럼 한 문단으로 쓴다. 반드시 `정답:`으로 시작하고 `해설:`을 포함한다.
- 퀴즈 창 높이는 가장 긴 질문·정답에 맞춰진다. 너무 길게 쓰지 않는다.

---

## 6. 외부 리소스·작업 폴더 (제작 안내 2·3장)

> 경로 규칙의 자세한 설명·예시·단계별 할 일은 **docs/paths.md**. 아래는 요약.

- **폴더 이름**: `m{학년}_{영어_콘텐츠명}` (예: `m1_moon_phase`). **모든 폴더·파일 이름은 영문+숫자, 공백은 `_`** (단원 폴더는 소문자). 한글·공백은 FTP 업로드·실행 오류를 낸다.
- **이미지·영상·음성·데이터 파일**을 쓰면 단원 폴더 안에 `contents/` 폴더를 만들어 거기에 둔다. 안 쓰면 `contents/`를 만들지 않는다.
  - 불러올 때는 **상대경로만**: `./contents/image1.png`. 절대경로(`C:/…`)·남의 인터넷 주소(`https://…/image1.png`)는 쓰지 않는다 (폴더를 옮기거나 원본이 지워지면 안 보임).
  - 쓰는 파일은 모두 `01_spec.json`의 `media`에 `{file: "contents/…", source: "출처·권리"}`로 적는다 (N2). 단원 데이터 JS도 `contents/*_data.js`에 둔다.
  - 기구·물체 그림은 **코드로 그리는 것이 기본**이다 (2026-10-18 결정: 이미지 합성은 어색함). SA의 참고 그림(clarchive)은 **절대 `contents/`에 넣지 않는다** (원본 배포 금지).
- **전달**: G4 승인 뒤 `index.html`(+ `contents/`)을 `.zip` 하나로 묶는다 (`check_unit.py --package`).
- **기본 허용 도메인**: `cdata2.tsherpa.co.kr`, `www.tsherpa.co.kr`, `cdn.jsdelivr.net`, `cdn.tailwindcss.com`, `fonts.googleapis.com`, `fonts.gstatic.com`. 지도·실시간 데이터처럼 꼭 필요한 도메인만 `01_spec.json` `formula_or_source`에 출처 URL로 적어 추가 허용한다.
- 로고: 템플릿의 `t_logo_black.png`, `t_logo_short.png`만 쓴다.

---

## 7. 판정 스크립트용 규칙 블록

```yaml
version: 2

template:
  dir: templates/unit
  types: [T_Fixed, T_Floating]          # 01_spec.json#template 값으로 고른다
  locked_markers: ["🚫"]
  editable_zones: [A, B, C, F, I, EDIT_ZONE]
  exceptions_from: 01_spec.json#locked_zone_exceptions   # [{zone, reason}] — G4 사람 승인 필수
  required_functions: [initSimulation, draw, updatePhysics, bindInputEvents]
  required_markers:                     # 필수 유지 5가지 (지우면 실패)
    - '<header'
    - 'id="workspace"'
    - '<footer'
    - 'href="https://www.tsherpa.co.kr"'
    - 'id="sim-title-el"'
    - 'id="helpBtn"'
    - 'id="helpBox"'
    - 'id="fullscreen-btn"'
    - 'id="resetBtn"'
    - 'id="simCanvas"'
  features:                             # removed_features 값: 지우면 흔적 0, 남기면 모두 있어야 함
    sound: ['id="sound-toggle-btn"', 'id="volume-popup"', 'uiSound']
    env_canvas: ['id="env-label-canvas"']
    env_panel: ['id="env-label-panel"']
    concept: ['id="conceptBtn"', 'id="conceptBox"']
    quiz: ['id="quizBtn"', 'id="quizBox"']
    zoom: ['id="zoomInBtn"', 'id="zoomOutBtn"']
    drag: ['/* 캔버스 드래그 */']
    panel: ['id="floating-control-panel"']   # T_Floating만

sections:
  - { name: title,      selector: "#sim-title-el" }
  - { name: guide,      selector: "#helpBox" }
  - { name: concept,    selector: "#conceptBox", feature: concept }
  - { name: simulation, selector: "#simCanvas" }
  - { name: quiz,       selector: "#quizBox", feature: quiz }
  - { name: footer,     selector: "footer", text_contains: "chunjae co.ltd" }

tokens:                                 # :root 값이 이것과 정확히 같아야 함
  --font-size-title: 1.275rem
  --font-size-modal: 1.15rem
  --font-size-guide: 1.025rem
  --font-size-desc: 1rem
  --font-size-small: 0.9rem
  --font-size-tiny: 0.75rem
  --color-text-main: "#334155"
  --color-text-sub: "#475569"
  --color-text-light: "#64748b"
  --color-primary: "#4f46e5"
  --color-primary-bg: "#e0e7ff"
  --color-tab-bg: "#d8e0ff80"
  --color-action: "#059669"
  --color-action-hover: "#047857"
  --color-pause: "#e11d48"
  --color-pause-bg: "#fff1f2"
  --color-pause-border: "#fecdd3"
  --color-obs1: "#ea580c"

font_family: ["Noto Sans KR", "sans-serif"]

spec:
  standard_code_regex: '^\[(9과\d{2}-\d{2}|1[0-2][가-힣]+\d{0,2}(-\d{2}){1,2})\]$'   # 중 [9과NN-NN], 고 [10통과1-01-01]·[12물리01-01]

names:
  unit_folder_regex: '^[mh][1-3]_[a-z0-9_]+$'   # m=중학교, h=고등학교 (2026-11-12 사용자 확정)
  file_regex: '^[A-Za-z0-9_.-]+$'

radius_classes: [rounded, rounded-t, rounded-r, rounded-b, rounded-md, rounded-lg, rounded-xl, rounded-2xl, rounded-full]
hex_colors_allowed_only_in_zones: [F]

content:
  title_required: true
  guide_steps: { min: 3, max: 5 }
  concept: { min: 1, max: 4, colors: [orange, green, blue, purple] }
  quizzes: { min: 3, answer_prefix: "정답:", answer_contains: "해설:" }

hidden_forbidden: ["#conceptBtn", "#quizBtn"]   # 남겨 둔 버튼에 hidden 클래스가 있으면 실패

external_hosts:
  base: [cdata2.tsherpa.co.kr, www.tsherpa.co.kr, cdn.jsdelivr.net, cdn.tailwindcss.com, fonts.googleapis.com, fonts.gstatic.com]
  per_unit_from: 01_spec.json#formula_or_source
```
