from showa.modules import config
# import config
from showa.lib.database import Postgres
from showa.lib import logs
from datetime import datetime
import pandas as pd


def reconstruct_df(df, date_time, line, chamber):
    print(f"plotting..for {chamber}")
    dfSpeed = df[['Speed']]
    dfSpeed = dfSpeed.astype(float)
    dfTorque = df[['Torque']]
    dfTorque = dfTorque.astype(float)
    dfRecon = pd.concat([dfSpeed, dfTorque], axis=1)
    # print(f"lenght of index is {len(df.index)}")
    dfRecon.insert(0, 'Index', range(len(df.index)))
    dfRecon.insert(1, 'date_time', datetime.now().replace(microsecond=0))
    dfRecon.insert(2, 'line', line)
    dfRecon.insert(3, 'chamber', chamber)
    # print(dfRecon)
    return dfRecon


def upload_(newdf):
    myPg = None
    print("Uploading to database..")
    try:
        myPg = Postgres(config.url, config.database, config.user,
                        config.password)
        myPg.connect()
        print("Connection succeeded for features..")
        listy = newdf.to_csv(None, header=False, index=False).split('\n')
        vals = [','.join(ele.split()) for ele in listy]
        for i in vals:
            y = i.split(",")
            # combine date time string to sigle column
            y[1: 3] = [' '.join(y[1: 3])]
            x = list(y)
            if not x[0] == '':
                x[0] = int(x[0])
            else:
                pass
            z = tuple(x)
            if z == ('', ''):
                pass
            else:
                strSQL = f"INSERT INTO gv.gv_torque values {z}"
                myPg.execute(strSQL)
        myPg.commit()
    except Exception as err:
        print(f"Upload Error Occured: {str(err)}")
        logs.logError(
            f"Upload Error Occured: {str(err)}", includeErrorLine=True)
    finally:
        if myPg is not None:
            myPg.close()
