import * as THREE from 'three'

/**
 * A bamboo steamer, built procedurally, to replace the ramen bowl the hologram used
 * to assemble itself into.
 *
 * The hologram only ever reads raw `position` attributes and concatenates them
 * (see Hologram.combineBuffer), so every transform has to be baked into the geometry
 * — a mesh's own position/rotation would simply be ignored.
 *
 * Dimensions match the bowl it replaces: roughly 107 x 78 x 92, sitting between
 * y = 60 and y = 138, so the existing scale and drop animation still work.
 */

const RADIUS = 46
const FLOOR = 62

function steam(x, z, turns, height, base)
{
    const points = []
    for(let i = 0; i <= 40; i++)
    {
        const k = i / 40
        points.push(new THREE.Vector3(
            x + 9 * Math.sin(k * Math.PI * turns),
            base + k * height,
            z + 9 * Math.cos(k * Math.PI * turns),
        ))
    }
    return new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points), 48, 2.2, 10, false)
}

function dumpling(x, z)
{
    const body = new THREE.SphereGeometry(17, 40, 24)
    body.scale(1, 0.85, 1)
    body.translate(x, 112, z)

    // the pleated top
    const top = new THREE.ConeGeometry(9, 14, 32, 6)
    top.translate(x, 128, z)

    return [body, top]
}

export default function buildDimSumModel()
{
    const parts = []

    // two stacked bamboo tiers, open so the mesh reads as a basket
    for(const base of [FLOOR, FLOOR + 27])
    {
        const tier = new THREE.CylinderGeometry(RADIUS, RADIUS, 26, 96, 10, true)
        tier.translate(0, base + 13, 0)
        parts.push(tier)

        const rim = new THREE.TorusGeometry(RADIUS, 2.6, 10, 96)
        rim.rotateX(Math.PI * 0.5)
        rim.translate(0, base + 26, 0)
        parts.push(rim)
    }

    // the weave: a few vertical slats so it doesn't read as a plain cylinder
    for(let i = 0; i < 16; i++)
    {
        const angle = (i / 16) * Math.PI * 2
        const slat = new THREE.BoxGeometry(2.5, 52, 3, 1, 12, 1)
        slat.translate(Math.cos(angle) * RADIUS, FLOOR + 27, Math.sin(angle) * RADIUS)
        parts.push(slat)
    }

    // dumplings in the top tier, poking above the rim
    for(const [x, z] of [[-24, -12], [24, -12], [0, 26]])
    {
        parts.push(...dumpling(x, z))
    }

    // steam
    parts.push(steam(-26, 0, 3, 44, 132))
    parts.push(steam(4, -18, 4, 52, 130))
    parts.push(steam(26, 14, 3, 40, 134))

    const group = new THREE.Group()
    for(const geometry of parts)
    {
        group.add(new THREE.Mesh(geometry))
    }
    return group
}
