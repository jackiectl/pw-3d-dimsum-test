import * as THREE from 'three'
import Experience from '../Experience.js'

/**
 * Re-letters and re-badges the shop without touching the model file.
 *
 * The signage is letter/icon geometry merged into a handful of neon meshes, so it
 * can't be changed by swapping a texture. Instead each mesh is split into connected
 * components (union-find over welded vertices), the components that make up the old
 * artwork are dropped from the index, and a glowing plane is hung where they were.
 *
 * All the boxes below are in WORLD space — the meshes carry a transform, so their
 * local coordinates are not these.
 */

// "JESSE'S RAMEN": a row of thin glyphs on the sign face
const isShopLetter = (size, min, max) =>
    size[0] < 0.06 && size[1] < 0.5 && size[2] < 0.5 && min[1] > 0.80 && max[1] < 1.50

// the ramen bowl outline, sitting above the sign
const isBowl = (size, min) =>
    size[1] > 0.7 && size[1] < 1.1 && min[1] > 1.6 && min[1] < 2.0

// the chopsticks, higher again
const isChopstick = (size, min) => min[1] > 2.9 && size[2] > 1.0

// the tall sign on the shop's flank, reading RAMEN top to bottom (letters and frame
// are one component here, so the whole board goes and a plane replaces it)
const isVerticalSign = (size, min) => size[1] > 2.5 && size[2] < 0.25 && min[2] < -3.4

const SHOP_SIGN = { x: -2.465, y: 1.145, z: -0.965, width: 4.05, height: 0.70 }
const POLE_SIGN = { x: -4.120, y: -0.371, z: -4.747, size: 0.709 }
const FOOD_ICON = { x: -2.380, y: 2.640, z: 0.640, width: 2.05, height: 1.85 }
const CHINESE = { x: -1.700, y: -0.720, z: -0.924, width: 3.80, height: 0.62 }

// the signature painted on the ground; it read "Jesse Zhou / Management Consultant"
const FLOOR_SIG = { x: -5.029, y: -2.715, z: 1.482, width: 2.33, depth: 3.19 }

// world-space box tests for the unlit-copy strip
const inside = (min, max, box) =>
    min[0] > box[0][0] && max[0] < box[0][1] &&
    min[1] > box[1][0] && max[1] < box[1][1] &&
    min[2] > box[2][0] && max[2] < box[2][1]
const small = (size, cap) => size[0] < cap && size[1] < cap && size[2] < cap

export default class Signs
{
    constructor()
    {
        this.experience = new Experience()
        this.scene = this.experience.scene
        this.resources = this.experience.resources
        this.shop = this.experience.world.dimSumShop

        this.removed = {}

        // shop name
        this.removed.letters = this.stripComponents(this.shop.neonPink, isShopLetter)
        this.addPlane('shopSign', SHOP_SIGN, 'signShopTexture', { transparent: true })

        // ramen bowl -> dim sum steamer
        this.removed.bowl = this.stripComponents(this.shop.neonBlue, isBowl)
        this.removed.chopsticks = this.stripComponents(this.shop.neonPink, isChopstick)
        this.shop.neonYellow.visible = false        // the noodle strands
        this.addPlane('foodIcon', FOOD_ICON, 'signFoodTexture', { transparent: true })

        // the Chinese sign read "delicious noodle soup"
        this.shop.chinese.visible = false
        this.addPlane('chineseSign', CHINESE, 'signChineseTexture', { transparent: true })

        // the pole sign's barcode + "j zhou" exist twice, as geometry and baked into
        // the shop texture, so hiding the geometry only uncovers the baked copy — this
        // replacement is opaque and covers the whole plate
        this.shop.jackieBlack.visible = false
        this.addPlane('poleSign', { ...POLE_SIGN, width: POLE_SIGN.size, height: POLE_SIGN.size },
                      'signPoleTexture', { transparent: false })

        this.shop.jackieJoined.visible = false
        this.addFloorSignature()

        // the tall RAMEN board on the flank: pink and blue carry its frame and glow,
        // and neonGreen is nothing but its letters
        this.removed.verticalPink = this.stripComponents(this.shop.neonPink, isVerticalSign)
        this.removed.verticalBlue = this.stripComponents(this.shop.neonBlue, isVerticalSign)
        this.shop.neonGreen.visible = false
        this.addVerticalSign()

        // every neon element exists twice: the lit tubes above, and a dark
        // "switched-off" copy merged into the main shop mesh — strip those too
        this.removed.unlitCopies = this.stripComponents(this.shop.dimSumShop, (s, mn, mx) =>
            (small(s, 0.7) && inside(mn, mx, [[-2.70, -2.15], [ 0.70, 1.60], [-3.10,  1.15]])) ||  // JESSE'S RAMEN
            (small(s, 0.8) && inside(mn, mx, [[-3.35, -2.70], [ 0.90, 3.65], [-3.70, -3.30]])) ||  // vertical RAMEN
            (small(s, 0.7) && inside(mn, mx, [[-1.80, -1.55], [-1.05, -0.40], [-2.90,  1.05]])) ||  // old Chinese glyphs
            (small(s, 2.0) && inside(mn, mx, [[-2.50, -2.00], [ 1.70, 3.70], [-0.35,  2.10]])))    // bowl + chopsticks + noodles
    }

    addVerticalSign()
    {
        const texture = this.resources.items.signVerticalTexture
        texture.flipY = true
        texture.encoding = THREE.sRGBEncoding
        texture.needsUpdate = true

        // it lies in the XY plane, so PlaneGeometry needs no rotation
        const geometry = new THREE.PlaneGeometry(0.78, 2.72)

        this.verticalSign = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({
            map: texture,
            transparent: true,
            depthWrite: false,
            side: THREE.DoubleSide,
        }))
        this.verticalSign.position.set(-3.00, 2.275, -3.47)
        this.verticalSign.name = 'verticalSign'

        this.scene.add(this.verticalSign)
    }

    addFloorSignature()
    {
        const texture = this.resources.items.signFloorTexture
        texture.flipY = true
        texture.encoding = THREE.sRGBEncoding
        // the original signature reads along Z, the plane's long axis; the art is
        // drawn landscape, so turn it a quarter turn on the plane
        texture.center.set(0.5, 0.5)
        texture.rotation = Math.PI / 2
        texture.needsUpdate = true

        const geometry = new THREE.PlaneGeometry(FLOOR_SIG.width, FLOOR_SIG.depth)
        geometry.rotateX(-Math.PI * 0.5)      // lie flat on the ground

        this.floorSignature = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({
            map: texture,
            transparent: true,
            depthWrite: false,
        }))
        this.floorSignature.position.set(FLOOR_SIG.x, FLOOR_SIG.y, FLOOR_SIG.z)
        this.floorSignature.name = 'floorSignature'

        this.scene.add(this.floorSignature)
    }

    /**
     * Rebuild a mesh's index without the triangles whose connected component matches
     * `matches(size, min, max)`. Returns how many triangles were dropped.
     */
    stripComponents(mesh, matches)
    {
        const geometry = mesh.geometry
        const position = geometry.attributes.position
        const index = geometry.index
        const triangles = index ? index.count / 3 : position.count / 3
        const vertexAt = i => (index ? index.getX(i) : i)

        // weld by quantised position: a glyph's own triangles join up, separate glyphs
        // stay separate
        const ids = new Map()
        const welded = new Array(triangles * 3)
        for(let i = 0; i < triangles * 3; i++)
        {
            const v = vertexAt(i)
            const key = `${Math.round(position.getX(v) * 1000)},${Math.round(position.getY(v) * 1000)},${Math.round(position.getZ(v) * 1000)}`
            if(!ids.has(key)) ids.set(key, ids.size)
            welded[i] = ids.get(key)
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
                point.fromBufferAttribute(position, vertexAt(t * 3 + k)).applyMatrix4(mesh.matrixWorld)
                const p = [point.x, point.y, point.z]
                for(let a = 0; a < 3; a++)
                {
                    if(p[a] < b.min[a]) b.min[a] = p[a]
                    if(p[a] > b.max[a]) b.max[a] = p[a]
                }
            }
        }

        const doomed = new Set()
        for(const [root, b] of bounds)
        {
            const size = [b.max[0] - b.min[0], b.max[1] - b.min[1], b.max[2] - b.min[2]]
            if(matches(size, b.min, b.max)) doomed.add(root)
        }

        const keep = []
        let dropped = 0
        for(let t = 0; t < triangles; t++)
        {
            if(doomed.has(find(welded[t * 3])))
            {
                dropped++
                continue
            }
            keep.push(vertexAt(t * 3), vertexAt(t * 3 + 1), vertexAt(t * 3 + 2))
        }

        geometry.setIndex(keep)
        geometry.computeBoundingSphere()
        return dropped
    }

    addPlane(name, box, textureName, { transparent })
    {
        const texture = this.resources.items[textureName]

        // Resources loads every 'texture' with flipY = false to match glTF's UV
        // convention; these planes use PlaneGeometry's own UVs, which want it back on.
        texture.flipY = true
        texture.encoding = THREE.sRGBEncoding
        texture.needsUpdate = true

        const material = transparent
            ? new THREE.MeshBasicMaterial({ map: texture, transparent: true, depthWrite: false, side: THREE.DoubleSide })
            : new THREE.MeshBasicMaterial({ map: texture })

        const geometry = new THREE.PlaneGeometry(box.width, box.height)
        geometry.rotateY(-Math.PI * 0.5)      // face -X, width running along Z

        const mesh = new THREE.Mesh(geometry, material)
        mesh.position.set(box.x, box.y, box.z)
        mesh.name = name

        this.scene.add(mesh)
        this[name] = mesh
        return mesh
    }
}
