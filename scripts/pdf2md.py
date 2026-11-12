"""PDF → Markdown (PyMuPDF). 사용: python pdf2md.py <pdf> <out.md> [쪽 범위 a-b]
쪽마다 '## p.N' (PDF 쪽번호), 본문보다 큰 글자 줄은 ###/#### 제목, 블록 안 줄은 한 문단으로 잇는다. 그림은 넣지 않는다."""
import collections
import sys
from pathlib import Path

import fitz

pdf, out = sys.argv[1], Path(sys.argv[2])
d = fitz.open(pdf)
a, b = (map(int, sys.argv[3].split('-')) if len(sys.argv) > 3 else (1, len(d)))

# 본문 글자 크기 = 문서에서 글자 수가 가장 많은 크기
cnt = collections.Counter()
for i in range(len(d)):
    for blk in d[i].get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            for sp in ln['spans']:
                cnt[round(sp['size'] * 2) / 2] += len(sp['text'].strip())
body = cnt.most_common(1)[0][0]

parts = [f'# {Path(pdf).stem}\n\n> 원본: `{Path(pdf).name}` ({len(d)}쪽). `p.N`은 PDF 쪽번호(책에 인쇄된 쪽수와 다를 수 있음). 그림·표 모양은 원본 PDF로 확인.\n']
for i in range(a - 1, b):
    page = d[i]
    lines_out = []
    for blk in sorted(page.get_text('dict')['blocks'], key=lambda x: (round(x['bbox'][1]), x['bbox'][0])):
        para = []
        for ln in blk.get('lines', []):
            text = ''.join(sp['text'] for sp in ln['spans']).strip()
            if not text:
                continue
            size = max(sp['size'] for sp in ln['spans'] if sp['text'].strip())
            heading = len(text) >= 2 and not text.replace(' ', '').replace(',', '').replace('.', '').isdigit()
            if heading and size >= body * 1.8:
                lines_out += [' '.join(para)] if para else []
                para = []
                lines_out.append(f'### {text}')
            elif heading and size >= body * 1.3:
                lines_out += [' '.join(para)] if para else []
                para = []
                lines_out.append(f'#### {text}')
            else:
                para.append(text)
        if para:
            lines_out.append(' '.join(para))
    parts.append(f'\n---\n\n## p.{i + 1}\n\n' + '\n\n'.join(lines_out) + '\n')
out.write_text(''.join(parts), encoding='utf-8')
print(out.name, f'p.{a}-{b}', f'body={body}pt', out.stat().st_size, 'bytes')
