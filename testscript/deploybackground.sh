python3 -m venv App
source App/bin/activate
pip install Flask flask_cors gnupg

# Running the Application
echo "Running the Application..."
#python App/app.py

# Running the Application in the background
nohup python App/app.py --host=0.0.0.0 --port=5000 &

if [ $? -eq 0 ]; then
    echo "The application is now running in the background."
    echo "You can close this terminal, and the application will continue to run."
else
    echo "Failed to start the application."
fi
