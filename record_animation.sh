#!/bin/bash

# Configuration
IMAGE_PATH="sif.jpg"
OUTPUT_CAST="animation.cast"
OUTPUT_GIF="animation.gif"
DURATION="5s"
WIDTH=80

echo "--- Starting ASCII Animation Recording ---"
echo "Recording for $DURATION..."

# Record using timeout to stop the loop after 5 seconds
# We use --foreground and --signal=INT to ensure the sub-process receives the interrupt
timeout --foreground --signal=INT $DURATION asciinema rec $OUTPUT_CAST -c "python3 ascii_animator.py $IMAGE_PATH $WIDTH"

if [ -f "$OUTPUT_CAST" ]; then
    echo "--- Recording Complete: $OUTPUT_CAST ---"
    echo "Generating high-quality GIF..."

    # Convert .cast to .gif using agg (Asciinema Gif Generator)
    # --theme: monokai for a dark theme matching GitHub's look
    # --fps-cap: 12 (to match the 1/12 sleep in ascii_animator.py)
    if command -v agg &> /dev/null
    then
        agg --theme "monokai" --fps-cap 12 --speed 1.0 "$OUTPUT_CAST" "$OUTPUT_GIF"
        if [ -f "$OUTPUT_GIF" ]; then
            echo "--- Success! GIF created: $OUTPUT_GIF ---"
            # Cleanup cast file
            rm "$OUTPUT_CAST"
        else
            echo "Error: GIF generation failed."
        fi
    else
        echo "Error: 'agg' not found. Please install it to convert .cast to .gif."
        echo "Download from: https://github.com/asciinema/agg"
    fi
else
    echo "Error: Recording failed. Ensure 'asciinema' is installed (sudo apt install asciinema)."
fi
