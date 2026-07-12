/**
 * Break a merged mesh into connected components and print each one's world-space
 * bounding box. The neon sign is one merged geometry (letters + frame + the ramen
 * bowl icon), so this is how we find which triangles are the letters.
 *
 *   node tools/split.mjs <meshName>
 */
import http from 'http'
import fs from 'fs'
import path from 'path'
import puppeteer from 'puppeteer-core'

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
const ROOT = path.join(process.cwd(), 'dist')
const PORT = 8126

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
await page.goto(`http://localhost:${PORT}/`, { waitUntil: 'networkidle2', timeout: 120000 })
await page.waitForSelector('.start', { visible: true, timeout: 120000 })
await page.click('.start')
await new Promise(r => setTimeout(r, 6000))

const result = await page.evaluate((meshName) => {
    const shop = window.experience.world.dimSumShop
    let mesh = null
    shop.model.traverse(c => { if (c.isMesh && c.name === meshName) mesh = c })
    if (!mesh) return { error: 'not found' }

    const pos = mesh.geometry.attributes.position
    const idx = mesh.geometry.index
    const triCount = idx ? idx.count / 3 : pos.count / 3
    const vertOf = i => (idx ? idx.getX(i) : i)

    // union-find over vertices, welded by quantised position so separate letters
    // stay separate but a letter's own triangles join up
    const key = v => `${Math.round(pos.getX(v) * 1000)},${Math.round(pos.getY(v) * 1000)},${Math.round(pos.getZ(v) * 1000)}`
    const weld = new Map()
    for (let v = 0; v < pos.count; v++) {
        const k = key(v)
        if (!weld.has(k)) weld.set(k, weld.size)
    }
    const rep = v => weld.get(key(v))

    const parent = new Array(weld.size).fill(0).map((_, i) => i)
    const find = a => { while (parent[a] !== a) { parent[a] = parent[parent[a]]; a = parent[a] } return a }
    const union = (a, b) => { a = find(a); b = find(b); if (a !== b) parent[a] = b }

    for (let t = 0; t < triCount; t++) {
        const a = rep(vertOf(t * 3)), b = rep(vertOf(t * 3 + 1)), c = rep(vertOf(t * 3 + 2))
        union(a, b); union(b, c)
    }

    // group triangles by component, and record each component's world bbox
    const comps = new Map()
    const m = mesh.matrixWorld.elements
    const xf = (x, y, z) => [
        m[0] * x + m[4] * y + m[8] * z + m[12],
        m[1] * x + m[5] * y + m[9] * z + m[13],
        m[2] * x + m[6] * y + m[10] * z + m[14],
    ]

    for (let t = 0; t < triCount; t++) {
        const root = find(rep(vertOf(t * 3)))
        if (!comps.has(root)) comps.set(root, { tris: 0, min: [1e9, 1e9, 1e9], max: [-1e9, -1e9, -1e9] })
        const c = comps.get(root)
        c.tris++
        for (let k = 0; k < 3; k++) {
            const v = vertOf(t * 3 + k)
            const [wx, wy, wz] = xf(pos.getX(v), pos.getY(v), pos.getZ(v))
            c.min[0] = Math.min(c.min[0], wx); c.max[0] = Math.max(c.max[0], wx)
            c.min[1] = Math.min(c.min[1], wy); c.max[1] = Math.max(c.max[1], wy)
            c.min[2] = Math.min(c.min[2], wz); c.max[2] = Math.max(c.max[2], wz)
        }
    }

    const out = [...comps.values()]
        .map(c => ({
            tris: c.tris,
            min: c.min.map(v => +v.toFixed(2)),
            max: c.max.map(v => +v.toFixed(2)),
            size: c.max.map((v, i) => +(v - c.min[i]).toFixed(2)),
        }))
        .sort((a, b) => a.min[0] - b.min[0])

    return { total: triCount, components: out.length, out }
}, process.argv[2])

console.log(JSON.stringify(result, null, 1))
await browser.close()
server.close()
process.exit(0)
