# Bonfire ASCII Generator

A high-fidelity terminal-based ASCII animator and converter specifically tuned for Soulslike art. Features localized fire physics, wind sway, and true-color ANSI support.

## Features
- **Realistic Wind Sway**: Localized horizontal movement for fire tips using vertically-proportional sine waves.
- **Color-Based Isolation**: Fire-pixel masking ensures the knight, sword, and ground stay 100% static while the fire flickering.
- **Edge-Aware Mapping**: Detects vertical metallic edges (like the Greatsword of Artorias) to force high-density character representation.
- **Zero-Flicker Playback**: Pre-calculates 15 physics frames for smooth terminal performance at 10-12 FPS.

## Usage

### Animator (Dynamic)
Requires `Pillow`.
```bash
python3 ascii_animator.py sif.jpg 80 
```
*Press `Ctrl+C` to stop.*

### Converter (Static)
```bash
python3 ascii_converter.py sif.jpg 80 2.2 1.4
```

## Optimizations
- **Horizontal Dilation**: Uses PIL MaxFilter to beef up thin vertical structures.
- **Gamma Correction**: Calibrated at 0.7 to lift the knight's armor from deep shadows.
- **Background Filtering**: Strict <30 luminance threshold for absolute black terminal backgrounds.
