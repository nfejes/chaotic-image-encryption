from scipy.misc import imread,imshow
import chaosencrypt as ce
import numpy as np

# Read image
print('Loading image...')
im = imread('../image.jpg')

# Downsample and use red layer
im = im[::2,::2,0]
shape = im.shape

# Show
imshow(im)

# Key
key = {'a':3.9,'n':10,'r':4}

# Encrypt
print('Encrypting image (pisarchik)...')
enc_im = ce.encrypt(im,key,'pisarchik')

# Decrypt
print('Decrypting image (pisarchik)...')
#dec_im = ce.decrypt(enc_im,key,'pisarchik')
dec_im = ce.pisarchik.decrypt_real(enc_im.reshape(-1),key).reshape(shape)
imshow(dec_im)

# Diff
A_im = ce.pisarchik.DA(im,key['a'])
imshow(A_im - dec_im)
print('Max diff:',np.max(np.abs(A_im - dec_im)))



