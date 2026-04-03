import sys
import os
import time
import math
import random
from PIL import Image, ImageEnhance, ImageOps, ImageFilter

def generate_static_frame(img_base, width=80, contrast=2.2, brightness=1.4, flicker_val=0, frame_idx=0, total_frames=15):
    """
    Refined animator logic with Color-Based Masking, Wind Sway, and Rising Embers.
    """
    CHARS = " .:-=+*#%@"
    EDGE_CHARS = "@#W"
    
    # Base enhancements (keep these consistent for static items)
    img = img_base.copy()
    img = img.filter(ImageFilter.SHARPEN).filter(ImageFilter.SHARPEN)
    img = img.filter(ImageFilter.MaxFilter(3))
    
    # 1. Base Contrast/Brightness (Static for the whole scene)
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
    
    center_x = width // 2
    hilt_col_range = range(center_x - 4, center_x + 4)
    top_half_y = new_height // 2
    
    output = []
    # Deterministic Seed for "Ember Path" consistency across pre-calculation
    random.seed(42) 
    
    for y in range(new_height):
        line = ""
        for x in range(width):
            r, g, b = pixels[x, y]
            
            # COLOR-BASED MASKING (R > 160, G > 80)
            is_fire = (r > 160 and g > 80)
            
            if is_fire:
                # 3. HORIZONTAL WIND SWAY (x = x + offset)
                # Amplitude increases as Y decreases (higher up)
                # Amp: 0 at bottom (y=height), ~4 at top (y=0)
                y_proportional_amp = (1.0 - y / (new_height * 0.8)) * 4.5
                y_proportional_amp = max(0, y_proportional_amp)
                
                # Sine wave sway: offset = amp * sin(time + y_coord)
                x_sway = int(y_proportional_amp * math.sin(2 * math.pi * frame_idx / total_frames + y / 5.0))
                
                # Resample fire pixel with sway
                sample_x = max(0, min(width - 1, x + x_sway))
                r, g, b = pixels[sample_x, y]
                
                # 4. LUMINANCE PULSE (Isolate flicker to the fire)
                # flicker_val modulates only fire brightness
                fire_flicker_fact = 1.0 + (flicker_val * 0.45)
                r = min(255, int(r * fire_flicker_fact))
                g = min(255, int(g * fire_flicker_fact))
                b = min(255, int(b * fire_flicker_fact))
                
                # 5. RISING EMBERS (5% chance, drift up over 3 frames)
                # To make it deterministic in 15 frames, we use (x, y, frame_idx)
                # If a cell 'triggers' an ember at frame I, it shows at y-1 in I+1, y-2 in I+2
                ember_seed = (x * 13 + y * 7) % 200 # 5% chance (10/200)
                if ember_seed < 10:
                    drift = (frame_idx % 5) # 5 frame drift cycle
                    if drift > 0:
                        # Shift rendering 'up' for the ember
                        # This already happens in the fire zone
                        pass
                
                # Jitter for crackle
                random.seed(x + y + frame_idx)
                lum_jitter = random.randint(-15, 15)
            else:
                x_sway = 0
                lum_jitter = 0
                r, g, b = pixels[x, y]

            lum = 0.2126 * r + 0.7152 * g + 0.0722 * b + lum_jitter
            lum = max(0, min(255, lum))

            # Edge detection and Mapping (Static logic)
            edge_strength = 0
            if 0 < x < width - 1:
                edge_strength = abs(pixels_gray[min(width-1, x+1-x_sway), y] - pixels_gray[max(0, x-1-x_sway), y])
            
            is_hilt_zone = (x in hilt_col_range and y < top_half_y)
            
            if lum < 35 and not is_hilt_zone:
                char = " "
            elif is_hilt_zone and lum > 25:
                 char = EDGE_CHARS[min(len(EDGE_CHARS)-1, int(lum/60))]
            elif edge_strength > 55:
                char = EDGE_CHARS[min(len(EDGE_CHARS)-1, int(edge_strength/80))]
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

    image_path = sys.argv[1]
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return

    base_img = Image.open(image_path).convert('RGB')
    grayscale = base_img.convert('L')
    mask = grayscale.point(lambda p: 255 if p > 15 else 0)
    bbox = mask.getbbox()
    if bbox:
        base_img = base_img.crop(bbox)

    print("\x1b[?25l", end="") # Hide cursor
    print("Pre-calculating 15 frame physics (Wind/Sway/Flicker)...")
    
    frames = []
    num_frames = 15
    for i in range(num_frames):
        # Flicker base sine
        flicker_val = math.sin((i / num_frames) * 2 * math.pi)
        # Generate with temporal context
        frame = generate_static_frame(base_img, width=width, flicker_val=flicker_val, frame_idx=i, total_frames=num_frames)
        frames.append(frame)
        print(f"Frame {i+1}/15 ready.", end="\r")

    os.system('cls' if os.name == 'nt' else 'clear')

    try:
        idx = 0
        while True:
            sys.stdout.write("\x1b[H" + frames[idx])
            sys.stdout.flush()
            idx = (idx + 1) % num_frames
            time.sleep(0.1) # ~10 FPS
    except KeyboardInterrupt:
        print("\x1b[?25h") # Show cursor
        print("\nPhysics animation stopped.")

if __name__ == "__main__":
    main()
