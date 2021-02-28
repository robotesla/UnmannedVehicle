#! /usr/bin/env python
import rospy
import tf
from nav_msgs.msg import Odometry
from std_msgs.msg import Header


def callback(msg):
    result = msg.pose

    br = tf.TransformBroadcaster()
    
    br.sendTransform((result.pose.position.x,result.pose.position.y,result.pose.position.z),
                     (result.pose.orientation.x,result.pose.orientation.y,result.pose.orientation.z,result.pose.orientation.w),
                     rospy.Time.now(),
                     "base_link",
                     "odom")



rospy.init_node('tf_odom_to_base_link')
sub = rospy.Subscriber('/odom', Odometry, callback)

rospy.spin()



