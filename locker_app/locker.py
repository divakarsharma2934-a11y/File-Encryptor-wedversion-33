#!/usr/bin/env python3
"""
locker.py - File Encryption and Decryption Utility
Supports XOR, Base64, and combined XOR+Base64 encryption
"""

import argparse
import base64
import sys
import os
from datetime import datetime
from itertools import cycle
import codecs


def log(message):
    "Print timestamped log message"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def read_file(path):
    "Read file in binary mode"
    try:
        with open(path, "rb") as f:
            return f.read()
    except FileNotFoundError:
        log(f"ERROR: Input file not found: {path}")
        sys.exit(1)
    except PermissionError:
        log(f"ERROR: Permission denied reading file: {path}")
        sys.exit(1)
    except Exception as e:
        log(f"ERROR: Failed to read file: {e}")
        sys.exit(1)


def write_file(path, data):
    "Write data to file in binary mode"
    try:
        # auto-create directory
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
    except PermissionError:
        log(f"ERROR: Permission denied writing file: {path}")
        sys.exit(1)
    except Exception as e:
        log(f"ERROR: Failed to write file: {e}")
        sys.exit(1)


def xor_encrypt(data, key):
    "XOR encrypt/decrypt data"
    if len(key) == 0:
        raise ValueError("Key cannot be empty")

    # Optimization: Use list comprehension or generator which is slightly faster than loop with append
    # But for large data, we should ideally use a C extension or numpy. 
    # Since we are sticking to stdlib, we can try to process in chunks if we change the architecture,
    # but for now let's just make the loop faster.
    
    # Using itertools.cycle is cleaner and often faster
    from itertools import cycle
    return bytes(b ^ k for b, k in zip(data, cycle(key)))


def xor_decrypt(data, key):
    "XOR decrypt = XOR encrypt"
    return xor_encrypt(data, key)


def b64_encrypt(data):
    """
    Encode data using Base64.
    """
    try:
        return base64.b64encode(data)
    except Exception as e:
        raise ValueError(f"Base64 encoding failed: {e}")


def b64_decrypt(data):
    """
    Decode Base64 encoded data.
    """
    try:
        return base64.b64decode(data)
    except Exception as e:
        raise ValueError(f"Base64 decoding failed: {e}")


import hashlib

SIGNATURE = b"LOCKER_V1"


def get_key_hash(key):
    "Hash the key using SHA-256 to ensure unique keys for similar passwords"
    return hashlib.sha256(key).digest()


def encrypt_data(data, key, algo):
    """
    Encrypt data using the specified algorithm and key.
    Adds a signature to the data for verification during decryption.
    """
    # Hash the key to prevent "1111" == "11" issues
    hashed_key = get_key_hash(key)
    
    # Prepend signature for verification
    data_to_encrypt = SIGNATURE + data
    
    if algo == "xor":
        return xor_encrypt(data_to_encrypt, hashed_key)
    elif algo == "base64":
        # For base64, we just encode the signed data
        return b64_encrypt(data_to_encrypt)
    elif algo == "xor+base64":
        return b64_encrypt(xor_encrypt(data_to_encrypt, hashed_key))
    else:
        raise ValueError(f"Invalid algorithm: {algo}")


# Streaming Support

def chunked_reader(f, chunk_size=8190):
    """Yield chunks from a file-like object."""
    while True:
        data = f.read(chunk_size)
        if not data:
            break
        yield data

def xor_generator(iterator, key):
    """Yield XOR encrypted chunks from input iterator."""
    keystream = cycle(key)
    for chunk in iterator:
        yield bytes(b ^ k for b, k in zip(chunk, keystream))

def b64_encode_generator(iterator):
    """Yield Base64 encoded chunks from input iterator."""
    encoder = codecs.getincrementalencoder("base64")()
    for chunk in iterator:
        yield encoder.encode(chunk, final=False)
    yield encoder.encode(b"", final=True)

def encrypt_stream(file_obj, key, algo):
    """
    Stream encryption from a file object.
    Returns a generator yielding encrypted bytes.
    """
    hashed_key = get_key_hash(key)
    
    def source_stream():
        yield SIGNATURE
        yield from chunked_reader(file_obj)
    
    if algo == "xor":
        yield from xor_generator(source_stream(), hashed_key)
    elif algo == "base64":
        yield from b64_encode_generator(source_stream())
    elif algo == "xor+base64":
        yield from b64_encode_generator(xor_generator(source_stream(), hashed_key))
    else:
        raise ValueError(f"Invalid algorithm: {algo}")


def decrypt_data(data, key, algo):
    """
    Decrypt data using the specified algorithm and key.
    Verifies the signature to ensure data integrity and correct key usage.
    """
    hashed_key = get_key_hash(key)
    
    decrypted = None
    if algo == "xor":
        decrypted = xor_decrypt(data, hashed_key)
    elif algo == "base64":
        decrypted = b64_decrypt(data)
    elif algo == "xor+base64":
        decrypted = xor_decrypt(b64_decrypt(data), hashed_key)
    else:
        raise ValueError(f"Invalid algorithm: {algo}")
        
    # Verify signature
    if not decrypted.startswith(SIGNATURE):
        raise ValueError("Invalid password or corrupted file")
        
    # Return data without signature
    return decrypted[len(SIGNATURE):]


def validate_args(args):
    "Validate CLI arguments"
    if args.encrypt and args.decrypt:
        log("ERROR: Cannot use both --encrypt and --decrypt")
        sys.exit(1)

    if not args.encrypt and not args.decrypt:
        log("ERROR: Must specify --encrypt OR --decrypt")
        sys.exit(1)

    valid_algos = ["xor", "base64", "xor+base64"]
    if args.algo not in valid_algos:
        log(f"ERROR: Invalid algorithm. Must be one of: {', '.join(valid_algos)}")
        sys.exit(1)

    if not os.path.exists(args.input):
        log(f"ERROR: Input file does not exist: {args.input}")
        sys.exit(1)

    if not os.path.isfile(args.input):
        log(f"ERROR: Input must be a file (not directory)")
        sys.exit(1)

    if not args.key:
        log("ERROR: Key cannot be empty")
        sys.exit(1)


def main():
    """
    Main entry point for the command-line interface.
    Parses arguments and executes the requested encryption/decryption operation.
    """
    parser = argparse.ArgumentParser(
        description="File Encryption & Decryption Utility"
    )

    parser.add_argument("--encrypt", action="store_true", help="Encrypt file")
    parser.add_argument("--decrypt", action="store_true", help="Decrypt file")
    parser.add_argument("--algo", required=True, help="xor / base64 / xor+base64")
    parser.add_argument("--key", required=True, help="Encryption key")
    parser.add_argument("--input", required=True, help="Input file")
    parser.add_argument("--output", required=True, help="Output file")

    args = parser.parse_args()
    validate_args(args)

    key = args.key.encode("utf-8")
    data = read_file(args.input)

    if args.encrypt:
        log(f"Encrypting using: {args.algo}")
        result = encrypt_data(data, key, args.algo)
    else:
        log(f"Decrypting using: {args.algo}")
        result = decrypt_data(data, key, args.algo)

    write_file(args.output, result)
    log(f"SUCCESS: Output saved → {args.output}")


if __name__ == "__main__":
    main()
