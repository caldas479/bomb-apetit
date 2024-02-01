import json
import copy

from datetime import datetime
from .algos import generate_signature, encrypt_with_public_key, decrypt_with_private_key, check_security

def readJSONFromFile(file_path):
    """Reads JSON data from a file.

    :param file_path: Path to the JSON file.
    :type file_path: str
    :return: JSON data from the file.
    :rtype: dict or None
    """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return 
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in file {file_path}: {e}")
        return

def writeJSONToFile(file_path, data):
    """Writes JSON data to a file.

    :param file_path: Path to the JSON file.
    :type file_path: str
    :param data: JSON data to be written.
    :type data: dict
    """
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return 

def protect(file_path, private_key_path, public_key_path, output_file_path):
    """Protects a JSON document by encrypting and adding a digital signature.

    :param file_path: Path to the input JSON file.
    :type file_path: str
    :param private_key_path: Path to the private key file.
    :type private_key_path: str
    :param public_key_path: Path to the public key file.
    :type public_key_path: str
    :param output_file_path: Path to the output protected JSON file.
    :type output_file_path: str
    """
    try:
        json_object = readJSONFromFile(file_path)
        
        obj = protect_json(json_object,private_key_path,public_key_path)

        # Write JSON object with security to the document
        writeJSONToFile(output_file_path, obj)

        print(f"The document {file_path} is protected!")

    except Exception as e:
        print(e)
        return


def check(file_path, key_path):
    """Checks the integrity and authenticity of a protected JSON document.

    :param file_path: Path to the input JSON file.
    :type file_path: str
    :param key_path: Path to the key file for verification.
    :type key_path: str
    """
    try:
        json_object = readJSONFromFile(file_path)

        result = check_json(json_object,key_path)

        print("Document is protected!") if result else print("Document is not protected!")
    
    except Exception as e:
            print(e)
            return
    

def unprotect(file_path, private_key_path, output_file_path):
    """Removes protection from a JSON document by decrypting and removing security details.

    :param file_path: Path to the input protected JSON file.
    :type file_path: str
    :param key_path: Path to the key file for decryption.
    :type key_path: str
    :param output_file_path: Path to the output unprotected JSON file.
    :type output_file_path: str
    """
    try:
        json_object = readJSONFromFile(file_path)

        obj = unprotect_json(json_object,private_key_path)
        
        # Write JSON object without security to the document
        writeJSONToFile(output_file_path, obj)
        
        print(f"The document {file_path} is not protected!")
    
    except Exception as e:
        print(e)
        return
        
def help():
    """Displays help information for using ChefLock."""
    print(f"Help for ChefLock:")
    print(f"ChefLock help - Print this help message")
    print(f"ChefLock protect (input-file) (key) (output-file) ... - Protect the input file")
    print(f"ChefLock check (input-file) (key) - Check the input file for protection")
    print(f"ChefLock unprotect (input-file) (key) (output-file) ... - Unprotect the input file")


def protect_json(json_object, private_key_path, public_key_path):
    """Protects a JSON object by encrypting and adding a digital signature.

    :param json_objcet: Object to protect.
    :type file_path: JSON object
    :param private_key_path: Path to the private key file.
    :type private_key_path: str
    :param public_key_path: Path to the public key file.
    :type public_key_path: str
    """
    try:
        obj = copy.deepcopy(json_object)
        mealVoucher = obj.get("restaurantInfo", {}).get("mealVoucher")
        
        if mealVoucher is not None:
            encrypted_mealvoucher = encrypt_with_public_key(mealVoucher, public_key_path)
            #convert the cipher to hexadecimal in order to be JSON-serializable
            obj["restaurantInfo"]["mealVoucher"] = encrypted_mealvoucher.hex()

        # Add timestamp --> freshness
       # obj["timestamp"] = datetime.now().isoformat()

        # Generate and add digital signature --> authenticity
        signature = generate_signature(json.dumps(obj), private_key_path)
        obj["signature"] = signature

        return obj

    except Exception as e:
        print(e)
        return


def check_json(json_object, key_path):
    """Checks the integrity and authenticity of a protected JSON object.

    :param file_path: Path to the input JSON file.
    :type file_path: str
    :param key_path: Path to the key file for verification.
    :type key_path: str
    """
    
    obj = copy.deepcopy(json_object)
    if "signature" not in obj:
        return False

    # Store received hmac from document if exists
    signature_received = obj["signature"]

    # Remove hmac from object
    obj.pop("signature")

    # Verify if document is protected
    return check_security(signature_received, obj, key_path)


def unprotect_json(json_object, private_key_path):
    """Removes protection from a JSON object by decrypting and removing security details.

    :param json_objcet: Object to protect.
    :type file_path: JSON object
    :param private_key_path: Path to the key file for decryption.
    :type private_key_path: str
    """
    obj = copy.deepcopy(json_object)

    mealVoucher = obj.get("restaurantInfo", {}).get("mealVoucher")
    
    if mealVoucher is not None:
        decrypted_mealvoucher = decrypt_with_private_key(mealVoucher, private_key_path)
        obj["restaurantInfo"]["mealVoucher"] = decrypted_mealvoucher

    #Remove timestamp and hmac
    if "signature" in obj:
        obj.pop("signature")
        #obj.pop("timestamp")
    
    return obj
    
    
def help():
    """Displays help information for using ChefLock."""
    print(f"Help for ChefLock:")
    print(f"ChefLock help - Print this help message")
    print(f"ChefLock protect (input-file) (key) (output-file) ... - Protect the input file")
    print(f"ChefLock check (input-file) (key) - Check the input file for protection")
    print(f"ChefLock unprotect (input-file) (key) (output-file) ... - Unprotect the input file")

"""
protect('../intro/inputs/document1.json', '../keys/restaurants/bk/private_key.pem', '../keys/users/user1/public_key.pem', '../intro/outputs/doc1_user1_protected')
protect('../intro/inputs/document1.json', '../keys/restaurants/bk/private_key.pem', '../keys/users/user2/public_key.pem', '../intro/outputs/doc1_user2_protected')
protect('../intro/inputs/document1.json', '../keys/restaurants/bk/private_key.pem', '../keys/users/user3/public_key.pem', '../intro/outputs/doc1_user3_protected')

protect('../intro/inputs/document2.json', '../keys/restaurants/mc/private_key.pem', '../keys/users/user1/public_key.pem', '../intro/outputs/doc2_user1_protected')
protect('../intro/inputs/document2.json', '../keys/restaurants/mc/private_key.pem', '../keys/users/user2/public_key.pem', '../intro/outputs/doc2_user2_protected')
protect('../intro/inputs/document2.json', '../keys/restaurants/mc/private_key.pem', '../keys/users/user3/public_key.pem', '../intro/outputs/doc2_user3_protected')

protect('../intro/inputs/document3.json', '../keys/restaurants/kfc/private_key.pem', '../keys/users/user1/public_key.pem', '../intro/outputs/doc3_user1_protected')
protect('../intro/inputs/document3.json', '../keys/restaurants/kfc/private_key.pem', '../keys/users/user2/public_key.pem', '../intro/outputs/doc3_user2_protected')
protect('../intro/inputs/document3.json', '../keys/restaurants/kfc/private_key.pem', '../keys/users/user3/public_key.pem', '../intro/outputs/doc3_user3_protected')
"""