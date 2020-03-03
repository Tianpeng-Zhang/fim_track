#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import PoseStamped,Pose, Twist
from std_msgs.msg import Float32MultiArray
import numpy as np
import sys
from spin_and_collect import spin_and_collect

class calibrate_meas_coef:
	def __init__(self):
		self.robot_pose=None
		self.target_pose=None
		self.light_readings=None

		self.robot_loc_stack=[]
		self.target_loc_stack=[]
		self.light_reading_stack=[]

		self.awake_freq=10
		
		
	def robot_pose_callback_(self,data):
		# print(data.pose)
		self.robot_pose=data.pose
		
	def target_pose_callback_(self,data):
		self.target_pose=data.pose

	def light_callback_(self,data):
		print(data.data)
		self.light_readings=data.data

	def pose2xz(self,pose):
		return np.array([pose.position.x,pose.position.z])
	
	def record_data(self,robot_namespace,target_namespace):
		rospy.init_node('calibrate_meas_coef',anonymous=True)
		
		rpose_topic="/vrpn_client_node/{}/pose".format(robot_namespace)
		tpose_topic="/vrpn_client_node/{}/pose".format(target_namespace)

		robot_pose=rospy.Subscriber(rpose_topic, PoseStamped, self.robot_pose_callback_)
		target_pose=rospy.Subscriber(tpose_topic, PoseStamped, self.target_pose_callback_)
		light_sensor=rospy.Subscriber("/{}/sensor_readings".format(robot_namespace), Float32MultiArray, self.light_callback_)
		
		rate=rospy.Rate(self.awake_freq)

		while (not rospy.is_shutdown()):
			if not(self.robot_pose==None or self.target_pose==None or self.light_readings==None):
				print(self.robot_pose)
				print('target:',self.target_pose)
				print('light:',self.light_readings)
				self.robot_loc_stack.append(self.pose2xz(self.robot_pose))
				self.target_loc_stack.append(self.pose2xz(self.target_pose))
				self.light_reading_stack.append(np.array(self.light_readings))
			rate.sleep()
		
		
		np.savetxt('robot_loc_{}.txt'.format(robot_namespace),np.array(self.robot_loc_stack),delimiter=',')
		np.savetxt('target_loc_{}.txt'.format(target_namespace),np.array(self.target_loc_stack),delimiter=',')
		np.savetxt('light_readings_{}.txt'.format(robot_namespace),np.array(self.light_reading_stack),delimiter=',')

if __name__ == '__main__':
	arguments = len(sys.argv) - 1

	# print(arguments,sys.argv)
	position = 1
	# Get the robot name passed in by the user
	robot_namespace=''
	if arguments>=position:
		robot_namespace=sys.argv[position]

	position = 2
	# Get the robot name passed in by the user
	target_namespace='Lamp'
	if arguments>=position:
		target_namespace=sys.argv[position]

	cmc=calibrate_meas_coef()
	cmc.record_data(robot_namespace,target_namespace)