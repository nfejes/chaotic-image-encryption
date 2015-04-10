import numpy as np
#import chaosencrypt.pisarchik
from chaosencrypt import logistic

def x_range(a):
	return (4 * a**2 - a**3) / 16, a / 4

def bitexpand(A,bits):
	"""
	Expand uint8 to uint[bits].
	"""
	assert A.dtype.kind == 'u'

	# Convert
	B = np.array(A,dtype='uint%d'%bits)
	B <<= (bits - 8)
	return B


def bitreduce(A):
	"""
	Reduce uintX to uint8.
	"""
	assert A.dtype.kind == 'u'
	bits = 8 * A.itemsize

	# Find invalid numbers
	mask = (1 << (bits-8)) - 1
	#assert ( np.sum((A & mask) != 0) + np.sum((A >> bits) != 0) ) == 0
	if ( np.sum((A & mask) != 0) + np.sum((A >> bits) != 0) ) > 0:
		print('Warning: invalid:', np.sum((A & mask) != 0) , np.sum((A >> bits) != 0))

	# Convert
	return np.right_shift(A,bits-8,np.empty(A.shape,dtype='uint8'))


def uint2float(A,bits,x_min,x_max=None):
	# FIXME
	"""
	Digital to analog, modified as of definition in [Solak].
	Converts uint8 to floating point.
	"""
	if x_max is None:
		x_min,x_max = x_range(x_min)
	return x_min + (x_max - x_min) * A / ((1 << bits) - 1)
	#return x_min + (x_max - x_min) * (A + 0.5) / 256


def float2uint(A,bits,x_min,x_max=None):
	# FIXME
	"""
	Analog to digital, as defined in [Solak].
	Converts floating point to uint8.
	"""
	if x_max is None:
		x_min,x_max = x_range(x_min)

	# Invalid numbers?
	assert (np.sum(A > x_max) + np.sum(A < x_min)) == 0

	v = np.around((A - x_min) * ((1 << bits) - 1) / (x_max - x_min))
	#print(v,(A - x_min) , ((1 << bits) - 1) , (x_max - x_min))
	return v


def A(u,bits):
	"""
	A(u,bits)
	Map too large values into attractor.
	"""
	mask = np.uint64((1 << bits) - 1)
	print(type(bits),type(mask),type(u))
	return u & mask


def B(u,bits):
	"""
	B(u,bits)
	Map too small values into attractor.
	"""
	mask = np.uint64((1 << bits) - 1)
	print(type(bits),type(mask),type(u))
	return u & mask


def __test_key(key):
	if not isinstance(key,dict) or set(key) != set(['a','n','r','bits']):
		raise ValueError("Expected key to be dict with 'a','n','r', and 'bits'")

	if not 3.57 < key['a'] < 4:
		raise ValueError("Invalid key['a'], must be (3.57 < key['a'] < 4)")


def encrypt(im,key):
	# Ensure valid key
	__test_key(key)

	# Allocate encoded message
	enc = bitexpand(im,key['bits'])

	# Encrypt
	encrypt_message(enc,key)

	# Return encoded message
	return enc


def decrypt(msg,key):
	# Ensure valid key
	__test_key(key)

	# Don't alter original message
	msg = msg.copy()

	# Decrypt
	decrypt_message(msg,key)

	return bitreduce(msg)

def generate_fn(a,n,bits):
	x_min,x_max = x_range(a)
	dl = logistic.logistic(a)
	MAX = ((1 << bits) - 1)
	dx = x_max - x_min
	k = MAX / dx

	def fn(u):
		x = x_min + u / k
		for _ in range(n):
			x = a * x * (1 - x)
		assert 0 <= x <= 1
		return int(np.around((u - x_min) * k))
	return fn
		

	

def encrypt_message(msg,key):
	# Ensure valid key
	__test_key(key)

	# Keys
	a,n,r,bits = [key[i] for i in ('a','n','r','bits')]

	# Constants and functions
	fn = generate_fn(a,n,bits)
	y = msg.flat

	# Iteration loop
	for j in range(r):
		# Pixel loop (int cast prevents overflow)
		#v = int(fn(y[-1])) + y[0]
		#msg[0] = A(v, bits)
		# Pixel loop
		# note: when i == 0, then y[i] = int(fn(y[-1])) + y[0]
		for i in range(len(y)):
			y0 = y[i]
			v = fn(y[i-1]) + y[i]
			y[i] = A(v, bits)
			assert y0 == B(y[i] - fn(y[i-1]), bits)



def decrypt_message(msg,key):
	# Ensure valid key
	__test_key(key)

	# Keys
	a,n,r,bits = [key[i] for i in ('a','n','r','bits')]

	# Constants and functions
	fn = generate_fn(a,n,bits)
	y = msg.flat

	# Iteration loop
	for j in range(r):
		# Pixel loop (reverse)
		# note: when i == 0, then y[i] = B(y[0] - int(fn(y[-1])), bits)
		for i in range(len(y)-1,-1,-1):
			y[i] = B(y[i] - fn(y[i-1]), bits)

