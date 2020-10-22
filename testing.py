import datetime as dt


delta_day = dt.timedelta(days=1)
delta_week = dt.timedelta(days=7)
end_date = dt.date.today()
initial_date = end_date - delta_week

print(f'fecha final: {end_date.weekday()}')
print(f'fecha inicial: {initial_date.weekday()}')

# if end_date.day == 1:
