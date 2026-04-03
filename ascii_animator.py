import sys
import os
import time
import math
import random
from PIL import Image, ImageEnhance, ImageOps, ImageFilter

def generate_frame(img_base, width=80, contrast=2.2, brightness=1.4, flicker_val=0, frame_idx=0, total_frames=24):
    """
    Refined Animator with CONSTRAINED SWORD MAPPING and Metallic Pulsing.
    Allows the hilt to breathe with firelight while maintaining a solid silhouette.
    """
    CHARS = " .:-=+*#%@"
    SWORD_CHARS = "+=*#@W" # Heavy Palette for structural weight
    EDGE_CHARS = "@#W"
    
    img = img_base.copy()
    img = img.filter(ImageFilter.SHARPEN).filter(ImageFilter.SHARPEN)
    img = img.filter(ImageFilter.MaxFilter(3))
    
    # 1. Base Preprocessing
    img = ImageEnhance.Brightness(img).enhance(brightness)
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = img.point(lambda p: pow(p/255.0, 0.7) * 255)

    # 2. Scaling
    original_width, original_height = img.size
    aspect_ratio = original_height / float(original_width)
    new_height = int(width * aspect_ratio * 0.45)
    img = img.resize((width, new_height), Image.Resampling.LANCZOS)
    
    img_gray = img.convert('L')
    pixels = img.load()
    pixels_gray = img_gray.load()
    
    # Structural Lock Zone
    center_x = width // 2
    # The hilt is usually about 6-8 chars wide at 80 width
    hilt_col_range = range(center_x - 3, center_x + 4)
    top_half_y = new_height // 2
    
    # Flicker Clamp: 0.8 base floor
    flicker_ratio = 0.8 + (0.2 * ((flicker_val + 1) / 2))
    
    output = []
    for y in range(new_height):
        line = ""
        for x in range(width):
            r, g, b = pixels[x, y]
            is_fire = (r > 160 and g > 80)
            is_hilt_zone = (x in hilt_col_range and y < top_half_y)
            
            # Base luminance (to decide if part of the sword silhouette)
            base_lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
            is_sword_member = (is_hilt_zone and base_lum > 35)

            x_sway = 0
            if is_fire and not is_sword_member:
                # 3. Wind Physics (Breeze from the right)
                wind_amp = (1.0 - y / (new_height * 0.8)) * 5.5
                wind_amp = max(0, wind_amp)
                phase = (frame_idx / total_frames) * 2 * math.pi + (y / 6.0)
                x_sway = int(wind_amp * (math.sin(phase) - 0.5))
                sx = max(0, min(width - 1, x - x_sway))
                r, g, b = pixels[sx, y]

            # Apply flicker pulse
            f_ratio = flicker_ratio if (is_fire or is_sword_member) else 1.0
            r_f, g_f, b_f = min(255, int(r * f_ratio)), min(255, int(g * f_ratio)), min(255, int(b * f_ratio))
            
            # 4. METALLIC DARKENING (0.85 multiplier) to distinguish sword from fire
            if is_sword_member:
                r_f, g_f, b_f = int(r_f * 0.85), int(g_f * 0.85), int(b_f * 0.85)

            # Noise for crackle (Deterministic)
            random.seed(x + y + frame_idx)
            lum_jitter = random.randint(-10, 10) if is_fire else 0
            
            lum = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f + lum_jitter
            lum = max(0, min(255, lum))

            edge_strength = 0
            if 0 < x < width - 1:
                shifted_x = max(0, min(width-1, x - x_sway))
                edge_strength = abs(pixels_gray[min(width-1, shifted_x+1), y] - pixels_gray[max(0, shifted_x-1), y])
            
            # 5. CONSTRAINED CHARACTER MAPPING (The Fix)
            if is_sword_member:
                # Map to the Heavy Palette (+=*#@W)
                # We use sword_lum to pick from the restricted set
                char_idx = int((lum / 255) * (len(SWORD_CHARS) - 1))
                char = SWORD_CHARS[char_idx]
            elif lum < 35:
                char = " "
            elif edge_strength > 55:
                char = EDGE_CHARS[min(len(EDGE_CHARS)-1, int(edge_strength/80))]
            elif 40 <= lum <= 100:
                char = "=" if lum < 65 else "*"
            else:
                char_index = int((lum / 255) * (len(CHARS) - 1))
                char = CHARS[char_index]
            
            line += f"\x1b[38;2;{int(r_f)};{int(g_f)};{int(b_f)}m{char}"
        
        output.append(line + "\x1b[0m")

    return "\n".join(output)

def main():
    if len(sys.argv) < 2:
        print("Usage: python ascii_animator.py <image_path> [width]")
        return

    image_path = sys.argv[1]
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    if not os.path.exists(image_path): return

    base_img = Image.open(image_path).convert('RGB')
    mask = base_img.convert('L').point(lambda p: 255 if p > 15 else 0)
    bbox = mask.getbbox()
    if bbox: base_img = base_img.crop(bbox)

    print("\x1b[?25l", end="")
    print("Pre-calculating 24 frame cinematic physics with Constrained Mapping...")
    
    frames = []
    num_frames = 24
    for i in range(num_frames):
        f_val = math.sin((i / num_frames) * 2 * math.pi)
        frame = generate_frame(base_img, width=width, flicker_val=f_val, frame_idx=i, total_frames=num_frames)
        frames.append(frame)
        print(f"Frame {i+1}/24 ready.", end="\r")

    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        idx = 0
        while True:
            sys.stdout.write("\x1b[H" + frames[idx])
            sys.stdout.flush()
            idx = (idx + 1) % num_frames
            time.sleep(1/12)
    except KeyboardInterrupt:
        print("\x1b[?25h\nAnimator closed.")

if __name__ == "__main__":
    main()
