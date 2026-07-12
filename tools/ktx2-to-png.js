/**
 * Decode KTX2 (BasisLZ) textures to PNG using the Basis transcoder that ships
 * with three.js in this project's node_modules. No global tooling required.
 *
 *   node tools/ktx2-to-png.js <file-or-dir> [...] --out <dir>
 */
const fs = require('fs')
const path = require('path')
const { PNG } = require('pngjs')

const BASIS_DIR = path.join(__dirname, '..', 'node_modules', 'three', 'examples', 'js', 'libs', 'basis')
const wasmBinary = fs.readFileSync(path.join(BASIS_DIR, 'basis_transcoder.wasm'))

// The emscripten glue clobbers module.exports under CommonJS, so evaluate it in
// a wrapper and grab the factory directly.
const BASIS = new Function(
    'module', 'exports', '__filename', '__dirname',
    fs.readFileSync(path.join(BASIS_DIR, 'basis_transcoder.js'), 'utf8') + '\n;return BASIS;'
)({}, {}, path.join(BASIS_DIR, 'basis_transcoder.js'), BASIS_DIR)

const cTFRGBA32 = 13

function collect(target, acc) {
    const stat = fs.statSync(target)
    if (stat.isDirectory()) {
        for (const name of fs.readdirSync(target)) collect(path.join(target, name), acc)
    } else if (target.toLowerCase().endsWith('.ktx2')) {
        acc.push(target)
    }
    return acc
}

async function main() {
    const args = process.argv.slice(2)
    const outIdx = args.indexOf('--out')
    const outDir = outIdx === -1 ? 'decoded' : args[outIdx + 1]
    const inputs = (outIdx === -1 ? args : args.slice(0, outIdx)).flatMap(t => collect(t, []))

    if (!inputs.length) {
        console.error('no .ktx2 files found')
        process.exit(1)
    }

    const basis = await BASIS({ wasmBinary })
    basis.initializeBasis()

    fs.mkdirSync(outDir, { recursive: true })

    for (const file of inputs) {
        const ktx2 = new basis.KTX2File(new Uint8Array(fs.readFileSync(file)))

        if (!ktx2.isValid()) {
            console.error(`invalid: ${file}`)
            ktx2.delete()
            continue
        }

        const width = ktx2.getWidth()
        const height = ktx2.getHeight()

        if (!ktx2.startTranscoding()) {
            console.error(`transcode start failed: ${file}`)
            ktx2.close()
            ktx2.delete()
            continue
        }

        const size = ktx2.getImageTranscodedSizeInBytes(0, 0, 0, cTFRGBA32)
        const dst = new Uint8Array(size)

        if (!ktx2.transcodeImage(dst, 0, 0, 0, cTFRGBA32, 0, -1, -1)) {
            console.error(`transcode failed: ${file}`)
            ktx2.close()
            ktx2.delete()
            continue
        }

        ktx2.close()
        ktx2.delete()

        const png = new PNG({ width, height })
        png.data = Buffer.from(dst.buffer, dst.byteOffset, size)

        const out = path.join(outDir, path.basename(file).replace(/\.ktx2$/i, '.png'))
        fs.writeFileSync(out, PNG.sync.write(png))
        console.log(`${path.basename(file)}  ${width}x${height}  ->  ${out}`)
    }
}

main().catch(err => { console.error(err); process.exit(1) })
