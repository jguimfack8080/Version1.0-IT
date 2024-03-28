#!/bin/bash

BASE_URL="http://127.0.0.1:5000"
USER_DB_FILE="users_db.json"
#rm $USER_DB_FILE

# Test des Endpunkts zum Erstellen eines Kontos
echo "Teste den Endpunkt zum Erstellen eines Kontos..."
curl -X POST -H "Content-Type: application/json" -d '{"account-id": "testuser", "password": "Passworduser-It-@Sicherheit@2024"}' "$BASE_URL/create"
echo

# Test des Endpunkts zum Auflisten von Konten
echo "Teste den Endpunkt zum Auflisten von Konten..."
curl -X GET "$BASE_URL/list"
echo

# Test des Anmelde-Endpunkts
echo "Teste den Anmelde-Endpunkt..."
curl -X POST -F "account-id=testuser" -F "password=Passworduser-It-@Sicherheit@2024" "$BASE_URL/login"
echo

# Test des Endpunkts zum Registrieren eines Schlüssels
echo "Teste den Endpunkt zum Registrieren eines Schlüssels..."

curl -X POST -F "account-id=testuser" -F "password=Passworduser-It-@Sicherheit@2024" -F "email-address=jeunaj3@gmail.com" -F "key-id=C42A BE97 D36A 66A3 BE08 C901 71B0 CC60 9829 C312" -F "pgp-key=@./Jordan Jeuna_jeunaj3@gmail.com-0x71B0CC609829C312-pub.asc" "$BASE_URL/register"
echo

# Extrahiere den challenge_token für "testuser"
challenge_token=$(jq -r '.testuser.challenge_token' "$USER_DB_FILE")
# Sicherstellen, dass ein challenge_token gefunden wurde
if [ -z "$challenge_token" ]; then
    echo "Kein challenge_token für 'testuser' gefunden."
    exit 1
fi

# Test des Endpunkts zum Beantworten einer Herausforderung mit dem extrahierten challenge_token
#echo "Teste den Endpunkt zum Beantworten einer Herausforderung..."
#curl -X POST -F "account-id=testuser" -F "challenge-response=$challenge_token" "$BASE_URL/respond_challenge"
#echo

#curl -X POST \
  #-F "account-id=testuser" \
  #-F "challenge-token=$challenge_token" \
  #-F "signed-pgp-key=@./pgp-key.asc" \
  #http://localhost:5000/challenge-response
