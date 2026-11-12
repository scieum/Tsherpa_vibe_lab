// 교과서·지도서 PDF → 쪽 표시가 붙은 텍스트, 또는 일부 쪽만 담은 작은 PDF (macOS PDFKit, 추가 설치 없음)
// 사용:
//   osascript -l JavaScript scripts/extract_textbook.js <pdf> <out.txt>             # 전체 텍스트
//   osascript -l JavaScript scripts/extract_textbook.js <pdf> <out.pdf> <쪽|쪽-쪽>   # 그 쪽만 PDF로 (그림·그래프 확인용)
// 텍스트 출력: "=== p{PDF쪽번호} ===" 줄 뒤에 그 쪽 텍스트. PDF 쪽번호는 책에 인쇄된 쪽수와 다를 수 있다.
// 쪽 PDF는 Read 도구(pages)로 열어 그림을 본다. 원본이 100MB를 넘어 Read가 안 될 때 쓴다.
ObjC.import('PDFKit');
ObjC.import('Foundation');

function run(argv) {
  if (argv.length < 2) return 'usage: extract_textbook.js <pdf> <out.txt> | <pdf> <out.pdf> <쪽|쪽-쪽>';
  const doc = $.PDFDocument.alloc.initWithURL($.NSURL.fileURLWithPath(argv[0]));
  if (doc.isNil()) return 'error: PDF를 열 수 없음: ' + argv[0];
  const n = doc.pageCount;

  if (argv.length >= 3) {
    const m = String(argv[2]).match(/^(\d+)(?:-(\d+))?$/);
    if (!m) return 'error: 쪽 범위 형식은 12 또는 12-15';
    const a = Math.max(1, +m[1]), b = Math.min(n, +(m[2] || m[1]));
    if (a > b) return 'error: 쪽 범위가 PDF(' + n + '쪽) 밖';
    const out = $.PDFDocument.alloc.init;
    for (let i = a; i <= b; i++) out.insertPageAtIndex(doc.pageAtIndex(i - 1), i - a);
    if (!out.writeToFile(argv[1])) return 'error: 저장 실패 ' + argv[1];
    return 'ok p' + a + '-' + b + ' → ' + argv[1];
  }

  const parts = [];
  for (let i = 0; i < n; i++) {
    const s = doc.pageAtIndex(i).string;
    parts.push('=== p' + (i + 1) + ' ===\n' + (s.isNil() ? '' : s.js));
  }
  $(parts.join('\n')).writeToFileAtomicallyEncodingError(argv[1], true, $.NSUTF8StringEncoding, null);
  return 'ok ' + n + ' pages → ' + argv[1];
}
