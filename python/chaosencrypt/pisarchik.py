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
	if not isinstance(key,dict) or set(key) != set(['a','n','r']):
		raise ValueError("Expected key to be dict with 'a','n', and 'r'")

	if not 3.57 < key['a'] < 4:
		raise ValueError("Invalid key['a'], must be (3.57 < key['a'] < 4)")


def DA_org(im,x_min,x_max=None):
	"""
	Digital to analog, as defined in [Solak].
	Converts uint8 to floating point.
	"""
	if x_max is None:
		x_min,x_max = x_range(x_min)
	return x_min + (x_max - x_min) * im / 255


def DA(im,x_min,x_max=None):
	"""
	Digital to analog, modified as of definition in [Solak].
	Converts uint8 to floating point.
	"""
	if x_max is None:
		x_min,x_max = x_range(x_min)
	return x_min + (x_max - x_min) * (im + 0.5) / 256


def AD(y,x_min,x_max=None):
	"""
	Analog to digital, as defined in [Solak].
	Converts floating point to uint8.
	"""
	if x_max is None:
		x_min,x_max = x_range(x_min)

	# Fix invalid numbers
	invalid = (np.sum(y > x_max) + np.sum(y < x_min))
	y[y > x_max] = x_max
	y[y < x_min] = x_min
	if invalid > 0:
		print("Warning: %d of %d out of range values (A)" % (invalid,r.size))

	x = (y - x_min) * 256 / (x_max - x_min)
	r = np.floor(x)
	invalid = (np.sum(r > 255) + np.sum(r < 0))
	if invalid > 0:
		print("Warning: %d of %d out of range values (D)" % (invalid,r.size))
	return np.floor(x,np.empty(x.shape,dtype='uint8'))


def A(u,x_min,x_max=None):
	"""
	A(u,a), A(u,x_min,x_max)
	Map too large values into attractor, as defined in [Solak].
	"""
	if x_max is None:
		x_min,x_max = x_range(x_min)
	v = -1
	if u <= x_max:
		v = u
	elif x_max < u <= 2*x_max-x_min:
		v = u - (x_max - x_min)
	else:
		v = u - 2*(x_max - x_min)

	assert x_min < v <= x_max
	return v


def B(u,x_min,x_max=None):
	"""
	B(u,a), B(u,x_min,x_max)
	Map too small values into attractor, as defined in [Solak].
	"""
	if x_max is None:
		x_min,x_max = x_range(x_min)
	v = -1
	if u >= x_min:
		v = u
	elif -x_max + 2*x_min <= u < x_min:
		v = u + (x_max - x_min)
	else:
		v = u + 2*(x_max - x_min)

	assert x_min < v <= x_max
	return v


def logistic_map(x,a,n=1):
	for _ in range(n):
		x = a * x * (1 - x)
	return x


def encrypt(im,key):
	# Ensure valid key
	__test_key(key)

	# Recode to floating point
	enc = DA(im,key['a'])

	# Encrypt
	if len(im.shape) == 3:
		# Colors?
		for i in range(3):
			encrypt_float(enc[:,:,i],key)
	else:
		encrypt_float(enc,key)
	return enc


def encrypt_float(msg,key):
	# Ensure valid key
	__test_key(key)

	# Keys
	a,n,r = [key[i] for i in ('a','n','r')]

	# Variables and functions (notation from Solak)
	x_min,x_max = x_range(a)
	fn = lambda x: logistic_map(x,a,n)

	# Flatten image
	y = msg.flat

	# Iteration loop
	for j in range(r):
		# Pixel loop
		for i in range(len(y)):
			y[i] = A(fn(y[i-1]) + y[i], x_min, x_max)


def decrypt(im,key):
	# Ensure valid key
	__test_key(key)

	# Allocate copy
	dec = im.copy()

	# Decrypt
	if len(im.shape) == 3:
		# Colors?
		for i in range(3):
			decrypt_float(dec[:,:,i],key)
	else:
		decrypt_float(dec,key)

	# Return uint8 image
	return AD(dec,key['a'])


def decrypt_float(msg,key):
	# Ensure valid key
	__test_key(key)

	# Keys
	a,n,r = [key[i] for i in ('a','n','r')]

	# Variables and functions (notation from Solak)
	x_min,x_max = x_range(a)
	fn = lambda x: logistic_map(x,a,n)

	# Work arrays (current and previous)
	y = msg.flat

	# Iteration loop
	for j in range(r):
		# Reverse pixel loop
		for i in range(len(y)-1,-1,-1):
			y[i] = B(y[i] - fn(y[i-1]), x_min, x_max)

