import binascii


def convertAscii_Hex(cd):
    """ ASCII to HEX conversion"""
    x = bytes(cd, 'utf-8')
    y = str(binascii.hexlify(x), 'ascii')
    cd = ' '.join(a+b for a, b in zip(y[::2], y[1::2]))
    return(cd)


def cmdStr(inputC, inputD):
    """Create command string from command input and data input,
    Checksum is added. Return bytearray"""
    SOH = '01 '
    STX = ' 02 '
    ETX = ' 03'
    a = convertAscii_Hex(inputC).split()
    b = convertAscii_Hex(inputD).split()
    for i in range(0, len(a)):
        a[i] = int(a[i], 16)
    for i in range(0, len(b)):
        b[i] = int(b[i], 16)
    total = int(STX, 16)+int(ETX, 16) + sum(a) + sum(b)
    dummy = str(hex(total))
    checksum = convertAscii_Hex(''.join((dummy[-2:]).split()).upper())
    return bytearray.fromhex(SOH+convertAscii_Hex(inputC)+STX +
                             convertAscii_Hex(inputD)+ETX+" "+checksum)


def dataLen(command):
    """Look up table for data length of corresponding commands"""
    dataLenDict = {'85': 6, 'B6': 6, '04': 10, '36': 10,
                   '02': 14, '05': 14, '37': 22}
    return dataLenDict[command]


def selection_TorS(stationNo, selection):
    cmdLst = ['02', '02',
              '36', 'B6', '36', 'B6',
              '36', 'B6', '36', '36',
              '36', 'B6', 'B6', 'B6',
              'B6', 'B6', 'B6', '36',
              'B6', '36', 'B6', '36',
              'B6', '36', '36', 'B6',
              'B6', 'B6']
    newCmdLst = [f'{stationNo}' + i for i in cmdLst]
    if selection == 'speed':
        dataLst = ['13', '11',
                   '10', '00FFFFFFFF0001FFFF', '10', '00FFFFFFFF0001FFFF',
                   '10', '00FFFFFFFF0001FFFF', '03', '02',
                   '02', '111EA5', '0281F0', '00FFFFFFFF0001FFFF',
                   '00FFFFFFFF0001FFFF', '00FFFFFFFF0001FFFF',
                   '00FFFFFFFF0001FFFF', '10',
                   '00FFFFFFFF0001FFFF', '10', '00FFFFFFFF0001FFFF', '10',
                   '00FFFFFFFF0001FFFF', '01', '02', '010000',
                   '028182', '101EA5']
    elif selection == 'torque':
        dataLst = ['13', '11',
                   '10', '00FFFFFFFF01FFFFFF', '10', '00FFFFFFFF0100FFFF',
                   '10', '00FFFFFFFF0100FFFF', '03', '02',
                   '02', '111EA5', '0281F0', '00FFFFFFFF0100FFFF',
                   '00FFFFFFFF0100FFFF', '00FFFFFFFF0100FFFF',
                   '00FFFFFFFF0100FFFF', '10',
                   '00FFFFFFFF0100FFFF', '10', '00FFFFFFFF0100FFFF', '10',
                   '00FFFFFFFF0100FFFF', '01', '02', '010001',
                   '028182', '101EA5']
    else:
        dataLst = []
    return [cmdStr(x, y) for x, y in zip(newCmdLst, dataLst)]


def checkerCmd(stationNo):
    """command to detect zero speed"""
    return cmdStr(f'{stationNo}36', '00')


def midCmd(stationNo):
    return [cmdStr(f'{stationNo}36', i) for i in ['00', '03', '03', '00']]


def fetchCmd(stationNo):
    new_str = []
    for x in range(4):
        for i in [hex(a)[2:].zfill(2).upper() for a in range(0, 256)]:
            i = i + f"000{x}"
            new_str.append(i)
    return [cmdStr(f"{stationNo}37", i) for i in new_str]


def endCmd(stationNo):
    initDatalst = ["05", "02", "01", "03"]
    initCmdlst = [f'{stationNo}' + "36" for i in range(5)]
    return [cmdStr(x, y) for x, y in zip(initCmdlst, initDatalst)]


if __name__ == '__main__':
    stationNo = '5'
    lol = (selection_TorS(stationNo, 'speed'))
    for i in lol:
       print(i)
    # # print(midCmd(stationNo))
    # fetchy = fetchCmd(stationNo)
    # del fetchy[-274:]
    # # print(fetchy)
    # # print(endCmd(stationNo))
    # print(len(fetchy))
