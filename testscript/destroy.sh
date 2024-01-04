#!/bin/bash
pkill -f "python App/app.py"
if [ $? -eq 0 ]; then
    echo "Die Flask App wurde deaktiviert"
fi
