#!/bin/bash

# Prerequisites
echo "Installing Prerequisites..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx

# Install Python Dependencies
echo "Installing Python Dependencies..."


# Setting up Virtual Environment
echo "Setting up Virtual Environment..."
python3 -m venv App
source App/bin/activate
pip install Flask flask_cors gnupg

# Running the Application
echo "Running the Application..."
python App/app.py

echo "The application is now running. Access it at http://127.0.0.1:5000/"

