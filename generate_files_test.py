import generate_files
import datetime as dt
from dateutil.relativedelta import relativedelta

report_initial_date = dt.date(2020,7,1)
report_last_date = dt.date(2020,10,23)
number_of_days = report_last_date - report_initial_date

delta_day = dt.timedelta(days=1)
#report_initial_date += delta_day
report_last_date += delta_day

for act_day in range(number_of_days.days):
    end_date = report_initial_date + act_day * delta_day
    generate_files.generate_reports(end_date)