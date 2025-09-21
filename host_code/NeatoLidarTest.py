#borowed some code based on code from Nicolas "Xevel" Saugnier

import serial
import binascii
import time, math, sys

def serial_dump():
    with serial.Serial('COM4', 115200) as ser:
        count = 0
        while True:
            byte = ser.read(1)
            hexval = binascii.hexlify(byte)
            if hexval == b'fa':
                start = True #who knows if we need this...
                print()
            print(str(b) + ":", end='')
            count += 1

lidarData = [[] for i in range(360)] #A list of 360 elements Angle, Distance , quality

angle = 0
init_level = 0
index = 0

def update_view( angle, data ):
    """Updates the view of a sample.
    Takes the angle (an int, from 0 to 359) and the list of four bytes of data in the order they arrived.
    """
    global offset, use_outer_line, use_line
    #unpack data using the denomination used during the discussions
    x = data[0]
    x1= data[1]
    x2= data[2]
    x3= data[3]
    
    angle_rad = angle * math.pi / 180.0
    c = math.cos(angle_rad)
    s = -math.sin(angle_rad)

    dist_mm = x | (( x1 & 0x3f) << 8) # distance is coded on 13 bits ? 14 bits ?
    quality = x2 | (x3 << 8) # quality is on 16 bits
    lidarData[angle] = [dist_mm,quality]
    dist_x = dist_mm*c
    dist_y = dist_mm*s
    sys.stdout.write('\r')
    sys.stdout.flush()
    sys.stdout.write(str(lidarData[0]))
    sys.stdout.flush()

def checksum(data):
    """Compute and return the checksum as an int.
    data -- list of 20 bytes (as ints), in the order they arrived in.
    """
    # group the data by word, little-endian
    data_list = []
    for t in range(10):
        data_list.append( data[2*t] + (data[2*t+1]<<8) )
    
    # compute the checksum on 32 bits
    chk32 = 0
    for d in data_list:
        chk32 = (chk32 << 1) + d

    # return a value wrapped around on 15bits, and truncated to still fit into 15 bits
    checksum = (chk32 & 0x7FFF) + ( chk32 >> 15 ) # wrap around to fit into 15 bits
    checksum = checksum & 0x7FFF # truncate to 15 bits
    return int( checksum )

def compute_speed(data):
    speed_rpm = float( data[0] | (data[1] << 8) ) / 64.0
    return speed_rpm

def read_lidar():
    global init_level, angle, index
    nb_errors = 0
    with serial.Serial('COM4', 115200) as ser:
        while True:
            #time.sleep(0.00001) # do not hog the processor power

            if init_level == 0 :
                b = ord(ser.read(1))
                # start byte
                if b == 0xFA :
                    init_level = 1
                    #print lidarData
                else:
                    init_level = 0
            elif init_level == 1:
                # position index
                b = ord(ser.read(1))
                if b >= 0xA0 and b <= 0xF9 :
                    index = b - 0xA0
                    init_level = 2
                elif b != 0xFA:
                    init_level = 0
            elif init_level == 2 :
                # speed
                b_speed = [b for b in ser.read(2)]
                
                # data
                b_data0 = [b for b in ser.read(4)]
                b_data1 = [b for b in ser.read(4)]
                b_data2 = [b for b in ser.read(4)]
                b_data3 = [b for b in ser.read(4)]

                # for the checksum, we need all the data of the packet...
                # this could be collected in a more elegent fashion...
                all_data = [ 0xFA, index+0xA0 ] + b_speed + b_data0 + b_data1 + b_data2 + b_data3

                # checksum
                b_checksum = [b for b in ser.read(2) ]
                incoming_checksum = int(b_checksum[0]) + (int(b_checksum[1]) << 8)

                # verify that the received checksum is equal to the one computed from the data
                if checksum(all_data) == incoming_checksum:
                    speed_rpm = compute_speed(b_speed)
                    
                    update_view(index * 4 + 0, b_data0)
                    update_view(index * 4 + 1, b_data1)
                    update_view(index * 4 + 2, b_data2)
                    update_view(index * 4 + 3, b_data3)
                else:
                    # the checksum does not match, something went wrong...
                    nb_errors +=1
                    
                    # display the samples in an error state
                    update_view(index * 4 + 0, [0, 0x80, 0, 0])
                    update_view(index * 4 + 1, [0, 0x80, 0, 0])
                    update_view(index * 4 + 2, [0, 0x80, 0, 0])
                    update_view(index * 4 + 3, [0, 0x80, 0, 0])
                    
                init_level = 0 # reset and wait for the next packet
                
            else: # default, should never happen...
                init_level = 0


if __name__ == '__main__':
    #serial_dump()
    read_lidar()
    with serial.Serial('COM4', 115200) as ser:
        count = 0
        init_level = 0
        index = 0
        angle = 0

        while True:
            #byte = ser.read(1)
            b = ord(ser.read(1))
            #hexval = binascii.hexlify(byte)
            if b == 0xFA:# hexval == b'fa':
                start = True #who knows if we need this...
                print()
            print(str(b) + ":", end='')
            count += 1