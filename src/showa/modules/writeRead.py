import serial
from showa.lib import logs
from showa.modules import config, plotty, commands
# import config
# import plotty
# import commands
from time import sleep
import time
import pandas as pd
from datetime import datetime
import serial.tools.list_ports


class Error(Exception):
    """Base class for other exceptions"""
    pass


class portDisconnectError(Error):
    """Raised when b'' is detected."""
    pass


def resetElapsedTime():
    time_start = time.perf_counter()
    return(time_start)


def elapsedTime(x):
    time_elapsed = time.perf_counter() - x
    return(time_elapsed)


def serObj(url):
    return serial.Serial(
        port=url,
        baudrate=config.baud_rate,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_EVEN,
        stopbits=1, timeout=config.tout)


def getCOM():
    # for real physical ports
    comlist = serial.tools.list_ports.comports()
    return [i.device for i in comlist][0]


def bytes_to_read(func):
    """[Specify the length of data to read]
    [return the list of data lengths for a given function]
    """
    return [commands.dataLen(i[2:4].decode()) for i in func]


def prepInit(station, selection):
    """Prepare intial commands up until checker commands"""
    z = commands.selection_TorS(station, selection)
    return zip(z, bytes_to_read(z))


def greetings(ser):
    """Catch greetings from console server"""
    for i in range(4):
        print(ser.readline())
    ser.reset_input_buffer()
    sleep(config.fdelay)


def read_routine(ser, x, y):
    ser.write(x)
    sleep(config.fdelay)
    readback = ser.read(y)
    if readback == b'':
        raise portDisconnectError
    print(readback)
    return readback


# convert hexstring to signed decimal
def decodeOut(hexstr, bits):
    value = int(hexstr, 16)
    if value & (1 << (bits-1)):
        value -= 1 << bits
    return(value)


def speedClean(B_array):
    firstPart = B_array[:-7]
    midPart = str(firstPart[7:])
    speed = midPart[:-4]
    speed_result = decodeOut(speed, config.decodeBits)
    return speed_result


def torqueClean(B_array):
    firstPart = B_array[:-7]
    midPart = str(firstPart[7:])
    torque = midPart[4:]
    torque_result = decodeOut(torque, config.decodeBits)/10
    return torque_result


def fullSequence(line, chamber, url):
    """send all serial commands in sequence"""
    try:
        # Init Objects
        ser = None

        logs.logInfo("Start Full sequence")

        ser = serObj(url)
        result = {}
        # station = commands.LUT(chamber)
        station = '0'
        selection = 'speed'
        # for selection in ['speed']:
        dataList = []
        ser.close()
        ser.open()
        # initiate connection
        # greetings(ser)
        # read and write init serial commands
        for x, y in prepInit(station, selection):
            read_routine(ser, x, y)
        # start timer
        x = resetElapsedTime()
        # check speed 0
        ser.write(commands.checkerCmd(station))
        sleep(config.fdelay)
        speed = ser.read(10)
        while speed[2:7] != b'A0000':
            ser.write(commands.checkerCmd(station))
            sleep(config.fdelay)
            speed = ser.read(10)
            if(elapsedTime(x) >= config.max_duration):
                raise Exception("The carrier is not moving.")
                break
        # read and write middle commands
        for x, y in zip(commands.midCmd(station),
                        bytes_to_read(commands.midCmd(station))):
            read_routine(ser, x, y)
        # fetch data
        # check graph type
        fetchy = commands.fetchCmd(station)
        del fetchy[-224:]
        for x, y in zip(fetchy, bytes_to_read(fetchy)):
            dataList.append(read_routine(ser, x, y).decode())
        # read and write ending commands
        for x, y in zip(commands.endCmd(station),
                        bytes_to_read(commands.endCmd(station))):
            read_routine(ser, x, y)
        ser.close()
        logs.logInfo("Serial Closed")
        ser = None
        result['original'] = dataList
        return result
    except Exception as e:
        logs.logError("Error at fullSequence : {}".format(e),
                      includeErrorLine=True)
        raise e
    finally:
        if ser is not None:
            ser.close()
            logs.logInfo("Serial Closed")


def test_ports(chamber, url):
    """send all serial commands in sequence"""
    ser = serObj(url)
    ser.open()
    # initiate connection
    greetings(ser)


def main():
    dateTime = datetime.now().strftime(config.pngdate)
    line = '203'
    temp = {'P19': 'socket://128.53.66.38:5047'}
    # temp = mainDict(line)
    # print(temp)
    for chamber, v in temp.items():
        try:
            print(f'{chamber}:{v}')
            dataDict = fullSequence(chamber, v)
            df = pd.DataFrame.from_dict(dataDict)
            df['Speed'] = df['original'].apply(lambda x: speedClean(x))
            df['Torque'] = df['original'].apply(lambda x: torqueClean(x))
            df = df.drop(['original'], axis=1)
            # df = df[50:-224]
            df = df.reset_index(drop=True)
            # df.to_csv(f"{chamber}.csv", sep=';', index=True, mode='w')
            dfSpeed = df['Speed']
            dfTorque = df['Torque']
            # print(dfTorque.head(10))
            plotty.plot(line, chamber, dfSpeed, dfTorque, dateTime)
        except portDisconnectError as e:
            print(e)
        except Exception as error:
            print(error)


if __name__ == '__main__':
    # # main()
    # line_list = config.ipConfig.keys()
    # listy = [mainDict(i) for i in line_list]
    # try:
    #     for dicty in listy:
    #         for chamber, v in dicty.items():
    #             print(f'{chamber}:{v}')
    #             test_ports(chamber, v)
    # except Error as e:
    #     print(e)
    # line_list = config.ipConfig.keys()
    # listy = [mainDict(line) for line in line_list]
    # for i in listy:
    #     for x in i:
    #         line, chamber, v = x
    #         print(line, chamber, v)
    station = '0'
    selection = 'speed'
    for x, y in prepInit(station, selection):
        print(x, y)
