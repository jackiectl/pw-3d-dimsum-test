# Changing the words in the shop

Everything written anywhere in the 3D scene lives in [`content.json`](content.json).
Edit that file, then:

```bash
npm run textures     # repaints every screen from content.json, re-encodes to KTX2
npm run dev          # look at it
```

No code changes, no coordinates, no image editor.

## Why a build step at all?

The scene has no text objects. Every word is either **pixels baked into a texture**
(all the screens) or **3D letter geometry** (the neon signs). Neither can be changed
at runtime the way a web page's DOM can. So `npm run textures` is what a browser does
for HTML — it lays the text out and rasterises it — just ahead of time instead of on
every page load.

The pipeline:

```
content.json
     |
     v
tools/make-*.py        paint the text onto the pristine original screens
     |                 (originals are decoded once and cached in .cache/)
     v
tools/png-to-ktx2.mjs  compress to the GPU format the site loads
     |
     v
static/textures/       <- what Three.js reads at runtime
```

## What maps to what

| in `content.json` | where it shows up |
|---|---|
| `shop.name` | the big neon sign over the shop |
| `shop.chineseSign` | the green Chinese neon under the awning |
| `shop.verticalSign` | the tall sign on the shop's flank |
| `shop.floorName1/2`, `floorRole` | the signature painted on the ground |
| `shop.poleLabel` | the barcode sign on the lamppost |
| `bigScreen.arcTagline` | the arc of text around your portrait |
| `about`, `experience`, `skills` | the three big screens (and their mobile versions) |
| `projects[]` | the vending machine: menu tiles + the 8 detail pages |
| `credits` | the arcade cabinet |

## Limits

The layouts are fixed boxes, so text has to fit roughly the same space as what's
there now. Long text wraps and can overrun its card; short text leaves a gap. After
a big change, eyeball `.cache/textures/painted/*_preview.png` (upright renders of
every screen) before shipping.

`npm run shots` renders the actual 3D scene from five angles into `.cache/shots/` if
you want to check a sign in place.

## Adding a project

Append an entry to `projects[]` in `content.json` — but note the vending machine has
exactly **8 slots** baked into its 3D model, so a 9th project would need a slot to be
freed, not just added here.
