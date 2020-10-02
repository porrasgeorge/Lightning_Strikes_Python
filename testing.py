import math
import simplekml
# import matplotlib
# import matplotlib.pyplot as plt
import numpy as np

# Data for plotting
def ellipse_polygon(lat, long, major_err, minor_err, azimuth):

    a = major_err / 2
    b = minor_err / 2
    o = azimuth

    lat = 70
    long = -84

    # constants
    earth_radius = 6373
    side_number = 72
    vert_km_to_degrees_ratio = math.degrees(1/earth_radius)
    hor_km_to_degrees_ratio = vert_km_to_degrees_ratio / abs(math.cos(math.radians(lat)))

    angle = np.arange(0.0, 2*math.pi, 2*math.pi /side_number)
    R = a*b/(np.sqrt(np.power(a*np.cos(angle),2)+np.power(b*np.sin(angle),2)))
    new_angle = angle - math.radians(o)

    x = R * np.cos(new_angle) * hor_km_to_degrees_ratio
    y = R * np.sin(new_angle) * vert_km_to_degrees_ratio

    ellipse = []
    for i in range(len(x)):
        ellipse.append((long + x[i], lat + y[i]))

    return ellipse

ellipse = ellipse_polygon()

kml = simplekml.Kml()
pol = kml.newpolygon(name=f'la vaca lola')
pol.outerboundaryis = ellipse
kml.save(f'lola.kml')



# fig, ax = plt.subplots()
# ax.plot(x, y)

# fig.savefig("test.png")
# plt.axis('equal')
# plt.show()

# major_minor_ratio = major_error/minor_error

# x_adjust = major_minor_ratio * math.cos(math.radians(azimuth_error))
# y_adjust = major_minor_ratio * math.sin(math.radians(azimuth_error))
 



# print(vert_km_to_degrees_ratio)
# print(hor_km_to_degrees_ratio)

# number_points = 36
# angle_advanced = 2*math.pi/number_points

# circle = []
# for i in range(number_points):
#     angle = i * angle_advanced
#     x_val = center_lon_deg + math.cos(angle)
#     y_val = center_lat_deg + math.sin(angle)
#     circle.append((x_val, y_val))

# print





##vert_distance_deg = radious_km * vert_km_to_degrees_ratio
##hor_distance_deg = radious_km * hor_km_to_degrees_ratio



#crear un circulo
#calcular las nuevas distancias
#rotar el ratio
#aplicarle el ratio rotado


#sacar las componentes del factor con la rotacion ya hecha
