#!/usr/bin/env python3
"""사용자의 Chrome(로그인된 상태)을 AppleScript로 다루는 도구. SA 일러스트 단계에서 오케스트레이터가 쓴다.

준비: Chrome 메뉴 보기 > 개발자 > 'Apple Events의 자바스크립트 허용'을 켠다 (끝나면 꺼도 된다).

사용:
  python3 scripts/chrome.py check                 # JS 실행 가능 여부
  python3 scripts/chrome.py open <url>            # 새 탭에서 열기. 이후 명령은 **이 탭만** 대상 (탭 id를 기억)
  python3 scripts/chrome.py go <url>              # 기억한 탭을 다른 주소로 이동
  python3 scripts/chrome.py url                   # 기억한 탭 URL·제목
  python3 scripts/chrome.py text [최대글자]        # 기억한 탭 본문 텍스트
  python3 scripts/chrome.py images                # 기억한 탭 이미지 목록 (JSON: src, alt, 크기)
  python3 scripts/chrome.py links [필터]           # 기억한 탭 링크 목록 (JSON: href, text)
  python3 scripts/chrome.py js '<자바스크립트>'     # 기억한 탭에서 실행, 결과 출력
  python3 scripts/chrome.py download <url> <파일> [키=값 …]  # 로그인 쿠키로 받아 저장 (키=값이 있으면 폼 POST)
"""
import base64
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# 사용자가 다른 탭(원격 데스크톱 등)으로 옮겨도 그 탭을 건드리지 않도록, open으로 연 탭 id만 쓴다
STATE = Path(tempfile.gettempdir()) / 'tsherpa_chrome_tab.txt'


def osa(script):
    r = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr.strip())
    return r.stdout.rstrip('\n')


def tab_do(action):
    # 기억한 탭 id를 찾아 action(AppleScript 문장, 탭 변수 t, return으로 값 반환)을 실행
    if not STATE.exists():
        sys.exit('먼저 open <url>로 탭을 여세요')
    tid = STATE.read_text().strip()
    return osa(f'''tell application "Google Chrome"
  repeat with w in windows
    repeat with t in tabs of w
      if (id of t as text) is "{tid}" then
        {action}
      end if
    end repeat
  end repeat
  error "기억한 탭(id {tid})이 닫혔습니다. open으로 다시 여세요."
end tell''')


def js(code):
    return tab_do(f'return (execute t javascript {json.dumps(code, ensure_ascii=False)})')


def wait_loaded(timeout=20):
    end = time.time() + timeout
    time.sleep(0.5)
    while time.time() < end:
        if tab_do('return (loading of t)') == 'false':
            return
        time.sleep(0.5)


def main(a):
    if not a:
        sys.exit(__doc__)
    cmd = a[0]
    if cmd == 'check':
        print('ok' if js('1+1') == '2' else 'fail')
    elif cmd == 'open':
        tid = osa(f'tell application "Google Chrome" to tell front window to get id of (make new tab with properties {{URL:{json.dumps(a[1], ensure_ascii=False)}}})')
        STATE.write_text(tid)
        wait_loaded()
        print(tab_do('return (URL of t)'))
    elif cmd == 'go':
        tab_do(f'set URL of t to {json.dumps(a[1], ensure_ascii=False)}\n        return "ok"')
        wait_loaded()
        print(tab_do('return (URL of t)'))
    elif cmd == 'url':
        print(tab_do('return (URL of t) & " | " & (title of t)'))
    elif cmd == 'text':
        n = int(a[1]) if len(a) > 1 else 8000
        print(js(f'document.body.innerText.slice(0, {n})'))
    elif cmd == 'images':
        print(js('JSON.stringify([...document.images].filter(i=>i.naturalWidth>40)'
                 '.map(i=>({src:i.currentSrc||i.src,alt:i.alt,w:i.naturalWidth,h:i.naturalHeight})))'))
    elif cmd == 'links':
        f = json.dumps(a[1] if len(a) > 1 else '')
        print(js(f'JSON.stringify([...document.links].map(l=>({{href:l.href,text:l.innerText.trim().slice(0,80)}}))'
                 f'.filter(l=>(l.href+l.text).includes({f})))'))
    elif cmd == 'js':
        print(js(a[1]))
    elif cmd == 'download':
        url, out = a[1], a[2]
        form = dict(kv.split('=', 1) for kv in a[3:])
        opts = (f'{{credentials:"include",method:"POST",body:new URLSearchParams({json.dumps(form, ensure_ascii=False)})}}'
                if form else '{credentials:"include"}')
        # 비동기 fetch 결과를 window 변수에 담고 기다린다 (execute javascript는 Promise를 기다리지 않음)
        js(f'window.__dl=null;fetch({json.dumps(url)},{opts}).then(r=>{{if(!r.ok)throw r.status;window.__dlType=r.headers.get("content-type")+" | "+r.headers.get("content-disposition");return r.blob()}})'
           '.then(b=>new Promise(res=>{const f=new FileReader();f.onload=()=>res(f.result);f.readAsDataURL(b)}))'
           '.then(d=>window.__dl=d).catch(e=>window.__dl="ERR:"+e);"started"')
        for _ in range(120):
            v = js('window.__dl===null?"":window.__dl')
            if v:
                break
            time.sleep(0.5)
        else:
            sys.exit('download timeout')
        if v.startswith('ERR:'):
            sys.exit('download failed: ' + v)
        data = base64.b64decode(v.split(',', 1)[1])
        with open(out, 'wb') as fh:
            fh.write(data)
        js('window.__dl=null;""')
        print(f'saved {len(data)} bytes → {out} ({js("String(window.__dlType)")})')
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main(sys.argv[1:])
