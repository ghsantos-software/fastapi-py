# Funções de senha.
# hash_password  -> transforma a senha em "hash" (texto embaralhado, irreversível)
# verify_password -> confere se a senha digitada bate com o hash guardado
import bcrypt


def hash_password(password: str) -> str:
    # o bcrypt só aceita até 72 bytes; cortamos o excedente
    return bcrypt.hashpw(password.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8")[:72], hashed.encode("utf-8"))