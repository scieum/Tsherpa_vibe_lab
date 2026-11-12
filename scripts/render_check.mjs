// 헤드리스 Chrome으로 단원 페이지를 열어 콘솔 에러를 세고 화면을 캡처한다.
// 사용: node scripts/render_check.mjs <index.html> <screenshot.png>
// 출력: {"errors": [...], "screenshot": "..."} (JSON 한 줄)
// Chrome 경로는 CHROME_PATH 환경변수로 바꿀 수 있다. 추가 설치 없이 DevTools 프로토콜만 쓴다.
import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const [htmlPath, shotPath] = process.argv.slice(2);
if (!htmlPath || !shotPath) {
    console.error('사용: node scripts/render_check.mjs <index.html> <screenshot.png>');
    process.exit(2);
}
const CHROME = process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const WAIT_MS = 4000;
const profile = mkdtempSync(join(tmpdir(), 'unit-render-'));

const chrome = spawn(CHROME, [
    '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
    `--user-data-dir=${profile}`, '--remote-debugging-port=0', '--window-size=1440,900', 'about:blank'
], { stdio: ['ignore', 'ignore', 'pipe'] });

const finish = (result, code = 0) => {
    process.stdout.write(JSON.stringify(result) + '\n');
    chrome.kill('SIGKILL');
    try { rmSync(profile, { recursive: true, force: true }); } catch { }
    process.exit(code);
};
const timer = setTimeout(() => finish({ errors: ['render_check: 시간 초과 (30초)'], screenshot: null }, 1), 30000);

const browserWs = await new Promise((ok, fail) => {
    let buf = '';
    chrome.stderr.on('data', d => {
        buf += d;
        const m = buf.match(/DevTools listening on (ws:\/\/\S+)/);
        if (m) ok(m[1]);
    });
    chrome.on('exit', () => fail(new Error('Chrome이 종료됨')));
}).catch(e => finish({ errors: [`render_check: Chrome 실행 실패 (${e.message})`], screenshot: null }, 1));

const port = new URL(browserWs).port;
const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
const page = targets.find(t => t.type === 'page');
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise(ok => ws.addEventListener('open', ok, { once: true }));

let nextId = 0;
const pending = new Map();
const errors = [];
let loaded = null;
const loadedPromise = new Promise(ok => { loaded = ok; });

ws.addEventListener('message', ev => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg.result || {}); pending.delete(msg.id); return; }
    if (msg.method === 'Runtime.exceptionThrown') {
        const d = msg.params.exceptionDetails;
        errors.push(`exception: ${d.exception?.description?.split('\n')[0] || d.text} (line ${d.lineNumber + 1})`);
    } else if (msg.method === 'Runtime.consoleAPICalled' && msg.params.type === 'error') {
        errors.push(`console.error: ${msg.params.args.map(a => a.value ?? a.description ?? '').join(' ')}`);
    } else if (msg.method === 'Log.entryAdded' && msg.params.entry.level === 'error') {
        const e = msg.params.entry;
        errors.push(`${e.source}: ${e.text}${e.url ? ` (${e.url})` : ''}`);
    } else if (msg.method === 'Page.loadEventFired') {
        loaded();
    }
});
const send = (method, params = {}) => new Promise(ok => {
    const id = ++nextId;
    pending.set(id, ok);
    ws.send(JSON.stringify({ id, method, params }));
});

await send('Runtime.enable');
await send('Log.enable');
await send('Page.enable');
await send('Page.navigate', { url: pathToFileURL(resolve(htmlPath)).href });
await loadedPromise;
await new Promise(ok => setTimeout(ok, WAIT_MS));

const shot = await send('Page.captureScreenshot', { format: 'png' });
writeFileSync(shotPath, Buffer.from(shot.data, 'base64'));
clearTimeout(timer);
finish({ errors, screenshot: resolve(shotPath) });
