#!/bin/bash
# Continuously sync gauge_status.json to public folder
while true; do
    if [ -f "gauge_status.json" ]; then
        cp gauge_status.json ../public/gauge_status.json 2>/dev/null
    fi
    sleep 0.5
done
