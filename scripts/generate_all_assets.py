#!/usr/bin/env python3
import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_LOGO = os.path.join(REPO_ROOT, "..", "petrol-pump-erp-m", "public", "logo.png")
if not os.path.exists(SOURCE_LOGO):
    SOURCE_LOGO = "/home/wafa-tech/petrol-pump-erp-m/public/logo.png"

DESKTOP_BUILD = os.path.join(REPO_ROOT, "desktop-app", "build")
ANDROID_RES = os.path.join(REPO_ROOT, "android-app", "android", "app", "src", "main", "res")
ANDROID_WWW = os.path.join(REPO_ROOT, "android-app", "www")

os.makedirs(DESKTOP_BUILD, exist_ok=True)
os.makedirs(ANDROID_WWW, exist_ok=True)

print(f"Loading source logo from: {SOURCE_LOGO}")
logo_raw = Image.open(SOURCE_LOGO).convert("RGBA")

# Ensure crisp square base
base_size = max(logo_raw.size)
logo_square = Image.new("RGBA", (base_size, base_size), (0, 0, 0, 0))
offset = ((base_size - logo_raw.width) // 2, (base_size - logo_raw.height) // 2)
logo_square.paste(logo_raw, offset, logo_raw)

# -------------------------------------------------------------
# 1. Desktop Icons & NSIS Installer Assets
# -------------------------------------------------------------
print("Generating Desktop App assets...")
icon_512 = logo_square.resize((512, 512), Image.Resampling.LANCZOS)
icon_512.save(os.path.join(DESKTOP_BUILD, "icon.png"), "PNG")

# Multi-resolution Windows ICO
ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
icon_512.save(os.path.join(DESKTOP_BUILD, "icon.ico"), format="ICO", sizes=ico_sizes)

# NSIS Header (150x57)
nsis_header = Image.new("RGBA", (150, 57), (7, 11, 20, 255))
header_draw = ImageDraw.Draw(nsis_header)
# subtle red accent line at bottom
header_draw.rectangle([0, 54, 150, 57], fill=(215, 25, 32, 255))
header_logo = logo_square.resize((46, 46), Image.Resampling.LANCZOS)
nsis_header.paste(header_logo, (6, 5), header_logo)
nsis_header.convert("RGB").save(os.path.join(DESKTOP_BUILD, "installerHeader.bmp"), "BMP")

# NSIS Sidebar (164x314)
nsis_sidebar = Image.new("RGBA", (164, 314), (7, 11, 20, 255))
sidebar_draw = ImageDraw.Draw(nsis_sidebar)
for y in range(314):
    factor = y / 314.0
    r = int(7 + (215 - 7) * 0.15 * factor)
    g = int(11 * (1 - factor * 0.5))
    b = int(20 + 10 * factor)
    sidebar_draw.line([(0, y), (164, y)], fill=(r, g, b, 255))
sidebar_logo = logo_square.resize((110, 110), Image.Resampling.LANCZOS)
nsis_sidebar.paste(sidebar_logo, (27, 45), sidebar_logo)
nsis_sidebar.convert("RGB").save(os.path.join(DESKTOP_BUILD, "installerSidebar.bmp"), "BMP")

# -------------------------------------------------------------
# 2. Android WWW Web Assets
# -------------------------------------------------------------
print("Generating Android WWW assets...")
icon_512.save(os.path.join(ANDROID_WWW, "icon.png"), "PNG")

# -------------------------------------------------------------
# 3. Master Splash Screen Generator
# -------------------------------------------------------------
def create_splash_graphic(width, height):
    """Creates a high-end luxury dark glassmorphic splash image."""
    img = Image.new("RGBA", (width, height), (7, 11, 20, 255))
    draw = ImageDraw.Draw(img)

    # Subtle radial glow from center/top
    cx = width // 2
    cy = int(height * 0.42)
    max_radius = int(math.hypot(width, height) * 0.45)
    
    # Render radial glow steps
    for r in range(max_radius, 0, -25):
        alpha = int(45 * (1.0 - (r / max_radius)) ** 1.6)
        glow_color = (215, 25, 32, alpha)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=glow_color)

    # Center Logo sizing
    min_dim = min(width, height)
    logo_dim = int(min_dim * 0.42)
    logo_dim = max(96, min(logo_dim, 400))
    resized_logo = logo_square.resize((logo_dim, logo_dim), Image.Resampling.LANCZOS)

    # Drop shadow for logo
    shadow_pad = 20
    shadow_img = Image.new("RGBA", (logo_dim + shadow_pad*2, logo_dim + shadow_pad*2), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_img)
    shadow_draw.ellipse([shadow_pad, shadow_pad, logo_dim + shadow_pad, logo_dim + shadow_pad], fill=(0, 0, 0, 140))
    shadow_blur = shadow_img.filter(ImageFilter.GaussianBlur(12))

    lx = cx - (logo_dim // 2)
    ly = cy - (logo_dim // 2) - int(min_dim * 0.05)
    img.paste(shadow_blur, (lx - shadow_pad, ly - shadow_pad + 8), shadow_blur)
    img.paste(resized_logo, (lx, ly), resized_logo)

    # Typography
    font_path_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_path_reg = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    title_size = max(14, int(min_dim * 0.052))
    sub_size = max(10, int(min_dim * 0.032))
    badge_size = max(9, int(min_dim * 0.026))

    try:
        font_title = ImageFont.truetype(font_path_bold, title_size)
        font_sub = ImageFont.truetype(font_reg if 'font_reg' in locals() else font_path_reg, sub_size)
        font_badge = ImageFont.truetype(font_path_bold, badge_size)
    except:
        font_title = font_sub = font_badge = ImageFont.load_default()

    # Draw Badge: VITAL PETROLEUM FRANCHISE
    badge_text = "● VITAL PETROLEUM FRANCHISE"
    bbox_b = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw = bbox_b[2] - bbox_b[0]
    bh = bbox_b[3] - bbox_b[1]
    by = ly + logo_dim + int(min_dim * 0.04)
    bx = cx - (bw // 2)

    pad_h, pad_v = 12, 5
    draw.rounded_rectangle([bx - pad_h, by - pad_v, bx + bw + pad_h, by + bh + pad_v], radius=10, fill=(215, 25, 32, 45), outline=(215, 25, 32, 90), width=1)
    draw.text((bx, by), badge_text, fill=(255, 90, 95, 255), font=font_badge)

    # Station Title
    title_text = "MEHAR FILLING STATION"
    bbox_t = draw.textbbox((0, 0), title_text, font=font_title)
    tw = bbox_t[2] - bbox_t[0]
    ty = by + bh + pad_v * 2 + int(min_dim * 0.025)
    draw.text((cx - (tw // 2), ty), title_text, fill=(255, 255, 255, 255), font=font_title)

    # Subtitle
    sub_text = "Official Enterprise ERP Portal"
    bbox_s = draw.textbbox((0, 0), sub_text, font=font_sub)
    sw = bbox_s[2] - bbox_s[0]
    sy = ty + (bbox_t[3] - bbox_t[1]) + 8
    draw.text((cx - (sw // 2), sy), sub_text, fill=(148, 163, 184, 255), font=font_sub)

    return img.convert("RGB")

# Generate web splash
web_splash = create_splash_graphic(1080, 1920)
web_splash.save(os.path.join(ANDROID_WWW, "splash.png"), "PNG")
print("Saved web splash screen: android-app/www/splash.png")

# -------------------------------------------------------------
# 4. Android Native Mipmap & Splash Resources
# -------------------------------------------------------------
def generate_android_res():
    if not os.path.exists(ANDROID_RES):
        print(f"Android res directory {ANDROID_RES} does not exist yet. Run cap add android first.")
        return

    print("Generating native Android app icons and splash drawables...")
    # Launcher Icon sizes
    mipmaps = {
        "mipmap-mdpi": (48, 108),
        "mipmap-hdpi": (72, 162),
        "mipmap-xhdpi": (96, 216),
        "mipmap-xxhdpi": (144, 324),
        "mipmap-xxxhdpi": (192, 432),
    }

    for folder, (icon_sz, fg_sz) in mipmaps.items():
        folder_path = os.path.join(ANDROID_RES, folder)
        os.makedirs(folder_path, exist_ok=True)

        # Standard icon
        ic = logo_square.resize((icon_sz, icon_sz), Image.Resampling.LANCZOS)
        ic.save(os.path.join(folder_path, "ic_launcher.png"), "PNG")

        # Round icon (circular mask)
        mask = Image.new("L", (icon_sz, icon_sz), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse([0, 0, icon_sz, icon_sz], fill=255)
        ic_round = Image.new("RGBA", (icon_sz, icon_sz), (0, 0, 0, 0))
        ic_round.paste(ic, (0, 0), mask)
        ic_round.save(os.path.join(folder_path, "ic_launcher_round.png"), "PNG")

        # Adaptive Foreground (safe zone 66% center)
        fg_img = Image.new("RGBA", (fg_sz, fg_sz), (0, 0, 0, 0))
        inner_sz = int(fg_sz * 0.66)
        inner_logo = logo_square.resize((inner_sz, inner_sz), Image.Resampling.LANCZOS)
        fg_img.paste(inner_logo, ((fg_sz - inner_sz)//2, (fg_sz - inner_sz)//2), inner_logo)
        fg_img.save(os.path.join(folder_path, "ic_launcher_foreground.png"), "PNG")

    # Native Splash Screen drawables
    splash_targets = {
        "drawable": (480, 800),
        "drawable-port-mdpi": (320, 480),
        "drawable-port-hdpi": (480, 800),
        "drawable-port-xhdpi": (720, 1280),
        "drawable-port-xxhdpi": (960, 1600),
        "drawable-port-xxxhdpi": (1280, 1920),
        "drawable-land-mdpi": (480, 320),
        "drawable-land-hdpi": (800, 480),
        "drawable-land-xhdpi": (1280, 720),
        "drawable-land-xxhdpi": (1600, 960),
        "drawable-land-xxxhdpi": (1920, 1280),
    }

    for folder, (w, h) in splash_targets.items():
        folder_path = os.path.join(ANDROID_RES, folder)
        os.makedirs(folder_path, exist_ok=True)
        splash_img = create_splash_graphic(w, h)
        splash_img.save(os.path.join(folder_path, "splash.png"), "PNG")

    print("Native Android assets generated successfully.")

if __name__ == "__main__":
    generate_android_res()
    print("All initial assets generation complete!")
