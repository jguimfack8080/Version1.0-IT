# -*- coding: utf-8 -*-
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
import imaplib
import email
from email import policy
import re
import pgpy
from pgpy.constants import SignatureType
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


def sign_and_export_key(public_key_path, user_account_id, email_address, key_Id):
    # Chemins des fichiers de clés
    private_key_path = 'my-private-key.asc'  # Remplacez par le chemin de votre clé privée
    output_dir = 'signedKey'  # Répertoire où sera enregistrée la clé publique signée
    output_path = os.path.join(output_dir, f"signed-key-{user_account_id}-{key_Id}.asc")  

    # Vérifier si le répertoire existe, sinon le créer
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Charger votre propre clé privée
    my_private_key, _ = pgpy.PGPKey.from_file(private_key_path)

    # Assurez-vous que cette ligne est correcte avec la passphrase de votre clé privée
    passphrase = 'Jordan'
    assert my_private_key.is_protected

    # Déverrouille la clé privée avec la passphrase
    with my_private_key.unlock(passphrase):
        # Charger la clé publique de votre ami
        user_public_key, _ = pgpy.PGPKey.from_file(public_key_path)

        # Signer chaque User ID associé à la clé publique de votre ami
        for user_id in user_public_key.userids:
            # Créer une signature de certification Positive_Cert
            signature = my_private_key.certify(user_id, SignatureType.Positive_Cert)
            # Et attacher la signature au User ID
            user_id |= signature

    # Sauvegarder la clé publique signée
    with open(output_path, 'w') as f:
        f.write(str(user_public_key))  # Écrit la représentation ASCII armorée de la clé

    print(f"La clé publique a été signée et enregistrée dans '{output_path}'")
    # Construire le corps de l'e-mail de notification
    notification_email_body = f"Moin {user_account_id},\n\nIhre PGP-Schlüsselregistrierung wurde erfolgreich abgeschlossen. \n\nIm Anhang finden Sie Ihren signierten Schlüssel. \n\n\n Grüße vom Team-06 (Nelly und Jordan)"

    # Envoi de l'email (remplacer ceci avec votre propre fonction d'envoi d'e-mails)
    utils.send_email(email_address, "[ACME-PGP] Registrierung erfolgreich", notification_email_body, attachment=output_path)



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

    challenge_token_encrypted = gpg.encrypt(challenge_token['token'], fingerprint)
    print("Voici la valeur du token de l'utilisateur: ", challenge_token['token'])
    # Envoi de l'e-mail avec la pièce jointe
    challenge_email_body = (
    f"Moin {account_id},\n\n"
    f"Wichtig: Ein Teil der Nachricht ist verschlüsselt. Sie müssen die Nachricht mit Ihrem privaten Schlüssel entschlüsseln, um zu bestätigen, dass der öffentliche Schlüssel Ihnen gehört. Dazu benötigen Sie Ihren privaten Schlüssel.\n\n"
    f"Um die Registrierung Ihres PGP-Schlüssels abzuschließen, antworten Sie bitte auf diese E-Mail mit dem Challenge-Token im angegebenen Format.\n\n"
    f"Im Betreff Ihrer E-Mail sollte stehen: 'Re: [ACME-PGP] Response'. Im Text der E-Mail geben Sie bitte folgendes Format ein:\n"
    f"Challenge-token: 'Ihr per E-Mail erhaltenes Token'\n\n"
    f"Sobald Sie mit dem korrekten Token geantwortet haben und die verschlüsselte Nachricht entschlüsselt haben, ist Ihre Registrierung abgeschlossen. Sie erhalten dann eine Benachrichtigungs-E-Mail, die die erfolgreiche Registrierung Ihres PGP-Schlüssels bestätigt und auch Ihren signierten Schlüssel im Anhang enthält.\n\n"
    f"Ihr Challenge-Token ist in dieser E-Mail enthalten, jedoch koennen Sie ihn erst sehen, sobald Sie die E-Mail entschlüsselt haben. Ihr Challenge-Token lautet: {challenge_token['token']}\n\n"
    f"Vielen Dank für Ihr Verständnis und Ihre Zusammenarbeit.\n\n"
    f"Grüße von Nelly und Jordan"
)


    encrypted_challenge_email_body = gpg.encrypt(challenge_email_body, fingerprint)
    
    if not encrypted_challenge_email_body.ok:
        return jsonify({'error': 'Fehler beim Verschlüsseln der Challenge-Nachricht'}), 500
    
    # Construire le nom de fichier avec le format spécifié pour l'enregistrement et l'envoi par e-mail
    filename = f"{account_id}-{email_address}-{key_id}.asc"
    # Envoyer le fichier PGP en tant que pièce jointe dans l'e-mail
    utils.send_email(email_address, "[ACME-PGP] Register", str(encrypted_challenge_email_body), attachment=pgp_key_file.filename)
     
     # Enregistrer le fichier joint dans le répertoire "keys"
    keys_directory = "public_keys_users"
    if not os.path.exists(keys_directory):
        os.makedirs(keys_directory)

    public_keys_path = os.path.join(keys_directory, filename)

    # Revenir au début du fichier
    pgp_key_file.seek(0)

    # Enregistrer le fichier avec son contenu
    pgp_key_file.save(public_keys_path)


    # Attendre que le token expire
    user = 'jguimfackjeuna'
    password = 'Jeunaj3'
    host = 'smail.hs-bremerhaven.de'
    # Connectez-vous au serveur IMAP et récupérez les e-mails
    imap = imaplib.IMAP4_SSL(host)
    imap.login(user, password)
    imap.select('inbox')

    while not is_token_expired():
        
        # Recherchez les e-mails dans la boîte de réception
        tmp, messages = imap.search(None, 'ALL')
        messages = messages[0].split()[::-1]  # Inverser l'ordre de la liste des numéros de messages
        
        # Parcourez chaque e-mail dans la boîte de réception
        for num in messages:
            tmp, data = imap.fetch(num, '(RFC822)')
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email, policy=policy.default)
            
            # Vérifiez si l'e-mail correspond à la réponse à la challenge
            if msg['Subject'] == 'Re: [ACME-PGP] Response':
                #Extraire l'adresse mail de celui qui a envoye le mail
                sender_email_for_response = re.search(r'<(.*?)>', msg['From']).group(1)

                print ("La valeur de sender_email_for_response est: ", sender_email_for_response)
                if sender_email_for_response == email_address:
                    payload = ""
                    for part in msg.walk():
                        if part.get_content_type() == 'text/plain':
                            payload += part.get_payload(decode=True).decode()
                    match = re.search(r'Challenge-token: "(.*?)"', payload)
                    if match:
                        token_value = match.group(1)
                        # Si le token correspond, envoyez un e-mail de notification et renvoyez une réponse JSON appropriée
                        if token_value == user_data['challenge_token']['token']:
                            #Dans la methode suivante, le mail de confirmatiotion est envoye
                            #sign_and_export_key(imported_key_id, email_address, account_id)
                            sign_and_export_key(public_keys_path, account_id, email_address, imported_key_id)
                            del user_data['challenge_token']
                            del user_data['pending_key_fingerprint']
                            del user_data['pending_email']
                            utils.save_data(users_db)
                            return jsonify({'message': 'Registration successful. Notification email sent.'}), 200
                        else:
                        # Si le token ne correspond pas, attendez 1 seconde avant de vérifier à nouveau
                            time.sleep(1)
                else:
                    print ("L'adresse mail de l'expediteur: ", sender_email_for_response, "est differente de l'adresse de register: ", email_address)
        # Fermez la connexion IMAP
    imap.close()
    imap.logout()

    # Si le token a expiré sans correspondance, supprimez le token expiré de la base de données
    # et renvoyez une réponse JSON appropriée
    if is_token_expired():
        del user_data['challenge_token']
        del user_data['pending_key_fingerprint']
        del user_data['pending_email']
        utils.save_data(users_db)
        return jsonify({'error': 'Votre token n\'est plus valide'}), 400

    return jsonify({'message': 'Herausforderung gesendet. Bitte antworten Sie, um die Registrierung abzuschließen.'}), 200

if __name__ == '__main__':
    app.run(debug=True)
