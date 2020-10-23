import simplekml
import pyodbc
import datetime
import csv
import pandas as pd
import numpy as np
import math
from pathlib import Path
from dateutil import tz


#######################################################################################################
#######################################################################################################
#######################################################################################################
def lightnings_db_connection():
    server = '192.168.4.11'
    database = 'LightningStrikes'
    password = 'lightnings'
    username = 'lightnings'
    cnxn = pyodbc.connect(driver='{SQL Server}', host=server, database=database,
                          user=username, password=password, autocommit=True)
    return cnxn


#######################################################################################################
#######################################################################################################
#######################################################################################################
def read_lightnings(event_datetime, cooperative, date_period=1):

    cnxn = lightnings_db_connection()
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
def lightnings_count_by_area(initial_date, final_date, cooperative, limited_by_polygon = 1):

    cnxn = lightnings_db_connection()
    sql = f'exec [GetLightningsCount_API] \'{initial_date}\', \'{final_date}\', \'{cooperative}\', \'{limited_by_polygon}\''
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
        ballon_color = point_iconcolor(i)
        icon_color = simplekml.Color.changealpha('99', ballon_color)
        kml_style_pos = simplekml.Style()
        kml_style_neg = simplekml.Style()
        kml_style_pol_50 = simplekml.Style()
        kml_style_pol_99 = simplekml.Style()
        kml_style_pos.labelstyle.scale = 0
        kml_style_neg.labelstyle.scale = 0
        kml_style_pos.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/wht-circle.png'
        kml_style_neg.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/wht-blank.png'
        kml_style_pos.iconstyle.color = icon_color
        kml_style_neg.iconstyle.color = icon_color
        kml_style_pos.balloonstyle.bgcolor = ballon_color
        kml_style_neg.balloonstyle.bgcolor = ballon_color
        kml_style_pol_50.linestyle.width = 3
        kml_style_pol_50.linestyle.color = icon_color
        kml_style_pol_99.linestyle.width = 6
        kml_style_pol_99.linestyle.color = icon_color
        kml_styles.append([kml_style_neg, kml_style_pos, kml_style_pol_50, kml_style_pol_99])
    return kml_styles


#######################################################################################################
#######################################################################################################
#######################################################################################################
def ellipse_polygon(longitude, latitude, major_err, minor_err, azimuth, probability = 0):

    if probability == 0:
        a = major_err / 2
        b = minor_err / 2
    elif probability == 1:
        a = 1.82 * major_err / 2
        b = 1.82 * minor_err / 2
    else:
        a = 2.57 * major_err / 2
        b = 2.57 * minor_err / 2
   
    ## constants
    EARTH_RADIUS = 6373
    NUMBER_SIDES = 72
    STEP = 2*math.pi/NUMBER_SIDES

    ## ratio kn/degrees acording to latitude
    vert_km_to_degrees_ratio = math.degrees(1/EARTH_RADIUS)
    hor_km_to_degrees_ratio = vert_km_to_degrees_ratio / abs(math.cos(math.radians(latitude)))

    ## creating the ellipse
    angle = np.arange(0.0, 2*math.pi + STEP, STEP)
    R = a*b/(np.sqrt(np.power(a*np.cos(angle),2)+np.power(b*np.sin(angle),2)))
    new_angle = angle - math.radians(azimuth)

    x = R * np.cos(new_angle) * hor_km_to_degrees_ratio
    y = R * np.sin(new_angle) * vert_km_to_degrees_ratio

    ellipse = []
    for i in range(len(x)):
        ellipse.append((longitude + x[i], latitude + y[i]))

    return ellipse

#######################################################################################################
#######################################################################################################
#######################################################################################################
def create_kml_by_time(lightnings_df, info_data, add_error_ellipses = False):
        
    lightnings_lenght = len(lightnings_df)
    light_len_disable = lightnings_lenght > 10000
    
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

    print(f'{info_data["cooperative"]}: {len(lightnings_df)} TIME')

    kml_styles = kml_point_styles()
    ellipse_polystyle = simplekml.PolyStyle(fill=0, outline=1)
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
            if add_error_ellipses:
                ellipse_fol = minute_fol.newfolder(name='Areas de probabilidad')
            
            for _, row in mn_df.iterrows():
                point = minute_fol.newpoint(
                    name=row['Fecha_Hora'].strftime("%Y/%m/%d %H:%M:%S"))
                point_timestamp = row['Fecha_Hora'].replace(second=0, microsecond=0).isoformat()
                
                if add_error_ellipses:
                    # ellipse_50 = ellipse_fol.newpolygon(
                    #     name=f'{row["Fecha_Hora"].strftime("%Y/%m/%d %H:%M:%S")} 50%')
                    # ellipse_50.outerboundaryis = ellipse_polygon(row['Longitud'], row['Latitud'], row["Error_Mayor"], row["Error_Minor"], row["Error_Azimuth"])
                    # ellipse_50.style = kml_styles[row["Category_ABS"]][2]
                    # ellipse_50.polystyle = ellipse_polystyle
                    # ellipse_50.visibility = 0
                    # ellipse_50.timestamp.when = point_timestamp
                    ##ellipse_50.timespan.end = (row['Fecha_Hora']+datetime.timedelta(minutes=30)).isoformat()

                    ellipse_99 = ellipse_fol.newpolygon(
                        name=f'{row["Fecha_Hora"].strftime("%Y/%m/%d %H:%M:%S")} 99%')
                    ellipse_99.outerboundaryis = ellipse_polygon(row['Longitud'], row['Latitud'], row["Error_Mayor"], row["Error_Minor"], row["Error_Azimuth"], probability = 2)
                    ellipse_99.style = kml_styles[row["Category_ABS"]][3]
                    ellipse_99.polystyle = ellipse_polystyle
                    ellipse_99.visibility = 0
                    ellipse_99.timestamp.when = point_timestamp
                
                point.coords = [(row['Longitud'], row['Latitud'])]
                point.style = kml_styles[row["Category_ABS"]][row['Category_dir']]
                if light_len_disable:
                    point.visibility = 0
                point.timestamp.when = point_timestamp
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
                
    full_path = f'{info_data["base_path"]}\\{info_data["date"].strftime("%m-%B")}\\{info_data["cooperative"]}'
    Path(full_path).mkdir(parents=True, exist_ok=True)
    if add_error_ellipses:
        kml.save(
            f'{full_path}\\{info_data["cooperative"]}_{info_data["date"]}_porFecha (Elipses).kml')
    else:
        kml.save(
            f'{full_path}\\{info_data["cooperative"]}_{info_data["date"]}_porFecha.kml')


#######################################################################################################
#######################################################################################################
#######################################################################################################
def create_kml_by_amplitude(lightnings_df, info_data):
    
    lightnings_lenght = len(lightnings_df)
    
    if lightnings_lenght == 0:
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

    print(f'{info_data["cooperative"]}: {len(lightnings_df)} AMPLITUDE')
    
    kml_styles = kml_point_styles()
    kml = simplekml.Kml()
    unique_categories = lightnings_df.Category_ABS.unique()
    for category in unique_categories:
        category_df = lightnings_df[lightnings_df.Category_ABS == category]
        category_fol = kml.newfolder(
            name=f'{categories[category]} ({len(category_df)} descargas)')
        for _, row in category_df.iterrows():
            point = category_fol.newpoint(
                name=row['Fecha_Hora'].strftime("%Y/%m/%d %H:%M:%S"))
            point.coords = [(row['Longitud'], row['Latitud'])]
            point.style = kml_styles[row["Category_ABS"]][row['Category_dir']]
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

    full_path = f'{info_data["base_path"]}\\{info_data["date"].strftime("%m-%B")}\\{info_data["cooperative"]}'
    Path(full_path).mkdir(parents=True, exist_ok=True)
    kml.save(
        f'{full_path}\\{info_data["cooperative"]}_{info_data["date"]}_por_Amplitud.kml')


# #######################################################################################################
# #######################################################################################################
# #######################################################################################################
def create_csv_by_time(lightnings_df, info_data):
    if len(lightnings_df) == 0:
        return None

    lightnings_df = lightnings_df.sort_values(by='Fecha_Hora', ascending=True)

    print(f'{info_data["cooperative"]}: {len(lightnings_df)} CSV')

    full_path = f'{info_data["base_path"]}\\{info_data["date"].strftime("%m-%B")}\\{info_data["cooperative"]}'
    #path_to_file = "kml"
    Path(full_path).mkdir(parents=True, exist_ok=True)
    lightnings_df.to_excel(
        f'{full_path}\\{info_data["cooperative"]}_{info_data["date"]}.xlsx', sheet_name="Descargas", index=False)
    # lightnings_df.to_csv(
    #     f'{full_path}\\{info_data["cooperative"]}_{info_data["date"]}.csv', index=False)


#######################################################################################################
#######################################################################################################
#######################################################################################################
def create_kml_by_area(lightnings_df, info_data, file_name_append = ""):
    
    print(f'{info_data["cooperative"]}: {len(lightnings_df)} AREA')
    
    if len(lightnings_df) == 0:
        return None
    
    def create_kml_style(style_color):
        kml_style_color = simplekml.Style()
        kml_style_color.linestyle.width = 0
        kml_style_color.polystyle.color = style_color
        kml_style_color.labelstyle.scale = 0
        return kml_style_color
    
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

    kml_style_color4 = create_kml_style('AA0000ff')
    kml_style_color3 = create_kml_style('AA14F0FF')
    kml_style_color2 = create_kml_style('AAff0000')
    kml_style_color1 = create_kml_style('AAFFFFFF')
    kml_style_color0 = create_kml_style('AAFF78B4')
    
    kml = simplekml.Kml()
    unique_categories = lightnings_df.Category.unique()
    for category in unique_categories:
        category_df = lightnings_df[lightnings_df.Category == category]
        category_fol = kml.newfolder(
            name=f'{categories[category]} ({len(category_df)} Areas)')
        for _, row in category_df.iterrows():
            if info_data['h_3d']:
                pol_height = high_factor * row["Cantidad"] ** 2 + min_height
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

    if (info_data['period'] == 'week'):
        full_path = f'{info_data["base_path"]}\\semanal'
        Path(full_path).mkdir(parents=True, exist_ok=True)
        kml.save(
            f'{full_path}\\{info_data["cooperative"]}_{info_data["date"].strftime("%Y-%m-%d")}{file_name_append}.kml')
    else:
        full_path = f'{info_data["base_path"]}\\mensual'
        Path(full_path).mkdir(parents=True, exist_ok=True)
        kml.save(
            f'{full_path}\\{info_data["cooperative"]}_{info_data["date"].strftime("%Y-%B")}{file_name_append}.kml')

#######################################################################################################
#######################################################################################################
#######################################################################################################
def create_kml_live_data():
    def kml_create(lightnings_df):
        kml_style_red = simplekml.Style()
        kml_style_red.iconstyle.icon.href = 'icons/bolt.png'
        kml_style_red.iconstyle.scale = 2
        kml_style_red.labelstyle.scale = 0
        kml_style_red.iconstyle.color = simplekml.Color.red
        kml_style_yellow = simplekml.Style()
        kml_style_yellow.iconstyle.icon.href = 'icons/bolt.png'
        kml_style_yellow.iconstyle.scale = 1.5
        kml_style_yellow.labelstyle.scale = 0
        kml_style_yellow.iconstyle.color = simplekml.Color.yellow
        kml_style_highlighted = simplekml.Style()
        kml_style_highlighted.iconstyle.icon.href = 'icons/bolt.png'
        kml_style_highlighted.iconstyle.scale = 2.5
        kml_style_highlighted.labelstyle.scale = 1.5
        kml_style_highlighted.iconstyle.color = simplekml.Color.orange
        ellipse_style_red = simplekml.Style()
        ellipse_style_red.linestyle.width = 3
        ellipse_style_red.linestyle.color = simplekml.Color.red
        ellipse_style_red.polystyle.fill = 0
        ellipse_style_red.polystyle.outline = 1
        ellipse_style_yellow = simplekml.Style()
        ellipse_style_yellow.linestyle.width = 2
        ellipse_style_yellow.linestyle.color = simplekml.Color.yellow
        ellipse_style_yellow.polystyle.fill = 0
        ellipse_style_yellow.polystyle.outline = 1

        kml = simplekml.Kml()
        ellipses_fol = kml.newfolder(name=f'Elipses de error')
        with_timestamp = (max(lightnings_df.Fecha_Hora) - min(lightnings_df.Fecha_Hora)) > datetime.timedelta(minutes=60)
        
        for _, row in lightnings_df.iterrows():
            point = kml.newpoint(
                name=row['Fecha_Hora'].strftime("%H:%M:%S"))
            
            point.coords = [(row['Longitud'], row['Latitud'])]
            point.stylemap.highlightstyle = kml_style_highlighted
            
            if row['Category']:
                point.stylemap.normalstyle = kml_style_red
            else:
                point.stylemap.normalstyle = kml_style_yellow    
            
            if with_timestamp:
                point.timestamp.when = row['Fecha_Hora'].replace(second=0, microsecond=0).isoformat()
            else:
                ellipse = ellipses_fol.newpolygon(name=row['Fecha_Hora'].strftime("%H:%M:%S"))
                ellipse.outerboundaryis = ellipse_polygon(row['Longitud'], row['Latitud'], row["Error_Mayor"], row["Error_Minor"], row["Error_Azimuth"], probability = 2)
                ellipse.visibility = 0
                if row['Category']:
                    ellipse.style = ellipse_style_red
                else:
                    ellipse.style = ellipse_style_yellow
                
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
                </style>
                <body>
                <TABLE class="styled-table">
                    <TR><TH>Hora</TH> <TD>{row['Fecha_Hora'].strftime("%Y/%m/%d %H:%M:%S")}</TD></TR>
                    <TR><TH>Intensidad</TH> <TD>{row["Intensity"]}kA</TD></TR>
                    <TR><TH>Num. sensores</TH> <TD>{row["Sensors_Involved"]} </TD></TR>
                </TABLE>
                </body>'''

        return kml

    delta_time_report1 = datetime.timedelta(hours=4)
    delta_time_report2 = datetime.timedelta(minutes=30)
    end_date = datetime.datetime.now().replace(second=0, microsecond=0)
    initial_date_report1 = end_date - delta_time_report1
    initial_date_report2 = end_date - delta_time_report2

    full_path = f'\\\\192.168.3.233\\Public\\Lightnings'
    coop_id = 5
    
    lightnings_df = read_lightnings(initial_date_report1, coop_id)
    print(f'descargas: {len(lightnings_df)} LIVE DATA')
    if len(lightnings_df) != 0:
        lightnings_df = lightnings_df.sort_values(by='Fecha_Hora', ascending=True)
        lightnings_df['Intensity'] = lightnings_df['Intensity'] / 1000
        lightnings_df['Category'] = (end_date - lightnings_df['Fecha_Hora']) <= datetime.timedelta(minutes=30)
        kml = kml_create(lightnings_df)
        Path(full_path).mkdir(parents=True, exist_ok=True)
    else:
        kml = simplekml.Kml()
        point = kml.newpoint(name= f'No hay descargas - {end_date.strftime("%H:%M")}')
        point.coords = [(-85.5, 10.1)]
        point.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/info.png'
        point.style.labelstyle.scale = 3
        point.style.labelstyle.color = simplekml.Color.red
    kml.save(f'{full_path}\\Conelectricas_4hours.kml')

    lightnings_df2 = lightnings_df[lightnings_df['Fecha_Hora'] >= initial_date_report2].copy(deep=True)
    if len(lightnings_df2) != 0:
        lightnings_df2['Category'] = (end_date - lightnings_df2['Fecha_Hora']) <= datetime.timedelta(minutes=10)
        kml2 = kml_create(lightnings_df2)
    else:
        kml2 = simplekml.Kml()
        point = kml2.newpoint(name= f'No hay descargas - {end_date.strftime("%H:%M")}')
        point.coords = [(-85.5, 10.1)]
        point.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/info.png'
        point.style.labelstyle.scale = 3
        point.style.labelstyle.color = simplekml.Color.red
    kml2.save(f'{full_path}\\Conelectricas_30minutes.kml')

  