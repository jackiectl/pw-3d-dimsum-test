/**
 * Load the built site in a headless browser, click START, and screenshot the 3D
 * scene. Without this there is no way to actually see what the geometry changes
 * look like.
 *
 *   node tools/shoot.mjs <out.png> [waitMs] [--click x,y]
 *
 * Serves ./dist itself, so run `npm run build` first.
 */
import http from 'http'
import fs from 'fs'
import path from 'path'
import puppeteer from 'puppeteer-core'

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
const ROOT = path.join(process.cwd(), 'dist')
const PORT = 8123

const TYPES = {
    '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css',
    '.ktx2': 'application/octet-stream', '.basis': 'application/octet-stream',
    '.gltf': 'model/gltf+json', '.bin': 'application/octet-stream',
    '.mp4': 'video/mp4', '.mp3': 'audio/mpeg', '.m4a': 'audio/mp4',
    '.png': 'image/png', '.jpg': 'image/jpeg', '.wasm': 'application/wasm',
    '.json': 'application/json', '.svg': 'image/svg+xml', '.ico': 'image/x-icon',
}

const server = http.createServer((req, res) => {
    const rel = decodeURIComponent(req.url.split('?')[0])
    let file = path.join(ROOT, rel === '/' ? 'index.html' : rel)
    if (!fs.existsSync(file) || fs.statSync(file).isDirectory()) file = path.join(ROOT, 'index.html')
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream' })
    fs.createReadStream(file).pipe(res)
})

const out = process.argv[2] || 'shot.png'
const settle = Number(process.argv[3] || 9000)
const clickArg = process.argv.indexOf('--click')

await new Promise(r => server.listen(PORT, r))

const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: 'new',
    args: ['--no-sandbox', '--use-gl=angle', '--enable-webgl', '--ignore-gpu-blocklist',
           '--enable-unsafe-swiftshader', '--window-size=1600,1000'],
})

const page = await browser.newPage()
await page.setViewport({ width: 1600, height: 1000 })

const errors = []
page.on('pageerror', e => errors.push(String(e)))
page.on('console', m => { if (m.type() === 'error') errors.push(m.text()) })

await page.goto(`http://localhost:${PORT}/`, { waitUntil: 'networkidle2', timeout: 120000 })

// wait for the loader to finish, then enter the shop
await page.waitForSelector('.start', { visible: true, timeout: 120000 })
await page.click('.start')
await new Promise(r => setTimeout(r, settle))

if (clickArg !== -1) {
    const [x, y] = process.argv[clickArg + 1].split(',').map(Number)
    await page.mouse.click(x, y)
    await new Promise(r => setTimeout(r, 3500))
}

await page.screenshot({ path: out })
console.log('wrote', out)
if (errors.length) {
    console.log('--- runtime errors ---')
    for (const e of [...new Set(errors)].slice(0, 12)) console.log('  ' + e)
} else {
    console.log('no runtime errors')
}

await browser.close()
server.close()
process.exit(0)
