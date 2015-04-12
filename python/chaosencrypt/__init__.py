import numpy as np
import chaosencrypt.pisarchik
import chaosencrypt.discrete_pisarchik


def encrypt(im,key,method):
	# Encrypt
	if method == 'pisarchik':
		return pisarchik.encrypt(im,key)
	if method == 'discrete_pisarchik':
		return discrete_pisarchik.encrypt(im,key)
	else:
		raise ValueError('Invalid encryption method "%s"' % str(method))


def decrypt(im,key,method):
	# Decrypt
	if method == 'pisarchik':
		return pisarchik.decrypt(im,key)
	if method == 'discrete_pisarchik':
		return discrete_pisarchik.decrypt(im,key)
	else:
		raise ValueError('Invalid decryption method "%s"' % str(method))
