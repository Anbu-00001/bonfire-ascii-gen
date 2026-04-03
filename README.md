![Soulslike ASCII Bonfire](final_bonfire.gif)

# 🕯️ Soulslike ASCII Bonfire

*The flow of time itself is convoluted; with heroes centuries old phasing in and out.*

A high-fidelity, performance-optimized terminal animation engine designed to bring the atmospheric warmth and isolation of a Dark Souls bonfire to your command line. Built with Python and standard ANSI escape codes, this project renders a cinematic, flicker-fused experience with realistic fire physics.

## ⚔️ Technical Achievements

This engine goes beyond simple ASCII conversion, implementing advanced rendering techniques for structural stability and visual depth:

- **Pre-calculated Frame Buffer**: To ensure a stutter-free 12 FPS experience, the engine pre-renders all 24 frames of the animation cycle into a high-speed memory buffer. This allows for complex image processing, sharpening, and contrast lifting without impacting the runtime loop's performance.
- **Sine-wave Wind Displacement**: Flames are mathematically displaced using a frequency-modulated sine-wave algorithm. This simulates a natural environmental breeze, causing the fire to 'lick' towards the left and settle back with fluid, organic motion.
- **Base-Frame Compositing**: To prevent 'structural decay' during the darkest flicker frames, the engine captures a **Perfect Base Structure** of the sword and hilt. By compositing this 'structural floor' behind the fire, the sword remains a solid, unbreakable silhouette even as the bonfire's light oscillates.

## 🔥 Features

- **True-Color ANSI support**: Full RGB color mapping using `\x1b[38;2;R;G;Bm` escape sequences.
- **80% Flicker Clamping**: Calibrated flicker logic ensures the fire never drops into blackout, maintaining a constant 'crispy' glow.
- **Strict Background Thresholding**: Luminance < 35 is mapped to absolute blank space for 100% clean terminal rendering.
- **Gamma Calibration**: Pre-configured at `0.7` to lift the heavy metal textures of the knight's armor from deep shadows.

## 🛠️ Usage

Ensure you have `Pillow` installed for image processing:
```bash
pip install Pillow
```

### 🕯️ Run the Animation
Recommended for standard 80x24 terminals:
```bash
python3 ascii_animator.py sif.jpg 80
```
*Use `Ctrl+C` to extinguish the flame.*

### 📸 Static Conversion
Optimized for high-fidelity exports:
```bash
python3 ascii_converter.py sif.jpg 80
```

## ✨ Credits

This project is an open-source tribute to the **Dark Souls** series by FromSoftware. The pixel art inspiration and atmospheric vibes are rooted in the 'Soulslike' genre and its legacy of environmental storytelling.

*Don't get hollow.*

Co-authored-by: name <anbuxolo@gmail.com>
