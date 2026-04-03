import sys
import os
from PIL import Image, ImageEnhance, ImageOps, ImageFilter

def convert_to_ascii(image_path, width=80, contrast=2.2, brightness=1.4):
    """
    Final refined ASCII conversion for Soulslike art. 
    Includes Hilt-weighting and strategic sharpening.
    """
    CHARS = " .:-=+*#%@" # Standard inverted set
    EDGE_CHARS = "@#W"   # High-density for metallic edges
    
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found.")
        return

    try:
        img = Image.open(image_path).convert('RGB')
        
        # 1. Auto-Crop (Subject focus)
        grayscale = img.convert('L')
        mask = grayscale.point(lambda p: 255 if p > 15 else 0)
        bbox = mask.getbbox()
        if bbox:
            img = img.crop(bbox)

        # 2. STRATEGIC SHARPENING (x2)
        # Prevents the hilt and handle from 'bleeding' into the background
        img = img.filter(ImageFilter.SHARPEN).filter(ImageFilter.SHARPEN)

        # 3. Horizontal Dilation (Spread the metallic highlights)
        img = img.filter(ImageFilter.MaxFilter(3))

        # 4. Visual Prep (Shadow lift and Contrast)
        img = ImageEnhance.Brightness(img).enhance(brightness)
        img = ImageEnhance.Contrast(img).enhance(contrast)
        img = img.point(lambda p: pow(p/255.0, 0.7) * 255)

        # 5. Scaling (Balanced at 0.45)
        original_width, original_height = img.size
        aspect_ratio = original_height / float(original_width)
        new_height = int(width * aspect_ratio * 0.45)
        img = img.resize((width, new_height), Image.Resampling.LANCZOS)
        
        img_gray = img.convert('L')
        pixels = img.load()
        pixels_gray = img_gray.load()
        
        # Detect the 'Hilt Zone' (Center-top area)
        center_x = width // 2
        hilt_col_range = range(center_x - 4, center_x + 4)
        top_half_y = new_height // 2
        
        output = []
        for y in range(new_height):
            line = ""
            for x in range(width):
                r, g, b = pixels[x, y]
                
                # Perceived Luminance
                lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
                
                # Edge detection for metallic structures
                edge_strength = 0
                if 0 < x < width - 1:
                    edge_strength = abs(pixels_gray[x+1, y] - pixels_gray[x-1, y])
                
                # 6. HILT WEIGHTING LOGIC
                # Force handle thickness in center-top columns
                is_hilt_zone = (x in hilt_col_range and y < top_half_y)
                
                # STRICT BACKGROUND Threshold
                if lum < 35 and not is_hilt_zone:
                    char = " "
                # Special Case: Hilt zone padding
                elif is_hilt_zone and lum > 25:
                     char = EDGE_CHARS[min(len(EDGE_CHARS)-1, int(lum/60))]
                # Sharp Edge detection (Sword handle/blade)
                elif edge_strength > 55:
                    char = EDGE_CHARS[min(len(EDGE_CHARS)-1, int(edge_strength/80))]
                # 7. LOWER-MID LUMINANCE BOOST (Range 40-80)
                elif 40 <= lum <= 100:
                    # Map to medium density (= or *)
                    char = "=" if lum < 65 else "*"
                else:
                    # Standard luminance mapping
                    char_index = int((lum / 255) * (len(CHARS) - 1))
                    char = CHARS[char_index]
                
                # ANSI TrueColor (24-bit RGB)
                line += f"\x1b[38;2;{int(r)};{int(g)};{int(b)}m{char}"
            
            output.append(line + "\x1b[0m")

        print("\n".join(output))

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ascii_converter.py <image_path> [width] [contrast] [brightness]")
    else:
        path = sys.argv[1]
        w = int(sys.argv[2]) if len(sys.argv) > 2 else 80
        c = float(sys.argv[3]) if len(sys.argv) > 3 else 2.2
        b = float(sys.argv[4]) if len(sys.argv) > 4 else 1.4
        convert_to_ascii(path, w, c, b)
