#!/bin/bash
pkill -f "python app.py"
if [ $? -eq 0 ]; then
    echo "Die Flask App wurde deaktiviert"
fi
