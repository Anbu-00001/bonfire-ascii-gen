# Bonfire ASCII Generator

A high-fidelity terminal-based ASCII animator and converter specifically tuned for Soulslike art. Features localized fire physics, wind sway, and true-color ANSI support.

## Key Features
- **Constrained Sword Mapping**: The hilt and blade use a dynamic "Heavy Palette" (`+=*#@W`). This allows the metal to realistically react to firelight pulses while ensuring it never thinned or drops to light characters like `.` or `:`.
- **Cinematic 24-Frame Loop**: Optimized 24-frame pre-calculation engine for a silky-smooth, cinematic rotation.
- **Realistic Wind Dynamics**: Flames 'lick' toward the left and settle back to center, simulating a consistent environmental breeze from the right.
- **80% Flicker Clamping**: Calibrated flicker logic ensures the bonfire maintains a constant, 'crispy' glow without ever dropping into blackout frames.
- **Metallic Darkening**: A subtle luminance multiplier is applied specifically to the sword to give the metal a heavier, more atmospheric texture compared to the fire.

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
