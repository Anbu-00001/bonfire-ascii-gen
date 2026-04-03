# Bonfire ASCII Generator

A high-fidelity terminal-based ASCII animator and converter specifically tuned for Soulslike art. Features localized fire physics, wind sway, and true-color ANSI support.

## Key Features
- **Base Frame Compositing**: The sword hilt is rendered from a static "Perfect Base Plate" and overlaid onto the animation. This ensures the sword is 100% immune to fire physics, preventing thinning or flickering.
- **Cinematic 24-Frame Loop**: Optimized 24-frame pre-calculation engine for a silky-smooth, cinematic rotation.
- **Realistic Wind Dynamics**: Flames 'lick' toward the left and settle back to center, simulating a consistent environmental breeze from the right.
- **80% Flicker Clamping**: Calibrated flicker logic ensures the bonfire maintains a constant, 'crispy' glow without ever dropping into blackout frames.
- **Edge-Aware Mapping**: Specifically detects vertical metallic edges to force high-density character representation.

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
