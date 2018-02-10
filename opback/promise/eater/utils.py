# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Leann Mak
# Email: leannmak@139.com
# Date: Aug 11, 2016
#
# This is the utility module of eater package.

from .. import app
import md5
from passlib.apps import custom_app_context as pwd_context


def md5_password(password):
    """
        Hash salted password with md5 algorithm.
    """
    secreted_password = password + app.config['SECRET_KEY']
    salted_password = md5.new(secreted_password).hexdigest() +\
        app.config['PSW_SALT']
    return md5.new(salted_password).hexdigest()


def hash_password(password):
    """
        Use encrypt to store md5-hashed password.
    """
    return pwd_context.encrypt(md5_password(password))


def verify_password(password, password_hash):
    """
        Verify and update the md5-hashed password stored.
    """
    password = md5_password(password)
    valid, new_hash = pwd_context.verify_and_update(
        password, password_hash)
    if valid:
        if new_hash:
            password_hash = new_hash
    return valid, password_hash


import binascii
import rsa


def decrypt(privatekey, ciphertext):
    with open(privatekey) as privatefile:
        p = privatefile.read()
        pri = rsa.PrivateKey.load_pkcs1(p)
    ciphertextAscii = binascii.a2b_hex(ciphertext)
    plaintext = rsa.decrypt(ciphertextAscii, pri)
    return plaintext


def encrypt(publickey, plaintext):
    with open(publickey) as publicfile:
        p = publicfile.read()
        pub = rsa.PublicKey.load_pkcs1(p)
    ciphertextAscii = rsa.encrypt(plaintext, pub)
    ciphertext = binascii.b2a_hex(ciphertextAscii)
    return ciphertext
