#!/usr/bin/env python


'''
This is a boiler plate script that contains an example on how to subscribe a rostopic containing camera frames 
and store it into an OpenCV image to use it further for image processing tasks.
Use this code snippet in your code or you can also continue adding your code in the same file
'''

# 			PUBLICATIONS					SUBSCRIPTIONS
# 		/destination_coordinates			/qr_command
#		/qr_status


from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2, time
import numpy as np
import rospy

from pyzbar import pyzbar

from std_msgs.msg import Bool, Float32
from geometry_msgs.msg import Vector3



class image_proc():

	# Initialise everything
	def __init__(self):
		rospy.init_node('barcode_test') #Initialise rosnode 

		# Subscribing to /edrone/camera/image_raw 
		rospy.Subscriber("/edrone/camera/image_raw", Image, self.image_callback) #Subscribing to the camera topic

		self.img = np.empty([]) # This will contain your image frame from camera
		self.bridge = CvBridge()

		# to know when to scan
		self.scan = False

		self.qr_status = False

		# scanned coordinates x = lat, y = long, z = alt
		self.destination_coordinates = Vector3()
		self.destination_coordinates.x = 0.0
		self.destination_coordinates.y = 0.0
		self.destination_coordinates.z = 0.0



		# Subscribing to /qr_command
		rospy.Subscriber("/qr_command", Bool, self.qr_command_callback)

		# Publishing /destination_coordinates, /qr_status
		self.coordinates_pub = rospy.Publisher("/destination_coordinates", Vector3, queue_size=1)
		self.qr_status_pub = rospy.Publisher("/qr_status", Bool, queue_size=1)

		time.sleep(2.5)



	# Callback function of camera topic
	def image_callback(self, data):
		try:
			self.img = self.bridge.imgmsg_to_cv2(data, "bgr8") # Converting the image to OpenCV standard image
			#cv2.imshow("Image", self.img)
			#cv2.waitKey(0)
		except CvBridgeError as e:
			print(e)
			return

	# Callback function for qr command
	def qr_command_callback(self, input):
		self.scan = input.data


	# To decode qr code and find destination coordinates
	def qr_scan(self):
		
		# TODO decode qr

		if self.scan:

			decoded_image = pyzbar.decode(self.img)
			#print(decoded_image)

			# checking if qr is exist

			if len(decoded_image) > 0:

				self.qr_status = True

				raw_data = decoded_image[0].data
				print(raw_data)
				coordinates = raw_data.split(",")

				# sending destination coordinates

				self.destination_coordinates.x = float(coordinates[0])
				self.destination_coordinates.y = float(coordinates[1])
				self.destination_coordinates.z = float(coordinates[2])

			# publishing required results

		self.coordinates_pub.publish(self.destination_coordinates)
		self.qr_status_pub.publish(self.qr_status)


if __name__ == '__main__':
	image_proc_obj = image_proc()
	r = rospy.Rate(10)
	
	# running appropriate function continuously in loop
	while not rospy.is_shutdown():
		image_proc_obj.qr_scan()
		r.sleep()
