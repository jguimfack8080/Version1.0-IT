from flask import request, jsonify
import hashlib
import uuid
import json
import os
import gnupg
from datetime import datetime, timedelta
import utils

def create_account():
    users_db = utils.load_data()
    data = request.json
    original_account_id = data.get('account-id')
    password = data.get('password')

    if not original_account_id or not password:
        return jsonify({'error': 'Konto-ID und Passwort sind erforderlich'}), 400

    if original_account_id in users_db:
        return jsonify({'error': 'Es existiert schon ein Konto mit diesem Konto-ID'}), 409  # 409 Conflict

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    modified_account_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, original_account_id))

    user_data = {
        'original_account_id': original_account_id,
        'hashed_password': hashed_password,
        'modified_account_id': modified_account_id,
        'registered_keys': {}  # Initialize an empty dictionary for registered keys
    }

    users_db[original_account_id] = user_data
    utils.save_data(users_db)

    return jsonify({'account-id': original_account_id, 'modified-account-id': modified_account_id}), 201

def list_accounts():
    print("Endpoint /list called")  # Add this line for debugging
    users_db = utils.load_data()
    account_list = {
        user_data['original_account_id']: {
            'creator-account-id': user_data['original_account_id'],
            'modified-account-id': user_data['modified_account_id']
        }
        for user_data in users_db.values()
    }
    return jsonify(account_list), 200

def login():
    users_db = utils.load_data()  # Laden der Benutzerdatenbank
    data = request.form
    account_id = data.get('account-id')
    password = data.get('password')

    # Überprüfen, ob Konto-ID und Passwort bereitgestellt wurden
    if not account_id or not password:
        return jsonify({'error': 'Konto-ID und Passwort sind erforderlich'}), 400

    # Suche nach dem Benutzer in der Datenbank
    user_data = utils.find_user(account_id, users_db)
    if not user_data:
        return jsonify({'error': 'Konto nicht gefunden'}), 404

    # Überprüfen des Passworts
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if user_data['hashed_password'] != hashed_password:
        return jsonify({'error': 'Authentifizierung fehlgeschlagen'}), 401  # Unauthorized

    # Erfolgreiche Authentifizierung
    # Hier können Sie weitere Schritte durchführen, wie z.B. ein Token generieren
    return jsonify({'message': 'Erfolgreich angemeldet'}), 200


