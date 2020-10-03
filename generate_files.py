import datetime as dt
import lightnings as light
from dateutil.relativedelta import relativedelta

cooperatives = {1: 'Coopeguanacaste', 2: 'Coopelesca',
                3: 'Coopealfaroruiz', 4: 'Coopesantos' , 5: 'Conelectricas' }

delta_day = dt.timedelta(days=1)
delta_month = - relativedelta(months=-1)
end_date = dt.date.today()
initial_date = end_date - delta_day
base_path = f'\\\\192.168.3.233\\planificacion\\Descargas Atmosfericas'

# print(f'\n\nfecha: {initial_date}')
# for coop_id in cooperatives.keys():
#     if coop_id <5:
#         info_data = {
#             'cooperative': cooperatives[coop_id],
#             'date': initial_date,
#             'base_path': base_path}
#         lightning_df = light.read_lightnings(initial_date, coop_id)
#         light.create_kml_by_time(lightning_df, info_data)
#         light.create_kml_by_time(lightning_df, info_data, True)
#         light.create_kml_by_amplitude(lightning_df, info_data)
#         light.create_csv_by_time(lightning_df, info_data)

print(f'today:  {end_date.day}')
if end_date.day == 1:
    initial_date = end_date - delta_month

    ## only Conelectricas report
    coop_id = 5
    info_data = {   'cooperative': cooperatives[coop_id],
                    'date': initial_date,
                    'base_path': base_path,
                    'h_3d': True}
    print(initial_date)
    print(delta_month)
    print(end_date)
    lightnings_df = light.lightnings_count_by_area(initial_date, end_date, coop_id)
    print(lightnings_df)
    light.create_kml_by_area(lightnings_df, info_data)
