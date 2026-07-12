/**
 * Encode PNGs back to KTX2 (ETC1S / BasisLZ) so the screens stay GPU-compressed —
 * a raw 2048² PNG costs 16 MB of VRAM, the KTX2 costs a quarter of that.
 *
 *   node tools/png-to-ktx2.mjs <file-or-dir> [...] --out <dir>
 *
 * isYFlip stays false: the PNGs came out of the decoder in stored order, so we
 * write them back in stored order.
 */
import fs from 'fs'
import path from 'path'
import { PNG } from 'pngjs'
import { encodeToKTX2 } from 'ktx2-encoder'

const imageDecoder = async (buffer) => {
    const png = PNG.sync.read(Buffer.from(buffer))
    return { width: png.width, height: png.height, data: new Uint8Array(png.data) }
}

const collect = (target, acc = []) => {
    if (fs.statSync(target).isDirectory()) {
        for (const name of fs.readdirSync(target)) collect(path.join(target, name), acc)
    } else if (target.endsWith('.png') && !target.includes('_preview')) {
        acc.push(target)
    }
    return acc
}

const args = process.argv.slice(2)
const cut = args.indexOf('--out')
const outDir = cut === -1 ? 'encoded' : args[cut + 1]
const inputs = (cut === -1 ? args : args.slice(0, cut)).flatMap(t => collect(t))

fs.mkdirSync(outDir, { recursive: true })

for (const file of inputs) {
    const png = new Uint8Array(fs.readFileSync(file))
    const ktx2 = await encodeToKTX2(png, {
        isKTX2File: true,
        isUASTC: false,          // ETC1S + BasisLZ, same as the original textures
        qualityLevel: 255,
        compressionLevel: 2,
        generateMipmap: true,
        isPerceptual: true,
        isSetKTX2SRGBTransferFunc: true,
        isYFlip: false,
        imageDecoder,
    })
    const out = path.join(outDir, path.basename(file).replace(/\.png$/, '.ktx2'))
    fs.writeFileSync(out, ktx2)
    console.log(`${path.basename(file)}  ${(png.length / 1024).toFixed(0)}KB png -> ${(ktx2.length / 1024).toFixed(0)}KB ktx2`)
}
