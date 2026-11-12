// V 화면 점검: 단원 페이지를 헤드리스 Chrome에서 조작하며 상태별로 캡처한다.
// 사용: node scripts/scenario_shots.mjs <단원폴더> [출력폴더]
// 시나리오: <단원폴더>/scenarios.json (오케스트레이터가 V 단계에서 쓴다)
//   { "viewport": [1440, 900],
//     "steps": [ { "do": "radio", "name": "valveOpt", "value": "open" },
//                { "do": "select", "id": "liquidMixSelect", "index": 1 },
//                { "do": "option", "value": "parallel" },   // 템플릿 커스텀 드롭다운(#customSelectList li[data-value])
//                { "do": "click", "id": "pourBtn" },
//                { "do": "js", "code": "..." },
//                { "do": "wait", "ms": 3000 },
//                { "do": "viewport", "size": [844, 390], "touch": true },   // 폰 가로 (폭 < 768은 자동 터치)
//                { "do": "viewport", "size": [390, 844] },   // 모바일 세로 (⋮ 더보기: { "do": "click", "id": "moreMenuBtn" })
//                { "do": "fullscreen", "on": true },   // 전체화면 흉내 (헤드리스는 실제 전체화면 불가)
//                { "do": "shot", "name": "2_draining" } ] }
// 출력: {"errors": [...], "shots": [...]} (JSON 한 줄). 추가 설치 없이 DevTools 프로토콜만 쓴다.
import { spawn } from 'node:child_process';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { basename, join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const [unitDir, outArg] = process.argv.slice(2);
if (!unitDir) {
    console.error('사용: node scripts/scenario_shots.mjs <단원폴더> [출력폴더]');
    process.exit(2);
}
const scn = JSON.parse(readFileSync(join(unitDir, 'scenarios.json'), 'utf-8'));
const outDir = resolve(outArg || join(tmpdir(), 'unit_shots_' + basename(resolve(unitDir))));
mkdirSync(outDir, { recursive: true });
const [vw, vh] = scn.viewport || [1440, 900];
const CHROME = process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const profile = mkdtempSync(join(tmpdir(), 'unit-scn-'));
const chrome = spawn(CHROME, ['--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
    `--user-data-dir=${profile}`, '--remote-debugging-port=0', `--window-size=${vw},${vh}`, 'about:blank'],
    { stdio: ['ignore', 'ignore', 'pipe'] });
const errors = [], shots = [];
const finish = (code = 0) => {
    process.stdout.write(JSON.stringify({ errors, shots }) + '\n');
    chrome.kill('SIGKILL');
    try { rmSync(profile, { recursive: true, force: true }); } catch { }
    process.exit(code);
};
setTimeout(() => { errors.push('scenario_shots: 시간 초과 (120초)'); finish(1); }, 120000);

const bw = await new Promise(ok => {
    let b = '';
    chrome.stderr.on('data', d => { b += d; const m = b.match(/DevTools listening on (ws:\/\/\S+)/); if (m) ok(m[1]); });
});
const port = new URL(bw).port;
const page = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find(t => t.type === 'page');
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise(ok => ws.addEventListener('open', ok, { once: true }));
let id = 0;
const pend = new Map();
let loaded;
const loadedP = new Promise(ok => { loaded = ok; });
ws.addEventListener('message', ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pend.has(m.id)) { pend.get(m.id)(m.result || {}); pend.delete(m.id); return; }
    if (m.method === 'Runtime.exceptionThrown') {
        const d = m.params.exceptionDetails;
        errors.push(`exception: ${d.exception?.description?.split('\n')[0] || d.text} (line ${d.lineNumber + 1})`);
    } else if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') {
        errors.push(`console.error: ${m.params.args.map(a => a.value ?? a.description ?? '').join(' ')}`);
    } else if (m.method === 'Page.loadEventFired') loaded();
});
const send = (method, params = {}) => new Promise(ok => { const i = ++id; pend.set(i, ok); ws.send(JSON.stringify({ id: i, method, params })); });
const sleep = ms => new Promise(ok => setTimeout(ok, ms));
const run = async code => {
    const r = await send('Runtime.evaluate', { expression: code, returnByValue: true });
    if (r.exceptionDetails) errors.push(`step 실패: ${code.slice(0, 80)} → ${r.exceptionDetails.exception?.description?.split('\n')[0]}`);
    return r.result?.value;
};
const q = s => JSON.stringify(s);

await send('Runtime.enable');
await send('Page.enable');
await send('Page.navigate', { url: pathToFileURL(resolve(unitDir, 'index.html')).href });
await loadedP;
await sleep(2500);

for (const st of scn.steps || []) {
    if (st.do === 'radio') await run(`document.querySelector('input[name=${q(st.name)}][value=${q(st.value)}]').click()`);
    else if (st.do === 'select') await run(`(()=>{const s=document.getElementById(${q(st.id)}); s.selectedIndex=${st.index}; s.dispatchEvent(new Event('change',{bubbles:true})); s.dispatchEvent(new Event('input',{bubbles:true}))})()`);
    else if (st.do === 'option') await run(`document.querySelector('#customSelectList li[data-value=${q(st.value)}]').click()`);
    else if (st.do === 'click') await run(`document.getElementById(${q(st.id)}).click()`);
    else if (st.do === 'js') await run(st.code);
    else if (st.do === 'fullscreen') {
        // 헤드리스는 requestFullscreen 권한이 없어 #workspace:fullscreen 상태를 CSS로 흉내 낸다 (on: true/false)
        await run(`(()=>{const w=document.getElementById('workspace'); if(!w) throw new Error('#workspace 없음');
            const on=${!!st.on || st.on === undefined};
            Object.assign(w.style, on ? {position:'fixed', inset:'0', width:'100vw', height:'100vh', maxWidth:'none', margin:'0', zIndex:'50', backgroundColor:'#f8fafc', padding:'1rem', overflowY:'hidden'}
                                      : {position:'', inset:'', width:'', height:'', maxWidth:'', margin:'', zIndex:'', backgroundColor:'', padding:'', overflowY:''});
            window.dispatchEvent(new Event('resize'));})()`);
    }
    else if (st.do === 'wait') await sleep(st.ms || 1000);
    else if (st.do === 'viewport') {
        // 폰·태블릿은 터치로 흉내 낸다 (hover 없음 → 데스크톱 버튼 숨고 ⋮ 더보기 메뉴 표시). touch 생략 시 폭 < 768이면 터치
        const touch = st.touch ?? st.size[0] < 768;
        await send('Emulation.setTouchEmulationEnabled', { enabled: touch, maxTouchPoints: touch ? 5 : 1 });
        await send('Emulation.setDeviceMetricsOverride', { width: st.size[0], height: st.size[1], deviceScaleFactor: 1, mobile: touch });
    }
    else if (st.do === 'shot') {
        await sleep(300);
        const s = await send('Page.captureScreenshot', { format: 'png' });
        const f = join(outDir, `${st.name}.png`);
        writeFileSync(f, Buffer.from(s.data, 'base64'));
        shots.push(f);
    } else errors.push(`알 수 없는 step: ${JSON.stringify(st)}`);
}
finish(errors.length ? 1 : 0);
