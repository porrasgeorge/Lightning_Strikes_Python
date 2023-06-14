import lightnings as light
import pandas as pd
import pyodbc
import simplekml

def createPolygons():
    cnxn = light.lightnings_db_connection()
    sql = f'exec [GetLocationPolygons]'
    lines_and_polygons = pd.read_sql_query(sql, cnxn)
    cnxn.close()

    lines_and_polygons['Name'] = lines_and_polygons['Name'].apply(
        lambda x: x.replace(" ", ""))
    
    
    lines = lines_and_polygons[lines_and_polygons["Geom_type"] == 1]
    polygons = lines_and_polygons[lines_and_polygons["Geom_type"] != 1]
    
   
    unique_lines = lines["Name"].unique()
    unique_polygons = polygons["Name"].unique()

    kml = simplekml.Kml()
    ## Lineas de transmision
    lines_fol = kml.newfolder(name='Lineas de transmision')
    for line in unique_lines:
        line_df = lines[lines["Name"] == line]
        ls = lines_fol.newlinestring(name=line)
        points=[]
        for _, point in line_df.iterrows():
            points.append((point["longitude"], point["latitude"]))
        ls.coords = points
        ls.style.linestyle.color = simplekml.Color.purple
        ls.style.linestyle.width = 5
        ls.extrude = 1



    ## Poligonos
    polygon_fol = kml.newfolder(name='Areas')
    for area in unique_polygons:
        area_df = polygons[polygons["Name"] == area]
        pol = polygon_fol.newpolygon(name=area)
        points=[]
        for _, point in area_df.iterrows():
            points.append((point["longitude"], point["latitude"]))
        points.append(points[0])
        pol.outerboundaryis = points
        pol.extrude = 1
        pol.style.linestyle.color = simplekml.Color.red
        pol.style.linestyle.width = 5
        pol.polystyle.fill = 0
    kml.save('\\\\192.168.15.15\\planificacion\\Descargas Atmosfericas\\Areas y Lineas de transmision.kml')
  
createPolygons()


