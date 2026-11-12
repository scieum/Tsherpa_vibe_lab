# 산출물 (outputs)

## 폴더 구조
```
Tsherpa_vibe coding/
├─ CLAUDE.md                     ← 오케스트레이터 (R7)
├─ ref/                          ← ★ 절대 기준: 공식 템플릿 2종 + 제작 안내 PDF (고치지 않음)
├─ docs/                         ← 기준 문서
│  ├─ design.md                  ← ★ 규칙 SSOT
│  └─ paths.md                   ← ★ 파일 경로 규칙 (상대 경로만)
├─ templates/unit/T_Fixed.html   ← 공식 템플릿 (ref/T_Fixed_260909.html 그대로)
├─ templates/unit/T_Floating.html← 공식 템플릿 (ref/T_Floating_260909.html 그대로)
├─ templates/unit/00_input.md    ← 단원 입력 양식 (새 단원 폴더로 복사)
├─ scripts/                      ← 판정 스크립트 (R5) + extract_textbook.js(PDF→텍스트)
├─ inbox/textbook/mid/           ← 중학교 교과서·지도서 PDF
├─ inbox/textbook/high/<과목>/   ← 고등학교 교과서·지도서 PDF (물리학, 생명과학 …)
├─ inbox/textbook/_text/         ← 쪽 표시 텍스트 (학교급 상관없이 <책 이름>.txt)
├─ inbox/refs/<slug>/            ← SA 참고 그림 (업로드 제외)
└─ units/
   └─ {영역}/m{학년}_{영어_단원명}/     ← 이름은 영문 소문자·숫자·_ 만
      ├─ .baseline.json          ← 시작 시점 docs/templates/scripts 해시 (G3 비교용)
      ├─ 00_input.md             ← 단원 입력 (purpose.md의 4칸)
      ├─ 00_research.json        ← S0 성취기준·교과서·지도서 조사 (쪽 번호)
      ├─ 01_spec.json            ← S1 단원 명세 (+ template, removed_features, media)
      ├─ 02_content.json         ← S2 개념 정리 + 퀴즈
      ├─ 03_reference.json       ← SA 참고 그림 목록 + 스타일 메모 (그림 파일은 inbox/refs/에, 페이지에는 안 넣음)
      ├─ index.html              ← S3 결과물 ┐
      ├─ contents/               ← (쓸 때만) ├ 업로드 대상 = zip 안에 들어가는 것
      │  └─ sound1.mp3, *_data.js …        ┘   불러올 때 ./contents/… 상대경로
      ├─ scenarios.json          ← V 화면 점검 조작 시나리오 (scenario_shots.mjs 입력)
      ├─ 04_review.json          ← G4 판정 결과 + 승인 기록
      └─ m{학년}_{영어_단원명}.zip ← G4 승인 뒤 전달물 (안: <폴더명>/index.html + contents/)
```

- 영역: `phy` / `chem` / `bio` / `ear` (`chem`, `bio`는 추정. 실제 T셀파 경로와 다르면 수정)
- 단원 폴더: `m{학년}_{영어_단원명}` (예: `units/ear/m1_moon_phase`). 한글·공백 금지 (FTP 업로드·실행 오류).

## 파일 형식과 셀 수 있는 조건
| 파일 | 형식 | 필수 칸 |
|---|---|---|
| `00_input.md` | Markdown | 단원명·학년·영역 / 성취기준 / 조작 변수 / 개념·퀴즈 메모 — 4칸 모두 비어 있지 않음 |
| `00_research.json` | JSON | `standards`(지도서 출처), `textbook_pages`, `terms`, `activities`, `teaching_notes`, `sim_points` — 항목마다 `<책 이름> p.<쪽>` |
| `01_spec.json` | JSON | `standards` ≥ 1, `variables` ≥ 1 (range: `min` < `max` + `unit` / select: `options` ≥ 2), `formula_or_source` ≥ 1줄, `template` (`T_Fixed`/`T_Floating`), `removed_features` [] (env_canvas·env_panel 중 하나 이상), (선택) `media` [{file: "contents/…", source}], (선택) `locked_zone_exceptions` [{zone, reason}] |
| `02_content.json` | JSON | CONTENT_CONFIG와 같은 키. `concept` 1~4 (삭제 시 []), `quizzes` ≥ 3 (삭제 시 []), 각 항목에 `standard_ref` |
| `03_reference.json` | JSON | `style_notes` ≥ 1, `items[]`: title, source_url, file(inbox/refs), notes (또는 `skipped` 이유) |
| `index.html` | HTML | design.md 규칙 블록 기준 |
| `contents/` | 폴더 | 쓸 때만. 파일 이름 영문·숫자·`_`, 모두 `01_spec.json` `media`에 출처 |
| `04_review.json` | JSON | 판정 결과 + 승인 기록 |
| `<폴더명>.zip` | zip | `check_unit.py --package`로 생성. `index.html` + `contents/`만 (작업 파일 제외) |

## 규칙 SSOT
- `docs/design.md` 1개. 사람이 읽는 설명 + 스크립트가 읽는 YAML 규칙 블록. 기준은 `ref/`의 공식 템플릿·제작 안내.

## 재개
- 다시 실행하면 단원 폴더에서 **처음으로 없는 파일**부터 이어서 만든다.
- 되돌아갈 때는 그 단계의 파일과 그 뒤 파일을 지우고 다시 만든다.
