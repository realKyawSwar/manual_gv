import json
from pathlib import Path


here = Path(__file__).resolve().parents[3]
configPath = str(here) + "/config/"

with open(configPath+'config.json') as config_file:
    config = json.load(config_file)


# writeUpload config
# Line = config['writeUpload']['Line']
comOffset = config['writeUpload']['comportOffset']
plotEnable = config['writeUpload']['plotEnable']
csvEnable = config['writeUpload']['csvEnable']

# Serial config
baud_rate = config['serial']['baudrate']
tout = config['serial']['timeout']
delay1 = config['serial']['delay1']
fdelay = config['serial']['fdelay']
decodeBits = config['serial']['decodeBits']
max_duration = config['serial']['max_duration']


# Graph Parameters
controlLine = config['graph']['controlLine']
picPath = config['graph']['picPath']
facecolor = config['graph']['facecolor']
torquecolor = config['graph']['torquecolor']
speedcolor = config['graph']['speedcolor']
gridcolor = config['graph']['gridcolor']
pngdate = config['graph']['pngdate']
dateonGraph = config['graph']['dateonGraph']

carrierStopCount = []
unresponsiveList = []
ch_retry = []
