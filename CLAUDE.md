# T셀파 중등 과학 바이브코딩 하네스

단원별 과학 시뮬레이션 페이지를 같은 디자인으로 만든다.
결과물: `units/{영역}/m{학년}_{영어_단원명}/index.html` (+ 필요하면 `contents/`) → 승인 뒤 `<폴더명>.zip` (업로드 대기 상태에서 끝, 업로드는 하네스 밖)

## 기준 문서 (먼저 읽기)
- ★ **절대 기준 (레퍼런스)**: `ref/T_Fixed_260909.html`, `ref/T_Floating_260909.html` (공식 템플릿), `ref/바이브코딩 콘텐츠 제작 관련 안내.pdf` (제작 규격·검수 기준). 하네스 문서와 다르면 레퍼런스가 맞다.
- 서비스·금지 규칙: docs/story-service.md (N1 개념 오류 금지, N2 출처 없는 저작물 금지)
- 파이프라인: docs/pipeline.md · 산출물: docs/outputs.md · 게이트: docs/gates.md · 역할: docs/roles.md
- 규칙 SSOT: docs/design.md (7장 YAML이 판정 기준)
- ★ 파일 경로: **docs/paths.md** — units/에 넣는 모든 작품은 이 문서대로 만든다 (절대 경로 금지, `./contents/…` 상대 경로만, `../` 금지)
- 템플릿: `templates/unit/T_Fixed.html`(제어 패널 오른쪽 고정, 기본) / `templates/unit/T_Floating.html`(제어 패널이 캔버스 안에 떠 있음·이동·닫기, 패널이 필요 없으면 이것을 고르고 패널 삭제) — 레퍼런스를 그대로 복사한 것. S1이 `01_spec.json`의 `template`으로 고른다.
- 교과서·지도서: 학교급별 `inbox/textbook/mid/*.pdf`(중학교), `inbox/textbook/high/<과목>/*.pdf`(고등학교: 물리학·생명과학 …) → 텍스트는 학교급 상관없이 `inbox/textbook/_text/<책 이름>.txt` (P1에서 추출). 단원 폴더가 `m…`이면 mid, `h…`이면 high를 본다

## 단원 = 새 폴더 1개
- 새 콘텐츠를 만들 때마다 `units/{영역}/m{학년}_{영어_단원명}/` 폴더를 **새로** 만든다. 중학교는 `m`, 고등학교는 `h` (예: `m2_solubility`, `h1_…`, 2026-11-12 확정). (영역: phy / chem / bio / ear, 고등 통합과학1·2는 과목 구분 없이 `integrated_science`, 2026-11-12 결정)
- **폴더·파일 이름은 영문+숫자, 공백은 `_`** (예: `m1_moon_phase`). 한글·공백은 FTP 업로드·실행 오류가 난다.
- 그 단원의 파일(00_input.md ~ 04_review.json, index.html, 03_reference.json, scenarios.json)은 모두 이 폴더 안에만 둔다. 다른 단원 폴더는 건드리지 않는다.
- 이미지·영상·음성·데이터 JS 같은 외부 파일을 쓰면 단원 폴더 안 `contents/`에 두고 **상대경로 `./contents/…`** 로만 부른다 (절대경로 `C:/…`·남의 URL·`../` 금지). 안 쓰면 `contents/`를 만들지 않는다. 자세한 규칙·예시는 **docs/paths.md** (S1·S3·G3·G4가 항상 참조). 기구·물체 그림은 여전히 코드로 그리는 것이 기본이다.
- 같은 이름의 폴더가 이미 있으면 덮어쓰지 않는다. "이어서 할지 / 다른 이름으로 새로 만들지" 사용자에게 묻는다.

## 흐름 (단계 전체)
개발 순서 원칙: **성취기준 확인 → 교과서·지도서 조사 → 입력과 대조 → 개발**.

| # | 단계 | 누가 | 하는 일 | 산출물 | 게이트 (실패 시) |
|---|---|---|---|---|---|
| 1 | P0 입력 | 오케스트레이터 | 폴더 생성, 00_input.md 4칸 질문(기본값 제시), `--baseline` | `00_input.md`, `.baseline.json` | G0 (사용자) |
| 2 | P1 교과서 준비 | 오케스트레이터 | 해당 학교급(`mid`/`high/<과목>`)·학년 교과서·지도서 텍스트가 `inbox/textbook/_text/`에 없으면 `extract_textbook.js`로 추출 | `_text/*.txt` | GR.text |
| 3 | S0 자료 조사 | unit-researcher | 지도서 성취기준 원문 → 교과서 쪽·용어·탐구 활동·사례 → 지도서 유의점·오개념·범위 (모두 쪽 번호) | `00_research.json` | GR (S0) |
| 4 | R 대조 ⏸ | 오케스트레이터 | `00_research.json`의 notes·out_of_scope와 00_input.md를 대조. **다른 점이 있으면 멈추고** 항목별 기본값(교과서 쪽)과 함께 질문 → 답대로 00_input.md 갱신 (결정 날짜 기록) | `00_input.md` 갱신 | 사용자 |
| 5 | S1 기획 | unit-planner | research 근거로 성취기준·변수·판정 규칙·출처 쪽 + **템플릿 유형(`template`)·지울 기능(`removed_features`)·외부 파일(`media`)** | `01_spec.json` | G1 (S1) |
| 6 | S2 콘텐츠 | unit-writer | 교과서 용어·사례, 지도서 오개념 반영한 가이드·개념·퀴즈 | `02_content.json` | G2 (S2) |
| 7 | SA 참고 그림 ⏸ | 오케스트레이터 | 사용자의 로그인된 Chrome으로 clarchive.co.kr에서 기구·물체 그림 후보 검색(`scripts/chrome.py`) → 후보를 보여주고 고른 것을 **참고용으로만** `inbox/refs/<slug>/`에 저장 → 모양·선 스타일 메모. **페이지에는 넣지 않고 S3이 코드로 직접 그린다** (이미지 합성은 어색해서 쓰지 않음, 2026-10-18 결정). 참고가 필요 없으면 `skipped` | `03_reference.json` | GA (SA) |
| 8 | S3 구현 | unit-builder | `template`에 맞는 템플릿을 복사 → `removed_features`만 통째로 지우고 ✏️ 영역 채우기. 필수 유지 5가지(레이아웃·로고/제목·학습 가이드·전체화면·초기화)는 그대로. 기구·물체는 `03_reference.json`의 참고 그림을 보고 캔버스 코드로 그린다 | `index.html` (+ `contents/`) | G3 (S1/S2/SA/S3) |
| 8.5 | GQ 삽화 품질 | 오케스트레이터 | 장면별 캡처를 교과서 쪽 그림과 나란히 보고 5항목(형태·비례·질감·스타일·변화 표현) 1~3점 채점 (docs/gates.md). 모두 ≥ 2·평균 ≥ 2.5면 통과. 2번 실패하면 멈추고 **Higgsfield로 교과서 형태 삽화**를 제안 (크레딧, 사용자 승인) → 정적 기구만 `contents/` 이미지, 바뀌는 부분은 코드로 얹음 | `art_check.json` | GQ (S3 / 사용자) |
| 9 | V 화면 점검 | 오케스트레이터 | 조작 시나리오를 `scenarios.json`에 쓰고 `node scripts/scenario_shots.mjs <단원폴더>`로 상태별 캡처 → **모든 캡처를 직접 열어 본다** (겹침, 그림 밖으로 나간 채우기, 흐림, 잘린 라벨). 필수 캡처: 모드·선택지(커스텀 드롭다운은 `{"do":"option"}`)·버튼·퀴즈 정답, PC 1440×900·**넓은 화면 2560×1200**·**전체화면(`{"do":"fullscreen"}`, 2960×1300)**, 모바일 세로 **아이폰SE 375×667·S20 울트라 412×915**(+ `moreMenuBtn` 클릭한 ⋮ 상태), **모바일 가로 844×390(`"touch": true`)**, T_Floating이면 패널 닫힘 상태. 문제가 있으면 S3로 돌려보내고 다시 캡처. 캡처하지 못한 상태는 G4에 "확인 못 함"으로 적는다 | `scenarios.json` | 사람 눈 (S3) |
| 10 | G4 승인 ⏸ | 사용자 | 판정 결과 + 캡처 + 체크리스트(docs/gates.md: 실제 기기·브라우저 확인 포함) 확인 → "승인" / "반려, S{n}로". 승인하면 `check_unit.py --package`로 `<폴더명>.zip` (index.html + contents/) 생성 | `04_review.json`, `<폴더명>.zip` | — |

1. 각 단계가 끝나면 그 게이트를 판정한다 (unit-judge 또는 `check_unit.py`).
2. 멈추는 곳(⏸)은 G0(입력이 비었을 때), R(입력과 교과서가 다를 때), SA(참고 그림 선택), GQ 2회 실패(Higgsfield 제안), 3회 실패, G4뿐이다. 나머지는 자동으로 진행한다.
3. 실패하면 판정 결과의 "돌아갈 단계"로 가서 그 단계 파일과 뒤 파일을 지우고 다시 만든다 (지운 파일은 scratchpad에 백업).
4. 같은 단계로 3번 돌아가도 실패하면 멈추고 사용자에게 묻는다.
5. 질문할 때는 항목마다 기본값(교과서 근거)을 붙인다.
6. 사용자가 "승인"하면 04_review.json에 기록하고 `python3 scripts/check_unit.py <단원폴더> --package`로 전달용 zip을 만든 뒤 끝낸다.

### SA 참고 그림 절차 (Chrome)
- 준비: Chrome 보기 > 개발자 > "Apple Events의 자바스크립트 허용" 켜기 (사용자). `python3 scripts/chrome.py open https://www.clarchive.co.kr/` 뒤 `chrome.py check`가 ok여야 한다.
- 검색: 홈에서 `#searchKeywordInput`에 값 넣고 Enter → 결과 카드 `img[contentid]` (id, alt, 미리보기 src). 미리보기를 HTML 격자로 모아 headless Chrome으로 캡처해 후보를 보여준다.
- 저장(참고용): 고른 것만 `chrome.py download https://www.clarchive.co.kr/content/downloadFile inbox/refs/<slug>/<이름> content_id=<id>` (POST). 단원 폴더에는 두지 않는다 (업로드 제외).
- 기록: `03_reference.json` = `{"policy": "...", "ref_dir": "inbox/refs/<slug>", "style_notes": ["선·색·모양 메모"], "items": [{"title", "content_id", "source_url": "https://www.clarchive.co.kr/content/detail?content_id=<id>", "file", "notes"}]}` / 참고 없음: `{"skipped": "이유", "items": []}`
- 이용 조건(FAQ [저작권]): 저작권 천재교육·천재교과서, 원본 파일 배포 금지, 일부 떼어 쓰기 금지. 참고만 하고 코드로 새로 그리므로 페이지에 원본이 들어가지 않는다. **참고 그림을 단원 `contents/`에 넣지 않는다.**
- Chrome 제어는 `chrome.py open`으로 연 탭만 대상으로 한다 (사용자가 다른 탭으로 옮겨도 그 탭은 건드리지 않음).

## 재개
단원 폴더에서 처음으로 없는 파일부터 이어서 한다.
(00_input.md → 00_research.json → 01_spec.json → 02_content.json → 03_reference.json → index.html → art_check.json(GQ) → scenarios.json(V) → 04_review.json → `<폴더명>.zip`)
- 2026-11-12 이전(임시 템플릿 `templates/unit/index.html`)으로 만든 단원의 `index.html`은 새 템플릿 기준 G3를 통과하지 못한다. 이어서 할 때는 사용자에게 "S1(template 추가)·S3 다시 만들기"를 묻는다.

## 트리거
| 사용자 말 | 할 일 |
|---|---|
| "새 단원 만들어줘: …" | P0 → P1 → S0부터 |
| "○○ 단원 이어서 해줘" | 재개 규칙대로 진행 |
| "○○ 검사해줘" | unit-judge만 실행 (`--gate ALL`), 파일 수정 없음 |
| "승인" / "반려, S{n}로" | 04_review.json 기록 / 그 단계부터 다시 |

`.baseline.json`: 단원을 시작할 때 `python3 scripts/check_unit.py <단원폴더> --baseline`으로 1번만 쓴다 (docs/·templates/·scripts/ 해시). 하네스를 사용자 요청으로 고친 뒤 진행 중인 단원은 다시 기록한다.

## 판정·도구 스크립트
- `python3 scripts/check_unit.py <단원폴더> --gate G0|GR|G1|G2|GA|G3|ALL` (실패 시 종료 코드 1, 마지막 줄에 돌아갈 단계)
- G3은 `scripts/render_check.mjs`로 헤드리스 Chrome 콘솔 에러를 세고 화면을 캡처한다 (`--no-render`로 생략 가능).
- 교과서 텍스트: `osascript -l JavaScript scripts/extract_textbook.js <pdf> <out.txt>` (macOS PDFKit)
  - Windows: PyMuPDF로 같은 형식 추출 — `python -c "import fitz,sys;d=fitz.open(sys.argv[1]);open(sys.argv[2],'w',encoding='utf-8').write('
'.join(f'=== p{i+1} ===
'+q.get_text().strip() for i,q in enumerate(d)))" <pdf> inbox/textbook/_text/<책 이름>.txt`
  - 읽기용 Markdown: `python scripts/pdf2md.py <pdf> <같은 폴더/같은 이름.md> [a-b]` (PyMuPDF, 쪽마다 `## p.N`, 큰 글자는 제목). PDF는 그대로 둔다. 통합과학1·2 교과서는 변환 완료 (`inbox/textbook/high/통합과학/*.md`)
  - 고등 성취기준 코드는 지도서에 대괄호 없이 `10통과1-01-01`로 적혀 있다 → `[10통과1-01-01]`로 쓴다
- 교과서 쪽 PDF: `osascript -l JavaScript scripts/extract_textbook.js <pdf> <out.pdf> <쪽|쪽-쪽>` → Read로 그림·그래프 확인 (원본 PDF는 커서 Read 불가). S0·S3 에이전트에게 그래프 모양 참고로 넘긴다 (페이지에 넣지 않음)
- 상태별 캡처: `node scripts/scenario_shots.mjs <단원폴더> [출력폴더]` (V 단계, `scenarios.json` 필요. 폭 < 768 또는 `"touch": true`면 터치 기기로 흉내 → 실제 폰처럼 ⋮ 메뉴가 나온다)
- 전달용 묶음: `python3 scripts/check_unit.py <단원폴더> --package` → `<단원폴더>/<폴더명>.zip` (안: `<폴더명>/index.html` + `contents/`)
- Chrome 제어: `python3 scripts/chrome.py …` (SA 단계)
- 필요: macOS, python3(3.9+), node(18+), Google Chrome. 추가 설치 없음.
  - Windows에서 판정·캡처를 돌릴 때는 `CHROME_PATH="C:/Program Files/Google/Chrome/Application/chrome.exe"`, `python3` 대신 `python`. (`extract_textbook.js`·`chrome.py`는 macOS 전용)

## 금지
- 에이전트는 자기 파일 1개만 쓴다 (docs/roles.md).
- docs/, templates/, scripts/는 사용자가 요청할 때만 고친다.
- 템플릿 파일(`templates/unit/T_*.html`)은 레퍼런스와 같게 둔다. 고치지 않는다.
- 템플릿의 🚫 영역은 고치지 않는다. 허용되는 것은 **필요 없는 기능 통째로 지우기**(`removed_features`: sound·env_canvas·env_panel·concept·quiz·zoom·drag·panel)뿐이고, 쓰는 기능은 템플릿 디자인 그대로 둔다. 그 밖에 꼭 필요하면 01_spec.json의 locked_zone_exceptions에 이유를 적는다.
- 필수 유지 5가지(헤더/메인/푸터 구조, 로고·제목과 T셀파 링크, 학습 가이드 버튼·팝업, 전체화면 버튼, 캔버스 초기화 버튼)는 지우지 않는다.
- 교과서·성취기준에 없는 개념, 출처 없는 이미지·데이터를 넣지 않는다. 외부 파일은 `contents/` + 상대경로 + `01_spec.json` `media`에 출처.
- 참고 그림은 사용자 승인 없이 내려받지 않고, 페이지에 이미지로 넣지 않는다 (코드로 그린다). 로그인된 사이트에서 결제·구매·개인정보 입력은 하지 않는다.
- 판정 스크립트가 실패한 채로 G4로 넘어가지 않는다.
