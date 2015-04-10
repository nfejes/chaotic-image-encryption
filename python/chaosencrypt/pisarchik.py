import numpy as np

def x_range(a):
	return (4 * a**2 - a**3) / 16, a / 4

def __test_key(key):
	# Ensure valid key
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

	# Convert 2D to 1D
	shape = im.shape
	x = DA(im.reshape(-1),key['a'])

	# Encrypt
	y = encrypt_real(x,key)

	# Return reshaped image
	return y.reshape(shape)


def encrypt_real(im,key):
	# Ensure valid key
	__test_key(key)

	# Keys
	a,n,r = [key[i] for i in ('a','n','r')]

	# Variables and functions (notation from Solak)
	x_min,x_max = x_range(a)
	fn = lambda x: logistic_map(x,a,n)

	# Allocate array
	y = im.copy()

	# Iteration loop
	for j in range(r):
		# First step
		y[0] = A(fn(y[-1]) + y[0], x_min, x_max)
		# Pixel loop
		for i in range(1,len(im)):

			fny = fn(y[i-1])
			t = fny + y[i]
			print('A:',(t - fny) - y[i])
			while (t - fny) < y[i]:
				t = np.nextafter(t,np.inf)
				print('B:',(t - fny) - y[i])
			while (t - fny) > y[i]:
				t = np.nextafter(t,-np.inf)
				print('C:',(t - fny) - y[i])

			assert t - fny == y[i]

			y[i] = A(t, x_min, x_max)
			#y[i] = A(fn(y[i-1]) + y[i], x_min, x_max)
	
	return y


def decrypt(im,key):
	# Ensure valid key
	__test_key(key)

	# Convert 2D to 1D
	shape = im.shape
	x = im.reshape(-1)

	# Decrypt
	y = decrypt_real(x,key)

	# Return reshaped image
	return AD(y,key['a']).reshape(shape)


def decrypt_real(x,key):
	# Ensure valid key
	__test_key(key)

	# Keys
	a,n,r = [key[i] for i in ('a','n','r')]

	# Variables and functions (notation from Solak)
	x_min,x_max = x_range(a)
	fn = lambda x: logistic_map(x,a,n)

	# Work arrays (current and previous)
	y = x.copy()

	# Iteration loop
	for j in range(r):
		# Reverse pixel loop
		for i in range(len(x)-1,0,-1):
			y[i] = B(y[i] - fn(y[i-1]), x_min, x_max)
		# Final step
		y[0] = B(y[0] - fn(y[-1]), x_min, x_max)
	
	return y

