#!/bin/bash

# Prerequisites
echo "Checking and Installing Prerequisites..."

# List of packages to install
packages=("python3" "python3-pip" "python3-venv" "nginx" "jq")

# Loop through the packages
for package in "${packages[@]}"; do
    if dpkg -s $package &> /dev/null; then
        echo "$package is already installed."
    else
        echo "Installing $package..."
        sudo apt update
        sudo apt install -y $package

        # Check if the installation was successful
        if [ $? -eq 0 ]; then
            echo "$package has been successfully installed."
        else
            echo "Failed to install $package. Please check for errors."
        fi
    fi
done



