import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg



#clip1= cv2.VideoCapture('project_video.mp4')
image1 = mpimg.imread('straight_lines1.jpg')

def warp(img):
	img_size = (img.shape[1], img.shape[0])

	src = np.float32(
		[[850, 320],
		[865, 450],
		[533, 250],
		[535, 210]])

	dst = np.float32(
		[[870, 240],
		[870, 370],
		[520, 370],
		[520, 240]])

	M = cv2.getPerspectiveTransform(src, dst)

	warped = cv2.warpPerspective(img, M, img_size, flags=cv2.INTER_LINEAR)
    
    #return warped

def process_video(clip1):


	#while (clip1.isOpened()):
	#	ret, frame = clip1.read()

	hls = cv2.cvtColor(clip1, cv2.COLOR_RGB2HLS)
	s_channel = hls[:,:,2]

	frame = np.copy(clip1)

	gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

	sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0)
	abs_sobelx = np.absolute(sobelx)
	scaled_sobel = np.uint8(255*abs_sobelx/np.max(abs_sobelx))

	thresh_min = 20
	thresh_max = 100
	sxbinary = np.zeros_like(scaled_sobel)
	sxbinary[(scaled_sobel >= thresh_min) & (scaled_sobel <= thresh_max)]

	s_thresh_min = 170
	s_thresh_max = 255
	s_binary = np.zeros_like(s_channel)
	s_binary[(s_channel >= s_thresh_min) & (s_channel <= s_thresh_max)] = 1

	color_binary = np.dstack((np.zeros_like(sxbinary), sxbinary, s_binary))

	combined_binary = np.zeros_like(sxbinary)
	combined_binary[(s_binary ==1) | (sxbinary == 1)] = 1

	#cv2.imshow('frame', scaled_sobel)

	# Plotting thresholded images
	f, (ax1, ax2) = plt.subplots(1, 2, figsize=(20,10))
	ax1.set_title('Stacked thresholds')
	ax1.imshow(color_binary)

	ax2.set_title('Combined S channel and gradient thresholds')
	ax2.imshow(combined_binary, cmap='gray')


	find_the_lines(scaled_sobel)

		
	
	#	if cv2.waitKey(1) & 0xFF == ord('q'):
	#		break

		#return scaled_sobel

	#clip1.release()
	#cv2.destroyAllWindows()

def find_the_lines(binary_warped):
	#print (binary_warped.shape)
	# Assuming you have created a warped binary image called "binary_warped"
	# Take a histogram of the bottom half of the image
	histogram = np.sum(binary_warped[binary_warped.shape[0]//2:,:], axis=0)
	# Create an output image to draw on and  visualize the result
	out_img = np.dstack((binary_warped, binary_warped, binary_warped))*255
	# Find the peak of the left and right halves of the histogram
	# These will be the starting point for the left and right lines
	midpoint = np.int(histogram.shape[0]/2)
	leftx_base = np.argmax(histogram[:midpoint])
	rightx_base = np.argmax(histogram[midpoint:]) + midpoint

	# Choose the number of sliding windows
	nwindows = 9
	# Set height of windows
	window_height = np.int(binary_warped.shape[0]/nwindows)
	# Identify the x and y positions of all nonzero pixels in the image
	nonzero = binary_warped.nonzero()
	nonzeroy = np.array(nonzero[0])
	nonzerox = np.array(nonzero[1])
	# Current positions to be updated for each window
	leftx_current = leftx_base
	rightx_current = rightx_base
	# Set the width of the windows +/- margin
	margin = 100
	# Set minimum number of pixels found to recenter window
	minpix = 50
	# Create empty lists to receive left and right lane pixel indices
	left_lane_inds = []
	right_lane_inds = []

	# Step through the windows one by one
	for window in range(nwindows):
    	# Identify window boundaries in x and y (and right and left)
		win_y_low = binary_warped.shape[0] - (window+1)*window_height
		win_y_high = binary_warped.shape[0] - window*window_height
		win_xleft_low = leftx_current - margin
		win_xleft_high = leftx_current + margin
		win_xright_low = rightx_current - margin
		win_xright_high = rightx_current + margin
		# Draw the windows on the visualization image
		cv2.rectangle(out_img,(win_xleft_low,win_y_low),(win_xleft_high,win_y_high),
		(0,255,0), 2) 
		cv2.rectangle(out_img,(win_xright_low,win_y_low),(win_xright_high,win_y_high),
		(0,255,0), 2) 
		# Identify the nonzero pixels in x and y within the window
		good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & 
		(nonzerox >= win_xleft_low) &  (nonzerox < win_xleft_high)).nonzero()[0]
		good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & 
		(nonzerox >= win_xright_low) &  (nonzerox < win_xright_high)).nonzero()[0]
		# Append these indices to the lists
		left_lane_inds.append(good_left_inds)
		right_lane_inds.append(good_right_inds)
		# If you found > minpix pixels, recenter next window on their mean position
		if len(good_left_inds) > minpix:
			leftx_current = np.int(np.mean(nonzerox[good_left_inds]))
		if len(good_right_inds) > minpix:        
			rightx_current = np.int(np.mean(nonzerox[good_right_inds]))

	#	 Concatenate the arrays of indices
	left_lane_inds = np.concatenate(left_lane_inds)
	right_lane_inds = np.concatenate(right_lane_inds)

	# Extract left and right line pixel positions
	leftx = nonzerox[left_lane_inds]
	lefty = nonzeroy[left_lane_inds] 
	rightx = nonzerox[right_lane_inds]
	righty = nonzeroy[right_lane_inds] 

	# Fit a second order polynomial to each
	left_fit = np.polyfit(lefty, leftx, 2)
	right_fit = np.polyfit(righty, rightx, 2)



	# Generate x and y values for plotting
	ploty = np.linspace(0, binary_warped.shape[0]-1, binary_warped.shape[0] )
	left_fitx = left_fit[0]*ploty**2 + left_fit[1]*ploty + left_fit[2]
	right_fitx = right_fit[0]*ploty**2 + right_fit[1]*ploty + right_fit[2]

	out_img[nonzeroy[left_lane_inds], nonzerox[left_lane_inds]] = [255, 0, 0]
	out_img[nonzeroy[right_lane_inds], nonzerox[right_lane_inds]] = [0, 0, 255]

	#scv2.imshow('frame', out_img)
	plt.imshow(out_img)
	plt.plot(left_fitx, ploty, color='yellow')
	plt.plot(right_fitx, ploty, color='yellow')
	plt.xlim(0, 1280)
	plt.ylim(720, 0)

	plt.show()




process_video(image1)
#find_the_lines(color_and_gradient)
exit()
