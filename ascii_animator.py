import sys
import os
import time
import math
import random
from PIL import Image, ImageEnhance, ImageOps, ImageFilter

def get_processed_img(img_base, width, contrast, brightness):
    """Common image processing for both base plate and animated frames."""
    img = img_base.copy()
    img = img.filter(ImageFilter.SHARPEN).filter(ImageFilter.SHARPEN)
    img = img.filter(ImageFilter.MaxFilter(3))
    img = ImageEnhance.Brightness(img).enhance(brightness)
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = img.point(lambda p: pow(p/255.0, 0.7) * 255)
    
    original_width, original_height = img.size
    aspect_ratio = original_height / float(original_width)
    new_height = int(width * aspect_ratio * 0.45)
    img = img.resize((width, new_height), Image.Resampling.LANCZOS)
    return img

def generate_base_plate(img_base, width=80, contrast=2.2, brightness=1.4):
    """Generates a 2D grid representing the 'Perfect' static ASCII frame."""
    CHARS = " .:-=+*#%@"
    EDGE_CHARS = "@#W"
    
    img = get_processed_img(img_base, width, contrast, brightness)
    img_gray = img.convert('L')
    pixels = img.load()
    pixels_gray = img_gray.load()
    new_width, new_height = img.size

    grid = []
    for y in range(new_height):
        row = []
        for x in range(new_width):
            r, g, b = pixels[x, y]
            lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
            
            edge_stren = 0
            if 0 < x < new_width - 1:
                edge_stren = abs(pixels_gray[x+1, y] - pixels_gray[x-1, y])
            
            if lum < 35:
                char = " "
            elif edge_stren > 55:
                char = EDGE_CHARS[min(len(EDGE_CHARS)-1, int(edge_stren/80))]
            elif 40 <= lum <= 100:
                char = "=" if lum < 65 else "*"
            else:
                char_index = int((lum / 255) * (len(CHARS) - 1))
                char = CHARS[char_index]
            
            # Store the full ANSI string for this pixel
            row.append(f"\x1b[38;2;{int(r)};{int(g)};{int(b)}m{char}")
        grid.append(row)
    return grid

def generate_frame(img_base, base_plate, width=80, contrast=2.2, brightness=1.4, flicker_val=0, frame_idx=0, total_frames=24):
    """Generates an animated frame with the Base Plate overlay for the sword hilt."""
    CHARS = " .:-=+*#%@"
    EDGE_CHARS = "@#W"
    
    img = get_processed_img(img_base, width, contrast, brightness)
    img_gray = img.convert('L')
    pixels = img.load()
    pixels_gray = img_gray.load()
    new_width, new_height = img.size
    
    center_x = new_width // 2
    # Sword Zone: center_x - 3 to center_x + 3
    hilt_col_range = range(center_x - 3, center_x + 4)
    top_half_y = new_height // 2
    
    flicker_ratio = 0.8 + (0.2 * ((flicker_val + 1) / 2))

    output = []
    for y in range(new_height):
        line = ""
        for x in range(new_width):
            # THE PERFECT OVERLAY FIX: Check the Static Base Plate first for the hilt zone
            if x in hilt_col_range and y < top_half_y:
                base_pixel = base_plate[y][x]
                if "m " not in base_pixel: # If base character is NOT a space
                    line += base_pixel
                    continue
            
            r, g, b = pixels[x, y]
            is_fire = (r > 160 and g > 80)
            
            x_sway = 0
            if is_fire:
                # Wind bias: Lick left, settle center
                y_wind_amp = (1.0 - y / (new_height * 0.8)) * 5.0
                y_wind_amp = max(0, y_wind_amp)
                phase = (frame_idx / total_frames) * 2 * math.pi + (y / 7.0)
                x_sway = int(-abs(math.sin(phase)) * y_wind_amp)
                
                sx = max(0, min(new_width - 1, x - x_sway))
                r, g, b = pixels[sx, y]
                r, g, b = min(255, int(r * flicker_ratio)), min(255, int(g * flicker_ratio)), min(255, int(b * flicker_ratio))

            random.seed(x + y + frame_idx)
            lum_jitter = random.randint(-8, 8) if is_fire else 0
            lum = 0.2126 * r + 0.7152 * g + 0.0722 * b + lum_jitter
            lum = max(0, min(255, lum))

            edge_stren = 0
            if 0 < x < new_width - 1:
                shifted_x = max(0, min(new_width-1, x - x_sway))
                edge_stren = abs(pixels_gray[min(new_width-1, shifted_x+1), y] - pixels_gray[max(0, shifted_x-1), y])
            
            if lum < 35:
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
    if not os.path.exists(img_path): return

    base_img = Image.open(img_path).convert('RGB')
    mask = base_img.convert('L').point(lambda p: 255 if p > 15 else 0)
    bbox = mask.getbbox()
    if bbox: base_img = base_img.crop(bbox)

    print("\x1b[?25l", end="") # Hide cursor
    
    # 1. GENERATE STATIC BASE PLATE (The Anchor)
    print("Pre-rendering Static Base Plate...")
    base_plate = generate_base_plate(base_img, width=width)
    
    num_frames = 24
    print(f"Generating {num_frames} frames with Base Plate Compositing...")
    frames = []
    for i in range(num_frames):
        f_val = math.sin((i / num_frames) * 2 * math.pi)
        frame_str = generate_frame(base_img, base_plate, width=width, flicker_val=f_val, frame_idx=i, total_frames=num_frames)
        frames.append(frame_str)
        print(f"Processing: {i+1}/{num_frames}", end="\r")

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
