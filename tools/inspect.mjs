/**
 * Introspect the live scene: dump each shop mesh's world-space bounding box and
 * orientation, so sign geometry can be located precisely without opening Blender.
 *
 *   node tools/inspect.mjs [nameFilterRegex]
 */
import http from 'http'
import fs from 'fs'
import path from 'path'
import puppeteer from 'puppeteer-core'

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
const ROOT = path.join(process.cwd(), 'dist')
const PORT = 8124

const server = http.createServer((req, res) => {
    const rel = decodeURIComponent(req.url.split('?')[0])
    let file = path.join(ROOT, rel === '/' ? 'index.html' : rel)
    if (!fs.existsSync(file) || fs.statSync(file).isDirectory()) file = path.join(ROOT, 'index.html')
    res.writeHead(200)
    fs.createReadStream(file).pipe(res)
})
await new Promise(r => server.listen(PORT, r))

const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: 'new',
    args: ['--no-sandbox', '--use-gl=angle', '--enable-webgl', '--ignore-gpu-blocklist', '--enable-unsafe-swiftshader'],
})
const page = await browser.newPage()
await page.setViewport({ width: 1280, height: 800 })
await page.goto(`http://localhost:${PORT}/`, { waitUntil: 'networkidle2', timeout: 120000 })
await page.waitForSelector('.start', { visible: true, timeout: 120000 })
await page.click('.start')
await new Promise(r => setTimeout(r, 6000))

const filter = process.argv[2] || '.'

const info = await page.evaluate((filterSrc) => {
    const THREE = window.experience.THREE || null
    const shop = window.experience.world.dimSumShop
    const re = new RegExp(filterSrc, 'i')
    const rows = []

    const model = shop.model
    model.traverse((child) => {
        if (!child.isMesh || !re.test(child.name)) return
        child.geometry.computeBoundingBox()
        const bb = child.geometry.boundingBox.clone()
        bb.applyMatrix4(child.matrixWorld)
        const size = { x: bb.max.x - bb.min.x, y: bb.max.y - bb.min.y, z: bb.max.z - bb.min.z }
        rows.push({
            name: child.name,
            min: { x: +bb.min.x.toFixed(3), y: +bb.min.y.toFixed(3), z: +bb.min.z.toFixed(3) },
            max: { x: +bb.max.x.toFixed(3), y: +bb.max.y.toFixed(3), z: +bb.max.z.toFixed(3) },
            size: { x: +size.x.toFixed(3), y: +size.y.toFixed(3), z: +size.z.toFixed(3) },
            centre: {
                x: +((bb.min.x + bb.max.x) / 2).toFixed(3),
                y: +((bb.min.y + bb.max.y) / 2).toFixed(3),
                z: +((bb.min.z + bb.max.z) / 2).toFixed(3),
            },
            verts: child.geometry.attributes.position.count,
        })
    })
    return rows
}, filter)

console.log(JSON.stringify(info, null, 1))
await browser.close()
server.close()
process.exit(0)
