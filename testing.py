import numpy as np
import math
import datetime as dt


import generate_files as gf
import lightnings as light


# angles_degrees = list(range(0, 90, 10)) + list(range(90, 110, 2)) + list(range(110, 260, 10)) + list(range(260, 280, 2)) + list(range(280, 370, 10))

# print(angles_degrees)

# end_date = dt.date.today() - dt.timedelta(days=2)
# gf.generate_reports2(end_date)



light.create_kml_live_data()