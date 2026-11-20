#!/usr/bin/env python3
"""Generate VYRA's native Lottie splash from the approved glass monogram."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import base64, io, json, math, sys

logo_path, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
out_dir.mkdir(parents=True, exist_ok=True)
W, H, FPS, FRAMES = 432, 768, 60, 480

def png_bytes(image):
    stream = io.BytesIO()
    image.save(stream, format="PNG", optimize=True)
    return stream.getvalue()

def embedded_asset(name, image):
    payload = base64.b64encode(png_bytes(image)).decode("ascii")
    return {"id": name, "w": image.width, "h": image.height, "u": "",
            "p": "data:image/png;base64," + payload, "e": 1}

def static(value):
    return {"a": 0, "k": value}

def frame(t, start, end=None, hold=False):
    item = {"t": t, "s": start}
    if end is not None:
        item["e"] = end
    if hold:
        item["h"] = 1
    else:
        item["o"] = {"x": 0.33, "y": 0.0}
        item["i"] = {"x": 0.67, "y": 1.0}
    return item

def animated(*frames):
    return {"a": 1, "k": list(frames)}

def transform(position, scale=(100,100,100), opacity=100, rotation=0, anchor=(0,0,0)):
    return {
        "o": opacity if isinstance(opacity, dict) else static(opacity),
        "r": rotation if isinstance(rotation, dict) else static(rotation),
        "p": position if isinstance(position, dict) else static(position),
        "a": static(anchor),
        "s": scale if isinstance(scale, dict) else static(scale),
    }

def image_layer(index, name, width, height, position, scale=None, opacity=None, rotation=None):
    return {
        "ddd": 0, "ind": index, "ty": 2, "nm": name, "refId": name, "sr": 1,
        "ks": transform(position, scale or (100,100,100),
                        opacity if opacity is not None else 100,
                        rotation if rotation is not None else 0,
                        (width/2, height/2, 0)),
        "ao": 0, "ip": 0, "op": FRAMES, "st": 0, "bm": 0,
    }

# Convert the supplied dark chrome artwork to screen-blended transparency:
# dark glass stays subtle while its silver highlights remain visible on black.
source = Image.open(logo_path).convert("RGB").resize((350,350), Image.Resampling.LANCZOS)
logo = Image.new("RGBA", source.size)
logo.putdata([(255,255,255,max(r,g,b)) for r,g,b in source.getdata()])

# A thin glass ring with a travelling silver highlight.
ring = Image.new("RGBA", (380,380), (0,0,0,0))
draw = ImageDraw.Draw(ring)
draw.ellipse((4,4,376,376), outline=(220,225,235,35), width=2)
for i in range(48):
    angle = math.radians(250 + i*0.55)
    x, y = 190 + 186*math.cos(angle), 190 + 186*math.sin(angle)
    alpha = int(10 + 245*(i/48)**2)
    draw.ellipse((x-1.5,y-1.5,x+1.5,y+1.5), fill=(245,248,255,alpha))
ring = ring.filter(ImageFilter.GaussianBlur(0.45))

# Low-contrast radial glow that gently breathes behind the monogram.
glow = Image.new("RGBA", (420,420), (0,0,0,0))
pixels = glow.load()
for y in range(420):
    for x in range(420):
        distance = math.sqrt((x-210)**2 + (y-210)**2) / 210
        alpha = int(24 * max(0,1-distance)**2)
        pixels[x,y] = (205,212,225,alpha)
glow = glow.filter(ImageFilter.GaussianBlur(12))

# Silver VYRA wordmark, with the same wide tracking as the supplied HTML design.
wordmark = Image.new("RGBA", (360,84), (0,0,0,0))
mask = Image.new("L", (360,84), 0)
try:
    font = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-ExtraLight.otf", 52)
except OSError:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf", 52)
draw = ImageDraw.Draw(mask)
letters, spacing = "VYRA", 24
width = sum(draw.textlength(ch,font=font) for ch in letters) + spacing*(len(letters)-1)
x = (360-width)/2
for letter in letters:
    draw.text((x,6), letter, font=font, fill=255)
    x += draw.textlength(letter,font=font) + spacing
word_pixels, mask_pixels = wordmark.load(), mask.load()
for y in range(84):
    shade = int(255 - 95*(y/83))
    for x in range(360):
        if mask_pixels[x,y]:
            word_pixels[x,y] = (shade,shade,min(255,shade+4),mask_pixels[x,y])

track = Image.new("RGBA", (120,4), (0,0,0,0))
ImageDraw.Draw(track).rounded_rectangle((0,1,119,2), radius=1, fill=(235,238,245,42))
shine = Image.new("RGBA", (42,4), (0,0,0,0))
ImageDraw.Draw(shine).rounded_rectangle((0,1,41,2), radius=1, fill=(250,252,255,245))

assets = [
    embedded_asset("vyra_logo", logo),
    embedded_asset("vyra_ring", ring),
    embedded_asset("vyra_glow", glow),
    embedded_asset("vyra_wordmark", wordmark),
    embedded_asset("vyra_track", track),
    embedded_asset("vyra_shine", shine),
]

layers = [
    image_layer(1, "vyra_glow", 420,420, [216,320,0],
        scale=animated(frame(0,[100,100,100],[104,104,100]),
                       frame(180,[104,104,100],[100,100,100]),
                       frame(360,[100,100,100],[104,104,100]),
                       frame(480,[104,104,100])),
        opacity=animated(frame(0,[45],[60]), frame(180,[60],[45]),
                         frame(360,[45],[60]), frame(480,[60]))),
    image_layer(2, "vyra_ring", 380,380, [216,320,0],
        rotation=animated(frame(0,[0],[360]), frame(480,[360])),
        opacity=animated(frame(0,[0],[0],True), frame(125,[0],[100]),
                         frame(155,[100],[100],True), frame(480,[100]))),
    image_layer(3, "vyra_logo", 350,350,
        animated(frame(0,[216,-360,0],[216,320,0]),
                 frame(128,[216,320,0],[216,286,0]),
                 frame(158,[216,286,0],[216,320,0]),
                 frame(205,[216,320,0],[216,309,0]),
                 frame(235,[216,309,0],[216,320,0]),
                 frame(270,[216,320,0],[216,317,0]),
                 frame(295,[216,317,0],[216,320,0]),
                 frame(480,[216,320,0])),
        scale=animated(frame(0,[100,100,100],[100,100,100]),
                       frame(128,[100,100,100],[107,91,100]),
                       frame(158,[107,91,100],[98,103,100]),
                       frame(205,[98,103,100],[103,97,100]),
                       frame(235,[103,97,100],[100,100,100]),
                       frame(480,[100,100,100]))),
    image_layer(4, "vyra_wordmark", 360,84, [216,552,0],
        opacity=animated(frame(0,[0],[0],True), frame(145,[0],[100]),
                         frame(170,[100],[100],True), frame(480,[100]))),
    image_layer(5, "vyra_track", 120,4, [216,684,0],
        opacity=animated(frame(0,[0],[0],True), frame(162,[0],[100]),
                         frame(190,[100],[100],True), frame(480,[100]))),
    image_layer(6, "vyra_shine", 42,4,
        animated(frame(0,[155,684,0],[155,684,0],True),
                 frame(190,[155,684,0],[277,684,0]),
                 frame(298,[277,684,0],[155,684,0]),
                 frame(406,[155,684,0],[277,684,0]),
                 frame(480,[277,684,0])),
        opacity=animated(frame(0,[0],[0],True), frame(162,[0],[100]),
                         frame(190,[100],[100],True), frame(480,[100]))),
]

composition = {
    "v": "5.12.1", "fr": FPS, "ip": 0, "op": FRAMES, "w": W, "h": H,
    "nm": "VYRA Liquid Glass Splash", "ddd": 0, "bg": "#000000",
    "assets": assets, "layers": layers,
}
serialized = json.dumps(composition, separators=(",",":"), ensure_ascii=False)
validated = json.loads(serialized)
assert len(validated["layers"]) == 6 and len(validated["assets"]) == 6
assert all(a["p"].startswith("data:image/png;base64,") for a in validated["assets"])
for filename in ("morphe_startup_animation.json", "morphe_startup_animation_play.json"):
    (out_dir/filename).write_text(serialized, encoding="utf-8")
print(f"Generated VYRA Lottie splash: {len(serialized):,} chars, 6 layers, 6 embedded images.")
