import datetime as dt
import lightnings as light
from dateutil.relativedelta import relativedelta

def generate_reports(end_date):

    cooperatives = {1: 'Coopeguanacaste', 2: 'Coopelesca',
                    3: 'Coopealfaroruiz', 4: 'Coopesantos' , 5: 'Costa Rica' }

    delta_day = dt.timedelta(days=1)
    delta_week = dt.timedelta(days=7)
    delta_month = - relativedelta(months=-1)
    initial_date = end_date - delta_day
    base_path = f'\\\\192.168.15.15\\planificacion\\Descargas Atmosfericas'
    #base_path = 'C:\\Lightning_test'

    ######################################################################################
    ## reportes diarios
    print(f'\n\nfecha: {initial_date}')
    for coop_id in cooperatives.keys():
        info_data = {
                'cooperative': cooperatives[coop_id],
                'date': initial_date,
                'base_path': base_path}

        lightning_df = light.read_lightnings(initial_date, coop_id)

        ## for all cases
        light.create_kml_by_time(lightning_df, info_data)
        light.create_csv_by_time(lightning_df, info_data)
        ## for all cases but Conelectricas
        if coop_id <5:
            light.create_kml_by_time(lightning_df, info_data, True)
            light.create_kml_by_amplitude(lightning_df, info_data)

    ######################################################################################
    ## reportes semanal (lunes)
    if end_date.weekday() == 0:
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
        light.create_kml_by_area(lightnings_df, info_data, file_name_append="_rectangle")
        light.create_kml_by_area(lightnings_df, info_data, by_amp_sum=True, file_name_append="_energia")


    ######################################################################################
    ## reportes mensual (primer dia del mes)
    if end_date.day == 1:
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
        light.create_kml_by_area(lightnings_df, info_data, file_name_append="_rectangle")
        light.create_kml_by_area(lightnings_df, info_data, by_amp_sum=True, file_name_append="_energia")
    

def generate_reports2(end_date):
    lines = { 24: 'Linea 69', 25: 'Pocosol', 26: 'Linea Canalete' }
    delta_day = dt.timedelta(days=1)
    delta_week = dt.timedelta(days=7)
    delta_month = - relativedelta(months=-1)
    initial_date = end_date - delta_day
    #base_path = f'\\\\192.168.30.30\\planificacion\\Descargas Atmosfericas'
    base_path = 'C:\\Lightning_test'

    ######################################################################################
    ## reportes diarios
    print(f'\n\nfecha: {initial_date}')
    for coop_id in lines.keys():
        info_data = {
                'cooperative': lines[coop_id],
                'date': initial_date,
                'base_path': base_path}

        lightning_df = light.read_lightnings(initial_date, coop_id)
        print(lightning_df)

        # ## for all cases
        # light.create_kml_by_time(lightning_df, info_data)
        # light.create_csv_by_time(lightning_df, info_data)
        # ## for all cases but Conelectricas
        # if coop_id <5:
        #     light.create_kml_by_time(lightning_df, info_data, True)
        #     light.create_kml_by_amplitude(lightning_df, info_data) 
