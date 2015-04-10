import numpy as np
from chaosencrypt import logistic
from smartplot import smartplot

bits = 16
N = 500
M = 1000

AV = np.linspace(0,2**bits-1,N)
#AV = np.linspace(0,2**(bits-4)-1,N)
#AV = np.arange(0,100)
T = np.empty((N,M+1),dtype='int64')
NV = np.repeat(AV,M+1)

for i,A in enumerate(AV):
	print('step',i+1)
	A = int(A)
	dl = logistic.discrete(A,bits)
	#dl.step(2**(bits-1),M)
	#T[i] = dl.steps(None,M)
	T[i] = dl.steps(6871,M)

smartplot([NV,T.reshape(-1)],{'linewidth':0,'markersize':0.2,'axform':['0x%X','0x%X']})

