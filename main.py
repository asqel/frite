#!/bin/env python3
import os
import json
import shell
from getpass import getpass
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidTag
import visual

path = "data"

def make_key(passwd: str, salt: bytes) -> bytes:
	kfd = PBKDF2HMAC(
		algorithm = hashes.SHA256(),
		length = 32,
		salt = salt,
		iterations = 200000,
		backend = default_backend()
	);
	return kfd.derive(passwd.encode());

def encrypt(passwd: str, data: bytes) -> bytes:
	salt = os.urandom(16);
	key = make_key(passwd, salt);
	aes = AESGCM(key);
	nonce = os.urandom(12);
	ciphertext = aes.encrypt(nonce, data, None)
	return salt + nonce + ciphertext;

def decrypt(passwd: str, data: bytes) -> bytes:
	salt = data[:16];
	nonce = data[16:28];
	ciphertext = data[28:];

	key = make_key(passwd, salt);
	aesgcm = AESGCM(key);

	return aesgcm.decrypt(nonce, ciphertext, None);

def get_infos(passwd: str) -> dict[str, any]:
	res = {}
	with open(path, "a+b") as f:
		f.seek(0);
		data = f.read();
		if (not data):
			return {}
		res = json.loads(decrypt(passwd, data).decode("utf-8"));
	return res;

def write_infos(passwd: str, info):
	with open(path, "wb") as f:
		f.write(encrypt(passwd, json.dumps(info).encode("utf-8")));
	

def main() -> None:
	passwd = getpass("password > ");
	try:
		info = get_infos(passwd);
	except InvalidTag:
		print("Error: wrong password");
		return ;
	visual.start_visual(info)
	#shell.main(info)
	write_infos(passwd, info);

main();
