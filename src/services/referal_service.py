import random
import string


def generate_code(length=16):
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choices(chars, k=length))
