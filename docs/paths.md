# 파일 경로 규칙 (paths.md) — 절대 경로 금지, 상대 경로만

> 근거: `ref/바이브코딩 콘텐츠 제작 관련 안내.pdf` 2장(작업 폴더)·3장(contents 폴더의 파일을 상대 경로로 불러오기).
> **모든 단원(units/ 아래 작품)은 만들 때마다 이 문서를 따른다.** S1(`media`)·S3(`index.html`)·G3 판정·G4 묶음이 이 문서를 기준으로 한다.

## 1. 단원 폴더 = 업로드되는 한 덩어리

```
units/ear/                      ← 영역 폴더 (상위 폴더)
└─ m1_moon_phase/               ← 단원 폴더 (내 위치) — 이 폴더째 서버에 올라간다
   ├─ index.html                ← 나
   ├─ contents/                 ← 하위 폴더 (외부 파일이 있을 때만)
   │  ├─ image1.png
   │  ├─ sound1.mp3
   │  └─ moon_data.js
   └─ 00_input.md … 04_review.json, scenarios.json   ← 작업 파일 (zip에 안 들어감)
```

- 폴더·파일 이름: 영문 + 숫자, 공백은 `_` (한글·공백은 FTP 업로드·실행 오류). 단원 폴더는 `m{학년}_{영어_콘텐츠명}`.
- `index.html`이 쓰는 이미지·영상·음성·데이터 파일은 **전부 `contents/` 안에** 둔다. 안 쓰면 `contents/`를 만들지 않는다.
- 서버에 올라가는 것은 `index.html` + `contents/`뿐이다 (`check_unit.py --package`가 이 둘만 `<폴더명>.zip`으로 묶는다).

## 2. 절대 경로 — 쓰지 않는다 🚫

| 예 | 문제 |
|---|---|
| `<img src="C:/science/ear/m1_moon_phases/contents/image1.png">` | 폴더를 옮기거나 다른 컴퓨터·서버에 올리면 경로가 달라져 안 보임 |
| `<img src="https://example.com/blog/image1.png">` | 인터넷에서 원본이 지워지면 안 보임 (+ 출처·권리 문제, N2) |

- 예외: 템플릿에 원래 있는 T셀파 로고·라이브러리 주소(`cdata2.tsherpa.co.kr`, `cdn.jsdelivr.net` 등 design.md 6장 기본 도메인)와 `01_spec.json` `formula_or_source`에 신고한 데이터 도메인만 허용.

## 3. 상대 경로 — 이것만 쓴다 ✅

`./` = 내 위치(`index.html`이 있는 단원 폴더).

| 상황 | 코드 | 뜻 | 이 하네스에서 |
|---|---|---|---|
| 하위 폴더 | `src="./contents/image1.png"` | 내 옆 contents 폴더 안의 파일 | **유일하게 쓰는 형태** |
| 같은 폴더 | `src="./image1.png"` | 나랑 같은 폴더의 파일 | 쓰지 않음 (파일은 contents/에) |
| 상위 폴더 | `src="../image1.png"` | 상위 폴더로 나가서 불러옴 | **금지** (단원 폴더 밖은 zip·업로드에 안 들어감) |

→ 폴더 구조만 유지되면 컴퓨터가 바뀌거나 탑재 서버가 달라져도 코드를 고치지 않아도 된다.

### 코드에서 쓰는 모양
```html
<img src="./contents/image1.png" alt="…">
<script src="./contents/moon_data.js"></script>
```
```js
const clickSound = new Audio('./contents/sound1.mp3');   // 효과음 (sound 기능을 남겼을 때)
fetch('./contents/table.json')                            // 데이터 (file:// 로 열면 막히므로 가능하면 .js 데이터 파일로)
```

## 4. 단계별 할 일

| 단계 | 할 일 |
|---|---|
| S1 기획 | 쓸 파일을 `01_spec.json` `media`에 `{ "file": "contents/image1.png", "source": "출처·권리" }`로 적는다. 기구·물체 그림은 코드로 그리는 것이 기본 (교과서·clarchive 그림은 넣지 않음) |
| S3 구현 | 파일을 `<단원폴더>/contents/`에 두고 `./contents/파일명`으로만 부른다 |
| G3 판정 | `check_unit.py`가 검사: 참조마다 `./contents/` 시작 + 파일 존재 + `media`에 출처, 폴더·파일 이름 영문·숫자·`_` |
| G4 승인 | `check_unit.py --package` → `<폴더명>.zip` (안: `<폴더명>/index.html` + `<폴더명>/contents/…`) 로 전달 |

## 5. AI에게 시킬 때 프롬프트 예 (제작 안내 3장)
- 이미지: "현재 HTML 파일과 같은 위치에 contents라는 이름의 폴더가 있고, 그 안에 image1.png 파일이 있어. 이 이미지를 중앙에 넣어줘. **상대 경로**를 사용해서 작성해야 해."
- 음원: "효과음을 넣고 싶어. HTML 파일과 같은 위치에 contents라는 폴더가 있고 그 안에 sound1.mp3 파일이 들어 있어. OO 버튼을 눌렀을 때 해당 효과음이 재생되도록 해 줘. **상대 경로**를 사용해서 작성."
