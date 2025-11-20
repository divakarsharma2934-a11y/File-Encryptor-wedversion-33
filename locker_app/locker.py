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

    result = bytearray()
    key_len = len(key)

    for i, byte in enumerate(data):
        result.append(byte ^ key[i % key_len])

    return bytes(result)


def xor_decrypt(data, key):
    "XOR decrypt = XOR encrypt"
    return xor_encrypt(data, key)


def b64_encrypt(data):
    try:
        return base64.b64encode(data)
    except Exception as e:
        raise ValueError(f"Base64 encoding failed: {e}")


def b64_decrypt(data):
    try:
        return base64.b64decode(data)
    except Exception as e:
        raise ValueError(f"Base64 decoding failed: {e}")


def encrypt_data(data, key, algo):
    if algo == "xor":
        return xor_encrypt(data, key)
    elif algo == "base64":
        return b64_encrypt(data)
    elif algo == "xor+base64":
        return b64_encrypt(xor_encrypt(data, key))
    else:
        raise ValueError(f"Invalid algorithm: {algo}")


def decrypt_data(data, key, algo):
    if algo == "xor":
        return xor_decrypt(data, key)
    elif algo == "base64":
        return b64_decrypt(data)
    elif algo == "xor+base64":
        return xor_decrypt(b64_decrypt(data), key)
    else:
        raise ValueError(f"Invalid algorithm: {algo}")


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
