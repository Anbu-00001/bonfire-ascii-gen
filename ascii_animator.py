import sys
import os
import time
import math
import random
from PIL import Image, ImageEnhance, ImageOps, ImageFilter

def generate_frame(img_base, width=80, contrast=2.2, brightness=1.4, flicker_val=0, frame_idx=0, total_frames=24):
    """
    CRISPY OVERHAUL: Cinematic 24-frame logic with Structural Lock and Flicker Clamping.
    """
    CHARS = " .:-=+*#%@"
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
    
    # STRUCTURAL LOCK: Multi-column center mask for the sword hilt
    center_x = width // 2
    hilt_col_range = range(center_x - 3, center_x + 4)
    top_half_y = new_height // 2
    
    output = []
    
    # Flicker Clamp: 0.8 base + 0.2 oscillation (never below 80%)
    # flicker_val is sin(t) from -1.0 to 1.0
    flicker_ratio = 0.8 + (0.2 * ((flicker_val + 1) / 2)) # Maps sin to [0.8, 1.0]

    for y in range(new_height):
        line = ""
        for x in range(width):
            r, g, b = pixels[x, y]
            is_fire = (r > 160 and g > 80)
            is_hilt_zone = (x in hilt_col_range and y < top_half_y)
            
            x_sway = 0
            if is_fire and not is_hilt_zone:
                # 3. REALISTIC WIND BIAS (Lick left, settle center)
                y_wind_amp = (1.0 - y / (new_height * 0.8)) * 5.0
                y_wind_amp = max(0, y_wind_amp)
                
                # We use abs(sin) and negate it to ensure it only 'licks' to the left (-ve)
                phase = (frame_idx / total_frames) * 2 * math.pi + (y / 7.0)
                # Oscillation goes 0 -> -amp -> 0
                x_sway = int(-abs(math.sin(phase)) * y_wind_amp)
                
                # Resample fire pixel with wind displacement
                sx = max(0, min(width - 1, x - x_sway))
                r, g, b = pixels[sx, y]
                
                # Apply localized 80% flicker pulse
                r = min(255, int(r * flicker_ratio))
                g = min(255, int(g * flicker_ratio))
                b = min(255, int(b * flicker_ratio))

            # 4. MICRO-DITHERING (Exempting the Sword Hilt)
            random.seed(x + y + frame_idx)
            lum_jitter = random.randint(-8, 8) if (is_fire and not is_hilt_zone) else 0
            
            lum = 0.2126 * r + 0.7152 * g + 0.0722 * b + lum_jitter
            lum = max(0, min(255, lum))

            # Edge detection logic (aware of wind shift)
            edge_stren = 0
            if 0 < x < width - 1:
                shifted_x = max(0, min(width-1, x - x_sway))
                # Sample gray pixels for edge detection
                edge_stren = abs(pixels_gray[min(width-1, shifted_x+1), y] - pixels_gray[max(0, shifted_x-1), y])
            
            # Mapping Logic
            if is_hilt_zone:
                # Sword Hilt: Static anchor, no jitter, dense characters
                if lum > 25:
                    char = EDGE_CHARS[min(len(EDGE_CHARS)-1, int(lum/60))]
                else: 
                    char = " "
            elif lum < 35:
                char = " "
            elif edge_stren > 55:
                char = EDGE_CHARS[min(len(EDGE_CHARS)-1, int(edge_stren/80))]
            elif 40 <= lum <= 100:
                char = "=" if lum < 65 else "*"
            else:
                char_index = int((lum / 255) * (len(CHARS) - 1))
                char = CHARS[char_index]
            
            line += f"\x1b[38;2;{int(r)};{int(g)};{int(b)}m{char}"
        
        output.append(line + "\x1b[0m")

    return "\n".join(output)

def main():
    if len(sys.argv) < 2:
        print("Usage: python ascii_animator.py <image_path> [width]")
        return

    img_path = sys.argv[1]
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    
    if not os.path.exists(img_path):
        print(f"File not found: {img_path}")
        return

    # Auto-crop logic (Cached for all frames)
    base_img = Image.open(img_path).convert('RGB')
    mask = base_img.convert('L').point(lambda p: 255 if p > 15 else 0)
    bbox = mask.getbbox()
    if bbox: base_img = base_img.crop(bbox)

    print("\x1b[?25l", end="") # Hide cursor
    num_frames = 24
    print(f"Generating {num_frames} CRISpy cinematic frames...")
    
    frames = []
    for i in range(num_frames):
        f_val = math.sin((i / num_frames) * 2 * math.pi)
        frame_str = generate_frame(base_img, width=width, flicker_val=f_val, frame_idx=i, total_frames=num_frames)
        frames.append(frame_str)
        print(f"Processing: {i+1}/{num_frames}", end="\r")

    os.system('cls' if os.name == 'nt' else 'clear')

    try:
        idx = 0
        while True:
            # Overwrite at Home (0,0) for zero flicker
            sys.stdout.write("\x1b[H" + frames[idx])
            sys.stdout.flush()
            idx = (idx + 1) % num_frames
            # 12 FPS: intentional, natural flickering (1/12)
            time.sleep(1/12)
    except KeyboardInterrupt:
        print("\x1b[?25h\nAnimator closed.")

if __name__ == "__main__":
    main()
