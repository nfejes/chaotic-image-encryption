from scipy.misc import imread,imshow
import chaosencrypt as cenc
import numpy as np

# Read image
print('Loading image...')
im_org = imread('../image.jpg')

# Downsample
im = im_org[::3,::3,:].copy()

# Key
key = {'x':(0.393,-0.644),'p':21,'q':43,'xy':(-0.236,0.522),'r':16,'t':3,'N':3}

# Encrypt
print('Encrypting image (huang)...')
enc_im = cenc.encrypt(im,key,'huang')

# Decrypt
print('Decrypting image (huang)...')
dec_im = cenc.decrypt(enc_im,key,'huang')

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
	[np.concatenate((im,enc_im),1),
	 np.concatenate((dec_im,diff_im),1)]
,0))


