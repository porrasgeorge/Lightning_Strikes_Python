import datetime as dt
import lightnings as light
from dateutil.relativedelta import relativedelta

cooperatives = {1: 'Coopeguanacaste', 2: 'Coopelesca',
                3: 'Coopealfaroruiz', 4: 'Coopesantos' , 5: 'Conelectricas' }

delta_day = dt.timedelta(days=1)
delta_week = dt.timedelta(days=7)
delta_month = - relativedelta(months=-1)
end_date = dt.date.today()
initial_date = end_date - delta_day
base_path = f'\\\\192.168.3.233\\planificacion\\Descargas Atmosfericas'

######################################################################################
## reportes diarios
print(f'\n\nfecha: {initial_date}')
for coop_id in cooperatives.keys():
    info_data = {
            'cooperative': cooperatives[coop_id],
            'date': initial_date,
            'base_path': base_path}

    lightning_df = light.read_lightnings(initial_date, coop_id)
    if coop_id <5:
        light.create_kml_by_time(lightning_df, info_data)
        light.create_kml_by_time(lightning_df, info_data, True)
        light.create_kml_by_amplitude(lightning_df, info_data)
    ## for all cases
    light.create_csv_by_time(lightning_df, info_data)


######################################################################################
## reportes semanal (lunes)
if end_date.weekday() == 2:
    initial_date = end_date - delta_week

    ## only Conelectricas report
    coop_id = 5
    info_data = {   'cooperative': cooperatives[coop_id],
                    'date': initial_date,
                    'base_path': base_path,
                    'h_3d': True, 
                    'period': 'week'}
    lightnings_df = light.lightnings_count_by_area(initial_date, end_date, coop_id)
    light.create_kml_by_area(lightnings_df, info_data)

    lightnings_df = light.lightnings_count_by_area(initial_date, end_date, coop_id, 0)
    light.create_kml_by_area(lightnings_df, info_data, "_rectangle")


######################################################################################
## reportes mensual (primer dia del mes)
if end_date.day == 21:
    initial_date = end_date - delta_month

    ## only Conelectricas report
    coop_id = 5
    info_data = {   'cooperative': cooperatives[coop_id],
                    'date': initial_date,
                    'base_path': base_path,
                    'h_3d': True, 
                    'period': 'month'}
    lightnings_df = light.lightnings_count_by_area(initial_date, end_date, coop_id)
    light.create_kml_by_area(lightnings_df, info_data)

    lightnings_df = light.lightnings_count_by_area(initial_date, end_date, coop_id, 0)
    light.create_kml_by_area(lightnings_df, info_data, "_rectangle")