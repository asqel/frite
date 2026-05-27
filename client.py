import ssl
import socket
import hashlib
import sys

HOST = "localhost"
PORT = 42924

# --- Charger le certificat attendu (celui du serveur) ---
with open("cert.pem", "r") as f:
	pem_data = f.read()

# Convertir PEM → DER
expected_der = ssl.PEM_cert_to_DER_cert(pem_data)
expected_fingerprint = hashlib.sha256(expected_der).hexdigest()

print("Fingerprint attendu :", expected_fingerprint)

# --- Créer contexte SSL sans vérification CA ---
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

# --- Connexion ---
with socket.create_connection((HOST, PORT)) as sock:
	with context.wrap_socket(sock, server_hostname=HOST) as ssock:

		# Récupérer certificat serveur (en DER)
		server_cert = ssock.getpeercert(binary_form=True)
		server_fingerprint = hashlib.sha256(server_cert).hexdigest()

		print("Fingerprint serveur :", server_fingerprint)

		# Vérification stricte
		if server_fingerprint != expected_fingerprint:
			print("❌ Certificat invalide ! Arrêt.")
			sys.exit(1)

		print("✅ Certificat vérifié. Connexion sécurisée.")

		# Exemple requête HTTP
		request = (
			"POST / HTTP/1.1\r\n"
			f"Host: {HOST}\r\n"
			"Content-Type: application/json\r\n"
			"Content-Length: 18\r\n"
			"\r\n"
			'{"password":"x"}'
		)

		ssock.sendall(request.encode())
		response = ssock.recv(10)
		print("Réponse serveur :")
		print(response.decode())

