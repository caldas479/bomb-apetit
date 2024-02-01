#!/usr/bin/env python3

from secure_documents import *
import argparse

def handle_help():
    # Logic for help command
    help()

def handle_protect(input_file, key, public_key, output_file):
    # Logic for protect command
    print("Executing protect() command...")
    protect(input_file, key, public_key, output_file)

def handle_check(input_file, key):
    # Logic for check command
    print("Executing check() command...")
    check(input_file, key)

def handle_unprotect(input_file, key, output_file):
    # Logic for unprotect command
    print("Executing unprotect() command...")
    unprotect(input_file, key, output_file)


if __name__ == "__main__":
    global_parser = argparse.ArgumentParser(
        prog="ChefLock",
        description="Protect, Check and Unprotect your restaurant data | Manuel Albino, Tiago Caldas, Guilherme Lima | Instituto Superior Técnico 2023",
        epilog="Thanks for using %(prog)s! :)",
    )

    subparsers = global_parser.add_subparsers(
        title = "commands", help= "Command details"
    )

    protect_parser = subparsers.add_parser("protect", help="protect your file's data with a public key and a private key and output it to a file")
    protect_parser.add_argument("input_file", help="file to protect")
    protect_parser.add_argument("private_key", help="private key used to ensure authenticity")
    protect_parser.add_argument("public_key", help="public key used to encrypt mealVoucher")
    protect_parser.add_argument("output_file", help="file to output the protected data")
    protect_parser.set_defaults(func=handle_protect)

    check_parser = subparsers.add_parser("check", help="check your file's data authenticity and integrity with a public key")
    check_parser.add_argument("input_file", help="file to check")
    check_parser.add_argument("public_key", help="public key to ensure Digital Signature authenticity")
    check_parser.set_defaults(func=handle_check)

    unprotect_parser = subparsers.add_parser("unprotect", help="unprotect your file's data with a private key and output it to a file")
    unprotect_parser.add_argument("input_file", help="file to unprotect")
    unprotect_parser.add_argument("private_key", help="private key used to decrypt")
    unprotect_parser.add_argument("output_file", help="file to output the unprotected data")
    unprotect_parser.set_defaults(func=handle_unprotect)

    args = global_parser.parse_args()

    if args.func == handle_protect:
        args.func(args.input_file, args.private_key, args.public_key, args.output_file)
    elif args.func == handle_check:
        args.func(args.input_file, args.public_key)
    elif args.func == handle_unprotect:
        args.func(args.input_file, args.private_key, args.output_file)
