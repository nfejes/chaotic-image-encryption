from scipy.misc import imread,imshow
import chaosencrypt as ce
import numpy as np

# Read image
print('Loading image...')
im = imread('../image.jpg')

# Downsample and use red layer
im = im[::2,::2,0]
shape = im.shape

# Key
key = {'a':3.9,'n':10,'r':7}

# Encrypt
print('Encrypting image (pisarchik)...')
enc_im = ce.encrypt(im,key,'pisarchik')

# Decrypt
print('Decrypting image (pisarchik)...')
#dec_im = ce.decrypt(enc_im,key,'pisarchik')
dec_im = ce.pisarchik.decrypt_real(enc_im.reshape(-1),key).reshape(shape)

# Diff
A_im = ce.pisarchik.DA(im,key['a'])
print('Max diff:',np.max(np.abs(A_im - dec_im)))

# Show
diff = (A_im - dec_im)
diff_im = np.array((diff - np.min(diff)) / (np.max(diff) - np.min(diff))*255.99, dtype='uint8')
imshow(np.concatenate(
	[np.concatenate((im,ce.pisarchik.AD(enc_im,key['a'])),1),
	 np.concatenate((ce.pisarchik.AD(dec_im,key['a']),diff_im),1)]
,0))




