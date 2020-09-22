import simplekml
import pyodbc
import datetime
import csv
import pandas as pd
from pathlib import Path


#######################################################################################################
#######################################################################################################
#######################################################################################################
def read_lightnings(event_datetime, cooperative, date_period=1):
    server = '192.168.4.11'
    #server = '192.168.88.252'
    database = 'LightningStrikes'
    password = 'lightnings'
    username = 'lightnings'
    cnxn = pyodbc.connect(driver='{SQL Server}', host=server, database=database,
                          user=username, password=password, autocommit=True)

    sql = f'exec [GetAllLightnings_API] \'{event_datetime}\', \'{cooperative}\', \'{date_period}\''
    try:
        lightnings_df = pd.read_sql_query(sql, cnxn)
    except pyodbc.Error as err:
        print('Error !!!!! %s' % err)
        return None
    cnxn.close()
    return lightnings_df


#######################################################################################################
#######################################################################################################
#######################################################################################################
def point_iconstyle(value):
    if value > 0:
        return 'http://maps.google.com/mapfiles/kml/paddle/wht-circle.png'
    else:
        return 'http://maps.google.com/mapfiles/kml/paddle/wht-blank.png'


#######################################################################################################
#######################################################################################################
#######################################################################################################
def point_iconcolor(value):
    value = abs(value)
    if value >= 400:
        return simplekml.Color.red
    elif value >= 300:
        return simplekml.Color.lightcoral
    elif value >= 200:
        return simplekml.Color.orange
    elif value >= 120:
        return simplekml.Color.yellow
    elif value >= 80:
        return simplekml.Color.yellowgreen
    elif value >= 60:
        return simplekml.Color.gray
    elif value >= 40:
        return simplekml.Color.blue
    elif value >= 20:
        return simplekml.Color.purple
    elif value > 0:
        return simplekml.Color.white
    else:
        return simplekml.Color.deeppink

#######################################################################################################
#######################################################################################################
#######################################################################################################


def create_kml_by_time(lightnings_df, info_data):
    if len(lightnings_df) == 0:
        return None

    lightnings_df = lightnings_df.sort_values(by='Fecha_Hora', ascending=True)
    print(f'cantidad de descargas: {len(lightnings_df)}\n')

    lightnings_df['Intensity'] = lightnings_df['Intensity'] / 1000
    lightnings_df['Hour'] = lightnings_df['Fecha_Hora'].dt.hour
    lightnings_df['Minute'] = 5 * (lightnings_df['Fecha_Hora'].dt.minute // 5)

    print("Creando KML")
    kml = simplekml.Kml()
    unique_hours = lightnings_df.Hour.unique()
    for hr in unique_hours:
        hr_df = lightnings_df[lightnings_df.Hour == hr]
        hour_fol = kml.newfolder(name=f'{hr:02d}:00 ({len(hr_df)} descargas)')
        unique_mins = hr_df.Minute.unique()
        for mn in unique_mins:
            mn_df = hr_df[hr_df.Minute == mn]
            minute_fol = hour_fol.newfolder(
                name=f'{hr:02d}:{mn:02d} ({len(mn_df)} descargas)')
            for index, row in mn_df.iterrows():
                point = minute_fol.newpoint(
                    name=row['Fecha_Hora'].strftime("%Y/%m/%d %H:%M:%S"))
                point.coords = [(row['Longitud'], row['Latitud'])]
                point.description = f'Intensidad: {row["Intensity"]}kA'
                point.style.labelstyle.scale = 0
                ##point.visibility = 0
                point.style.iconstyle.icon.href = point_iconstyle(
                    row["Intensity"])
                point.style.iconstyle.color = point_iconcolor(row["Intensity"])

    print("Guardando KML")
    full_path = f'{info_data["base_path"]}\\{info_data["cooperative"]}'
    Path(full_path).mkdir(parents=True, exist_ok=True)
    kml.save(
        f'{full_path}\\{info_data["cooperative"]}_{info_data["date"]}_byDate.kml')
    print("Listo....")


#######################################################################################################
#######################################################################################################
#######################################################################################################
def create_kml_by_amplitude(lightnings_df, info_data):
    if len(lightnings_df) == 0:
        return None

    lightnings_df['Intensity'] = lightnings_df['Intensity'] / 1000
    lightnings_df['Intensity_ABS'] = abs(lightnings_df['Intensity'])
    lightnings_df = lightnings_df.sort_values(
        by='Intensity_ABS', ascending=False)
    lightnings_df['Category'] = lightnings_df['Intensity_ABS'].apply(
        lambda x: 8 if x >= 400 else (7 if x >= 300 else (
            6 if x >= 200 else(5 if x >= 120 else(
                4 if x >= 80 else(3 if x >= 60 else(
                    2 if x >= 40 else(1 if x >= 20 else 0))))))))

    print(f'cantidad de descargas: {len(lightnings_df)}\n')
    categories = {0: 'Menos de 20kA', 1: 'Entre 20kA y 40kA', 2: 'Entre 40kA y 60kA', 3: 'Entre 60kA y 80kA',
                  4: 'Entre 80kA y 120kA', 5: 'Entre 120kA y 200kA', 6: 'Entre 200kA y 300kA', 7: 'Mas de 300kA'}

    print("Creando KML")
    kml = simplekml.Kml()
    unique_categories = lightnings_df.Category.unique()
    for category in unique_categories:
        category_df = lightnings_df[lightnings_df.Category == category]
        category_fol = kml.newfolder(
            name=f'{categories[category]} ({len(category_df)} descargas)')
#        print(category_df)
        for index, row in category_df.iterrows():
            point = category_fol.newpoint(
                name=row['Fecha_Hora'].strftime("%Y/%m/%d %H:%M:%S"))
            point.coords = [(row['Longitud'], row['Latitud'])]
            point.description = f'Intensidad: {row["Intensity"]}kA'
            point.style.labelstyle.scale = 0
            ##point.visibility = 0
            point.style.iconstyle.icon.href = point_iconstyle(
                row["Intensity"])
            point.style.iconstyle.color = point_iconcolor(row["Intensity"])

    print("Guardando KML")

#    kml.save(f'kml\\{file_name}_byAmplitude.kml')
    full_path = f'{info_data["base_path"]}\\{info_data["cooperative"]}'
    Path(full_path).mkdir(parents=True, exist_ok=True)
    kml.save(
        f'{full_path}\\{info_data["cooperative"]}_{info_data["date"]}_byAmplitude.kml')
    print("Listo....")


# #######################################################################################################
# #######################################################################################################
# #######################################################################################################
def create_csv_by_time(lightnings_df, info_data):
    if len(lightnings_df) == 0:
        return None

    lightnings_df = lightnings_df.sort_values(by='Fecha_Hora', ascending=True)
    print(f'cantidad de descargas: {len(lightnings_df)}\n')

    print("Guardando CSV")

    full_path = f'{info_data["base_path"]}\\{info_data["date"].strftime("%m-%B")}\\{info_data["cooperative"]}'
    #path_to_file = "kml"
    Path(full_path).mkdir(parents=True, exist_ok=True)
    lightnings_df.to_excel(
        f'{full_path}\\{info_data["cooperative"]}_{info_data["date"]}.xlsx', sheet_name="Descargas", index=False)
    lightnings_df.to_csv(
        f'{full_path}\\{info_data["cooperative"]}_{info_data["date"]}.csv', index=False)

    print("Listo....")
