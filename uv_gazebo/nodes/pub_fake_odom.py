#! /usr/bin/env python
import rospy
import tf
from nav_msgs.msg import Odometry
from std_msgs.msg import Header
from gazebo_msgs.srv import GetModelState, GetModelStateRequest

rospy.init_node('odom_pub')

rospy.wait_for_service ('/uv/gazebo/get_model_state')
get_model_srv = rospy.ServiceProxy('/uv/gazebo/get_model_state', GetModelState)

odom = Odometry()
header = Header()
header.frame_id='odom'
odom.child_frame_id='base_link'
model = GetModelStateRequest()
model.model_name='ackermann_vehicle'

r = rospy.Rate(10)

while not rospy.is_shutdown():
    result = get_model_srv(model)

    br = tf.TransformBroadcaster()
    
    br.sendTransform((result.pose.position.x,result.pose.position.y,result.pose.position.z),
                     (result.pose.orientation.x,result.pose.orientation.y,result.pose.orientation.z,result.pose.orientation.w),
                     rospy.Time.now(),
                     "base_link",
                     "odom")

    r.sleep()
