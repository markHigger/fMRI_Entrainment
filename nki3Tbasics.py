
#import pyxid
#from collections import namedtuple
#rVal = namedtuple('rval', ['rt','strVal'])

"""
Taken from my octave serial code. Should? be the same for pyserial...
pulseKey = '5';  
thumbKey = '5%';
quitKey = KbName('q');  % only works when fMRI button box is NOT plugged in.

key1 = '4';
key2 = 'x';
key3 = 'n';
key4 = '1';
"""

def setupXID(pyxid):
    devices = pyxid.get_xid_devices()
    dev = devices[0] # get the first device to use
    if dev.is_response_device():
        dev.reset_base_timer()
        dev.reset_rt_timer()
        return dev			

#TODO: Check defaults against system.
def setupSerial(serial, COM='/dev/ttyS0', rate=19200, timeout=0):
    ser = serial.Serial(COM, rate, timeout=timeout,
        parity=serial.PARITY_EVEN, rtscts=1)
    dev = ser.open()
    if ser.is_open():
        return ser
    else:
        print("Error Opening %s" % COM)



def serWaitForPulseKey(ser,timer, kb, pulseKey):
    hasPulsed = False
    ser.flush_input()
    while hasPulsed == False:
        kPress = kb.get_key(keylist='q') # Allow clean escape by holding down 'q' key
        if kPress[0] != None:
            break
        resp = ser.read()
        if resp != 0:
            if char(resp) == pulseKey:
                hasPulsed = True
                ser.flush_input()
                return timer.get_time()

def serWaitForPressTimed(ser,timer, validKeys = [0,1,2,3], maxWait = 5000, timeoutKV = None, timeoutRT = -1.0):
    sTime = timer.get_time()
    hasPressed = False
    ser.reset_input_buffer() # Flush completely
    while hasPressed == False:
        resp = ser.read()
        if resp != 0:
            rt = round(timer.get_time() - sTime)
            if char(resp) in validKeys:  # WILL NEED TO EITHER CONVERT TO CHAR OR USE INT VAL COMPARITOR
                hasPressed = True
                return [kv,rt]
        if timer.get_time() - sTime >= maxWait:
            return [timeoutKV,timeoutRT]
            break


def waitForPressTimed(dev,timer, validKeys = [0,1,2,3], maxWait = 5000, timeoutKV = None, timeoutRT = -1.0):
    sTime = timer.get_time()
    hasPressed = False
    dev.con.flush_input()   
    while hasPressed == False:
        dev.poll_for_response()
        if dev.response_queue_size() > 0:
            response = dev.get_next_response()
            if response['pressed'] == True:
                kv = response['key']
                rt = round(timer.get_time() - sTime)
                if kv in validKeys:  ## Should iterate through acceptable values as well
                    hasPressed = True
                    return [kv,rt]
            dev.con.flush_input()
        if timer.get_time() - sTime >= maxWait:
            return [timeoutKV,timeoutRT]
            break

def waitForPressTimedX(dev,timer, validKeys, maxWait, timeoutKV, timeoutRT):
    sTime = timer.get_time()
    hasPressed = False
    dev.con.flush_input()   
    while hasPressed == False:
        dev.poll_for_response()
        if dev.response_queue_size() > 0:
            response = dev.get_next_response()
            if response['pressed'] == True:
                kv = response['key']
                rt = round(timer.get_time() - sTime)
                if kv in validKeys:  ## Should iterate through acceptable values as well
                    hasPressed = True
                    return [kv,rt]
        if timer.get_time() - sTime >= maxWait:
            return [timeoutKV,timeoutRT]
            break
            dev.con.flush_input() 


def waitForPress(dev,timer):
    sTime = timer.get_time()
    hasPressed = False
    dev.con.flush_input()   
    while hasPressed == False:
        dev.poll_for_response()
        if dev.response_queue_size() > 0:
            response = dev.get_next_response()
            if response['pressed'] == True:  ## Should iterate through acceptable values as well
                kv = response['key']
                rt = round(timer.get_time() - sTime)
                hasPressed = True
                return [kv,rt]
            dev.con.flush_input()  

def waitUntilTime(timer, wTime):
    while timer.get_time() < wTime:
        k = 1
        
# def waitForPulse(dev,timer):
#     hasPulsed = False
#     while hasPulsed == False:
#         dev.poll_for_response()
#         if dev.response_queue_size() > 0:
#             response = dev.get_next_response()
#             if response['pressed'] == True: # and response['key'] == '4':
#                 hasPulsed = True
# 		dev.con.flush_input()
#                 return timer.get_time()
                
def waitForPulse(dev, timer):
    hasPulsed = False
    while hasPulsed == False:
        dev.poll_for_response()
        if dev.response_queue_size() > 0:
            response = dev.get_next_response()
            if response['pressed'] == True:
                hasPulsed = True
                dev.con.flush_input()
#                return response
                return timer.get_time()

def waitForPulseKey(dev,timer, kb, pulseKey):
    hasPulsed = False
    while hasPulsed == False:
        kPress = kb.get_key(keylist='q') # Allow clean escape by holding down 'q' key
        if kPress[0] != None:
            break
        dev.poll_for_response()
        if dev.response_queue_size() > 0:
            response = dev.get_next_response()
            if response['pressed'] == True and response['key'] == pulseKey:
                hasPulsed = True
                dev.con.flush_input()
                return timer.get_time()

def waitForPulseKeyTimed(dev,timer, pulseKey, maxWait = 100000):
    hasPulsed = False
    pulseStartTime = timer.get_time()
    while hasPulsed == False:
        dev.poll_for_response()
        if dev.response_queue_size() > 0:
            response = dev.get_next_response()
            if response['pressed'] == True and response['kv'] == pulseKey:
                hasPulsed = True
                dev.con.flush_input()
                return timer.get_time()
            else:
                if timer.get_time() - pulseStartTime >= maxWait:
                    break

            
# def waitForPulseWithBreak(dev,timer, kb):
#     hasPulsed = False
#     while hasPulsed == False:

#         dev.poll_for_response()
#         if dev.response_queue_size() > 0:
#             response = dev.get_next_response()  
#             if response['pressed'] == True and response['key'] == '4':
#                 hasPulsed = True
#                 return timer.get_time()                  

#         dev.con.flush_input()
                    
def getRawInput(timer,rVal):
    tStart = timer.get_time()
    rInput = raw_input('Type Something: ')
    rt = round(timer.get_time() - tStart)
    retVal = rVal(rt,rInput)
    return retVal

def argLister(*args):
    for a in args:
        print(a)

def studyTime():
    import time
    now = time.localtime()
    out = "Run: " +  str(now.tm_mon) + "," + str(now.tm_mday) + "," + str(now.tm_year) + " at " + str(now.tm_hour) +":" + str(now.tm_min)+":"+str(now.tm_sec)
    return out

