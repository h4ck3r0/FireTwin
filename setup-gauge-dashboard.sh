#!/bin/bash

# Setup script to link gauge_status.json to NextJS public directory

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
GAUGE_READER_DIR="$PROJECT_DIR/gauge_reader"
PUBLIC_DIR="$PROJECT_DIR/public"

# Create public directory if it doesn't exist
mkdir -p "$PUBLIC_DIR"

# Create a symlink from public to gauge_status.json
if [ ! -L "$PUBLIC_DIR/gauge_status.json" ]; then
    ln -s "$GAUGE_READER_DIR/gauge_status.json" "$PUBLIC_DIR/gauge_status.json"
    echo "✓ Created symlink: $PUBLIC_DIR/gauge_status.json -> $GAUGE_READER_DIR/gauge_status.json"
else
    echo "✓ Symlink already exists"
fi

# Also create a fallback copy mechanism if symlinks don't work
cat > "$GAUGE_READER_DIR/sync_to_public.sh" << 'EOF'
#!/bin/bash
# Continuously sync gauge_status.json to public folder
while true; do
    if [ -f "gauge_status.json" ]; then
        cp gauge_status.json ../public/gauge_status.json 2>/dev/null
    fi
    sleep 0.5
done
EOF

chmod +x "$GAUGE_READER_DIR/sync_to_public.sh"
echo "✓ Created sync script for fallback"
echo ""
echo "Setup complete! You can now:"
echo "1. Run the gauge reader: python firedesk_integration.py"
echo "2. Run the dashboard: npm run dev"
echo "3. View live pressure at http://localhost:3000"
