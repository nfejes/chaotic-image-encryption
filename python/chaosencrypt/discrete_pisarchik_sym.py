import numpy as np
#import chaosencrypt.pisarchik
from chaosencrypt import logistic

def DA(im,bits):
	"""
	Digital to analog.
	Converts uint8 to int.
	"""
	#return im << (bits - 8)
	y = np.array(im,dtype='uint%d'%bits)
	return y << (bits - 8)


def AD(y,bits):
	"""
	Analog to digital.
	Converts int to uint8.
	"""
	# Find invalid numbers
	mask = (2 << (bits-8)) - 1
	print('y:',y)
	print('bits',bits)
	print('mask',mask)
	invalid = np.sum((y & mask) != 0) + np.sum((y >> bits) != 0)
	if invalid > 0:
		print("Warning: %d of %d out of range values (A)" % (invalid,y.size))

	return np.right_shift(y,bits-8,np.empty(y.shape,dtype='uint8'))


def A(u,bits):
	"""
	A(u,bits)
	Map too large values into attractor.
	"""
	return u % (1 << bits)

def B(u,bits):
	"""
	B(u,bits)
	Map too small values into attractor.
	"""
	return u % (1 << bits)

def __test_key(key):
	if not isinstance(key,dict) or set(key) != set(['A','n','r','bits']):
		raise ValueError("Expected key to be dict with 'A','n','r', and 'bits'")

	if not 0 < key['A'] < 2**key['bits']:
		raise ValueError("Invalid key['a'], must be (0 < key['A'] < 2**key['bits'])")

def encrypt(im,key):
	# Convert 2D to 1D
	shape = im.shape
	x = DA(im.reshape(-1),key['bits'])

	# Encrypt
	y = encrypt_real(x,key)

	# Return reshaped image
	return y.reshape(shape)


def decrypt(im,key):
	# Convert 2D to 1D
	shape = im.shape
	x = im.reshape(-1)

	# Decrypt
	y = decrypt_real(x,key)
	print('y.dtype:',y.dtype)

	# Return reshaped image
	return AD(y,key['bits']).reshape(shape)


def encrypt_real(im,key):
	# Ensure valid key
	__test_key(key)

	# Keys
	a,n,r,bits = [key[i] for i in ('A','n','r','bits')]

	# Functions
	dl = logistic.discrete(a,bits)
	fn = lambda X: dl.step(int(X),n)

	# Work arrays
	# TODO should ideally be 'uint%d'%bytes
	y1 = np.array(im,dtype='uint64') #im.copy()
	y2 = np.empty(im.shape,dtype='uint64')

	# Iteration loop
	for j in range(r):
		y2[0] = A(fn(int(y1[-1])) + y1[0], bits)
		# Pixel loop (the int cast ensures that the addition does not overflow)
		for i in range(1,len(im)):
			y2[i] = A(fn(int(y2[i-1])) + y1[i], bits)
		# Swap arrays
		y1,y2 = y2,y1
	
	return y1



def decrypt_real(x,key):
	# Ensure valid key
	__test_key(key)

	# Keys
	a,n,r,bits = [key[i] for i in ('A','n','r','bits')]

	# Functions
	dl = logistic.discrete(a,bits)
	fn = lambda X: dl.step(int(X),n)

	# Work arrays (current and previous)
	y_c = np.array(x,dtype='uint64') #x.copy()
	y_p = np.empty(x.shape,dtype='uint64')

	# Iteration loop
	for j in range(r):
		#if not y1.dtype == np.dtype('int64'):
		#	raise ValueError('strange stuff at j=%d'%j)
		# Reverse pixel loop
		for i in range(len(x)-1,0,-1):
			y_p[i] = B(int(y_c[i]) - fn(y_c[i-1]), bits)
		# Final step
		y_p[0] = B(int(y_c[0]) - fn(y_p[-1]), bits)
		# Swap arrays
		y_p,y_c = y_c,y_p
	
	return y_c

