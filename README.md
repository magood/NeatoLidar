# NeatoLidar
Collection of documentation and code samples to operate and get data off of a Neato Lidar module.

## My Impementation

I had a demo of getting data off the Neato Lidar many years ago, and I mostly remember what I was doing.

There was a small Arduino microcontroller running motor control code to keep the lidar motor at 300 RPM.  If not at the correct RPM, serial data is garbled.  The arduino was forwarding serial data back to a host computer running a Python script to decode the packed binary messages.

It is best to build a small circuit for the Arduino to drive the motor.  You don't necessarily need the exact transistor in the schematic (which I believe has been discontinued and is hard to find).  Many common standard transistors will be able to handle this small current draw.  It looks like in the video I didn't do this - I just powered it directly off the power supple and ran the data into a TTL-to-USB cable into a python script on my laptop - but for robotics use, this might result in some dropped rotations.  I think one of the documentation PDFs talks about this.  It's a cost-saving thing, basically.

There are schematics for a simple circuit for the microcontroller to be able to PWM the motor, and scripts to read and forward the data.  There are a couple host Python files to intepret them from the incoming serial data.

There are also STL files if you want to 3d-print a base for the unit.

I'm pretty sure that's how all this worked - this was many years ago and I only recently unearthed it.  YMMV.

Much of this is heavily borrowed from earlier work by other people, and I make no claim to ownership.  I believe this is all under permissive open source licenses.  If you own this code, and you have an issue with it being posted online, get in touch and I'll remove it.