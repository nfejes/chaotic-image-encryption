import numpy as np


def x_range(a):
	"""
	Get the valid x range (x_min,x_max) for the given [a] parameter.
	"""
	return (4 * a**2 - a**3) / 16, a / 4


def __test_key(key):
	"""
	Assert that the given key is valid.
	"""
	if not isinstance(key,dict) or set(key) != set(['a','n','r','bits']):
		raise ValueError("Expected key to be dict with 'a','n','r', and 'bits'")

	if not 3.57 < key['a'] < 4:
		raise ValueError("Invalid key['a'], must be (3.57 < key['a'] < 4)")


def bitexpand(A,bits):
	"""
	Expand uint8 to uint[bits].
	"""
	assert A.dtype.kind == 'u'

	# Convert
	B = np.array(A,dtype='uint%d'%bits)
	B <<= (bits - 8)
	return B


def bitreduce(A,bitassert=False):
	"""
	bitreduce(A,bitassert=False)
	Reduce uintX to uint8.
	if [bitassert] is true, assert that all lower bits are 0.
	"""
	assert A.dtype.kind == 'u'
	bits = 8 * A.itemsize

	# Invalid input?
	if bitassert:
		mask = (1 << (bits-8)) - 1
		assert np.sum((A & mask) != 0) == 0

	# Convert
	return np.right_shift(A,bits-8,np.empty(A.shape,dtype='uint8'))


def uint2float(A,bits,x_min,x_max=None):
	"""
	Converts uint[bits] to the corresponding floating point value in the range [x_min,x_max].
	"""
	if x_max is None:
		x_min,x_max = x_range(x_min)
	return x_min + (x_max - x_min) * A / ((1 << bits) - 1)


def float2uint(A,bits,x_min,x_max=None):
	"""
	Converts floating-points to uint[bits] mapped to fill [x_min,x_max].
	"""
	if x_max is None:
		x_min,x_max = x_range(x_min)

	# Invalid numbers?
	assert (np.sum(A > x_max) + np.sum(A < x_min)) == 0

	return np.around((A - x_min) * ((1 << bits) - 1) / (x_max - x_min))


def A(u,bits):
	"""
	A(u,bits)
	Map too large values into attractor.
	This function differs from the one defined in [Pisarchik].
	"""
	return u & ((1 << bits) - 1)


def B(u,bits):
	"""
	B(u,bits)
	Map too small values into attractor.
	This function differs from the one defined in [Pisarchik].
	"""
	return u & ((1 << bits) - 1)


def encrypt(im,key):
	# Ensure valid key
	__test_key(key)

	# Allocate encoded message
	enc = bitexpand(im,key['bits'])

	# Encrypt
	if len(im.shape) == 3:
		# Colors?
		for i in range(3):
			encrypt_message(enc[:,:,i],key)
	else:
		encrypt_message(enc,key)

	# Return encoded message
	return enc


def decrypt(msg,key):
	# Ensure valid key
	__test_key(key)

	# Don't alter original message
	msg = msg.copy()

	# Decrypt
	if len(msg.shape) == 3:
		# Colors?
		for i in range(3):
			decrypt_message(msg[:,:,i],key)
	else:
		decrypt_message(msg,key)

	return bitreduce(msg,True)


def __generate_fn(a,n,bits):
	x_min,x_max = x_range(a)
	MAX = ((1 << bits) - 1)
	dx = x_max - x_min
	k = MAX / dx

	def fn(u):
		x = x_min + u / k
		for _ in range(n):
			x = a * x * (1 - x)
		assert 0 <= x <= 1
		return int(np.around((x - x_min) * k))
	return fn


def encrypt_message(msg,key):
	# Ensure valid key
	__test_key(key)

	# Keys
	a,n,r,bits = [key[i] for i in ('a','n','r','bits')]

	# Constants and functions
	fn = __generate_fn(a,n,bits)
	y = msg.flat

	# Iteration loop
	for j in range(r):
		# Pixel loop (int cast prevents overflow)
		# note: when i == 0, then y[i] = int(fn(y[-1])) + y[0]
		for i in range(len(y)):
			y[i] = A(fn(y[i-1]) + int(y[i]), bits)


def encrypt_message_assert(msg,key):
	# Ensure valid key
	__test_key(key)

	# Keys
	a,n,r,bits = [key[i] for i in ('a','n','r','bits')]

	# Constants and functions
	fn = __generate_fn(a,n,bits)
	y = msg.flat

	# Iteration loop
	for j in range(r):
		for i in range(len(y)):
			y0 = y[i]
			v = fn(y[i-1]) + int(y[i])
			y[i] = A(v, bits)
			assert y0 == B(int(y[i]) - fn(y[i-1]), bits)


def decrypt_message(msg,key):
	# Ensure valid key
	__test_key(key)

	# Keys
	a,n,r,bits = [key[i] for i in ('a','n','r','bits')]

	# Constants and functions
	fn = __generate_fn(a,n,bits)
	y = msg.flat

	# Iteration loop
	for j in range(r):
		# Pixel loop (reverse)
		# note: when i == 0, then y[i] = B(y[0] - int(fn(y[-1])), bits)
		for i in range(len(y)-1,-1,-1):
			y[i] = B(int(y[i]) - fn(y[i-1]), bits)

