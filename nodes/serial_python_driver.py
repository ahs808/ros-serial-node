#!/usr/bin/env python3

'''
This script is meant to be run as a very basic converter node. It will
read in serial sentences from a serial device such as an RS232 GPS, or
any device that outputs serial strings. The script will parse out the
first comma separated value and use it as the ROS topic name to publish
to. The entire serial string will be preserved and published as a full
string so that it can be manipulated on the subscriber-side script.
Many serial devices use the first comma seperated value to declare
the serial string type, this is especially common in NMEA format serial
strings. If you are trying to read in serial strings that don't use a
fixed first value to declare the string type, then you need to modify
the code or else it will create too many publishers, it was not intended
to read that type of serial string.
'''

import rospy
import serial
import sys
from std_msgs.msg import String

class Ser(object):
    def __init__(self):
        self.pubs = {} # empty dict to populate with publishers
    def pub_msg(self, id, msg_str):
        if msg_str:
            if id:
                try:
                    self.pubs[id].publish(msg_str)
                except KeyError:
                    pub_topic = "serial_"+id
                    self.pubs[id] = rospy.Publisher(
                        pub_topic,
                        String,
                        queue_size=1,
                        latch=False)
                    self.pubs[id].publish(msg_str)
        else:
            rospy.logdebug("Problem publishing serial string - maybe empty")       

def parse_msg(rx):
    id = None
    aa = rx.split(',')
    msg_str = rx
    # list of characters to remove from id string
    id_rmv = ['$','%']
    # list of characters to remove from msg string
    msg_rmv = ['\r','\n','\n\r','\r\n'] 
    if len(aa) > 1:
        id = aa[0]
        for ii in id_rmv:
            id = id.replace(ii,'')
        for jj in msg_rmv:
            msg_str = msg_str.replace(jj,'')
    else:
        rospy.logdebug("String does not appear to use comma separated values")
    return id,msg_str

def main():
    try:
        rospy.init_node('serial_node', anonymous=False)
        # create ser obj
        ser_obj = Ser()
        ##############################################
        # PARAMETERS TO BE UPDATED BY THE USER
        #port = "/dev/ttyUSB0"
        port = "/dev/ttyACM0"

        baud = 115200
        # set the rate for this node to update at, typically
        # you will want your node to update slightly faster
        # than the rate your serial device is outputting
        rrate = rospy.Rate(5) # 5 Hz
        ##############################################
        try:
            ser = serial.Serial(port,baud)
        except serial.serialutil.SerialException:
            rospy.logdebug("Could not open the port <%s>"%port)
            sys.exit(2)
        while not rospy.is_shutdown():
            try:
                rx = ser.readline().decode('utf-8')
                id,msg_str = parse_msg(rx)
            except:
                id = None
                msg_str = None
            ser_obj.pub_msg(id,msg_str)
            rrate.sleep()
    except rospy.ROSInterruptException:
        pass

if __name__=='__main__':
    main()