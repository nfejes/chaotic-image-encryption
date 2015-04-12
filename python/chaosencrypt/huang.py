import numpy as np
from numpy import cos,arccos

def __test_key(key):
	"""
	Assert that the given key is valid.
	"""
	exkey = ['x','p','q','xy','r','t','N']
	if not isinstance(key,dict) or set(key) != set(exkey):
		raise ValueError("Expected key to be dict with keys: %s" % str(exkey))

	# t must be integer
	assert key['t'] == int(key['t'])
	# TODO validate keys
	#if not 3.57 < key['a'] < 4:
	#	raise ValueError("Invalid key['a'], must be (3.57 < key['a'] < 4)")


def __generate_x_set(N,T,x0):
	"""
	Generate x set of length N with transient T.
	E.g. {x_i}_(T+1)^(T+N)
	"""
	x = x0
	for _ in range(T):
		x = 8*(x**4) - 8*(x**2) + 1

	X = np.empty(N)
	for i in range(N):
		x = 8*(x**4) - 8*(x**2) + 1
		X[i] = x
	return X


def __generate_xy_set(N,T,xy0):
	"""
	Generate x set of length N with transient T.
	E.g. {x_i,y_i}_(T+1)^(T+N)
	"""
	alpha,beta = 2,6
	x,y = xy0
	for _ in range(T):
		x,y = 1 - alpha*(y**2), cos(beta * arccos(x))

	X = np.empty((N,2))
	for i in range(N):
		x,y = 1 - alpha*(y**2), cos(beta * arccos(x))
		X[i] = (x,y)
	return X


def __generate_H_L(m,n,key):
	# Keys	
	x,p,q = [key[i] for i in ('x','p','q')]

	# x_{bar|hat}'
	x_bar = __generate_x_set(m+n,p,x[0])
	x_hat = __generate_x_set(m+n,q,x[1])

	# P1,P2 and Q1,Q2
	P1,P2 = x_bar[:m],x_bar[m:]
	Q1,Q2 = x_hat[:n],x_hat[n:]

	# S1 and S2
	S1 = np.argsort(P2)
	S2 = np.argsort(Q2)

	# Get H and L (two rearrangements)
	L = np.argsort(Q1[S1]) # L <- Q1 based on size
	H = np.argsort(P1[S2])

	return H,L


def __generate_mu(m,n,key):
	# Keys	
	xy,r = [key[i] for i in ('xy','r')]

	# Generate set
	vxy = __generate_xy_set((m*n+1)//2,r,xy)
	v   = vxy.reshape(-1)[:m*n]
	
	# Mu
	mu = np.empty(m*n,dtype='uint8')
	np.mod(v*1e14,256,mu)
	return mu



def encrypt(im,key):
	# Ensure valid key
	__test_key(key)
	m,n = im.shape[0],im.shape[1]

	# Copy
	enc = im.copy()

	# Generate sets
	H,L = __generate_H_L(m,n,key)
	mu = __generate_mu(m,n,key)
	print('H',H.shape)
	print('L',L.shape)
	print('im',im.shape)

	# Encrypt
	if len(im.shape) == 3:
		# Colors?
		for i in range(3):
			for _ in range(key['N']):
				encrypt_message(enc[:,:,i],key,H,L,mu)
	else:
		for _ in range(key['N']):
			encrypt_message(enc,key,H,L,mu)

	return enc


def encrypt_message(msg,key,H,L,mu):
	# Scamble
	msg[:] = msg[H,:] # scramble rows
	msg[:] = msg[:,L] # scramble columns

	# Diffusion
	c = msg.flat
	t = key['t']
	# note: we use c0 = c[-1] = c[m*n-1], 
	#       and the mod() is inplicit as we use dtype=uint8
	for i in range(len(c)):
		c[i] = np.bitwise_xor(c[i] + t*mu[i] + c[i-1],mu[i])


def decrypt(msg,key):
	# Ensure valid key
	__test_key(key)
	m,n = msg.shape[0],msg.shape[1]

	# Copy
	dec = msg.copy()

	# Generate sets
	H,L = __generate_H_L(m,n,key)
	mu = __generate_mu(m,n,key)

	# Decrypt
	if len(msg.shape) == 3:
		# Colors?
		for i in range(3):
			for _ in range(key['N']):
				decrypt_message(dec[:,:,i],key,H,L,mu)
	else:
		for _ in range(key['N']):
			decrypt_message(dec,key,H,L,mu)

	return dec



def decrypt_message(msg,key,H,L,mu):
	# Un-diffusion
	c = msg.flat
	t = key['t']
	# note: we use c0 = c[-1] = c[m*n-1], 
	#       and the mod() is inplicit as we use dtype=uint8
	for i in range(len(c)-1,-1,-1):
		c[i] = np.bitwise_xor(c[i],mu[i]) - (t*mu[i] + c[i-1])
	#	c[i] = np.bitwise_xor(c[i] + t*mu[i] + c[i-1],mu[i])
	#	c[i] = (b[i] + t*mu[i] + c[i-1]) xor mu[i]
	#	c[i] xor mu[i] = (b[i] + t*mu[i] + c[i-1])
	#	(c[i] xor mu[i]) - (t*mu[i] + c[i-1]) = b[i]
	#	b[i] = (c[i] xor mu[i]) - (t*mu[i] + c[i-1])
	# Descramble
	Hi = np.argsort(H)
	Li = np.argsort(L)
	msg[:] = msg[Hi,:] # descramble rows
	msg[:] = msg[:,Li] # descramble columns
