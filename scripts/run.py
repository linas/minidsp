#!/usr/bin/env python
import rospy
from std_msgs.msg import String
import hid
from minidsp.msg import MiniDspData


class MiniDsp:
    vendor_id = 0x2752
    product_id = 0x1c

    def __init__(self):
        rospy.init_node('minidsp', log_level=rospy.DEBUG)
        self.data_pub = rospy.Publisher('~data', MiniDspData, queue_size=10)
        self.rate = rospy.Rate(rospy.get_param("rate_hz", 10))
        self.device = hid.device()

    def run(self):
        try:
            self.device.open(0x2752, 0x1c)
            self.device.set_nonblocking(1)

            while not rospy.is_shutdown():
                data = self.device.read(6)
                if data:
                    rospy.logdebug("raw minidsp data: %s", str(data))
                    msg = MiniDspData()
                    msg.vad = data[2]
                    msg.angle = data[3] << 8 | data[4]
                    msg.dir = data[5]
                    self.data_pub.publish(msg)
                self.rate.sleep()
        except IOError as e:
            rospy.logfatal(e)
        finally:
            rospy.loginfo("closing minidsp")
            self.device.close()


if __name__ == '__main__':
    try:
        minidsp = MiniDsp()
        minidsp.run()
    except rospy.ROSInterruptException:
        pass
