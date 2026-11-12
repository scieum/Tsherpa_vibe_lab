# 역할 (roles)

에이전트 정의는 `.claude/agents/*.md`. 모든 단계가 같은 단원 폴더를 쓰므로 편집 범위는 **파일 단위**로 나눈다.

| 에이전트 | 단계 | 쓸 수 있는 것 (이것만) | 읽는 것 | 도구 |
|---|---|---|---|---|
| `unit-researcher` | S0 | `00_research.json` | `00_input.md`, inbox/textbook/_text/*.txt (+ `mid/`·`high/<과목>/` PDF 쪽) | Read, Write, Glob, Grep |
| `unit-planner` | S1 | `01_spec.json` | `00_input.md`, `00_research.json`, docs/prd.md, docs/story-service.md | Read, Write |
| `unit-writer` | S2 | `02_content.json` | `01_spec.json`, `00_research.json`, docs/design.md 5장 | Read, Write |
| `unit-builder` | S3 | `index.html` (+ `contents/` 안 단원 데이터 `*_data.js`) — 03_reference.json 참고 그림을 보고 코드로 그림 | 01·02, docs/design.md, docs/paths.md, `templates/unit/<template>.html` | Read, Write, Edit |
| `unit-judge` 🔒 | G0~G3 | 없음 (읽기 전용) | 단원 폴더 전체, docs/design.md | Read, Bash(`python3 scripts/…`만) |
| 오케스트레이터 (메인 Claude) | P0·P1·R·SA·V·G4 | `00_input.md`, `.baseline.json`, `04_review.json`, `03_reference.json`, `scenarios.json`, `<폴더명>.zip`, inbox/refs/, inbox/textbook/_text | 전부 | 전부 |

- `docs/`, `templates/`, `scripts/`는 에이전트가 고치지 않는다. 사용자가 요청할 때만 오케스트레이터가 고친다. `ref/`(공식 템플릿·제작 안내)는 아무도 고치지 않는다.
- 편집 범위는 에이전트 설명서에 적고, G3에서 `docs/`·`templates/`·`scripts/` 해시가 바뀌지 않았는지 사후 확인한다. (훅 차단은 R8에서 필요하면 추가)
- 판정자는 결과를 출력만 한다. `04_review.json`은 G4 승인 뒤 오케스트레이터가 쓴다.

## 판정 스크립트
- `python3 scripts/check_unit.py <단원폴더> --gate G0|GR|G1|G2|GA|G3|ALL` (`--no-render`: 헤드리스 Chrome 생략, `--baseline`: .baseline.json 기록, `--package`: 승인 뒤 전달용 zip)
- 콘솔 에러·화면 캡처: `scripts/render_check.mjs` (check_unit.py가 G3에서 호출)
- 출력: 통과/실패 건수, 실패 항목 목록, 돌아갈 단계(S1/S2/S3). 실패가 1건이라도 있으면 종료 코드 1.

## 자연어 트리거
| 사용자가 이렇게 말하면 | 하는 일 |
|---|---|
| "새 단원 만들어줘: 중2 물리 빛의 반사" | 단원 폴더 생성 → `00_input.md` 4칸을 질문으로 채움 → S0부터 시작 |
| "○○ 단원 이어서 해줘" | 처음으로 없는 파일부터 이어서 진행 |
| "○○ 검사해줘" | 판정자만 실행 (G0~G3), 파일은 고치지 않음 |
| "승인" / "반려, S2로" | `04_review.json`에 기록 + 승인이면 zip 생성, 반려면 그 단계부터 다시 |
