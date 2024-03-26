from flask import Flask, request, jsonify
from flask_cors import CORS  # Importer CORS
import hashlib
import uuid
import json
import os
import time
import gnupg
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from smtplib import SMTP
from datetime import datetime, timedelta
import utils
import account_routes

app = Flask(__name__)
CORS(app) 

gpg = gnupg.GPG()

@app.route('/create', methods=['POST'])
def create_account_route():
    return account_routes.create_account()

@app.route('/list', methods=['GET'])
def list_accounts_route():
    return account_routes.list_accounts()

@app.route('/login', methods=['POST'])
def login_accounts_route():
    return account_routes.login()

@app.route('/register', methods=['POST'])
def register_key():
    # Suppose la fonction utils.load_data() est définie pour charger les données des utilisateurs depuis une source quelconque
    users_db = utils.load_data()
    data = request.form
    account_id = data.get('account-id')
    password = data.get('password')
    email_address = data.get('email-address')
    
    
    # Récupérer le key ID fourni par l'utilisateur et le formater en supprimant les espaces
    user_key_id = data.get('key-id')
    key_id = user_key_id.replace(" ", "")
    
    # Vérifier si le key ID est vide après suppression des espaces
    if not key_id:
        return jsonify({'error': 'Key ID invalide'}), 400

    if not account_id or not password or not email_address or not key_id:
        return jsonify({'error': 'Fehlende Pflichtfelder'}), 400

    pgp_key_file = request.files.get('pgp-key')
    if not pgp_key_file:
        return jsonify({'error': 'PGP key file is required'}), 400

    # Vérifier l'utilisateur
    user_data = utils.find_user(account_id, users_db)
    if not user_data:
        return jsonify({'error': 'Konto nicht gefunden!'}), 404

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if user_data['hashed_password'] != hashed_password:
        return jsonify({'error': 'Authentifizierung fehlgeschlagen!'}), 401  # Unauthorized

    # Vérifier si l'adresse e-mail est déjà enregistrée
    registered_keys = user_data.get('registered_keys', {})
    if email_address in registered_keys:
        return jsonify({'error': 'E-Mail Adresse bereits registriert!'}), 409  # Conflict

    # Importer la clé PGP
    import_result = gpg.import_keys(pgp_key_file.read())
    if not import_result.results or 'fingerprint' not in import_result.results[0]:
        return jsonify({'error': 'Ungültiger PGP-Schlüssel'}), 400

    fingerprint = import_result.results[0]['fingerprint']

    # Extraire le key ID de l'empreinte de la clé et le formater
    imported_key_id = fingerprint.upper()
    print("Key ID extrait de la clé PGP: ", imported_key_id)
    # Vérifier si le key ID correspond à celui fourni par l'utilisateur
    if key_id != imported_key_id:
        return jsonify({'error': 'Le key ID fourni ne correspond pas à celui du PGP key importé'}), 400

    # Générer et stocker le challenge token avec une date d'expiration de 10 secondes
    expiration_time = datetime.now() + timedelta(seconds=300)
    challenge_token = {'token': str(uuid.uuid4()), 'expiration_time': expiration_time.isoformat()}  # Convertir en ISO 8601
    user_data['challenge_token'] = challenge_token
    user_data['pending_key_fingerprint'] = fingerprint  # Stocker l'empreinte de la clé en attente
    user_data['pending_email'] = email_address
    utils.save_data(users_db)

    # Définir une fonction pour vérifier si le token a expiré
    def is_token_expired():
        return datetime.now() > expiration_time

    # Envoi de l'e-mail avec la pièce jointe
    challenge_email_body = f"Your challenge token is: {challenge_token['token']}\nPlease respond to this email with the correct token to complete the registration of your PGP key."
    encrypted_challenge_email_body = gpg.encrypt(challenge_email_body, fingerprint)
    
    if not encrypted_challenge_email_body.ok:
        return jsonify({'error': 'Fehler beim Verschlüsseln der Challenge-Nachricht'}), 500
    
    # Construire le nom de fichier avec le format spécifié pour l'enregistrement et l'envoi par e-mail
    filename = f"{account_id}-{email_address}-{key_id}.asc"
    # Envoyer le fichier PGP en tant que pièce jointe dans l'e-mail
    utils.send_email(email_address, "[ACME-PGP] Register", str(encrypted_challenge_email_body), attachment=pgp_key_file.filename)
     
     # Enregistrer le fichier joint dans le répertoire "keys"
    keys_directory = "keys"
    if not os.path.exists(keys_directory):
        os.makedirs(keys_directory)

    public_keys_path = os.path.join(keys_directory, filename)

    # Revenir au début du fichier
    pgp_key_file.seek(0)

    # Enregistrer le fichier avec son contenu
    pgp_key_file.save(public_keys_path)


    # Attendre que le token expire
    while not is_token_expired():
        time.sleep(1)  # Attendre 1 seconde avant de vérifier à nouveau l'expiration du token

    # Vérifier si le token a expiré
    if is_token_expired():
        # Supprimer le token expiré de la base de données
        del user_data['challenge_token']
        utils.save_data(users_db)
        return jsonify({'error': 'Votre token n\'est plus valide'}), 400

    return jsonify({'message': 'Challenge sent. Please respond to complete registration'}), 200



if __name__ == '__main__':
    app.run(debug=True)
