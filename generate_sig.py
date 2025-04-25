import hashlib


def generate_sig(parameters: dict, session_secret_key: str) -> str:
    sorted_parameters = sorted(parameters.items())
    key_value_string = ''.join(f"{key}={value}" for key, value in sorted_parameters)
    full_string = key_value_string + session_secret_key
    return hashlib.md5(full_string.encode("utf-8")).hexdigest()