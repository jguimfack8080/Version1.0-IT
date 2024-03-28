import pgpy
from pgpy.constants import SignatureType

# Chemins des fichiers de clés
private_key_path = 'my-private-key.asc'  # Remplacez par le chemin de votre clé privée
public_key_path = 'friend_public_key.asc'    # Chemin du fichier de clé publique de votre ami
output_path = 'signed-my-friends-public-key.asc'  # Fichier où sera enregistrée la clé publique signée

# Charger votre propre clé privée
my_private_key, _ = pgpy.PGPKey.from_file(private_key_path)

# Assurez-vous que cette ligne est correcte avec la passphrase de votre clé privée
passphrase = 'Jordan'
assert my_private_key.is_protected

# Déverrouille la clé privée avec la passphrase
with my_private_key.unlock(passphrase):
    # Charger la clé publique de votre ami
    friends_public_key, _ = pgpy.PGPKey.from_file(public_key_path)

    # Signer chaque User ID associé à la clé publique de votre ami
    for user_id in friends_public_key.userids:
        # Créer une signature de certification Positive_Cert
        signature = my_private_key.certify(user_id, SignatureType.Positive_Cert)
        # Et attacher la signature au User ID
        user_id |= signature

# Sauvegarder la clé publique signée
with open(output_path, 'w') as f:
    f.write(str(friends_public_key))  # Écrit la représentation ASCII armorée de la clé

print(f"La clé publique a été signée et enregistrée dans '{output_path}'")