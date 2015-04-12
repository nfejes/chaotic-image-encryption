from scipy.misc import imread,imshow
import chaosencrypt as cenc
import numpy as np

from chaosencrypt.pisarchik import AD,DA

# Read image
print('Loading image...')
im_org = imread('../image.jpg')

# Downsample
im = im_org[::2,::2,:].copy()

# Key
key = {'a':3.9,'n':10,'r':7}

# Encrypt
print('Encrypting image (pisarchik)...')
enc_im = cenc.encrypt(im,key,'pisarchik')

# Decrypt
print('Decrypting image (pisarchik)...')
#dec_im = cenc.decrypt(enc_im,key,'pisarchik')
dec_im = enc_im.copy()
for i in range(3):
	cenc.pisarchik.decrypt_float(dec_im[:,:,i],key)

# Diff
A_im = DA(im,key['a'])
print('Max diff:',np.max(np.abs(A_im - dec_im)))

# Show
diff = (A_im - dec_im)
diff_im = np.array((diff - np.min(diff)) / (np.max(diff) - np.min(diff))*255.99, dtype='uint8')
imshow(np.concatenate(
	[np.concatenate((im,AD(enc_im,key['a'])),1),
	 np.concatenate((AD(dec_im,key['a']),diff_im),1)]
,0))

