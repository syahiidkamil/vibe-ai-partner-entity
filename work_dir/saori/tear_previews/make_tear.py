"""Saori's tear-sprite generator — a translucent glassy droplet, drawn from code.

The look: mostly clear water (skin shows through the body), a bright catch-light
rim, a small specular highlight + a sparkle, and light pooling brighter toward the
round bottom. Supersampled (SS x) then downscaled with LANCZOS for clean edges.
Tweak params, re-run, until it's right.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFilter, ImageChops

SS = 8
HERE = os.path.dirname(os.path.abspath(__file__))


def _clamp01(x):
    return max(0.01, min(0.99, x))


def make_tear(W, H, cx, cy, R, apex_y,
              tint_top=(236, 245, 252), tint_bot=(206, 228, 248),
              alpha_body=46, alpha_max=224):
    """Bulb = circle (cx,cy,R); apex = point (cx,apex_y); sides are true tangents."""
    w, h = W * SS, H * SS
    L = cy - apex_y
    theta = math.acos(_clamp01(R / L))
    a_r, a_l = math.pi / 2 - theta, math.pi / 2 + theta
    pts = [(cx * SS, apex_y * SS)]
    n = 300
    start, end = a_r, a_l - 2 * math.pi
    for i in range(n + 1):
        t = start + (end - start) * i / n
        pts.append(((cx + R * math.cos(t)) * SS, (cy - R * math.sin(t)) * SS))

    M = Image.new('L', (w, h), 0)
    ImageDraw.Draw(M).polygon(pts, fill=255)
    M = M.filter(ImageFilter.GaussianBlur(SS * 0.5))
    Mclip = M.point(lambda v: 255 if v > 4 else 0)

    # bright inner rim = shape minus a blurred copy (edge glow of a water bead)
    rim = ImageChops.subtract(M, M.filter(ImageFilter.GaussianBlur(SS * 3.2)))
    rim = rim.filter(ImageFilter.GaussianBlur(SS * 0.8)).point(lambda v: min(255, int(v * 2.3)))

    # light pools brighter toward the bottom of the droplet
    pcol = Image.new('L', (1, h))
    for y in range(h):
        pcol.putpixel((0, y), int(255 * (y / (h - 1)) ** 1.7))
    pool = ImageChops.multiply(pcol.resize((w, h)), Mclip).point(lambda v: int(v * 0.55))

    # specular highlight (upper-left) + a tiny sparkle (upper-right)
    hi = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(hi)
    hx, hy, rx, ry = cx - R * 0.30, cy - R * 0.55, R * 0.20, R * 0.32
    d.ellipse([(hx - rx) * SS, (hy - ry) * SS, (hx + rx) * SS, (hy + ry) * SS], fill=255)
    hi = hi.filter(ImageFilter.GaussianBlur(SS * 1.2))
    sp = Image.new('L', (w, h), 0)
    sx, sy, sr = cx + R * 0.20, cy - R * 0.10, R * 0.07
    ImageDraw.Draw(sp).ellipse([(sx - sr) * SS, (sy - sr) * SS, (sx + sr) * SS, (sy + sr) * SS], fill=255)
    sp = sp.filter(ImageFilter.GaussianBlur(SS * 0.5))
    hi = ImageChops.add(hi, sp)

    # alpha = faint clear body + rim + pooled bottom + highlights, clipped to shape
    a = M.point(lambda v: alpha_body if v > 8 else 0)
    a = ImageChops.add(a, rim.point(lambda v: int(v * 0.60)))
    a = ImageChops.add(a, pool)
    a = ImageChops.add(a, hi.point(lambda v: int(v * 0.90)))
    a = ImageChops.multiply(a, Mclip).point(lambda v: min(v, alpha_max))

    # body: cool near-white, a touch bluer at the bottom
    bcol = Image.new('RGB', (1, h))
    for y in range(h):
        f = y / (h - 1)
        bcol.putpixel((0, y), tuple(int(tint_top[k] + (tint_bot[k] - tint_top[k]) * f) for k in range(3)))
    body = bcol.resize((w, h))
    white = Image.new('RGB', (w, h), (255, 255, 255))
    bright = ImageChops.add(rim.point(lambda v: int(v * 0.85)), hi)
    rgb = Image.composite(white, body, bright)

    out = rgb.convert('RGBA')
    out.putalpha(a)
    return out.resize((W, H), Image.LANCZOS)


droplet = make_tear(140, 210, 70, 135, 52, 18)
# Slim tear, bluer + a touch more body so it reads clearly on the small avatar.
slim = make_tear(120, 236, 60, 152, 40, 12,
                 tint_top=(198, 226, 250), tint_bot=(116, 182, 240),
                 alpha_body=84, alpha_max=238)
# Cry tear: rounder bead, deeper blue, heavier — the full weeping drop.
cry = make_tear(140, 210, 70, 128, 56, 26,
                tint_top=(180, 216, 250), tint_bot=(86, 158, 234),
                alpha_body=98, alpha_max=246)
droplet.save(os.path.join(HERE, 'tear_droplet.png'))
slim.save(os.path.join(HERE, 'tear_slim.png'))
cry.save(os.path.join(HERE, 'tear_cry.png'))

# On-skin preview: skin swatch + faint cheek blush, both tears placed, so the
# translucency reads the way it will on her face.
prev = Image.new('RGBA', (460, 320), (247, 220, 199, 255))
blush = Image.new('RGBA', prev.size, (0, 0, 0, 0))
ImageDraw.Draw(blush).ellipse([70, 165, 240, 305], fill=(255, 172, 172, 80))
blush = blush.filter(ImageFilter.GaussianBlur(24))
prev = Image.alpha_composite(prev, blush)
prev.alpha_composite(droplet, (70, 50))
prev.alpha_composite(slim, (272, 40))
prev.convert('RGB').save(os.path.join(HERE, 'preview_on_skin.png'))

print("wrote tear_droplet.png, tear_slim.png, preview_on_skin.png")
