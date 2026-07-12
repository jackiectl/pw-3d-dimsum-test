/**
 * Screenshot the built site from several camera positions in one browser run.
 *
 *   node tools/views.mjs <outDir> <name:px,py,pz:lx,ly,lz> [...]
 *
 * A bare name of "default" keeps the entry camera. Also prints Signs.removed
 * and any page errors.
 */
import http from 'http'
import fs from 'fs'
import path from 'path'
import puppeteer from 'puppeteer-core'

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
const ROOT = path.join(process.cwd(), 'dist')
const PORT = 8133

const server = http.createServer((req, res) => {
    const rel = decodeURIComponent(req.url.split('?')[0])
    let file = path.join(ROOT, rel === '/' ? 'index.html' : rel)
    if (!fs.existsSync(file) || fs.statSync(file).isDirectory()) file = path.join(ROOT, 'index.html')
    res.writeHead(200)
    fs.createReadStream(file).pipe(res)
})
await new Promise(r => server.listen(PORT, r))

const outDir = process.argv[2]
fs.mkdirSync(outDir, { recursive: true })
const views = process.argv.slice(3).map(spec => {
    const [name, pos, look] = spec.split(':')
    return { name, pos: pos?.split(',').map(Number), look: look?.split(',').map(Number) }
})

const browser = await puppeteer.launch({
    executablePath: CHROME, headless: 'new',
    args: ['--no-sandbox', '--use-gl=angle', '--enable-webgl', '--ignore-gpu-blocklist', '--enable-unsafe-swiftshader'],
})
const page = await browser.newPage()
await page.setViewport({ width: 1600, height: 1000 })
const errors = []
page.on('pageerror', e => errors.push(String(e)))
page.on('console', m => { if (m.type() === 'error') errors.push(m.text()) })
await page.goto(`http://localhost:${PORT}/`, { waitUntil: 'networkidle2', timeout: 120000 })
await page.waitForSelector('.start', { visible: true, timeout: 120000 })
await page.click('.start')
await new Promise(r => setTimeout(r, 7000))

console.log('removed:', JSON.stringify(await page.evaluate(() => window.experience.world.signs.removed)))

for (const v of views) {
    if (v.pos) {
        await page.evaluate(({ pos, look }) => {
            const exp = window.experience
            exp.camera.update = () => {}
            exp.camera.instance.position.set(...pos)
            exp.camera.instance.lookAt(...look)
        }, v)
        await new Promise(r => setTimeout(r, 700))
    }
    await page.screenshot({ path: path.join(outDir, v.name + '.png') })
    console.log('shot', v.name)
}
console.log('page errors:', JSON.stringify(errors))
await browser.close(); server.close(); process.exit(0)
