import sys
import os
import time
import math
import random
from PIL import Image, ImageEnhance, ImageOps, ImageFilter

def get_processed_img(img_base, width, contrast, brightness):
    """Common image processing for both base structure and animated frames."""
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

def render_base_structure(img_base, width=80, contrast=2.2, brightness=1.4):
    """Generates a 2D grid of characters for the 'Perfect Base' (the structural floor)."""
    CHARS = " .:-=+*#%@"
    EDGE_CHARS = "@#W"
    
    img = get_processed_img(img_base, width, contrast, brightness)
    img_gray = img.convert('L')
    pixels_gray = img_gray.load()
    new_width, new_height = img.size

    grid = []
    for y in range(new_height):
        row = []
        for x in range(new_width):
            lum = pixels_gray[x, y]
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
            row.append(char)
        grid.append(row)
    return grid

def generate_frame(img_base, base_structure, sword_mask, width=80, contrast=2.2, brightness=1.4, flicker_val=0, frame_idx=0, total_frames=20):
    """Generates an animated frame with an Absolute Structural Floor for the sword."""
    CHARS = " .:-=+*#%@"
    SWORD_CHARS = "+=*#@W" 
    EDGE_CHARS = "@#W"
    WEAK_CHARS = (" ", ".", ":", "-")
    
    img = get_processed_img(img_base, width, contrast, brightness)
    img_gray = img.convert('L')
    pixels = img.load()
    pixels_gray = img_gray.load()
    new_width, new_height = img.size
    
    flicker_ratio = 0.8 + (0.2 * ((flicker_val + 1) / 2))

    output = []
    for y in range(new_height):
        line = ""
        for x in range(new_width):
            r, g, b = pixels[x, y]
            is_fire = (r > 160 and g > 80)
            
            # The mask check
            is_sword_member = (x, y) in sword_mask

            x_sway = 0
            if is_fire and not is_sword_member:
                y_wind_amp = (1.0 - y / (new_height * 0.8)) * 5.0
                y_wind_amp = max(0, y_wind_amp)
                phase = (frame_idx / total_frames) * 2 * math.pi + (y / 7.0)
                x_sway = int(-abs(math.sin(phase)) * y_wind_amp)
                sx = max(0, min(new_width - 1, x - x_sway))
                r, g, b = pixels[sx, y]

            # Apply flicker pulse
            f_ratio = flicker_ratio if (is_fire or is_sword_member) else 1.0
            r_f, g_f, b_f = min(255, int(r * f_ratio)), min(255, int(g * f_ratio)), min(255, int(b * f_ratio))
            
            if is_sword_member:
                r_f, g_f, b_f = int(r_f * 0.85), int(g_f * 0.85), int(b_f * 0.85)

            random.seed(x + y + frame_idx)
            lum_jitter = random.randint(-10, 10) if is_fire else 0
            lum = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f + lum_jitter
            lum = max(0, min(255, lum))

            edge_strength = 0
            if 0 < x < new_width - 1:
                shifted_x = max(0, min(new_width-1, x - x_sway))
                edge_strength = abs(pixels_gray[min(new_width-1, shifted_x+1), y] - pixels_gray[max(0, shifted_x-1), y])
            
            if is_sword_member:
                char_idx = int((lum / 255) * (len(SWORD_CHARS) - 1))
                char = SWORD_CHARS[char_idx]
                
                # THE STRUCTURAL FLOOR FIX: Intercept weak characters and force base char
                if char in WEAK_CHARS:
                    char = base_structure[y][x]
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
    is_record = "--record" in sys.argv
    img_path = sys.argv[1]
    
    # Simple width parsing that ignores the --record flag if present
    width = 80
    for arg in sys.argv[2:]:
        if arg.isdigit():
            width = int(arg)
            break
            
    if not os.path.exists(img_path): return

    # SILENT BOOT: If recording, hide cursor immediately and silently
    if is_record:
        sys.stdout.write("\x1b[?25l")
        sys.stdout.flush()

    base_img = Image.open(img_path).convert('RGB')
    mask = base_img.convert('L').point(lambda p: 255 if p > 15 else 0)
    bbox = mask.getbbox()
    if bbox: base_img = base_img.crop(bbox)

    if not is_record:
        print("\x1b[?25l", end="") # Hide cursor
    
    # 1. RENDER PERFECT BASE STRUCTURE (The Structural Floor)
    if not is_record:
        print("Capturing Perfect Base Structure...")
    base_structure = render_base_structure(base_img, width=width)
    
    # 2. MAP THE CORE: Create sword_mask from central columns
    if not is_record:
        print("Mapping Sword Core Mask...")
    new_width = len(base_structure[0])
    new_height = len(base_structure)
    center_x = new_width // 2
    # Define central columns for scanning (approx 15% width around center)
    scan_width = max(5, int(width * 0.15))
    sword_col_range = range(center_x - scan_width, center_x + scan_width + 1)
    
    sword_mask = set()
    for y in range(new_height):
        for x in sword_col_range:
            if base_structure[y][x] != " ":
                sword_mask.add((x, y))

    num_frames = 24
    frames = []
    
    # TOTAL SILENCE DURING COMPUTATION
    # We use a context manager or simple redirection to ensure no leaks
    _original_stdout = sys.stdout
    if is_record:
        sys.stdout = open(os.devnull, 'w')

    try:
        if not is_record:
            print(f"Generating {num_frames} frames with Absolute Structural Floor...")
        
        for i in range(num_frames):
            f_val = math.sin((i / num_frames) * 2 * math.pi)
            frame_str = generate_frame(base_img, base_structure, sword_mask, width=width, flicker_val=f_val, frame_idx=i, total_frames=num_frames)
            frames.append(frame_str)
            if not is_record:
                _original_stdout.write(f"Processing: {i+1}/{num_frames}\r")
                _original_stdout.flush()
    finally:
        if is_record:
            sys.stdout.close()
            sys.stdout = _original_stdout

    # THE CLEAN HANDOFF: No early prints, no intermediate clears.
    # The playback loop below will perform the first wipe bundled with the first frame.
    
    try:
        idx = 0
        if is_record:
            # EXTENDED RECORDING: Exactly 5 cycles through frames (10 seconds at 12fps)
            for _ in range(5):
                for idx in range(num_frames):
                    # ANTI-SCROLLING RENDER: Wipe screen for every frame to prevent stacking
                    sys.stdout.write("\033[2J\033[H" + frames[idx])
                    sys.stdout.flush()
                    time.sleep(1/12)
            
            # RECORDING HOLD: Ensure final buffer is captured
            time.sleep(1.0)
            sys.exit(0) # Silent Exit
        else:
            # NORMAL INFINITE LOOP
            while True:
                # ANTI-SCROLLING RENDER: Consistency across all modes
                sys.stdout.write("\033[2J\033[H" + frames[idx])
                sys.stdout.flush()
                idx = (idx + 1) % num_frames
                time.sleep(1/12)
    except KeyboardInterrupt:
        if not is_record:
            print("\x1b[?25h\nAnimator closed.")

if __name__ == "__main__":
    main()
