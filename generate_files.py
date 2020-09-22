import datetime as dt
import lightnings as light

cooperatives = {1: 'Coopeguanacaste', 2: 'Coopelesca',
                3: 'Coopealfaroruiz', 4: 'Coopesantos'}  # , 5: 'Conelectricas', 27: 'America_Central'}

delta_day = dt.timedelta(days=1)
end_date = dt.date.today() - delta_day
initial_date = end_date.replace(day=17, month=9)
#base_path = f'\\\\192.168.3.233\\comun\\DESCARGAS ATMOSFERICAS'
base_path = f'C:\\Lightning_test'

test = True

if not test:
    while initial_date <= end_date:
        print(f'\n\nfecha: {initial_date}')
        for coop_id in cooperatives.keys():
            info_data = {
                'cooperative': cooperatives[coop_id],
                'date': initial_date,
                'base_path': base_path}
            lightning_df = light.read_lightnings(initial_date, coop_id)
            light.create_kml_by_time(lightning_df, info_data)
            light.create_kml_by_amplitude(lightning_df, info_data)
            light.create_csv_by_time(lightning_df, info_data)
        initial_date += delta_day
else:
    # TESTING
    coop_id = 2
    info_data = {
        'cooperative': cooperatives[coop_id],
        'date': initial_date,
        'base_path': f'{base_path}\\test'}
    lightning_df = light.read_lightnings(initial_date, coop_id)
    light.create_kml_by_time(lightning_df, info_data)
    light.create_kml_by_amplitude(lightning_df, info_data)
    light.create_csv_by_time(lightning_df, info_data)
