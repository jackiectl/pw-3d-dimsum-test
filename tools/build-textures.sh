#!/usr/bin/env bash
#
# Repaint every screen in the shop from content/content.json and re-encode it.
#
#     npm run textures
#
# Edit content/content.json, run this, then `npm run dev`. Nothing else to touch:
# the pristine originals are decoded once and cached, each generator paints its
# text onto them, and the results go back out as KTX2 (the GPU-compressed format
# the site loads).
set -euo pipefail

cd "$(dirname "$0")/.."

PY=.venv/bin/python
ORIGINALS=../Ramen-Shop-main/static/textures/screens   # pristine, never written to
CACHE=.cache/textures
DECODED=$CACHE/decoded
PAINTED=$CACHE/painted
PHOTO=${PHOTO:-../Tianlang_Chen_CV_May/photo_ctlang_2.jpg}

mkdir -p "$DECODED" "$PAINTED"

# 1. decode the untouched originals once (cached — delete .cache to force a redo)
if [ ! -f "$DECODED/project1.png" ]; then
    echo "==> decoding pristine originals (one time)"
    node tools/ktx2-to-png.js \
        "$ORIGINALS/vendingMachineScreens" \
        "$ORIGINALS/aboutMeScreens" \
        "$ORIGINALS/arcadeScreens" \
        --out "$DECODED"
fi

# 2. paint this project's words onto them
echo "==> painting screens from content/content.json"
$PY tools/make-screens.py   "$DECODED" "$PAINTED"
$PY tools/make-projects.py  "$DECODED" "$PAINTED"
$PY tools/make-credits.py   "$DECODED" "$PAINTED"
$PY tools/make-bigscreen.py "$PHOTO"   "$PAINTED/bigScreenDefault.png"
$PY tools/make-signs.py     static/textures/signs
$PY tools/make-photowall.py static/textures/screens

# 3. encode back to KTX2, into the folders the site actually loads
echo "==> encoding to KTX2"
enc() {   # enc <dest-subdir> <file...>
    local dest="static/textures/screens/$1"; shift
    node tools/png-to-ktx2.mjs "$@" --out "$dest"
}

enc vendingMachineScreens \
    "$PAINTED/vendingMachineMenu.png" \
    "$PAINTED"/project[1-8].png
enc aboutMeScreens \
    "$PAINTED/bigScreenDefault.png" \
    "$PAINTED/bigScreenAbout.png" "$PAINTED/bigScreenSkills.png" "$PAINTED/bigScreenExperience.png" \
    "$PAINTED/bigScreenAboutMobile.png" "$PAINTED/bigScreenSkillsMobile.png" "$PAINTED/bigScreenExperienceMobile.png"
enc arcadeScreens \
    "$PAINTED/arcadeScreenCredits.png" "$PAINTED/arcadeScreenDefault.png"

echo
echo "done. upright previews to eyeball: $PAINTED/*_preview.png"
