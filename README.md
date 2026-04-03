# Bonfire ASCII Generator

A high-fidelity terminal-based ASCII animator and converter specifically tuned for Soulslike art. Features localized fire physics, wind sway, and true-color ANSI support.

## Features
- **Cinematic 24-Frame Loop**: Optimized 24-frame pre-calculation engine for a silky-smooth, cinematic rotation.
- **Structural Sword Lock**: A coordinate-based mask isolates the central hilt columns, ensuring the sword remains a 100% static anchor while the fire dances.
- **80% Flicker Clamping**: Calibrated flicker logic (`0.8 + 0.2 * sin(t)`) ensures the fire stays bright and 'crispy,' never dropping below 80% luminance to eliminate blackout frames.
- **Realistic Wind Bias**: Flames 'lick' toward the left and settle back to center, simulating a consistent environmental breeze.
- **Hand-Drawn 12 FPS Cadence**: Intentionally slowed playback speed for an atmospheric, hand-drawn animation feel.

## Usage

### Animator (Cinematic)
Requires `Pillow`.
```bash
# Recommended for standard terminals
python3 ascii_animator.py sif.jpg 80 
```
*Press `Ctrl+C` to stop.*

### Converter (Static)
```bash
# Optimized for high-fidelity exports
python3 ascii_converter.py sif.jpg 80 2.2 1.4
```

## Professional Optimizations
- **Horizontal Dilation**: Uses PIL MaxFilter to beef up thin vertical metallic structures.
- **Gamma Correction**: Calibrated at 0.7 to lift the knight's armor from deep shadows.
- **2x Strategic Sharpening**: Hardens hilt edges to prevent them from bleeding into the black background.
- **Strict Background Threshold**: Luminance < 35 is mapped to absolute ' ' (space) for 100% clean terminal rendering.
