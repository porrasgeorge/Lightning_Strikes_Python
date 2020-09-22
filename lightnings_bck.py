import simplekml
import pyodbc
import datetime
import csv
from pandas import DataFrame
from pathlib import Path

#######################################################################################################


def read_lightnings(event_datetime_str, cooperative, date_period=1):
    server = '192.168.4.11'
    database = 'LightningStrikes'
    password = 'lightnings'
    username = 'lightnings'
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server +
                          ';DATABASE='+database+';UID='+username+';PWD=' + password, autocommit=True)
    cursor = cnxn.cursor()

    event_datetime = datetime.datetime.strptime(event_datetime_str, "%Y-%m-%d")
    print(event_datetime)

    sql = "{CALL [GetAllLightnings_API] (?, ?, ?)}"
    values = (event_datetime, cooperative, date_period)

    try:
        lightnings_tuple = cursor.execute(sql, values).fetchall()
        print([column[0] for column in cursor.description])
    except pyodbc.Error as err:
        print('Error !!!!! %s' % err)
        return None

    cursor.close()
    del cursor
    cnxn.close()

    lightning_list = []
    for lightning in lightnings_tuple:
        lightning_list.append(list(lightning))

    return lightning_list


def lightnings_in_hor(lightning_ls):
    counter = 0
    for minute in lightning_ls:
        counter += len(minute)
    return counter


#######################################################################################################
#######################################################################################################
#######################################################################################################
def create_kml_by_time(lightning_list, file_name):

    print("Cargando de base de datos")
    lightning_list.sort(key=lambda x: x[0])
    print(f'cantidad de descargas: {len(lightning_list)}\n')

    if len(lightning_list) == 0:
        return None

    # print(lightning_list[0])
    print("Creando Dataframe")
    lightnings_df = DataFrame(lightning_list, columns=[
        'Date_Time', 'Longitude', 'Latitude', 'Amplitude', 'Error_Azimuth', 'Error_Mayor', 'Error_Minor'])

    lightning_list_array = []
    for i in range(0, 24):
        lis_hour = []
        for j in range(0, 12):
            lis_min = []
            lis_hour.append(lis_min)
        lightning_list_array.append(lis_hour)

    lightnings_df['Amplitude'] = lightnings_df['Amplitude'] / 1000
    # lightnings_df['Date'] = lightnings_df['Date_Time'].dt.date
    lightnings_df['Hour'] = lightnings_df['Date_Time'].dt.hour
    lightnings_df['Minute'] = lightnings_df['Date_Time'].dt.minute // 5

    print("Iterando dataframe")

    for index, row in lightnings_df.iterrows():
        lightning_list_array[row['Hour']][row['Minute']].append(
            [row['Date_Time'], row['Longitude'], row['Latitude'], row['Amplitude'], row['Error_Azimuth'], row['Error_Mayor'], row['Error_Minor']])

    print("Creando KML")

    kml = simplekml.Kml()
    for idx_hour, hour in enumerate(lightning_list_array):
        if (lightnings_in_hor(hour) > 0):
            hour_fol = kml.newfolder(name=f'{idx_hour:02d}:00')

            for idx_minute, minute in enumerate(hour):
                if (len(minute) > 0):
                    minute_fol = hour_fol.newfolder(
                        name=f'{idx_hour:02d}:{idx_minute*5:02d}')
                    for light in minute:
                        point = minute_fol.newpoint(
                            name=light[0].strftime("%Y/%m/%d %H:%M:%S"))
                        point.coords = [(light[1], light[2])]
                        point.description = f'Amplitud: {light[3]}kA'
                        point.style.labelstyle.scale = 0
                        point.visibility = 0

                        if light[3] > 0:
                            point.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/wht-circle.png'
                        elif light[3] < 0:
                            point.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/wht-blank.png'
                        else:
                            point.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/wht-stars.png'

                        if abs(light[3]) >= 400:
                            point.style.iconstyle.color = simplekml.Color.red
                        elif abs(light[3]) >= 300:
                            point.style.iconstyle.color = simplekml.Color.lightcoral
                        elif abs(light[3]) >= 200:
                            point.style.iconstyle.color = simplekml.Color.orange
                        elif abs(light[3]) >= 120:
                            point.style.iconstyle.color = simplekml.Color.yellow
                        elif abs(light[3]) >= 80:
                            point.style.iconstyle.color = simplekml.Color.yellowgreen
                        elif abs(light[3]) >= 60:
                            point.style.iconstyle.color = simplekml.Color.gray
                        elif abs(light[3]) >= 40:
                            point.style.iconstyle.color = simplekml.Color.blue
                        elif abs(light[3]) >= 20:
                            point.style.iconstyle.color = simplekml.Color.purple
                        elif abs(light[3]) > 0:
                            point.style.iconstyle.color = simplekml.Color.white
                        else:
                            point.style.iconstyle.color = simplekml.Color.deeppink
    print("Guardando KML")
    path_to_file = "\\\\192.168.3.233\\comun\\DESCARGAS ATMOSFERICAS"
    Path(path_to_file).mkdir(parents=True, exist_ok=True)
    kml.save(f'{path_to_file}\\{file_name}_byDate.kml')
    print("Listo....")


#######################################################################################################
#######################################################################################################
#######################################################################################################
def create_kml_by_amplitude(lightning_list, file_name):
    lightning_list.sort(key=lambda x: abs(x[3]), reverse=True)
    print(lightning_list[0])
    print(f'cantidad de descargas: {len(lightning_list)}\n')

    if len(lightning_list) == 0:
        return None

    categories_quant = 9

    lightnings_df = DataFrame(lightning_list, columns=[
        'Date_Time', 'Longitude', 'Latitude', 'Amplitude', 'Error_Azimuth', 'Error_Mayor', 'Error_Minor'])

    lightning_list_array = []
    for i in range(0, categories_quant):
        lis_categ = []
        lightning_list_array.append(lis_categ)

    # print(lightning_list_array)
    lightnings_df['Amplitude'] = lightnings_df['Amplitude'] / 1000
    lightnings_df['abs_Amplitude'] = abs(lightnings_df['Amplitude'])
    lightnings_df['Category'] = lightnings_df['abs_Amplitude'].apply(
        lambda x: 8 if x >= 400 else (7 if x >= 300 else (
            6 if x >= 200 else(5 if x >= 120 else(
                4 if x >= 80 else(3 if x >= 60 else(
                    2 if x >= 40 else(1 if x >= 20 else 0))))))))

    # print(lightnings_df)

    categories = {0: 'Menos de 20kA', 1: 'Entre 20kA y 40kA', 2: 'Entre 40kA y 60kA', 3: 'Entre 60kA y 80kA',
                  4: 'Entre 80kA y 120kA', 5: 'Entre 120kA y 200kA', 6: 'Entre 200kA y 300kA', 7: 'Mas de 300kA'}

    for index, row in lightnings_df.iterrows():
        lightning_list_array[row['Category']].append(
            [row['Date_Time'], row['Longitude'], row['Latitude'], row['Amplitude'], row['Error_Azimuth'], row['Error_Mayor'], row['Error_Minor']])

    kml = simplekml.Kml()
    for idx_cat, category in enumerate(lightning_list_array):
        if (lightnings_in_hor(category) > 0):
            category_fol = kml.newfolder(name=f'{categories[idx_cat]}')

            for light in category:
                point = category_fol.newpoint(
                    name=light[0].strftime("%Y/%m/%d %H:%M:%S"))
                point.coords = [(light[1], light[2])]
                point.description = f'Amplitud: {light[3]}kA'
                point.style.labelstyle.scale = 0
                point.visibility = 0

                if light[3] > 0:
                    point.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/wht-circle.png'
                elif light[3] < 0:
                    point.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/wht-blank.png'
                else:
                    point.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/wht-stars.png'

                if abs(light[3]) >= 400:
                    point.style.iconstyle.color = simplekml.Color.red
                elif abs(light[3]) >= 300:
                    point.style.iconstyle.color = simplekml.Color.lightcoral
                elif abs(light[3]) >= 200:
                    point.style.iconstyle.color = simplekml.Color.orange
                elif abs(light[3]) >= 120:
                    point.style.iconstyle.color = simplekml.Color.yellow
                elif abs(light[3]) >= 80:
                    point.style.iconstyle.color = simplekml.Color.yellowgreen
                elif abs(light[3]) >= 60:
                    point.style.iconstyle.color = simplekml.Color.gray
                elif abs(light[3]) >= 40:
                    point.style.iconstyle.color = simplekml.Color.blue
                elif abs(light[3]) >= 20:
                    point.style.iconstyle.color = simplekml.Color.purple
                elif abs(light[3]) > 0:
                    point.style.iconstyle.color = simplekml.Color.white
                else:
                    point.style.iconstyle.color = simplekml.Color.deeppink
    kml.save(f'kml\\{file_name}_byAmplitude.kml')


#######################################################################################################
#######################################################################################################
#######################################################################################################
def create_csv_by_time(lightning_list, file_name):

    print("Cargando de base de datos")
    lightning_list.sort(key=lambda x: x[0])
    print(f'cantidad de descargas: {len(lightning_list)}\n')

    if len(lightning_list) == 0:
        return None

    print("Guardando CSV")
    path_to_file = "\\\\192.168.3.233\\comun\\DESCARGAS ATMOSFERICAS"
    Path(path_to_file).mkdir(parents=True, exist_ok=True)
    with open(f'{path_to_file}\\{file_name}_byDate.csv', 'w', newline='') as csv_file:
        wr = csv.writer(csv_file)
        for item in lightning_list:
            wr.writerow(item)
    print("Listo....")
