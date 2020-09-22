
from datetime import timezone, datetime,  timedelta
from os import makedirs, path
import requests
import json
import pyodbc
import logging


log_filename = f'logs\\datalog_{datetime.now().strftime("%Y_%m")}_5min.log'
makedirs(path.dirname(log_filename), exist_ok=True)
logging.basicConfig(level=logging.INFO, filename=log_filename,
                    format='%(asctime)s Ln: %(lineno)d - %(message)s')

# centro del circulo
geocode_cr = '10.37, -84.00'

# creacion de fecha y hora
utc_dt_secs = datetime.now().timestamp()
utc_dt_secs_rounded = (utc_dt_secs//300)*300
utc_dt_rounded = (datetime.fromtimestamp(utc_dt_secs_rounded,
                                         tz=timezone.utc)-timedelta(minutes=5)).strftime("%Y%m%d%H%M")

print(utc_dt_rounded)


def API_request_save(API_location, API_datetime, lr_ID):
    # Base de datos
    server = '192.168.4.11'
    database = 'LightningStrikes'
    username = 'sa'
    password = 'Con3$adm.'
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server +
                          ';DATABASE='+database+';UID='+username+';PWD=' + password, autocommit=True)

    # API key
    apiKey = 'e3f4b0ed83574135b4b0ed8357b135d4'

    # Costa Rica
    url = "https://api.weather.com/v3/wx/lightning/recent/largeRegion/5minute"
    parameters_list = {'apiKey': apiKey,  'startDateTime': API_datetime,
                       'units': 'm', 'format': 'json', 'geocode': API_location}
    response_json = requests.get(url,  params=parameters_list).json()

    if response_json['success'] == False:
        logging.info("ERROR, REQUEST NOT SUCCEDED")
        for err in response_json['errors']:
            logging.info(err['error'])
    else:
        cursor = cnxn.cursor()
        sql = "{CALL InsertLightning_API (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)}"

        lightnings = response_json['lightning']
        logging.info(
            f'Date: {API_datetime}, Lightnings: {len(lightnings["intensity"])}')
        for i in range(len(lightnings['intensity'])):
            event_datetime = datetime.strptime(
                lightnings['validTimeUtc'][i], "%Y-%m-%dT%H:%M:%S.%f%z")
            values = (event_datetime, lightnings['latitude'][i], lightnings['longitude'][i], lightnings['intensity'][i], lightnings['errorAzimuth']
                      [i], lightnings['errorMajor'][i], lightnings['errorMinor'][i], lightnings['sensorsInvolved'][i], lightnings['strikeTypeCode'][i], lr_ID)
            try:
                cursor.execute(sql, values)
            except pyodbc.Error as err:
                logging.info(err)

        # Close and delete cursor
        cursor.close()
        del cursor

    # Close Connection
    cnxn.close()


logging.info("Fecha y Hora de los datos: " + str(utc_dt_rounded))

API_request_save(geocode_cr, utc_dt_rounded, 1)
