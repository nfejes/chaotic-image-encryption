from scipy.misc import imread,imshow
import chaosencrypt as cenc
import numpy as np

from chaosencrypt.discrete_pisarchik import bitexpand,bitreduce

# Read image
print('Loading image...')
im_org = imread('../image.jpg')

# Downsample
im = im_org[::3,::3,:].copy()

# Key
key = {'a':3.8,'n':10,'r':3,'bits':32}

# Encrypt
print('Encrypting image (discrete pisarchik)...')
enc_im = cenc.encrypt(im,key,'discrete_pisarchik')

# Decrypt
print('Decrypting image (discrete pisarchik)...')
dec_im = cenc.decrypt(enc_im,key,'discrete_pisarchik')

# Diff
diff = np.array(np.abs((im*1.0) - (dec_im*1.0)), dtype='int')
maxdiff = np.max(diff)
print('Max diff:', maxdiff)

# Show
if maxdiff == 0:
	diff_im = np.zeros(im.shape, dtype='uint8')
else:
	diff_im = np.array((diff - np.min(diff)) / (np.max(diff) - np.min(diff))*255.99, dtype='uint8')

print('[ original  |  encrypted   ]')
print('[ decrypted | abs(org-dec) ]')
imshow(np.concatenate(
	[np.concatenate((im,bitreduce(enc_im)),1),
	 np.concatenate((dec_im,diff_im),1)]
,0))

