# 게이트 (gates)

사람 승인은 G4 한 곳뿐이다. G0~G3(GR 포함)은 스크립트만 판정한다.
★ = docs/story-service.md의 "어기면 안 되는 것"(N1, N2)을 위반하면 걸리는 조건.

| 게이트 | 위치 | 통과 조건 (스크립트가 셈) | 실패 시 돌아갈 곳 |
|---|---|---|---|
| G0 입력 | S1 전 | `00_input.md` 4칸이 모두 비어 있지 않음 | 사용자에게 질문 |
| GR 자료 조사 | S0 후 | `00_research.json`: 성취기준 ≥ 1 (코드 형식 + 출처가 **지도서** 쪽)<br>교과서 쪽 범위 ≥ 1 (단원 학교급 폴더 `inbox/textbook/mid` 또는 `high/…`에 있는 책, 그 학교급 책은 모두 `_text/` 추출)<br>용어 ≥ 1, 탐구 활동 ≥ 1, 지도서 유의점 ≥ 1, 시뮬레이션 반영점 ≥ 1 — 모두 `<책 이름> p.<쪽>` 출처 | S0 |
| G1 명세 (멈칫 G-a) | S1 후 | ★N1 `standards` 코드가 `00_research.json`에 있음<br>`standards` ≥ 1, 코드가 design.md 7장 `standard_code_regex` (중 `[9과NN-NN]`, 고 `[10통과1-01-01]`·`[12물리01-01]`)<br>`variables`: range는 `min < max` + `unit` 있음, select는 `options` ≥ 2<br>`formula_or_source` ≥ 1줄<br>`template` ∈ {T_Fixed, T_Floating}<br>`removed_features` ⊆ {sound, env_canvas, env_panel, concept, quiz, zoom, drag, panel}<br>변수/조건 안내는 한 곳만 (`env_canvas`·`env_panel` 중 하나 이상 삭제)<br>`panel` 삭제는 T_Floating에서만 + concept·quiz·env_panel 함께 삭제<br>★N2 `media[]`마다 `contents/…` 경로 + 출처 | S1 |
| G2 콘텐츠 (멈칫 G-b) | S2 후 | guide steps 3~5개<br>concepts 1~4장, color ∈ {orange, green, blue, purple} (concept 삭제 시 `[]`)<br>quiz ≥ 3, `a`는 `정답:`으로 시작 + `해설:` 포함 (quiz 삭제 시 `[]`)<br>★N1 개념·퀴즈마다 `standard_ref` ∈ 01_spec의 성취기준 코드<br>★N1 퀴즈 정답 번호(①~⑤)가 그 문항 보기에 있음 | S2 |
| GA 참고 그림 | SA 후 | `03_reference.json` 있음, 항목 ≥ 1 또는 `skipped` 이유<br>항목마다 출처 URL, `style_notes` ≥ 1<br>★N2 참고 파일은 단원 폴더 밖(`inbox/refs/`) | SA |
| G3 화면 | S3 후 | 비교 기준 = `templates/unit/<template>.html`<br>필수 유지 요소 10개 있음 (헤더·`#workspace`·푸터, T셀파 로고 링크, 제목, 학습 가이드 버튼·팝업, 전체화면, 초기화, 캔버스)<br>`removed_features`에 적은 기능은 흔적 0, 안 적은 기능은 모두 있음<br>섹션 (design.md 7장 `sections`, 삭제한 개념·퀴즈 제외)<br>`:root` 토큰 18개 일치<br>🚫 영역 = 템플릿 — 기능을 지운 경우 **지우기만 한 차이**는 허용(지운 줄 수를 보고), 고치거나 끼워 넣은 줄은 실패 (`locked_zone_exceptions` 신고 영역 제외)<br>필수 함수 4개 (`initSimulation`, `draw`, `updatePhysics`, `bindInputEvents`)<br>`CONTENT_CONFIG` = `02_content.json`<br>남긴 `#conceptBtn`, `#quizBtn`에 `hidden` 없음<br>★N2 외부 파일은 `./contents/` 상대경로 + 파일 있음 + `media`에 출처 (템플릿 로고 제외, 절대경로·`../` 실패 — docs/paths.md)<br>단원 폴더 이름 `^m[1-3]_[a-z0-9_]+$`, 업로드 파일 이름 영문·숫자·`_`만<br>★N2 외부 도메인 ⊆ 기본 6개 + `formula_or_source`에 적은 도메인<br>헤드리스 Chrome 콘솔 에러 0건<br>`docs/`·`templates/`·`scripts/` 해시가 시작 때와 같음 | 원인별 S1 / S2 / S3 (pipeline.md) |
| GQ 삽화 품질 | G3 후, V 전 | Claude가 장면별 캡처를 교과서 쪽 그림과 나란히 보고 `art_check.json`에 채점 (아래 기준). 모든 항목 ≥ 2이고 평균 ≥ 2.5 | 1·2회째: S3 / 2회 실패: 사용자에게 Higgsfield 삽화 제안 ⏸ |
| G4 사람 승인 | S4 | `04_review.json`에 `approved: true`, `approver`, `date`, N1·N2·검수 체크 결과 → `<폴더명>.zip` 생성 | 사람이 고른 단계 |

## GQ 삽화 품질 (2026-11-12 추가)
- 대상: 기구·장치·장면 그림(시험관, 알코올램프, 비커, 용광로, 서식지 등). 입자 모형·그래프·라벨은 대상이 아니다.
- 방법: `scenario_shots.mjs`로 장면마다 PC 1440×900 캡처 1장 → 같은 장면의 교과서 쪽 그림(`scripts/pdf2md.py`나 PyMuPDF로 뽑은 PNG, 단원 폴더 밖)과 나란히 본다.
- 채점 (항목마다 1 = 어색함 / 2 = 쓸 만함 / 3 = 교과서 삽화 수준):
  1. 형태: 교과서 그림과 같은 기구 구성·연결 (빠지거나 틀린 부품 없음)
  2. 비례·원근: 크기 비율, 놓인 위치, 바닥에 떠 있지 않음
  3. 질감: 유리 투명도·반사, 액체 면, 불꽃, 금속 광택
  4. 스타일: 선 굵기·색이 한 장면 안에서 고르고 교과서 삽화 톤과 맞음
  5. 변화 표현: 색 변화·석출·기포 같은 관찰 결과가 한눈에 보임
- 기록: `art_check.json` = `{"round": n, "scenes": [{"scene", "shot", "textbook_ref", "scores": {"형태": n, …}, "fix": "고칠 점"}], "pass": bool}`
- 실패 1·2회째: `fix`를 S3에 넘겨 다시 그린다.
- 2회 실패: 멈추고 사용자에게 **Higgsfield로 교과서 형태 삽화 만들기**를 제안한다 (크레딧이 들므로 사용자 승인 필수). 승인하면
  - 정적인 기구 그림만 이미지로 만들어 `contents/`에 넣고(webp, 배경 투명), `01_spec.json` `media`에 "Higgsfield AI 생성(작업 번호)" 출처를 적는다.
  - 색 변화·석출·입자·라벨처럼 조작에 따라 바뀌는 부분은 계속 코드로 그려 이미지 위에 얹는다.
  - 교과서·clarchive 그림을 그대로 넣거나 따라 그리게 하지 않는다 (N2). 프롬프트에는 기구 이름·구성만 쓴다.

## G4 진행 방식
1. Claude가 G0~G3 판정 결과와 V 단계 캡처를 보여준다.
2. 사람이 아래 체크리스트를 확인하고 채팅으로 "승인" 또는 "반려 + 돌아갈 단계"를 말한다.
3. Claude가 그 내용을 `04_review.json`에 기록하고, 승인이면 `check_unit.py --package`로 zip을 만든다.

### G4 체크리스트
- [ ] N1: 성취기준 원문을 지도서 쪽(00_research.json)으로 확인했다.
- [ ] N1: 개념 카드 n장, 퀴즈 n문항을 교과서와 대조했다.
- [ ] N1: 시뮬레이션 결과(계산·그림)가 교과서 설명과 같다.
- [ ] N2: 외부 데이터·이미지 출처를 확인했다 (`03_reference.json`: 참고만 / `contents/` 파일은 `media` 출처).
- [ ] 템플릿: 고른 유형(T_Fixed/T_Floating)이 맞고, 지운 기능(`removed_features`)과 지운 줄(G3 보고)이 그 기능 코드뿐이다. 필수 유지 5가지가 그대로다.
- [ ] 화면: V 단계 캡처(PC 1440·2560·전체화면, 아이폰SE·S20 울트라 세로, 모바일 가로, ⋮ 메뉴)를 확인했고, 확대하면 글자·라벨·상자도 함께 커지며, 캡처에 없는 상태는 직접 확인했다.
- [ ] 검수 환경 (제작 안내 4장, 사람이 직접): PC·모바일 모두, 브라우저 크롬·엣지·웨일·삼성 인터넷·사파리(아이폰/아이패드). 개발자 도구(F12) 기기 툴바로 여러 기기·가로 모드를 보고, **링크를 만든 뒤 실제 기기로도 확인**한다.
- [ ] 🚫 영역 예외(`locked_zone_exceptions`)가 있으면 이유를 확인했다.

### 검수 때 정상인 것 (반려 사유 아님, 제작 안내 4-2)
- 기기·브라우저에 따라 시뮬레이터 영역이 작게 보일 수 있다.
- 모바일 세로 첫 화면에서는 ⋮(더보기)를 눌러야 학습 가이드·전체화면 버튼이 나온다.
- 모바일에서는 음량 버튼이 보이지 않는다.
- 아이폰(iOS)은 전체화면을 지원하지 않아 안내 팝업이 뜬다 (아이패드는 전체화면 가능).
- 카카오톡에서 링크로 열고 전체화면을 누르면 가로로 자동 전환된다. 그 밖의 브라우저는 상황에 따라 가로/세로로 바뀐다.

## 반복 제한
- 같은 단계로 3번 돌아가도 통과하지 못하면 멈추고 사용자에게 묻는다.
