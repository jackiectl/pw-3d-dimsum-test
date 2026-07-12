import * as THREE from 'three'
import Experience from '../Experience.js'

/**
 * The shop's name is letter geometry merged into the neonPink mesh, so it can't be
 * re-lettered by swapping a texture. Instead we split that mesh into connected
 * components, drop the ones that are the old letters, and hang a glowing plane
 * where they used to be.
 *
 * A letter component is thin on X (the sign's plane), short, and sits in the sign's
 * band of Y — which separates it from the sign's border tube (long on Z), the bowl
 * icon (tall) and the chopsticks (high up).
 */

const LETTER = {
    maxThickness: 0.06,     // letters are ~0.03 deep; the border tube is thicker
    maxSpan: 0.5,           // a glyph is ~0.3 wide; the border runs 4.65 along Z
    minY: 0.80,
    maxY: 1.50,
}

// where the old letters sat, in world space
const SIGN = {
    x: -2.465,              // just in front of the letters (camera looks from -X)
    y: 1.145,
    z: -0.965,
    width: 4.05,            // along Z
    height: 0.70,           // along Y
}

// The pole sign shows its barcode + "j zhou" twice over: once as letter geometry
// (jackieBlack) and once baked into the shop's misc texture. Hiding the geometry only
// uncovers the baked copy, so the replacement is an opaque face covering the whole
// pink plate.
const POLE = {
    x: -4.120,
    y: -0.371,
    z: -4.747,
    size: 0.709,            // matches the pink plate
}

export default class Signs
{
    constructor()
    {
        this.experience = new Experience()
        this.scene = this.experience.scene
        this.resources = this.experience.resources
        this.shop = this.experience.world.dimSumShop

        this.stripOldLetters(this.shop.neonPink)
        this.addShopSign()
        this.addPoleSign()
    }

    /**
     * Rebuild the mesh's geometry without the triangles belonging to letter-shaped
     * connected components.
     */
    stripOldLetters(mesh)
    {
        const geometry = mesh.geometry
        const position = geometry.attributes.position
        const index = geometry.index
        const triangles = index ? index.count / 3 : position.count / 3
        const vertexAt = i => (index ? index.getX(i) : i)

        // weld by quantised position so a glyph's own triangles join up but separate
        // glyphs stay separate
        const ids = new Map()
        const idOf = (v) =>
        {
            const key = `${Math.round(position.getX(v) * 1000)},${Math.round(position.getY(v) * 1000)},${Math.round(position.getZ(v) * 1000)}`
            if(!ids.has(key)) ids.set(key, ids.size)
            return ids.get(key)
        }

        const welded = new Array(triangles * 3)
        for(let i = 0; i < triangles * 3; i++)
        {
            welded[i] = idOf(vertexAt(i))
        }

        const parent = new Array(ids.size)
        for(let i = 0; i < parent.length; i++) parent[i] = i
        const find = (a) =>
        {
            while(parent[a] !== a) { parent[a] = parent[parent[a]]; a = parent[a] }
            return a
        }
        const union = (a, b) =>
        {
            a = find(a); b = find(b)
            if(a !== b) parent[a] = b
        }

        for(let t = 0; t < triangles; t++)
        {
            union(welded[t * 3], welded[t * 3 + 1])
            union(welded[t * 3 + 1], welded[t * 3 + 2])
        }

        // bounds per component, in WORLD space — the mesh carries a transform, so its
        // local coordinates are not the ones the thresholds below are expressed in
        mesh.updateWorldMatrix(true, false)
        const point = new THREE.Vector3()

        const bounds = new Map()
        for(let t = 0; t < triangles; t++)
        {
            const root = find(welded[t * 3])
            let b = bounds.get(root)
            if(!b)
            {
                b = { min: [Infinity, Infinity, Infinity], max: [-Infinity, -Infinity, -Infinity] }
                bounds.set(root, b)
            }
            for(let k = 0; k < 3; k++)
            {
                const v = vertexAt(t * 3 + k)
                point.fromBufferAttribute(position, v).applyMatrix4(mesh.matrixWorld)
                const p = [point.x, point.y, point.z]
                for(let a = 0; a < 3; a++)
                {
                    if(p[a] < b.min[a]) b.min[a] = p[a]
                    if(p[a] > b.max[a]) b.max[a] = p[a]
                }
            }
        }

        const isLetter = new Map()
        for(const [root, b] of bounds)
        {
            const size = [b.max[0] - b.min[0], b.max[1] - b.min[1], b.max[2] - b.min[2]]
            isLetter.set(root,
                size[0] < LETTER.maxThickness &&
                size[1] < LETTER.maxSpan &&
                size[2] < LETTER.maxSpan &&
                b.min[1] > LETTER.minY &&
                b.max[1] < LETTER.maxY
            )
        }

        const keep = []
        let dropped = 0
        for(let t = 0; t < triangles; t++)
        {
            if(isLetter.get(find(welded[t * 3])))
            {
                dropped++
                continue
            }
            keep.push(vertexAt(t * 3), vertexAt(t * 3 + 1), vertexAt(t * 3 + 2))
        }

        geometry.setIndex(keep)
        geometry.computeBoundingSphere()

        this.strippedTriangles = dropped
    }

    signMaterial(texture)
    {
        texture.colorSpace = THREE.SRGBColorSpace
        texture.flipY = true

        return new THREE.MeshBasicMaterial({
            map: texture,
            transparent: true,
            depthWrite: false,
            side: THREE.DoubleSide,
        })
    }

    addShopSign()
    {
        const geometry = new THREE.PlaneGeometry(SIGN.width, SIGN.height)
        geometry.rotateY(-Math.PI * 0.5)      // face -X, width running along Z

        this.shopSign = new THREE.Mesh(geometry, this.signMaterial(this.resources.items.signShopTexture))
        this.shopSign.position.set(SIGN.x, SIGN.y, SIGN.z)
        this.shopSign.name = 'shopSign'

        this.scene.add(this.shopSign)
    }

    addPoleSign()
    {
        this.shop.jackieBlack.visible = false

        const texture = this.resources.items.signPoleTexture
        texture.colorSpace = THREE.SRGBColorSpace

        // opaque: it has to hide the baked-in barcode and "j zhou" underneath
        const material = new THREE.MeshBasicMaterial({ map: texture })

        const geometry = new THREE.PlaneGeometry(POLE.size, POLE.size)
        geometry.rotateY(-Math.PI * 0.5)

        this.poleSign = new THREE.Mesh(geometry, material)
        this.poleSign.position.set(POLE.x, POLE.y, POLE.z)
        this.poleSign.name = 'poleSign'

        this.scene.add(this.poleSign)
    }
}
