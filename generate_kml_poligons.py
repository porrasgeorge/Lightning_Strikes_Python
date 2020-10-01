#import simplekml
import datetime as dt
import pandas as pd
import lightnings as light
cooperatives = {1: 'Coopeguanacaste', 2: 'Coopelesca',
                3: 'Coopealfaroruiz', 4: 'Coopesantos' , 5: 'Conelectricas' } #, 27: 'America_Central'}

end_date = dt.date.today()
initial_date = end_date.replace(day=1)
coop_id = 5
base_path = f'\\\\192.168.3.233\\planificacion\\Descargas Atmosfericas'
info_data = {   'cooperative': cooperatives[coop_id],
                'date': initial_date,
                'base_path': base_path,
                'h_3d': True}

lightnings_df = light.lightnings_count_by_area(initial_date, end_date, coop_id)
light.create_kml_by_area(lightnings_df, info_data)

# print(count_levels)
# print(lightnings_df)


