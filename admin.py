import hashlib,os
def generate_combined_hash(email: str, key: str) -> str:
    # Ensure the email is in lowercase to avoid case sensitivity issues
    email = email.lower()
    
    # Combine the email and key
    combined = email + key
    
    # Create a SHA-256 hash object
    hash_object = hashlib.sha256()
    
    # Update the hash object with the combined string encoded as bytes
    hash_object.update(combined.encode('utf-8'))
    
    # Get the hexadecimal representation of the hash
    hash_hex = hash_object.hexdigest()
    
    return hash_hex

def append_hash_to_file(hash_code: str, file_path: str):
    # Open the file in append mode
    with open(file_path, 'a+') as file:
        # Append the hash to the file
        file.write(hash_code + '\n')

def read_file(file_path: str):
    # Check if the file exists
    if not os.path.exists(file_path):
        # Create an empty file if it doesn't exist
        with open(file_path, 'w') as file:
            return ''
    
    # Open the file in read mode
    with open(file_path, 'r') as file:
        # Read and return the content of the file
        return file.read()

def is_email_in_file(email: str, key: str, file_path: str) -> bool:
    # Generate the hash for the email and key
    hash_code = generate_combined_hash(email, key)
    
    # Read the content of the file
    file_content = read_file(file_path)
    
    # Check if the hash is in the file content
    return hash_code in file_content.splitlines()


def contains_uva_email(email: str) -> bool:
    return '@uva.nl' in email or '@student.uva.nl' in email
