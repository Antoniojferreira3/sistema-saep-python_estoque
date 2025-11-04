import bcrypt

# Mude a senha aqui se quiser
password = "123456"

hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

print("Copie este hash para seu script SQL:")
print(hashed.decode('utf-8'))