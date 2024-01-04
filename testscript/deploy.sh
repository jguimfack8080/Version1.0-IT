# Setting up Virtual Environment
echo "Setting up Virtual Environment..."
python3 -m venv .
source bin/activate

# Install Python Dependencies
echo "Installing Python Dependencies..."
pip install Flask flask_cors gnupg

# Running the Application
echo "Running the Application..."
python app.py

echo "The application is now running. Access it at http://127.0.0.1:5000/"
