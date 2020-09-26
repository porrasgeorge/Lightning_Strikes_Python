#import simplekml
import datetime as dt
import pandas as pd
import lightnings as light

end_date = dt.date.today()
initial_date = end_date.replace(day=1)

lightnings_df = light.lightnings_count_by_area(initial_date, end_date, 2)
light.create_kml_by_area(lightnings_df)

# print(count_levels)
# print(lightnings_df)

