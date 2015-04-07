import numpy as np
import chaosencrypt.pisarchik


def encrypt(im,key,method):
	# Color image
	if len(im.shape) == 3:
		return [encrypt(im[:,:,layer],key,method) for layer in range(im.shape[2])]

	# Encrypt
	if method == 'pisarchik':
		return pisarchik.encrypt(im,key)
	else:
		raise ValueError('Invalid encryption method "%s"' % str(method))

def decrypt(im,key,method):
	# Color image
	if len(im.shape) == 3:
		return [decrypt(im[:,:,layer],key,method) for layer in range(im.shape[2])]

	# Encrypt
	if method == 'pisarchik':
		return pisarchik.decrypt(im,key)
	else:
		raise ValueError('Invalid decryption method "%s"' % str(method))
