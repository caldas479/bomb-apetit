from datetime import datetime

import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes

import json

THRESHOLD = 2

def generate_RSA(who):
    """Generate RSA key pair for encryption and decryption.

    Args:
        who (str): Identifier for the keys to be generated.

    Generates an RSA key pair (public and private keys) and saves them to files 
    named 'public_key.pem' and 'private_key.pem' in the 'keys/who/' directory.

    Returns:
        None
    """
    # Generate an RSA key pair
    key = rsa.generate_private_key(
        public_exponent=65537,  # Commonly used value for RSA
        key_size=2048,  # Key size in bits
        backend=default_backend()
    )

    # Get the public key in PEM format
    public_key = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Get the private key in PEM format
    private_key = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Save the keys to files (optional)
    with open('../keys/{}/public_key.pem'.format(who), 'wb') as f:
        f.write(public_key)

    with open('../keys/{}/private_key.pem'.format(who), 'wb') as f:
        f.write(private_key)

    print("Public and Private keys generated successfully for {}.".format(who))

def generate_signature(file_data, private_key_path):
    """Generate a digital signature for a given file data using a private key.

    Args:
        file_data (str): The content of the file as a string.
        private_key_path (str): Path to the private key file.

    Generates a digital signature for the file data using the private key located 
    at 'private_key_path'.

    Returns:
        str: Base64 encoded signature.
    """
    file_bytes = file_data.encode('utf-8')

    print(f"Reading key from {private_key_path}...")
    with open(private_key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )

    print(f"Signing the message")
    signature_bytes = private_key.sign(
        file_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
        )

    signature = base64.b64encode(signature_bytes).decode('utf-8')
    print(f"Generated Signature: {signature}")
    return signature

def verify_signature(signature_base64, json_object, public_key_path):
    """Verify the signature authenticity of a JSON object.

    Args:
        signature_base64 (str): Base64 encoded signature to be verified.
        json_object (dict): JSON object to be checked.
        public_key_path (str): Path to the public key file.

    Verifies the authenticity of the signature using the public key located at 'public_key_path'.

    Return (boolean): True if the signature is authentic.
    """

    print(f"Reading key from {public_key_path}...")
    with open(public_key_path, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )

    signature = base64.b64decode(signature_base64)
    message = json.dumps(json_object)

    try:
        print("Verifying Signature...")
        public_key.verify(
            signature,
            message.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        print("Signature is valid. The message is authentic.")
        return True
    except Exception as e:
        print(f"Signature verification failed. The message is not authentic")
        return False

def check_security(signature_base64, json_object, public_key_path):
    """Verify the security of a JSON object including freshness and signature authenticity.

    Args:
        signature_base64 (str): Base64 encoded signature to be verified.
        json_object (dict): JSON object to be checked.
        public_key_path (str): Path to the public key file.

    Verifies the freshness of the JSON object based on its timestamp, checks the 
    authenticity of the signature using the public key located at 'public_key_path'.

    Return (boolean): True if object is fresh and authentic
    """
    #print(f"Reading key from {public_key_path}...")
    #with open(public_key_path, "rb") as key_file:
    #    public_key = serialization.load_pem_public_key(
    #        key_file.read(),
    #        backend=default_backend()
    #    )

    #timestamp = json_object["timestamp"]

    #print("Verifying Freshness")
    #message_timestamp = datetime.fromisoformat(timestamp)
    #timestamp_now = datetime.now()

    #if (timestamp_now - message_timestamp).total_seconds() > THRESHOLD:
     #   print(f"The Freshness verification failed. The message is not authentic")
    #    return False
    #else:
    #    print("Freshness was successfully verified")
    
    return verify_signature(signature_base64, json_object, public_key_path)
        

def encrypt_with_public_key(data, public_key_path):
    """Encrypt data using a public key.

    Args:
        data (dict): Data to be encrypted (JSON serializable).
        public_key_path (str): Path to the public key file.

    Encrypts the input 'data' using the public key located at 'public_key_path'.

    Returns:
        bytes: Encrypted data.
    """
    #convert the JSON dict to str
    jsondata = json.dumps(data)

    print(f"Reading key from {public_key_path}...")
    with open(public_key_path, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )

    ciphertext = public_key.encrypt(
        jsondata.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

def decrypt_with_private_key(ciphertext, private_key_path):
    """Decrypt data using a private key.

    Args:
        ciphertext (str): Ciphertext to be decrypted.
        private_key_path (str): Path to the private key file.

    Decrypts the input 'ciphertext' using the private key located at 'private_key_path'.

    Returns:
        dict: Decrypted JSON object.
    """
    
    print(f"Reading key from {private_key_path}...")
    with open(private_key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )

    # Convert the hexadecimal string to bytes
    ciphertext_bytes = bytes.fromhex(ciphertext)

    # Decrypt the ciphertext
    decrypted_data = private_key.decrypt(
        ciphertext_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Convert the decrypted data to a JSON object
    json_object = json.loads(decrypted_data.decode('utf-8'))
    return json_object

def create_timestamp():
    return json.dumps(datetime.now().isoformat())

def check_timestamp(timestamp_old):
    timestamp_now = datetime.now()

    if (timestamp_now - datetime.fromisoformat(json.loads(timestamp_old))).total_seconds() > THRESHOLD:
       print(f"The Freshness verification failed. The message is not authentic")
       return False
    else:
       print("Freshness was successfully verified")
       return True
    
def write_key_to_file(serialized_key, file_path):
    key_bytes = serialized_key.encode('utf-8')
    with open(file_path, 'wb') as file:
        file.write(key_bytes)

def read_key(file_path):
    with open(file_path, 'rb') as file:
        rsa_key = serialization.load_pem_public_key(file.read(), backend=default_backend())

    # Serialize the RSA key to PEM format
    serialized_key = rsa_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return serialized_key.decode('utf-8')

