#! /usr/bin/env python
import rospy
import tf
from nav_msgs.msg import Odometry
# from geometry_msgs.msg import PoseWithCovariance,TwistWithCovariance
from std_msgs.msg import Header
from gazebo_msgs.srv import GetModelState, GetModelStateRequest

rospy.init_node('odom_pub')

rospy.wait_for_service ('/uv/gazebo/get_model_state')
get_model_srv = rospy.ServiceProxy('/uv/gazebo/get_model_state', GetModelState)
publisher = rospy.Publisher('gazebo/model_odom', Odometry, queue_size = 1)
# publisher_twist = rospy.Publisher('gazebo/model_twist', TwistWithCovariance, queue_size = 1)

# pose = PoseWithCovariance()
# twist = TwistWithCovariance()
header = Header()
odom = Odometry()
header.frame_id='odom'
model = GetModelStateRequest()
model.model_name='ackermann_vehicle'

r = rospy.Rate(10)

while not rospy.is_shutdown():
    result = get_model_srv(model)
    # print(result)
    odom.header = header
    odom.pose.pose = result.pose
    odom.pose.covariance= [0.05, 0,    0,    0,    0,    0,
                           0,    0.05, 0,    0,    0,    0,
                           0,    0,    0.06, 0,    0,    0,
                           0,    0,    0,    0.03, 0,    0,
                           0,    0,    0,    0,    0.03, 0,
                           0,    0,    0,    0,    0,    0.06]
    odom.twist.twist = result.twist
    odom.twist.covariance=[0.05, 0,    0,    0,    0,    0,
                           0,    0.05, 0,    0,    0,    0,
                           0,    0,    0.06, 0,    0,    0,
                           0,    0,    0,    0.03, 0,    0,
                           0,    0,    0,    0,    0.03, 0,
                           0,    0,    0,    0,    0,    0.06]
    publisher.publish(odom)

    br = tf.TransformBroadcaster()
    
    br.sendTransform((result.pose.position.x,result.pose.position.y,result.pose.position.z),
                     (result.pose.orientation.x,result.pose.orientation.y,result.pose.orientation.z,result.pose.orientation.w),
                     rospy.Time.now(),
                     "base_link",
                     "odom")

    r.sleep()
