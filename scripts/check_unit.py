#!/usr/bin/env python3
"""단원 폴더 판정 스크립트 (G0, GR, G1, G2, GA, G3).

사용:
  python3 scripts/check_unit.py <단원폴더> --gate G0|GR|G1|G2|GA|G3|ALL
  python3 scripts/check_unit.py <단원폴더> --baseline     # 시작 시점 해시를 .baseline.json에 기록
  python3 scripts/check_unit.py <단원폴더> --package      # G4 승인 뒤 전달용 <폴더명>.zip (index.html + contents/)

규칙은 docs/design.md 7장의 YAML 블록에서 읽는다 (SSOT). 게이트 정의는 docs/gates.md.
실패가 1건이라도 있으면 종료 코드 1. 마지막 줄에 돌아갈 단계(S1/S2/S3)를 출력한다.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DESIGN_MD = ROOT / 'docs' / 'design.md'
BASELINE_DIRS = ['docs', 'templates', 'scripts']
CIRCLED = '①②③④⑤'
STAGE_ORDER = ['사용자', 'S0', 'S1', 'S2', 'SA', 'S3']
TEXTBOOK_DIR = ROOT / 'inbox' / 'textbook'


# ─────────────────────────────────────────────────────────────
# design.md 7장 YAML 읽기 (PyYAML 없이 쓰는 최소 파서: 이 문서에서 쓰는 문법만 지원)
# ─────────────────────────────────────────────────────────────
def _strip_comment(line):
    out, quote = [], None
    for i, ch in enumerate(line):
        if quote:
            if ch == quote:
                quote = None
        elif ch in '"\'':
            quote = ch
        elif ch == '#' and (i == 0 or line[i - 1] in ' \t'):
            break
        out.append(ch)
    return ''.join(out).rstrip()


def _scalar(s):
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in '"\'':
        return s[1:-1]
    if s in ('true', 'false'):
        return s == 'true'
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        return s


def _flow(s, i=0):
    """[a, b] / {k: v} 형태를 읽는다. (값, 다음 위치)를 돌려준다."""
    while s[i] == ' ':
        i += 1
    if s[i] in '[{':
        close = ']' if s[i] == '[' else '}'
        is_map = s[i] == '{'
        result = {} if is_map else []
        i += 1
        while True:
            while s[i] in ' ,':
                i += 1
            if s[i] == close:
                return result, i + 1
            if is_map:
                j = s.index(':', i)
                key = s[i:j].strip()
                val, i = _flow(s, j + 1)
                result[key] = val
            else:
                val, i = _flow(s, i)
                result.append(val)
    if s[i] in '"\'':
        j = s.index(s[i], i + 1)
        return s[i + 1:j], j + 1
    j = i
    while j < len(s) and s[j] not in ',]}':
        j += 1
    return _scalar(s[i:j]), j


def _value(s):
    s = s.strip()
    if s.startswith(('[', '{')):
        return _flow(s)[0]
    return _scalar(s)


def parse_yaml(text):
    lines = [(len(l) - len(l.lstrip(' ')), l.strip())
             for l in (_strip_comment(x) for x in text.split('\n')) if l.strip()]

    def block(idx, indent):
        if lines[idx][1].startswith('- '):
            items = []
            while idx < len(lines) and lines[idx][0] == indent and lines[idx][1].startswith('- '):
                items.append(_value(lines[idx][1][2:]))
                idx += 1
            return items, idx
        result = {}
        while idx < len(lines) and lines[idx][0] == indent:
            key, _, rest = lines[idx][1].partition(':')
            idx += 1
            if rest.strip():
                result[key.strip()] = _value(rest)
            elif idx < len(lines) and lines[idx][0] > indent:
                result[key.strip()], idx = block(idx, lines[idx][0])
            else:
                result[key.strip()] = None
        return result, idx

    return block(0, lines[0][0])[0]


def load_rules():
    text = DESIGN_MD.read_text(encoding='utf-8')
    sec = text.split('## 7.', 1)[1]
    m = re.search(r'```yaml\n(.*?)```', sec, re.S)
    return parse_yaml(m.group(1))


# ─────────────────────────────────────────────────────────────
# 판정 결과 모음
# ─────────────────────────────────────────────────────────────
class Report:
    def __init__(self):
        self.items = []  # (gate, id, ok, msg, stage)

    def check(self, gate, cid, ok, msg, stage):
        self.items.append((gate, cid, bool(ok), msg, stage))
        return ok

    def fails(self):
        return [x for x in self.items if not x[2]]


def read_json(path, rep, gate, cid, stage):
    if not path.exists():
        rep.check(gate, cid, False, f'{path.name} 없음', stage)
        return None
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        rep.check(gate, cid, False, f'{path.name} JSON 형식 오류: {e}', stage)
        return None


# ─────────────────────────────────────────────────────────────
# G0 입력
# ─────────────────────────────────────────────────────────────
def gate_g0(unit, rules, rep):
    p = unit / '00_input.md'
    if not rep.check('G0', 'G0.exists', p.exists(), '00_input.md 있음', '사용자'):
        return
    text = re.sub(r'<!--.*?-->', '', p.read_text(encoding='utf-8'), flags=re.S)
    parts = re.split(r'^## ', text, flags=re.M)[1:]
    rep.check('G0', 'G0.sections', len(parts) == 4, f'## 칸 {len(parts)}/4', '사용자')
    for part in parts:
        title, _, body = part.partition('\n')
        filled = [l for l in body.split('\n') if l.strip() and l.strip().upper() != 'TODO']
        rep.check('G0', f'G0.filled:{title.strip()}', filled, f'"{title.strip()}" 칸 채움', '사용자')


# ─────────────────────────────────────────────────────────────
# GR 자료 조사 (성취기준 → 교과서 → 지도서)
# ─────────────────────────────────────────────────────────────
def research_codes(unit):
    try:
        r = json.loads((unit / '00_research.json').read_text(encoding='utf-8'))
        return {str(s.get('code', '')) for s in r.get('standards') or []}
    except (OSError, json.JSONDecodeError):
        return None


def gate_gr(unit, rules, rep):
    r = read_json(unit / '00_research.json', rep, 'GR', 'GR.exists', 'S0')
    if r is None:
        return
    # 학교급 폴더: inbox/textbook/mid/*.pdf, inbox/textbook/high/<과목>/*.pdf (단원 폴더 m… → mid, h… → high)
    level = 'high' if unit.name.startswith('h') else 'mid'
    books = sorted({f.stem for f in (TEXTBOOK_DIR / level).rglob('*.pdf')}, key=len, reverse=True)
    rep.check('GR', 'GR.books', books, f'inbox/textbook/{level} 교과서·지도서 PDF {len(books)}권', '사용자')
    # 텍스트는 조사에 실제로 인용한 책만 요구 (high에는 과목이 여러 개라 전부 추출할 필요 없음)
    raw = json.dumps(r, ensure_ascii=False)
    used = [b for b in books if b in raw] or books
    no_text = [b for b in used if not (TEXTBOOK_DIR / '_text' / f'{b}.txt').exists()]
    rep.check('GR', 'GR.text', not no_text, '교과서·지도서 텍스트 추출됨 (_text/)'
              + (f' (없음: {", ".join(no_text)})' if no_text else ''), '사용자')

    def cited(src):  # "<책 이름> p.<쪽>" 형식이고 책이 실제로 있는가
        src = str(src or '')
        return any(b in src for b in books) and re.search(r'p\.?\s*\d+', src)

    code_re = re.compile(rules['spec']['standard_code_regex'])
    stds = r.get('standards') or []
    rep.check('GR', 'GR.standards.count', len(stds) >= 1, f'성취기준 {len(stds)}개 (≥1)', 'S0')
    for i, s in enumerate(stds):
        code = str(s.get('code', ''))
        rep.check('GR', f'GR.standards[{i}].code', code_re.match(code), f'성취기준 코드 형식: {code}', 'S0')
        rep.check('GR', f'GR.standards[{i}].text', str(s.get('text', '')).strip(), f'성취기준 문장 있음: {code}', 'S0')
        rep.check('GR', f'GR.standards[{i}].source', cited(s.get('source')) and '지도서' in str(s.get('source')),
                  f'성취기준 출처가 지도서 쪽: {s.get("source")}', 'S0')
    tps = r.get('textbook_pages') or []
    rep.check('GR', 'GR.textbook_pages.count', len(tps) >= 1, f'교과서 쪽 범위 {len(tps)}건 (≥1)', 'S0')
    for i, t in enumerate(tps):
        ok = t.get('book') in books and '교과서' in str(t.get('book')) and re.search(r'\d', str(t.get('pages', ''))) and str(t.get('summary', '')).strip()
        rep.check('GR', f'GR.textbook_pages[{i}]', ok, f'교과서 쪽: {t.get("book")} {t.get("pages")}', 'S0')
    terms = [x for x in r.get('terms') or [] if str(x).strip()]
    rep.check('GR', 'GR.terms', len(terms) >= 1, f'교과서 용어 {len(terms)}개 (≥1)', 'S0')
    for key, need, label in [('activities', 1, '탐구 활동'), ('teaching_notes', 1, '지도서 유의점'),
                             ('sim_points', 1, '시뮬레이션 반영점'), ('examples', 0, '생활 사례')]:
        items = r.get(key) or []
        rep.check('GR', f'GR.{key}.count', len(items) >= need, f'{label} {len(items)}개 (≥{need})', 'S0')
        for i, it in enumerate(items):
            rep.check('GR', f'GR.{key}[{i}]', str(it.get('text', '')).strip() and cited(it.get('source')),
                      f'{label} 출처: {it.get("source")}', 'S0')
    notes = r.get('teaching_notes') or []
    rep.check('GR', 'GR.teaching_notes.guide', any('지도서' in str(n.get('source')) for n in notes),
              '지도서에서 온 유의점 1개 이상', 'S0')


# ─────────────────────────────────────────────────────────────
# G1 명세
# ─────────────────────────────────────────────────────────────
def gate_g1(unit, rules, rep):
    spec = read_json(unit / '01_spec.json', rep, 'G1', 'G1.exists', 'S1')
    if spec is None:
        return
    code_re = re.compile(rules['spec']['standard_code_regex'])
    stds = spec.get('standards') or []
    rep.check('G1', 'G1.standards.count', len(stds) >= 1, f'성취기준 {len(stds)}개 (≥1)', 'S1')
    for i, s in enumerate(stds):
        code = str(s.get('code', ''))
        rep.check('G1', f'G1.standards[{i}].code', code_re.match(code), f'성취기준 코드 형식: {code}', 'S1')
        rep.check('G1', f'G1.standards[{i}].text', str(s.get('text', '')).strip(), f'성취기준 문장 있음: {code}', 'S1')
        rcodes = research_codes(unit)
        rep.check('G1', f'G1.standards[{i}].research', rcodes is not None and code in rcodes,
                  f'성취기준이 00_research.json(지도서 확인)에 있음: {code}', 'S1')
    vars_ = spec.get('variables') or []
    rep.check('G1', 'G1.variables.count', len(vars_) >= 1, f'조작 변수 {len(vars_)}개 (≥1)', 'S1')
    for i, v in enumerate(vars_):
        name = v.get('name', f'#{i}')
        if v.get('type', 'range') == 'select':
            n = len(v.get('options') or [])
            rep.check('G1', f'G1.variables[{i}]', n >= 2, f'{name}: 선택지 {n}개 (≥2)', 'S1')
        else:
            mn, mx = v.get('min'), v.get('max')
            ok = isinstance(mn, (int, float)) and isinstance(mx, (int, float)) and mn < mx
            rep.check('G1', f'G1.variables[{i}].range', ok, f'{name}: min {mn} < max {mx}', 'S1')
            rep.check('G1', f'G1.variables[{i}].unit', str(v.get('unit', '')).strip(), f'{name}: 단위 있음', 'S1')
    fos = [x for x in (spec.get('formula_or_source') or []) if str(x).strip() and str(x).strip().upper() != 'TODO']
    rep.check('G1', 'G1.formula_or_source', len(fos) >= 1, f'공식·데이터 출처 {len(fos)}줄 (≥1)', 'S1')
    t = rules['template']
    rep.check('G1', 'G1.template', spec.get('template') in t['types'],
              f'템플릿 유형: {spec.get("template")} ({" / ".join(t["types"])})', 'S1')
    removed = spec.get('removed_features') or []
    bad = [f for f in removed if f not in t['features']]
    rep.check('G1', 'G1.removed_features', not bad, '삭제 기능이 허용 목록 안' + (f' (모름: {", ".join(bad)})' if bad else ''), 'S1')
    rep.check('G1', 'G1.env_once', {'env_canvas', 'env_panel'} & set(removed),
              '변수/조건 안내는 캔버스(env_canvas)·패널(env_panel) 중 한 곳만 (하나 이상 removed_features에)', 'S1')
    if 'panel' in removed:
        rep.check('G1', 'G1.panel', spec.get('template') == 'T_Floating' and {'concept', 'quiz', 'env_panel'} <= set(removed),
                  '제어 패널 삭제는 T_Floating에서만, concept·quiz·env_panel도 함께 삭제', 'S1')
    for i, m in enumerate(spec.get('media') or []):
        rep.check('G1', f'G1.media[{i}]', str(m.get('file', '')).startswith('contents/') and str(m.get('source', '')).strip(),
                  f'★N2 외부 파일 {m.get("file")}: contents/ 아래 + 출처 있음', 'S1')
    for i, e in enumerate(spec.get('locked_zone_exceptions') or []):
        rep.check('G1', f'G1.exceptions[{i}]', e.get('zone') and str(e.get('reason', '')).strip(),
                  f'🚫 예외 {e.get("zone")}: 이유 있음', 'S1')


# ─────────────────────────────────────────────────────────────
# G2 콘텐츠 (G3에서도 CONTENT_CONFIG에 같은 규칙을 다시 적용)
# ─────────────────────────────────────────────────────────────
def content_checks(cfg, rules, rep, gate, codes=None, removed=()):
    c = rules['content']
    stage = 'S2'
    rep.check(gate, f'{gate}.title', str(cfg.get('title', '')).strip(), '제목 있음', stage)
    guide = cfg.get('guide') or {}
    rep.check(gate, f'{gate}.guide.intro', str(guide.get('intro', '')).strip(), '가이드 소개 있음', stage)
    n = len(guide.get('steps') or [])
    g = c['guide_steps']
    rep.check(gate, f'{gate}.guide.steps', g['min'] <= n <= g['max'], f'가이드 단계 {n}개 ({g["min"]}~{g["max"]})', stage)

    concepts = cfg.get('concept') or []
    cc = c['concept']
    if 'concept' in removed:
        rep.check(gate, f'{gate}.concept.count', not concepts, f'개념 정리 삭제됨 → concept 비어 있음 ({len(concepts)}장)', stage)
    else:
        rep.check(gate, f'{gate}.concept.count', cc['min'] <= len(concepts) <= cc['max'],
                  f'개념 카드 {len(concepts)}장 ({cc["min"]}~{cc["max"]})', stage)
    for i, k in enumerate(concepts):
        rep.check(gate, f'{gate}.concept[{i}].color', k.get('color') in cc['colors'], f'개념 {i + 1} 색: {k.get("color")}', stage)
        rep.check(gate, f'{gate}.concept[{i}].text', str(k.get('title', '')).strip() and str(k.get('desc', '')).strip(),
                  f'개념 {i + 1} 제목·설명 있음', stage)
        if codes is not None:
            rep.check(gate, f'{gate}.concept[{i}].standard_ref', k.get('standard_ref') in codes,
                      f'★N1 개념 {i + 1} 성취기준 연결: {k.get("standard_ref")}', stage)

    quizzes = cfg.get('quizzes') or []
    qc = c['quizzes']
    if 'quiz' in removed:
        rep.check(gate, f'{gate}.quizzes.count', not quizzes, f'확인 퀴즈 삭제됨 → quizzes 비어 있음 ({len(quizzes)}문항)', stage)
    else:
        rep.check(gate, f'{gate}.quizzes.count', len(quizzes) >= qc['min'], f'퀴즈 {len(quizzes)}문항 (≥{qc["min"]})', stage)
    for i, q in enumerate(quizzes):
        a, qt = str(q.get('a', '')), str(q.get('q', ''))
        rep.check(gate, f'{gate}.quizzes[{i}].prefix', a.startswith(qc['answer_prefix']) and qc['answer_contains'] in a,
                  f'퀴즈 {i + 1} 정답이 "{qc["answer_prefix"]}"로 시작 + "{qc["answer_contains"]}" 포함', stage)
        m = re.match(r'\s*' + re.escape(qc['answer_prefix']) + r'\s*([' + CIRCLED + '])', a)
        if m:
            rep.check(gate, f'{gate}.quizzes[{i}].choice', m.group(1) in qt,
                      f'★N1 퀴즈 {i + 1} 정답 {m.group(1)}이 보기에 있음', stage)
        if codes is not None:
            rep.check(gate, f'{gate}.quizzes[{i}].standard_ref', q.get('standard_ref') in codes,
                      f'★N1 퀴즈 {i + 1} 성취기준 연결: {q.get("standard_ref")}', stage)


def gate_g2(unit, rules, rep):
    content = read_json(unit / '02_content.json', rep, 'G2', 'G2.exists', 'S2')
    if content is None:
        return
    spec = {}
    if (unit / '01_spec.json').exists():
        spec = json.loads((unit / '01_spec.json').read_text(encoding='utf-8'))
    codes = {s.get('code') for s in spec.get('standards') or []}
    content_checks(content, rules, rep, 'G2', codes, set(spec.get('removed_features') or []))


# ─────────────────────────────────────────────────────────────
# G3 화면
# ─────────────────────────────────────────────────────────────
ZONE_HEAD = re.compile(r'ZONE ([A-Z]) — ')


def split_regions(html, editable):
    """index.html을 영역별로 나눈다. ✏️ 영역은 따로, 나머지 🚫 영역은 ZONE 글자 또는 'HTML'로 묶는다."""
    html = re.sub(r'<title>.*?</title>', '<title></title>', html, count=1, flags=re.S)
    regions = {'HTML': []}
    edit = {}
    cur = 'HTML'
    header_end = None  # ZONE 머리 주석이 끝나는 표시('*/' 또는 '-->')까지는 본문이 아니다
    for line in html.split('\n'):
        s = line.strip()
        if header_end:
            regions['HTML'].append(s)
            if header_end in s:
                header_end = None
            continue
        m = ZONE_HEAD.search(s)
        if m and cur not in ('HTML', 'EDIT_ZONE'):
            cur = 'HTML'  # '끝' 표시가 없는 ZONE(예: E)은 다음 ZONE 머리에서 닫는다
        if cur == 'HTML' and m:
            regions['HTML'].append(s)
            cur = m.group(1)
            (edit if cur in editable else regions).setdefault(cur, [])
            header_end = None if '*/' in s else '*/'
            continue
        if cur == 'HTML' and '입력 폼 영역 시작' in s:
            regions['HTML'].append(s)
            cur = 'EDIT_ZONE'
            edit.setdefault(cur, [])
            header_end = None if '-->' in s else '-->'
            continue
        if (cur == 'EDIT_ZONE' and '입력 폼 영역 끝' in s) or (cur not in ('HTML', 'EDIT_ZONE') and f'ZONE {cur} 끝' in s):
            regions['HTML'].append(s)
            cur = 'HTML'
            continue
        if s:
            (edit if cur in editable else regions)[cur].append(s)
    return regions, edit


def only_deleted(old_lines, new_lines):
    """new가 old에서 글자를 지우기만 해서 나온 것인가 (예: 한 줄 안의 uiSound.playClick(); 삭제)"""
    import difflib
    a, b = '\n'.join(old_lines), '\n'.join(new_lines)
    return all(t in ('equal', 'delete') for t, *_ in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes())


def diff_count(a, b, allow_delete=False):
    """다른 줄 수, 첫 차이, 지운 줄 수. allow_delete면 '지우기만 한' 차이는 세지 않는다 (기능 삭제)."""
    import difflib
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    n, first, deleted = 0, None, 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        if allow_delete and (tag == 'delete' or (tag == 'replace' and only_deleted(a[i1:i2], b[j1:j2]))):
            deleted += i2 - i1
            continue
        n += max(i2 - i1, j2 - j1)
        if first is None:
            first = (b[j1] if j1 < len(b) else a[i1] if i1 < len(a) else '')[:80]
    return n, first, deleted


def extract_content_config(edit_a):
    js = '\n'.join(edit_a) + '\nprocess.stdout.write(JSON.stringify(CONTENT_CONFIG));'
    r = subprocess.run(['node', '-'], input=js, capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        err = [l for l in r.stderr.split('\n') if 'Error' in l]
        raise ValueError(err[0].strip() if err else r.stderr.strip()[:200])
    return json.loads(r.stdout)


def hash_tree():
    files = {}
    for d in BASELINE_DIRS:
        for p in sorted((ROOT / d).rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts and p.name != '.DS_Store':
                files[str(p.relative_to(ROOT))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return files


def strip_refs(cfg):
    cfg = json.loads(json.dumps(cfg))
    for key in ('concept', 'quizzes'):
        for item in cfg.get(key) or []:
            item.pop('standard_ref', None)
    return cfg


def gate_g3(unit, rules, rep, render=True):
    page = unit / 'index.html'
    if not rep.check('G3', 'G3.exists', page.exists(), 'index.html 있음', 'S3'):
        return
    html = page.read_text(encoding='utf-8')
    spec = {}
    if (unit / '01_spec.json').exists():
        spec = json.loads((unit / '01_spec.json').read_text(encoding='utf-8'))
    t = rules['template']
    ttype = spec.get('template')
    if not rep.check('G3', 'G3.template', ttype in t['types'], f'01_spec.json template: {ttype}', 'S1'):
        return
    tpl = (ROOT / t['dir'] / f'{ttype}.html').read_text(encoding='utf-8')
    removed = set(spec.get('removed_features') or [])
    asset_refs_check(unit, html, rep, tpl, spec)
    names_check(unit, rules, rep)

    # 필수 유지 요소 (제작 안내 PDF 1-2)
    for marker in t['required_markers']:
        rep.check('G3', f'G3.required.{marker[:30]}', marker in html, f'필수 유지 요소: {marker}', 'S3')
    # 삭제 가능 기능: 삭제 신고한 것은 흔적이 없고, 남긴 것은 그대로 있어야 함
    for feat, markers in t['features'].items():
        if feat == 'panel' and ttype != 'T_Floating':
            continue
        present = [m for m in markers if m in html]
        if feat in removed:
            rep.check('G3', f'G3.feature.{feat}', not present, f'기능 {feat} 삭제됨' + (f' (남은 흔적: {", ".join(present)})' if present else ''), 'S3')
        else:
            missing = [m for m in markers if m not in html]
            rep.check('G3', f'G3.feature.{feat}', not missing, f'기능 {feat} 유지' + (f' (없음: {", ".join(missing)} → 삭제했다면 removed_features에 신고)' if missing else ''), 'S3')

    # 섹션
    for sec in rules['sections']:
        if sec.get('feature') in removed:
            continue
        sel = sec['selector']
        ok = (f'id="{sel[1:]}"' in html) if sel.startswith('#') else (f'<{sel}' in html)
        if ok and sec.get('text_contains'):
            ok = sec['text_contains'] in html
        rep.check('G3', f'G3.section.{sec["name"]}', ok, f'섹션 {sec["name"]} ({sel})', 'S3')

    # :root 토큰
    m = re.search(r':root\s*\{(.*?)\}', html, re.S)
    actual = dict(re.findall(r'(--[\w-]+)\s*:\s*([^;]+);', m.group(1))) if m else {}
    for k, v in rules['tokens'].items():
        rep.check('G3', f'G3.token.{k}', actual.get(k, '').strip().lower() == str(v).lower(),
                  f'토큰 {k} = {v} (실제 {actual.get(k, "없음")})', 'S3')

    # 글꼴
    for f in rules['font_family'][:1]:
        rep.check('G3', 'G3.font', f in html, f'글꼴 {f} 사용', 'S3')

    # 🚫 영역 = 템플릿 (신고한 예외 제외)
    editable = set(rules['template']['editable_zones'])
    exceptions = {str(e.get('zone')) for e in spec.get('locked_zone_exceptions') or []}
    got, edit = split_regions(html, editable)
    want, _ = split_regions(tpl, editable)
    for zone in sorted(set(got) | set(want)):
        n, first, deleted = diff_count(want.get(zone, []), got.get(zone, []), allow_delete=bool(removed))
        label = '본문 HTML·CSS' if zone == 'HTML' else f'ZONE {zone}'
        note = f', 기능 삭제로 지운 줄 {deleted}개 — G4에서 확인' if deleted else ''
        if zone in exceptions:
            rep.check('G3', f'G3.locked.{zone}', True, f'🚫 {label}: 예외 신고됨 (다른 줄 {n}개{note})', 'S3')
        else:
            rep.check('G3', f'G3.locked.{zone}', n == 0,
                      f'🚫 {label} = {ttype}' + (f' (다른 줄 {n}개, 첫 차이: {first})' if n else '') + note, 'S3')

    # 필수 함수
    for fn in rules['template']['required_functions']:
        rep.check('G3', f'G3.function.{fn}', re.search(r'function\s+' + fn + r'\s*\(', html), f'함수 {fn}() 있음', 'S3')

    # 새 hex 색은 ZONE F 안에서만
    allowed = set(rules['hex_colors_allowed_only_in_zones'])
    for zone, lines in edit.items():
        if zone in allowed:
            continue
        hexes = sorted(set(re.findall(r'#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b', '\n'.join(lines))))
        rep.check('G3', f'G3.hex.{zone}', not hexes, f'{zone}에 hex 색 없음' + (f' (발견: {", ".join(hexes)})' if hexes else ''), 'S3')

    # 모서리 클래스
    radius = sorted({r for r in re.findall(r'\brounded(?:-[\w\[\].]+)?', html)} - set(rules['radius_classes']))
    rep.check('G3', 'G3.radius', not radius, '허용된 모서리 클래스만 사용' + (f' (발견: {", ".join(radius)})' if radius else ''), 'S3')

    # 숨기면 안 되는 버튼
    for sel in rules['hidden_forbidden']:
        if f'id="{sel[1:]}"' not in html and {'concept', 'quiz'} & removed:
            continue  # 기능 삭제로 버튼이 없음 (feature 검사에서 확인)
        bm = re.search(r'<button[^>]*id="' + sel[1:] + r'"[^>]*>', html, re.S)
        cls = re.search(r'class="([^"]*)"', bm.group(0)).group(1).split() if bm and 'class="' in bm.group(0) else []
        rep.check('G3', f'G3.visible.{sel}', bm and 'hidden' not in cls,
                  f'{sel} 버튼이 보임' + ('' if bm else ' (버튼 없음)') + (' (class에 hidden)' if 'hidden' in cls else ''), 'S3')

    # CONTENT_CONFIG = 02_content.json, 그리고 콘텐츠 규칙 재확인
    cfg = None
    try:
        cfg = extract_content_config(edit.get('A', []))
    except Exception as e:  # noqa: BLE001
        rep.check('G3', 'G3.content.parse', False, f'CONTENT_CONFIG 읽기 실패: {e}', 'S3')
    if cfg is not None:
        content_checks(cfg, rules, rep, 'G3', removed=removed)
        cpath = unit / '02_content.json'
        if cpath.exists():
            want_cfg = strip_refs(json.loads(cpath.read_text(encoding='utf-8')))
            rep.check('G3', 'G3.content.same', cfg == want_cfg, 'CONTENT_CONFIG = 02_content.json', 'S3')
        else:
            rep.check('G3', 'G3.content.same', False, '02_content.json 없음 (비교 불가)', 'S2')

    # ★N2 외부 도메인
    hosts_cfg = rules['external_hosts']
    declared = set()
    for line in spec.get('formula_or_source') or []:
        declared |= {urlparse(u).hostname for u in re.findall(r'https?://[^\s)"\']+', str(line))}
    allowed_hosts = set(hosts_cfg['base']) | declared
    texts = [html] + [p.read_text(encoding='utf-8', errors='ignore') for p in unit.glob('contents/*.js')]
    used = {h.lower() for t in texts for h in re.findall(r'https?://([A-Za-z0-9.-]+)', t)}
    bad = sorted(used - allowed_hosts)
    rep.check('G3', 'G3.hosts', not bad, '★N2 외부 도메인이 기본 + 신고 목록 안' + (f' (미신고: {", ".join(bad)})' if bad else ''), 'S3')

    # 기준 파일 해시
    bpath = unit / '.baseline.json'
    if bpath.exists():
        base = json.loads(bpath.read_text(encoding='utf-8'))['files']
        now = hash_tree()
        changed = sorted(k for k in set(base) | set(now) if base.get(k) != now.get(k))
        rep.check('G3', 'G3.baseline', not changed, 'docs/·templates/·scripts/ 변경 없음' + (f' (변경: {", ".join(changed)})' if changed else ''), '사용자')
    else:
        rep.check('G3', 'G3.baseline', False, '.baseline.json 없음 (오케스트레이터가 --baseline 실행)', '사용자')

    # 헤드리스 Chrome
    if render:
        shot = Path(tempfile.gettempdir()) / f'unit_{unit.name}.png'
        r = subprocess.run(['node', str(ROOT / 'scripts' / 'render_check.mjs'), str(page), str(shot)],
                           capture_output=True, text=True, timeout=60)
        try:
            res = json.loads(r.stdout.strip().split('\n')[-1])
        except (json.JSONDecodeError, IndexError):
            res = {'errors': [f'render_check 실행 실패: {r.stderr.strip()[:200]}'], 'screenshot': None}
        errs = res['errors']
        rep.check('G3', 'G3.console', not errs, f'콘솔 에러 {len(errs)}건' + ''.join(f'\n        - {e[:160]}' for e in errs[:5]), 'S3')
        if res.get('screenshot'):
            print(f'화면 캡처: {res["screenshot"]}')


# ─────────────────────────────────────────────────────────────
# GA 참고 그림 (SA: 참고만 하고 페이지에는 코드로 직접 그린다)
# ─────────────────────────────────────────────────────────────
def gate_ga(unit, rules, rep):
    d = read_json(unit / '03_reference.json', rep, 'GA', 'GA.exists', 'SA')
    if d is None:
        return
    items = d.get('items') or []
    skipped = str(d.get('skipped', '')).strip()
    rep.check('GA', 'GA.items', items or skipped,
              f'참고 그림 {len(items)}개' + (f' (생략 이유: {skipped})' if skipped else ''), 'SA')
    if items:
        notes = [x for x in d.get('style_notes') or [] if str(x).strip()]
        rep.check('GA', 'GA.style_notes', notes, f'코드로 그릴 모양·스타일 메모 {len(notes)}줄 (≥1)', 'SA')
    for i, it in enumerate(items):
        rep.check('GA', f'GA.items[{i}].source', str(it.get('source_url', '')).startswith('http'),
                  f'참고 출처 URL: {it.get("title")}', 'SA')
        f = str(it.get('file', ''))
        rep.check('GA', f'GA.items[{i}].outside', not f or not f.startswith(str(unit.relative_to(ROOT))),
                  f'★N2 참고 파일이 단원 폴더 밖(업로드 제외)에 있음: {f or "파일 없음"}', 'SA')


ASSET_RE = re.compile(r"""['"]([^'"\s]+\.(?:png|jpe?g|gif|webp|svg|mp3|wav|ogg|mp4|webm|js|json|csv))['"]""", re.I)


def asset_refs_check(unit, html, rep, tpl, spec):
    # 외부 파일은 contents/ 폴더 + 상대경로(./contents/…)로만, 01_spec.json media에 출처를 적은 것만 (제작 안내 PDF 2·3장)
    # 템플릿에 원래 있는 것(로고 등)과 http URL은 제외 (도메인은 G3.hosts에서 검사)
    refs = sorted({r for r in set(ASSET_RE.findall(html)) - set(ASSET_RE.findall(tpl)) if not r.startswith('http')})
    declared = {str(m.get('file', '')) for m in spec.get('media') or [] if str(m.get('source', '')).strip()}
    for r in refs:
        rel = r[2:] if r.startswith('./') else r
        ok = r.startswith('./contents/') and rel in declared and (unit / rel).is_file()
        rep.check('G3', f'G3.asset.{rel[:40]}', ok,
                  f'★N2 외부 파일 {r}: ./contents/ 상대경로 + 파일 있음 + 01_spec media에 출처', 'S3')
    rep.check('G3', 'G3.assets', True, f'외부 파일 참조 {len(refs)}개 (없으면 contents/ 폴더도 만들지 않음)', 'S3')


def names_check(unit, rules, rep):
    # 폴더·파일 이름은 영문+숫자+_만 (한글·공백은 FTP 업로드·실행 오류, 제작 안내 PDF 2장)
    rep.check('G3', 'G3.name.folder', re.match(rules['names']['unit_folder_regex'], unit.name),
              f'단원 폴더 이름: {unit.name}', '사용자')
    bad = [str(p.relative_to(unit)) for p in [unit / 'index.html', *(unit / 'contents').rglob('*')]
           if p.exists() and not re.match(rules['names']['file_regex'], p.name)]
    rep.check('G3', 'G3.name.files', not bad, '업로드 파일 이름이 영문·숫자·_ 만' + (f' (위반: {", ".join(bad)})' if bad else ''), 'S3')


def package(unit):
    """G4 승인 뒤 전달물: <폴더명>.zip 안에 <폴더명>/index.html (+ contents/)."""
    import zipfile
    out = unit / f'{unit.name}.zip'
    files = [unit / 'index.html', *sorted(p for p in (unit / 'contents').rglob('*') if p.is_file())]
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, f'{unit.name}/{f.relative_to(unit).as_posix()}')
    return out, len(files)


# ─────────────────────────────────────────────────────────────
GATES = {'G0': gate_g0, 'GR': gate_gr, 'G1': gate_g1, 'G2': gate_g2, 'GA': gate_ga, 'G3': gate_g3}


def main():
    ap = argparse.ArgumentParser(description='단원 폴더 판정 (G0, GR, G1, G2, GA, G3)')
    ap.add_argument('unit', help='단원 폴더 (예: units/phy/m2_light_reflection_refraction)')
    ap.add_argument('--gate', choices=['G0', 'GR', 'G1', 'G2', 'GA', 'G3', 'ALL'])
    ap.add_argument('--baseline', action='store_true', help='.baseline.json 기록')
    ap.add_argument('--no-render', action='store_true', help='G3에서 헤드리스 Chrome 검사 생략')
    ap.add_argument('--package', action='store_true', help='전달용 <폴더명>.zip 만들기 (index.html + contents/)')
    args = ap.parse_args()
    unit = Path(args.unit).resolve()

    if args.baseline:
        (unit / '.baseline.json').write_text(json.dumps(
            {'created': datetime.now().isoformat(timespec='seconds'), 'files': hash_tree()},
            ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'기록: {unit / ".baseline.json"}')
        return 0
    if args.package:
        out, n = package(unit)
        print(f'묶음: {out} (파일 {n}개)')
        return 0
    if not args.gate:
        ap.error('--gate, --baseline, --package 중 하나가 필요합니다')

    rules = load_rules()
    rep = Report()
    for g in (['G0', 'GR', 'G1', 'G2', 'GA', 'G3'] if args.gate == 'ALL' else [args.gate]):
        if g == 'G3':
            gate_g3(unit, rules, rep, render=not args.no_render)
        else:
            GATES[g](unit, rules, rep)

    print(f'단원: {unit.relative_to(ROOT) if unit.is_relative_to(ROOT) else unit}')
    for gate, cid, ok, msg, stage in rep.items:
        print(f'  {"✅" if ok else "❌"} [{cid}] {msg}')
    fails = rep.fails()
    ok_n = len(rep.items) - len(fails)
    if fails:
        back = min((f[4] for f in fails), key=STAGE_ORDER.index)
        print(f'결과: 통과 {ok_n} / 실패 {len(fails)} → 돌아갈 단계: {back}')
        return 1
    print(f'결과: 통과 {ok_n} / 실패 0 → 통과')
    return 0


if __name__ == '__main__':
    sys.exit(main())
