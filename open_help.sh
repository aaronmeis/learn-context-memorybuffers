#!/bin/bash
# Open help documentation in default browser
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open docs/help/index.html
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open docs/help/index.html
else
    echo "Please open docs/help/index.html manually in your browser"
fi
