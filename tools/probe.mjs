/**
 * Paint named meshes bright red and screenshot, so we can see which mesh is which
 * sign. Beats guessing from bounding boxes.
 *
 *   node tools/probe.mjs <out.png> <meshName[,meshName...]>
 */
import http from 'http'
import fs from 'fs'
import path from 'path'
import puppeteer from 'puppeteer-core'

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
const ROOT = path.join(process.cwd(), 'dist')
const PORT = 8125

const server = http.createServer((req, res) => {
    const rel = decodeURIComponent(req.url.split('?')[0])
    let file = path.join(ROOT, rel === '/' ? 'index.html' : rel)
    if (!fs.existsSync(file) || fs.statSync(file).isDirectory()) file = path.join(ROOT, 'index.html')
    res.writeHead(200)
    fs.createReadStream(file).pipe(res)
})
await new Promise(r => server.listen(PORT, r))

const out = process.argv[2]
const names = (process.argv[3] || '').split(',').filter(Boolean)

const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: 'new',
    args: ['--no-sandbox', '--use-gl=angle', '--enable-webgl', '--ignore-gpu-blocklist', '--enable-unsafe-swiftshader'],
})
const page = await browser.newPage()
await page.setViewport({ width: 1600, height: 1000 })
await page.goto(`http://localhost:${PORT}/`, { waitUntil: 'networkidle2', timeout: 120000 })
await page.waitForSelector('.start', { visible: true, timeout: 120000 })
await page.click('.start')
await new Promise(r => setTimeout(r, 7000))

const found = await page.evaluate((names) => {
    const shop = window.experience.world.dimSumShop
    const hits = []
    shop.model.traverse((child) => {
        if (child.isMesh && names.includes(child.name)) {
            child.material = child.material.clone()
            child.material.color?.setHex(0xff0000)
            child.material.map = null
            child.material.needsUpdate = true
            hits.push(child.name)
        }
    })
    return hits
}, names)

await new Promise(r => setTimeout(r, 1500))
await page.screenshot({ path: out })
console.log('highlighted:', found.join(', ') || '(none matched)')
await browser.close()
server.close()
process.exit(0)
