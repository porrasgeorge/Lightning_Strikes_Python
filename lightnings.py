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
def lightnings_count_by_area(initial_date, final_date, cooperative):
    server = '192.168.4.11'
    database = 'LightningStrikes'
    password = 'lightnings'
    username = 'lightnings'
    cnxn = pyodbc.connect(driver='{SQL Server}', host=server, database=database,
                          user=username, password=password, autocommit=True)

    sql = f'exec [GetLightningsCount_API] \'{initial_date}\', \'{final_date}\', \'{cooperative}\''
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
def point_iconcolor(value):
    
    if value == 8:
        return simplekml.Color.red
    elif value == 7:
        return simplekml.Color.lightcoral
    elif value == 6:
        return simplekml.Color.orange
    elif value == 5:
        return simplekml.Color.yellow
    elif value == 4:
        return simplekml.Color.yellowgreen
    elif value == 3:
        return simplekml.Color.gray
    elif value == 2:
        return simplekml.Color.blue
    elif value == 1:
        return simplekml.Color.purple
    elif value == 0:
        return simplekml.Color.white
    else:
        return simplekml.Color.deeppink


#######################################################################################################
#######################################################################################################
#######################################################################################################
def kml_point_styles():
    kml_styles = []
    for i in range(0, 9):
        kml_style_pos = simplekml.Style()
        kml_style_neg = simplekml.Style()
        kml_style_pos.labelstyle.scale = 0
        kml_style_neg.labelstyle.scale = 0
        kml_style_pos.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/wht-circle.png'
        kml_style_neg.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/wht-blank.png'
        kml_style_pos.iconstyle.color = point_iconcolor(i)
        kml_style_neg.iconstyle.color = point_iconcolor(i)
        kml_styles.append([kml_style_neg, kml_style_pos])
    return kml_styles


#######################################################################################################
#######################################################################################################
#######################################################################################################
def create_kml_by_time(lightnings_df, info_data):
    if len(lightnings_df) == 0:
        return None

    lightnings_df = lightnings_df.sort_values(by='Fecha_Hora', ascending=True)
    lightnings_df['Intensity'] = lightnings_df['Intensity'] / 1000
    lightnings_df['Hour'] = lightnings_df['Fecha_Hora'].dt.hour
    lightnings_df['Minute'] = 5 * (lightnings_df['Fecha_Hora'].dt.minute // 5)
    lightnings_df['Intensity_ABS'] = abs(lightnings_df['Intensity'])
    lightnings_df['Category_ABS'] = lightnings_df['Intensity_ABS'].apply(
        lambda x: 8 if x >= 400 else (7 if x >= 300 else (
            6 if x >= 200 else(5 if x >= 120 else(
                4 if x >= 80 else(3 if x >= 60 else(
                    2 if x >= 40 else(1 if x >= 20 else 0))))))))
    lightnings_df['Category_dir'] = lightnings_df['Intensity'].apply(
        lambda x: 1 if x >= 0 else 0)

    print(f'{info_data["cooperative"]}: Creando KML por Hora')
    print(f'cantidad de descargas: {len(lightnings_df)}')

    kml_styles = kml_point_styles()
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
                point.description = f'''<style>
.styled-table {{
    border-collapse: collapse;
    margin: 25px 0;
    font-size: 0.9em;
    font-family: sans-serif;
    min-width: 200px;
}}
.styled-table tbody tr {{
    border-bottom: 1px solid #dddddd;
}}
.styled-table tbody tr:nth-of-type(even) {{
    background-color: #e3e3e3;
}}
</style>
<body>
<TABLE class="styled-table">
    <TR><TH>Intensidad</TH> <TD>{row["Intensity"]}kA</TD></TR>
    <TR><TH>Num. sensores</TH> <TD>{row["Sensors_Involved"]} </TD></TR>
    <TR><TH>Error Eje Mayor</TH> <TD> {row["Error_Mayor"]}km </TD></TR>
    <TR><TH>Error Eje Menor</TH> <TD>{row["Error_Minor"]}km </TD></TR>
    <TR><TH>Error Azimut</TH> <TD>{row["Error_Azimuth"]}°</TD></TR>
</TABLE>
</body>'''
                point.style = kml_styles[row["Category_ABS"]][row['Category_dir']]
                
    print("Guardando KML")
    full_path = f'{info_data["base_path"]}\\{info_data["date"].strftime("%m-%B")}\\{info_data["cooperative"]}'
    Path(full_path).mkdir(parents=True, exist_ok=True)
    kml.save(
        f'{full_path}\\{info_data["cooperative"]}_{info_data["date"]}_byDate.kml')
    print("Listo....\n\n")


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
    lightnings_df['Category_ABS'] = lightnings_df['Intensity_ABS'].apply(
        lambda x: 8 if x >= 400 else (7 if x >= 300 else (
            6 if x >= 200 else(5 if x >= 120 else(
                4 if x >= 80 else(3 if x >= 60 else(
                    2 if x >= 40 else(1 if x >= 20 else 0))))))))
    lightnings_df['Category_dir'] = lightnings_df['Intensity'].apply(
        lambda x: 1 if x >= 0 else 0)

    categories = {0: 'Menos de 20kA', 1: 'Entre 20kA y 40kA', 2: 'Entre 40kA y 60kA', 3: 'Entre 60kA y 80kA',
                  4: 'Entre 80kA y 120kA', 5: 'Entre 120kA y 200kA', 6: 'Entre 200kA y 300kA', 7: 'Mas de 300kA'}

    print(f'{info_data["cooperative"]}: Creando KML por Amplitud')
    print(f'cantidad de descargas: {len(lightnings_df)}')
    
    kml_styles = kml_point_styles()
    kml = simplekml.Kml()
    unique_categories = lightnings_df.Category_ABS.unique()
    for category in unique_categories:
        category_df = lightnings_df[lightnings_df.Category_ABS == category]
        category_fol = kml.newfolder(
            name=f'{categories[category]} ({len(category_df)} descargas)')
        for index, row in category_df.iterrows():
            point = category_fol.newpoint(
                name=row['Fecha_Hora'].strftime("%Y/%m/%d %H:%M:%S"))
            point.coords = [(row['Longitud'], row['Latitud'])]
            #point.description = f'Intensidad: {row["Intensity"]}kA'
            point.description = f'''<style>
.styled-table {{
    border-collapse: collapse;
    margin: 25px 0;
    font-size: 0.9em;
    font-family: sans-serif;
    min-width: 200px;
}}
.styled-table tbody tr {{
    border-bottom: 1px solid #dddddd;
}}
.styled-table tbody tr:nth-of-type(even) {{
    background-color: #e3e3e3;
}}
</style>
<body>
<TABLE class="styled-table">
    <TR><TH>Intensidad</TH> <TD>{row["Intensity"]}kA</TD></TR>
    <TR><TH>Num. sensores</TH> <TD>{row["Sensors_Involved"]} </TD></TR>
    <TR><TH>Error Eje Mayor</TH> <TD> {row["Error_Mayor"]}km </TD></TR>
    <TR><TH>Error Eje Menor</TH> <TD>{row["Error_Minor"]}km </TD></TR>
    <TR><TH>Error Azimut</TH> <TD>{row["Error_Azimuth"]}°</TD></TR>
</TABLE>
</body>'''
            point.style = kml_styles[row["Category_ABS"]][row['Category_dir']]

    print("Guardando KML")

    full_path = f'{info_data["base_path"]}\\{info_data["date"].strftime("%m-%B")}\\{info_data["cooperative"]}'
    Path(full_path).mkdir(parents=True, exist_ok=True)
    kml.save(
        f'{full_path}\\{info_data["cooperative"]}_{info_data["date"]}_byAmplitude.kml')
    print("Listo....\n\n")


# #######################################################################################################
# #######################################################################################################
# #######################################################################################################
def create_csv_by_time(lightnings_df, info_data):
    if len(lightnings_df) == 0:
        return None

    lightnings_df = lightnings_df.sort_values(by='Fecha_Hora', ascending=True)

    print(f'{info_data["cooperative"]}: Creando CSV y XLSX')
    print(f'cantidad de descargas: {len(lightnings_df)}')

    full_path = f'{info_data["base_path"]}\\{info_data["date"].strftime("%m-%B")}\\{info_data["cooperative"]}'
    #path_to_file = "kml"
    Path(full_path).mkdir(parents=True, exist_ok=True)
    lightnings_df.to_excel(
        f'{full_path}\\{info_data["cooperative"]}_{info_data["date"]}.xlsx', sheet_name="Descargas", index=False)
    # lightnings_df.to_csv(
    #     f'{full_path}\\{info_data["cooperative"]}_{info_data["date"]}.csv', index=False)

    print("Listo....\n\n")


def create_kml_by_area(lightnings_df, info_data):

    lightnings_df['AVG_Amp'] = lightnings_df['AVG_Amp'] / 1000
    lightnings_df['MAX_Amp'] = lightnings_df['MAX_Amp'] / 1000

    max_count = max(lightnings_df.Cantidad)
    high_factor = 10000.0 / (max_count ** 2)
    count_levels = (max_count //10, (25*max_count)//100, (5*max_count)//10, (7*max_count)//10)
    lightnings_df['Category'] = lightnings_df['Cantidad'].apply(
            lambda x: 4 if x >= count_levels[3] else (3 if x >= count_levels[2] else (
                2 if x >= count_levels[1] else(1 if x >= count_levels[0] else 0))))

    categories = {0: f'Menos de {count_levels[0]} descargas', 
                    1: f'Entre {count_levels[0]} y {count_levels[1]-1} descargas', 
                    2: f'Entre {count_levels[1]} y {count_levels[2]-1} descargas', 
                    3: f'Entre {count_levels[2]} y {count_levels[3]-1} descargas',
                    4: f'Entre {count_levels[3]} y {max_count} descargas'}

    
    ancho_base = 0.018
    min_height = 1000

    kml = simplekml.Kml()
    kml_style_color4 = simplekml.Style()
    kml_style_color4.linestyle.width = 0
    kml_style_color4.polystyle.color = 'AA0000ff'
    kml_style_color4.labelstyle.scale = 0

    kml_style_color3 = simplekml.Style()
    kml_style_color3.linestyle.width = 0
    kml_style_color3.polystyle.color = 'AA14F0FF'
    kml_style_color3.labelstyle.scale = 0

    kml_style_color2 = simplekml.Style()
    kml_style_color2.linestyle.width = 0
    kml_style_color2.polystyle.color = 'AAff0000'
    kml_style_color2.labelstyle.scale = 0

    kml_style_color1 = simplekml.Style()
    kml_style_color1.linestyle.width = 0
    kml_style_color1.polystyle.color = 'AAFFFFFF'
    kml_style_color1.labelstyle.scale = 0

    kml_style_color0 = simplekml.Style()
    kml_style_color0.linestyle.width = 0
    kml_style_color0.polystyle.color = 'AAFF78B4'
    kml_style_color0.labelstyle.scale = 0
    
    unique_categories = lightnings_df.Category.unique()
    for category in unique_categories:
        category_df = lightnings_df[lightnings_df.Category == category]
        category_fol = kml.newfolder(
            name=f'{categories[category]} ({len(category_df)} Areas)')
        for index, row in category_df.iterrows():
            if info_data['h_3d']:
                pol_height = high_factor * row["Cantidad"] ** 2 + min_height;
            else:
                pol_height = min_height
            pol = category_fol.newpolygon(name=f'{int(row["Cantidad"])} descargas', extrude = 1 )
            pol.outerboundaryis = [(row['Longitud'] , row['Latitud'], pol_height ),
                                    (row['Longitud'] , row['Latitud'] + ancho_base, pol_height),
                                    (row['Longitud'] + ancho_base, row['Latitud'] + ancho_base, pol_height),
                                    (row['Longitud'] + ancho_base, row['Latitud'], pol_height ),
                                    (row['Longitud'] , row['Latitud'], pol_height )]
            pol.description = f'Intensidad Promedio: {row["AVG_Amp"]}kA \nIntensidad Maxima: {row["MAX_Amp"]}kA'
            pol.altitudemode = simplekml.AltitudeMode.relativetoground
            if row["Category"] == 4:
                pol.style = kml_style_color4
            elif row["Category"] == 3:
                pol.style = kml_style_color3
            elif row["Category"] == 2:
                pol.style = kml_style_color2
            elif row["Category"] == 1:
                pol.style = kml_style_color1
            else:
                pol.style = kml_style_color0

    print("Guardando KML")
    full_path = f'{info_data["base_path"]}\\mensual'
    Path(full_path).mkdir(parents=True, exist_ok=True)
    kml.save(
        f'{full_path}\\{info_data["cooperative"]}_{info_data["date"].strftime("%m-%B")}.kml')
    print("Listo....\n\n")
