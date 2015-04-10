import sympy as sp
import numpy as np

#class map_prototype:
#	
#	def __init__(self,params):
#		pass
#
#	def step(self,x=None,n=1):
#		pass
#
#	def steps(self,x=None,n=1):
#		pass

class logistic:
	
	def __init__(self,a):
		self.a = a
		self.next = 0

	def step(self,x=None,n=1):
		if x is None: x = self.next
		assert 0 <= x <= 1
		for _ in range(n):
			x = self.a * x * (1 - x)
			assert 0 <= x <= 1
		self.next = x
		return x


class discrete:
	__polydesc = None		

	def __init__(self,A_val,bits=32):
		if 3 < A_val < 4:
			a_min = 3.57
			a_max = 4
			A_val = (A_val - a_min) / (a_max - a_min)
			A_val = int(np.floor(A_val * (2**bits)))
		if discrete.__polydesc is None:
			self.__generate_polydesc()
		A,MAX = sp.symbols('A MAX')
		sub = {MAX:2**bits-1,A:A_val}
		self.num  = [int(n.subs(sub).simplify()) for n in discrete.__polydesc['num']]
		self.den  = [int(n.subs(sub).simplify()) for n in discrete.__polydesc['den']]
		self.N    = int(discrete.__polydesc['N'].subs(sub).simplify())
		self.D    = int(discrete.__polydesc['D'].subs(sub).simplify())
		self.next = 0
		self.max = (1 << bits) - 1
		#self.dtype = 'uint%d' % bits
		self.dtype = 'int64'

	
	def step(self,X=None,n=1):
		if X is None: X = self.next
		assert 0 <= X <= self.max, "X=%d, max=%d" % (X,self.max)
		for _ in range(n):
			X0 = X
			X = (( self.num[0]      // self.den[0]) + 
			     ((self.num[1]*X)   // self.den[1]) + 
			     ((self.num[2]*X*X) // self.den[2])  )
			X = (X * self.N) // self.D
			assert 0 <= X <= self.max, "X0=%d, X=%d, max=%d" % (X0,X,self.max)
		self.next = X
		return X

	def steps(self,X=None,n=1):
		if X is None: X = self.next
		assert 0 <= X <= self.max, "X=%d, max=%d" % (X,self.max)
		Y = np.empty(n+1,dtype=self.dtype)
		Y[0] = X
		for i in range(n):
			X = (( self.num[0]      // self.den[0]) + 
			     ((self.num[1]*X)   // self.den[1]) + 
			     ((self.num[2]*X*X) // self.den[2])  )
			X = (X * self.N) // self.D
			assert 0 <= X <= self.max, "X=%d, max=%d" % (X,self.max)
			Y[i+1] = X
		self.next = X
		return Y


	def __generate_polydesc(self):
		# Symbols
		a,x,y = sp.symbols('a x y')
		A,X,MAX = sp.symbols('A X MAX')
		
		# Attractor limits
		x_min = (4*a**2 - a**3) / 16
		x_max = a / 4
		
		# Functions
		#  f  : Attr  -> Attr
		#  g  : Attr  -> [0,1]
		#  gi : [0,1] -> Attr
		#  F  = g o f o gi : [0,1] -> [0,1]
		f  = lambda x: a*x*(1-x)
		g  = lambda x: (x - x_min) / (x_max - x_min)
		gi_expr = sp.solve(g(x) - y, x)[0]
		gi = lambda y_val: gi_expr.subs(y,y_val)
		F_expr = g(f(gi(x))).simplify()
		F = lambda x_val: F_expr.subs(x,x_val)
		
		# Parameters
		# From [Pisarchik]: 3.57 < a < 4
		a_min = sp.Rational(387,100) #357
		a_max = sp.Rational(400,100)
		
		# Map [0,1] -> [a_max,a_min]
		h  = lambda a: (a - a_min) / (a_max - a_min)
		hi_expr = sp.solve(h(a)-x,a)[0]
		hi = lambda x_val: hi_expr.subs(x,x_val)
		
		# Discretization of F
		FD = lambda X: (MAX * F(X/MAX)).subs(a, hi(A/MAX)).simplify()
		#FD(X).diff(C) = MAX*(1849*A**2 + 22102*A*MAX + 16049*MAX**2)/(1849*A**2 + 22102*A*MAX + 56049*MAX**2)

		# Taylor coefficients
		C  = [(FD(X).taylor_term(i,X) / X**i).simplify() for i in range(3)]
		
		# Polynomial descriptor
		num = [c.as_numer_denom()[0] for c in C]
		den = [c.as_numer_denom()[1] for c in C]
		ngcd = sp.gcd(sp.gcd(num[0],num[1]),num[2])
		dgcd = sp.gcd(sp.gcd(den[0],den[1]),den[2])

		# Descriptor
		discrete.__polydesc = {
			'num' : tuple([n/ngcd for n in num]),
			'den' : tuple([d/dgcd for d in den]),
			'N'   : ngcd,
			'D'   : dgcd
		}
		discrete.__polydesc = {
			'num' : tuple([n/ngcd for n in num]),
			'den' : tuple([d/dgcd for d in den]),
			'N'   : ngcd,
			'D'   : dgcd
		}
		#discrete.__polydesc = {
		#	'num' : tuple(num),
		#	'den' : tuple(den),
		#	'N'   : sp.Rational(1),
		#	'D'   : sp.Rational(1),
		#}

