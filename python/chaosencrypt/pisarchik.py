import numpy as np

def DA_org(im,x_min,x_max=None):
	"""
	Digital to analog, as defined in [Solak].
	Converts uint8 to floating point.
	"""
	if x_max is None:
		a = x_min
		x_min = (4 * a**2 - a**3) / 16
		x_max = a / 4
	return x_min + (x_max - x_min) * im / 255

def DA(im,x_min,x_max=None):
	"""
	Digital to analog, modified as of definition in [Solak].
	Converts uint8 to floating point.
	"""
	if x_max is None:
		a = x_min
		x_min = (4 * a**2 - a**3) / 16
		x_max = a / 4
	return x_min + (x_max - x_min) * (im + 0.5) / 256

def AD(y,x_min,x_max=None):
	"""
	Analog to digital, as defined in [Solak].
	Converts floating point to uint8.
	"""
	if x_max is None:
		a = x_min
		x_min = (4 * a**2 - a**3) / 16
		x_max = a / 4
	x = (y - x_min) * 255 / (x_max - x_min)
	return np.around(x,0,np.empty(x.shape,dtype='uint8'))

def A(u,x_min,x_max=None):
	"""
	A(u,a), A(u,x_min,x_max)
	Map too large values into attractor, as defined in [Solak].
	"""
	if x_max is None:
		a = x_min
		x_min = (4 * a**2 - a**3) / 16
		x_max = a / 4
	if u <= x_max:
		return u
	if x_max < u <= 2*x_max-x_min:
		return u - (x_max - x_min)
	else:
		return u - 2*(x_max - x_min)
		
def B(u,x_min,x_max=None):
	"""
	B(u,a), B(u,x_min,x_max)
	Map too small values into attractor, as defined in [Solak].
	"""
	if x_max is None:
		a = x_min
		x_min = (4 * a**2 - a**3) / 16
		x_max = a / 4
	if u >= x_min:
		return u
	if -x_max + 2*x_min <= u < x_min:
		return u + (x_max - x_min)
	else:
		return u + 2*(x_max - x_min)

def logistic_map(x,a,n=1):
	for _ in range(n):
		x = a * x * (1 - x)
	return x

def encrypt(im,key):
	# Convert 2D to 1D
	shape = im.shape
	x = DA(im.reshape(-1),key['a'])

	# Encrypt
	y = encrypt_real(x,key)

	# Return reshaped image
	return y.reshape(shape)

def encrypt_real(im,key):
	# Ensure valid key
	if not isinstance(key,dict) or set(key) != set(['a','n','r']):
		raise ValueError("Expected key to be dict with 'a','n', and 'r'")

	if not 3.57 < key['a'] < 4:
		raise ValueError("Invalid key['a'], must be (3.57 < key['a'] < 4)")

	# Keys
	a,n,r = [key[i] for i in ('a','n','r')]

	# Variables and functions (notation from Solak)
	x_min = (4 * a**2 - a**3) / 16
	x_max = a / 4
	fn = lambda x: logistic_map(x,a,n)

	# Allocate arrays
	y1 = im.copy()
	y2 = np.empty(y1.shape)

	# Iteration loop
	for j in range(r):
		y2[0] = A(fn(y1[-1]) + y1[0], x_min, x_max)
		# Pixel loop
		for i in range(1,len(im)):
			y2[i] = A(fn(y2[i-1]) + y1[i], x_min, x_max)
		# Swap arrays
		y1,y2 = y2,y1
	
	return y1


def decrypt(im,key):
	# Convert 2D to 1D
	shape = im.shape
	x = im.reshape(-1)

	# Decrypt
	y = decrypt_real(x,key)

	# Return reshaped image
	return AD(y,key['a']).reshape(shape)


def decrypt_real(x,key):
	# Ensure valid key
	if not isinstance(key,dict) or set(key) != set(['a','n','r']):
		raise ValueError("Expected key to be dict with 'a','n', and 'r'")

	if not 3.57 < key['a'] < 4:
		raise ValueError("Invalid key['a'], must be (3.57 < key['a'] < 4)")

	# Keys
	a,n,r = [key[i] for i in ('a','n','r')]

	# Variables and functions (notation from Solak)
	x_min = (4 * a**2 - a**3) / 16
	x_max = a / 4
	fn = lambda x: logistic_map(x,a,n)

	# Work arrays (current and previous)
	y_c = x.copy()
	y_p = np.empty(x.shape)

	# Iteration loop
	for j in range(r):
		# Reverse pixel loop
		for i in range(len(x)-1,0,-1):
			y_p[i] = B(y_c[i] - fn(y_c[i-1]), x_min, x_max)
		# Final step
		y_p[0] = B(y_c[0] - fn(y_p[-1]), x_min, x_max)
		# Swap arrays
		y_p,y_c = y_c,y_p
	
	return y_c

