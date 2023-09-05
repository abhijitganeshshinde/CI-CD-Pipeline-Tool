# from cryptography.fernet import Fernet

# # Decryption password
# password = b"mypassword"

# # Encrypted data from the Bash script
# encrypted_data = "encrypted_data_here"

# # Decrypt using cryptography
# cipher_suite = Fernet(Fernet.generate_key())
# decrypted_data = cipher_suite.decrypt(encrypted_data.encode())

# print("Decrypted data:", decrypted_data.decode())




from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64
import services.files_service as files_service
import os
import logging
from cryptography.fernet import Fernet
import subprocess

def get_password():

    try:
        # Encrypted data from OpenSSL
        # Define a default value for decrypted_text
        decrypted_text = ""
        current_path = os.getcwd()
        isreadable,encrypdata =files_service.read_text_file(os.path.join(current_path,"files","encrypted_file","encrypted_data.txt"))
        # Print the decrypted text
        print("Decrypted Text:", encrypdata)
        return encrypdata
    except subprocess.CalledProcessError as e:
        logging.error(f"Decryption failed: {e.stderr.decode('utf-8')}")
        return None
    except Exception as e:
        logging.error(f"An error occurred while getting password: {e}")
        return None
    
     

