import generate_files as gf
import datetime as dt
##from datetime import timedelta

end_date = dt.date.today() - dt.timedelta(days=1)
gf.generate_reports(end_date)
