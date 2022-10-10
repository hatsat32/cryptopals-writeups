"""
Orel Ben-Reuven
https://cryptopals.com/sets/6/challenges/46

RSA parity oracle

When does this ever happen?
This is a bit of a toy problem, but it's very helpful for understanding what RSA is doing
(and also for why pure number-theoretic encryption is terrifying).
Trust us, you want to do this before trying the next challenge. Also, it's fun.

Generate a 1024 bit RSA key pair.

Write an oracle function that uses the private key to answer the question "is the plaintext of this message even or odd"
(is the last bit of the message 0 or 1).
Imagine for instance a server that accepted RSA-encrypted messages and checked the parity of their
decryption to validate them, and spat out an error if they were of the wrong parity.

Anyways: function returning true or false based on whether the decrypted plaintext was even or odd, and nothing else.

Take the following string and un-Base64 it in your code (without looking at it!)
and encrypt it to the public key, creating a ciphertext:

VGhhdCdzIHdoeSBJIGZvdW5kIHlvdSBkb24ndCBwbGF5IGFyb3VuZCB3aXRoIHRoZSBGdW5reSBDb2xkIE1lZGluYQ==

With your oracle function, you can trivially decrypt the message.

Here's why:
- RSA ciphertexts are just numbers.
  You can do trivial math on them. You can for instance multiply a ciphertext by the RSA-encryption of another number;
  the corresponding plaintext will be the product of those two numbers.
- If you double a ciphertext (multiply it by (2**e)%n), the resulting plaintext will (obviously) be either even or odd.
- If the plaintext after doubling is even, doubling the plaintext didn't wrap the modulus ---
  the modulus is a prime number. That means the plaintext is less than half the modulus.

You can repeatedly apply this heuristic, once per bit of the message, checking your oracle function each time.

Your decryption function starts with bounds for the plaintext of [0,n].

Each iteration of the decryption cuts the bounds in half;
either the upper bound is reduced by half, or the lower bound is.

After log2(n) iterations, you have the decryption of the message.

Print the upper bound of the message as a string at each iteration; you'll see the message decrypt "hollywood style".

Decrypt the string (after encrypting it to a hidden private key) above.
"""

import base64
import math
from fractions import Fraction

from Utils.PublicKey import RSA


class Oracle:
    def __init__(self):
        self.rsa = RSA(1024)

    def validate_msg(self, cipher: int) -> bool:
        """ Return True if the parity bit is zero """
        msg = self.rsa.decrypt(cipher, output_bytes=False)
        return not msg & 1


def decrypt_attack(oracle, cipher: int):
    n = oracle.rsa.n
    low_frac, high_frac = Fraction(0), Fraction(1)  # fraction out of n
    low, high = 0, n

    num_repetitions = n.bit_length()
    for i in range(num_repetitions):
        # double the message
        cipher = (cipher * oracle.rsa.encrypt(2, input_bytes=False)) % n

        # check parity bit
        res = oracle.validate_msg(cipher)

        # the plaintext is less than half the modulus
        if res:
            high_frac = (high_frac - low_frac) / 2 + low_frac
            high = n * high_frac

        # the plaintext is more than half the modulus
        else:
            low_frac = (high_frac - low_frac) / 2 + low_frac
            low = n * low_frac

        msg = RSA.integer_to_bytes_squeezed(math.floor(high))
        print(f'Iteration {i}: {msg}')

    return msg


def main():
    oracle = Oracle()

    # given message
    msg = 'VGhhdCdzIHdoeSBJIGZvdW5kIHlvdSBkb24ndCBwbGF5IGFyb3VuZCB3aXRoIHRoZSBGdW5reSBDb2xkIE1lZGluYQ=='
    msg = base64.b64decode(msg)

    # encrypt with public key
    cipher = oracle.rsa.encrypt(msg)

    # decrypt the cipher
    recovered_message = decrypt_attack(oracle, cipher)
    print(f'{recovered_message=}')


if __name__ == '__main__':
    main()
