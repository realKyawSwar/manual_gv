from showa.lib import logs
from datetime import datetime
import pandas as pd
from showa.modules import config, writeRead, plotty
import os
import fnmatch


def main_tasks(df, date_time, line, chamber):
    df['Speed'] = df['original'].apply(lambda x:
                                       writeRead.speedClean(x))
    df['Torque'] = df['original'].apply(lambda x:
                                        writeRead.torqueClean(x))
    df = df.drop(['original'], axis=1)
    df = df[50:]
    df = df.reset_index(drop=True)
    dfSpeed = df['Speed']
    dfTorque = df['Torque']
    plotty.plot(line, chamber, dfSpeed, dfTorque, date_time)


def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


# main start; looping COM ports(devices) and run main code
def main(chamber, com):
    logs.initLogger()
    date_time = datetime.now().strftime(config.pngdate)
    line = 'Offline'
    try:
        dataDict = writeRead.fullSequence(line, chamber, com)
        df = pd.DataFrame.from_dict(dataDict)
        main_tasks(df, date_time, line, chamber)
        filepath = plotty.newDir(date_time, line)
        path = find(f'{line}_{chamber}_*', filepath).replace('/', '\\')
        os.startfile(path[0])
    except writeRead.portDisconnectError as e:
        logs.logError(f"{line} {chamber} Disconnected error: {e}",
                      includeErrorLine=True)
    except Exception as err:
        logs.logError(f"{line} {chamber} Error occured {err}",
                      includeErrorLine=True)
    finally:
        logs.closeLogger()


if __name__ == '__main__':
    main()
