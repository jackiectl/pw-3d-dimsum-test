/** Encode PNGs to .basis (the format the photo-wall screens use).
 *    node tools/png-to-basis.mjs <srcDir> <destDir>   */
import fs from 'fs'
import path from 'path'
import { PNG } from 'pngjs'
import { encodeToKTX2 } from 'ktx2-encoder'

const imageDecoder = async (buffer) => {
    const png = PNG.sync.read(Buffer.from(buffer))
    return { width: png.width, height: png.height, data: new Uint8Array(png.data) }
}

const [src, dest] = process.argv.slice(2)
fs.mkdirSync(dest, { recursive: true })

for (const name of fs.readdirSync(src).filter(f => f.endsWith('.png'))) {
    const basis = await encodeToKTX2(new Uint8Array(fs.readFileSync(path.join(src, name))), {
        isKTX2File: false,          // .basis container, not .ktx2
        isUASTC: false,
        qualityLevel: 255,
        compressionLevel: 2,
        generateMipmap: true,
        isPerceptual: true,
        isYFlip: false,
        imageDecoder,
    })
    const out = path.join(dest, name.replace('.png', '.basis'))
    fs.writeFileSync(out, basis)
    console.log(`${name} -> ${path.basename(out)} (${(basis.length / 1024).toFixed(0)}KB)`)
}
