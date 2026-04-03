#!/bin/bash

# Configuration
IMAGE_PATH="sif.jpg"
OUTPUT_CAST="animation.cast"
OUTPUT_GIF="animation.gif"
WIDTH=80

echo "--- Starting Silent ASCII Animation Recording ---"

# Record using the new --record flag for silent setup and one-shot execution
# We no longer need 'timeout' because the script self-terminates after one cycle
asciinema rec --overwrite $OUTPUT_CAST -c "python3 ascii_animator.py $IMAGE_PATH $WIDTH --record"

if [ -f "$OUTPUT_CAST" ]; then
    echo "--- Recording Complete: $OUTPUT_CAST ---"
    echo "Generating high-quality GIF..."

    # Convert .cast to .gif using agg (Asciinema Gif Generator)
    if command -v agg &> /dev/null
    then
        # Using --fps-cap 12 to match the animation's internal timing
        agg --theme "monokai" --fps-cap 12 --speed 1.0 "$OUTPUT_CAST" "$OUTPUT_GIF"
        if [ -f "$OUTPUT_GIF" ]; then
            echo "--- Success! GIF created: $OUTPUT_GIF ---"
            # Cleanup
            rm "$OUTPUT_CAST"
        else
            echo "Error: GIF generation failed."
        fi
    else
        echo "Error: 'agg' not found. Please install it to convert .cast to .gif."
    fi
else
    echo "Error: Recording failed."
fi
