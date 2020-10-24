import datetime as dt
import lightnings as light
from dateutil.relativedelta import relativedelta


cooperatives = {1: 'Coopeguanacaste', 2: 'Coopelesca',
                3: 'Coopealfaroruiz', 4: 'Coopesantos' , 5: 'Costa Rica' }

end_date = dt.date.today()
    

delta_day = dt.timedelta(days=1)
delta_week = dt.timedelta(days=7)
delta_month = - relativedelta(months=-1)
initial_date = end_date - delta_day
base_path = 'C:\\Lightning_test'

initial_date = end_date - delta_month

## only Conelectricas report
coop_id = 5
info_data = {   'cooperative': cooperatives[coop_id],
                'date': initial_date,
                'base_path': base_path,
                'h_3d': True, 
                'period': 'month'}

lightnings_df = light.lightnings_count_by_area(initial_date, end_date, coop_id)
light.create_kml_by_area(lightnings_df, info_data, file_name_append="_rectangle")
light.create_kml_by_area(lightnings_df, info_data, by_amp_sum=True, file_name_append="_energia")