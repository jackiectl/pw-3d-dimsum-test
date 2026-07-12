import * as THREE from 'three'
import Experience from '../Experience.js'

/**
 * Dim sum for the customer counter, built in code.
 *
 * The counter (the bar along the shop front, top at y = -1.76) originally
 * served ramen: two red bowls, one topped with a slab of noodles and a pair of
 * chopsticks leaning out. The noodles and leaning chopsticks are stripped from
 * the merged shop mesh, the bowls and soup stay, and procedurally built dim sum
 * takes over the free stretches of the bar: a two-tier bamboo steamer with har
 * gow, a lotus-leaf lo mai gai, and plates of char siu and cheung fun.
 *
 * The scene has no lights (everything is baked), so the props use basic
 * materials with the shading painted into vertex colours.
 */

const TABLE_Y = -1.76

// picked darker than they should read: the renderer's output encoding lifts them
const BAMBOO = 0xa87b3e
const BAMBOO_DARK = 0x7a5527
const WRAPPER = 0xeee2cc
const PLATE = 0xdde4ea
const CHAR_SIU = 0x9e2a1e
const CHAR_SIU_EDGE = 0xc65f28
const LOTUS = 0x5a7a3c
const LOTUS_DARK = 0x44602c

export default class CounterFood
{
    constructor()
    {
        this.experience = new Experience()
        this.scene = this.experience.scene
        this.shop = this.experience.world.dimSumShop
        this.signs = this.experience.world.signs

        this.stripNoodles()

        this.group = new THREE.Group()
        this.group.name = 'counterFood'

        this.group.add(this.steamerStack(-2.47, -1.45))
        this.group.add(this.loMaiGai(-2.42, -1.83))
        this.group.add(this.charSiuPlate(-2.50, 0.10))
        this.group.add(this.cheungFunPlate(-2.50, 0.52))

        this.scene.add(this.group)
    }

    stripNoodles()
    {
        const inside = (min, max, box) =>
            min[0] > box[0][0] && max[0] < box[0][1] &&
            min[1] > box[1][0] && max[1] < box[1][1] &&
            min[2] > box[2][0] && max[2] < box[2][1]

        this.removed = this.signs.stripComponents(this.shop.dimSumShop, (s, mn, mx) =>
            // the noodle slabs sitting on the front bowl (the wider soup disc
            // underneath spans past this box and stays)
            (s[1] < 0.06 && s[2] < 0.45 && inside(mn, mx, [[-2.70, -2.20], [-1.60, -1.49], [-0.90, -0.50]])) ||
            // the pair of chopsticks leaning out of that bowl
            (s[0] < 0.35 && s[2] < 0.15 && inside(mn, mx, [[-2.50, -2.05], [-1.75, -1.30], [-0.75, -0.54]])))
    }

    /** Paint fake lighting into vertex colours: tops bright, sides dimmer. */
    shaded(geometry, hex, floor = 0.68)
    {
        geometry.computeVertexNormals()
        const base = new THREE.Color(hex)
        const normal = geometry.attributes.normal
        const colors = new Float32Array(normal.count * 3)
        for(let i = 0; i < normal.count; i++)
        {
            const k = floor + (1 - floor) * Math.max(0, normal.getY(i))
            colors[i * 3] = base.r * k
            colors[i * 3 + 1] = base.g * k
            colors[i * 3 + 2] = base.b * k
        }
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))
        return new THREE.Mesh(geometry, CounterFood.material)
    }

    steamerTier(radius, height)
    {
        const tier = new THREE.Group()
        const wall = this.shaded(new THREE.CylinderGeometry(radius, radius, height, 24, 1, true), BAMBOO)
        wall.material.side = THREE.DoubleSide
        tier.add(wall)

        const rim = this.shaded(new THREE.TorusGeometry(radius, 0.012, 8, 24).rotateX(Math.PI / 2), BAMBOO_DARK)
        rim.position.y = height / 2
        tier.add(rim)
        return tier
    }

    dumpling(x, z, scale = 1)
    {
        const g = new THREE.Group()
        const body = this.shaded(new THREE.SphereGeometry(0.052 * scale, 16, 12).scale(1, 0.8, 1), WRAPPER)
        g.add(body)
        const top = this.shaded(new THREE.ConeGeometry(0.024 * scale, 0.035 * scale, 10, 1), WRAPPER)
        top.position.y = 0.045 * scale
        g.add(top)
        g.position.set(x, 0, z)
        return g
    }

    steamerStack(x, z)
    {
        const stack = new THREE.Group()
        const R = 0.21, H = 0.1

        const bottom = this.steamerTier(R, H)
        bottom.position.y = H / 2
        stack.add(bottom)

        const top = this.steamerTier(R, H)
        top.position.y = H * 1.5
        stack.add(top)

        // floor of the open top tier
        const mat = this.shaded(new THREE.CylinderGeometry(R - 0.015, R - 0.015, 0.012, 24), 0xd8c49a)
        mat.position.y = H * 1.2
        stack.add(mat)

        // har gow poking above the rim
        for(const [dx, dz] of [[-0.075, -0.045], [0.075, -0.045], [0, 0.085]])
        {
            const d = this.dumpling(dx, dz, 1.15)
            d.position.y = H * 1.2 + 0.062
            stack.add(d)
        }

        stack.position.set(x, TABLE_Y, z)
        return stack
    }

    loMaiGai(x, z)
    {
        const wrap = new THREE.Group()
        const body = this.shaded(new THREE.BoxGeometry(0.19, 0.09, 0.15), LOTUS)
        body.position.y = 0.045
        wrap.add(body)
        const strap = this.shaded(new THREE.BoxGeometry(0.2, 0.092, 0.035), LOTUS_DARK)
        strap.position.y = 0.045
        wrap.add(strap)
        wrap.position.set(x, TABLE_Y, z)
        wrap.rotation.y = 0.5
        return wrap
    }

    plate(radius)
    {
        const p = this.shaded(new THREE.CylinderGeometry(radius, radius * 0.8, 0.025, 24), PLATE, 0.8)
        p.position.y = 0.0125
        return p
    }

    charSiuPlate(x, z)
    {
        const g = new THREE.Group()
        g.add(this.plate(0.17))

        // a row of leaning slices
        for(let i = 0; i < 6; i++)
        {
            const slice = this.shaded(new THREE.BoxGeometry(0.17, 0.095, 0.026), CHAR_SIU)
            const glaze = this.shaded(new THREE.BoxGeometry(0.172, 0.02, 0.028), CHAR_SIU_EDGE)
            glaze.position.y = 0.04
            slice.add(glaze)
            slice.position.set(0, 0.075, -0.098 + i * 0.04)
            slice.rotation.x = -0.62
            g.add(slice)
        }

        g.position.set(x, TABLE_Y, z)
        g.rotation.y = -0.3
        return g
    }

    cheungFunPlate(x, z)
    {
        const g = new THREE.Group()
        g.add(this.plate(0.17))

        for(let i = 0; i < 3; i++)
        {
            const roll = this.shaded(
                new THREE.CapsuleGeometry
                    ? new THREE.CapsuleGeometry(0.034, 0.21, 4, 12).rotateZ(Math.PI / 2).scale(1, 0.82, 1)
                    : new THREE.CylinderGeometry(0.034, 0.034, 0.26, 12).rotateZ(Math.PI / 2).scale(1, 0.82, 1),
                WRAPPER, 0.72)
            roll.position.set(0, 0.05, -0.075 + i * 0.075)
            g.add(roll)
        }

        g.position.set(x, TABLE_Y, z)
        g.rotation.y = 0.25
        return g
    }
}

CounterFood.material = new THREE.MeshBasicMaterial({ vertexColors: true })
