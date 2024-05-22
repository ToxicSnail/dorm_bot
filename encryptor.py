from cryptography.fernet import Fernet

def write_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    return open("secret.key", "rb").read()

def encrypt_and_save_password(password):
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    fernet = Fernet(key)
    encrypted_password = fernet.encrypt(password.encode())
    with open("secret.txt", "wb") as encrypted_file:
        encrypted_file.write(encrypted_password)

password = input("Введите пароль, который нужно зашифровать: ")
encrypt_and_save_password(password)
