from scipy.misc import imread,imshow
import chaosencrypt as cenc
import numpy as np

from chaosencrypt.discrete_pisarchik import bitexpand,bitreduce

# Read image
print('Loading image...')
im = imread('../image.jpg')
#imshow(bitreduce(bitexpand(im,32),32))

# Downsample and use red layer
im = im[::2,::2,0]
shape = im.shape

# Key
key = {'a':3.8,'n':10,'r':3,'bits':8}

# Encrypt
print('Encrypting image (discrete pisarchik)...')
enc_im = cenc.encrypt(im,key,'discrete_pisarchik')

# Decrypt
print('Decrypting image (discrete pisarchik)...')
dec_im = cenc.decrypt(enc_im,key,'discrete_pisarchik')

# Diff
diff = -np.abs((im*1.0) - (dec_im*1.0))
print('Max diff:', np.max(diff))

# Show
diff_im = np.array((diff - np.min(diff)) / (np.max(diff) - np.min(diff))*255.99, dtype='uint8')
imshow(np.concatenate(
	[np.concatenate((im,bitreduce(enc_im)),1),
	 np.concatenate((dec_im,diff_im),1)]
,0))




