import sympy as sp

# Symbols
a,x,y = sp.symbols('a x y')
A,X,MAX = sp.symbols('A X MAX')

# Attractor limits
x_min = (4*a**2 - a**3) / 16
x_max = a / 4

# Functions
f  = lambda x: a*x*(1-x)
g  = lambda x: (x - x_min) / (x_max - x_min)
gi_expr = sp.solve(g(x) - y, x)[0]
gi = lambda y_val: gi_expr.subs(y,y_val)

# Functions:
#  f  : Attr  -> Attr
#  g  : Attr  -> [0,1]
#  gi : [0,1] -> Attr
# g o f o gi : [0,1] -> [0,1]

F_expr = g(f(gi(x))).simplify()
F = lambda x_val: F_expr.subs(x,x_val)

# Parameter
# From [Pisarchik]: 3.57 < a < 4
a_min = sp.Rational(357,100)
a_max = sp.Rational(4)

# Map [0,1] -> [x_max,x_min]
h  = lambda a: (a - a_min) / (a_max - a_min)
hi_expr = sp.solve(h(a)-x,a)[0]
hi = lambda x_val: hi_expr.subs(x,x_val)

#
#FD(X).diff(C) = MAX*(1849*A**2 + 22102*A*MAX + 16049*MAX**2)/(1849*A**2 + 22102*A*MAX + 56049*MAX**2)
#

# Discretization of F
FD = lambda X: (MAX * F(X/MAX)).subs(a, hi(A/MAX)).simplify()
C  = [(FD(X).taylor_term(i,X) / X**i).simplify() for i in range(3)]

# Polynomial descriptor
num = tuple([c.as_numer_denom()[0] for c in C])
den = tuple([c.as_numer_denom()[1] for c in C])
ngcd = sp.gcd(sp.gcd(num[0],num[1]),num[2])
dgcd = sp.gcd(sp.gcd(den[0],den[1]),den[2])
pdesc = {
	'num' : [n/ngcd for n in num],
	'den' : [d/dgcd for d in den],
	'N'   : ngcd,
	'D'   : dgcd
}

# Iterator
class discrete_logistic:
	def __init__(self,bits,A_val):
		#pdesc = self.__generate_pdesc()
		sub = {MAX:2**bits-1,A:A_val}
		self.num  = [int(n.subs(sub).simplify()) for n in pdesc['num']]
		self.den  = [int(n.subs(sub).simplify()) for n in pdesc['den']]
		self.N    = int(pdesc['N'].subs(sub).simplify())
		self.D    = int(pdesc['D'].subs(sub).simplify())
		self.next = 0
	
	def step(self,X=None,n=1):
		if X is None: X = self.next
		for _ in range(n):
			X = (( self.num[0]      // self.den[0]) + 
			     ((self.num[1]*X)   // self.den[1]) + 
			     ((self.num[2]*X*X) // self.den[2])  )
			X = (X * self.N) // self.D
		self.next = X
		return X

#
#% Discretization
#syms A X MAX
#FD = simplify(subs(MAX*F,{a,x},{hi(A/MAX),X/MAX}));
#
#% Polynomial coefficients
#C = simplify(coeffs(F,x));
#CD = simplify(subs(MAX*C,{a,x},{hi(A/MAX),X/MAX}));
#
#

