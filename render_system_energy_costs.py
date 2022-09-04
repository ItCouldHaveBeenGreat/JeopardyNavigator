import matplotlib.pyplot as plt
import numpy as np
import math


sun_planetary_parameter = 700000000
earth_orbit_average_radius = 1.0
points_of_interest = {
    'sun': [0, 0],
    'mercury': [0.308, 0.467],
    'venus': [0.718, 0.728],
    'earth': [0.983, 1.017],
    'mars': [1.381, 1.666],
    'main asteroid belt': [2.06, 3.27],
    'jupiter': [4.951, 5.457],
    'saturn': [9.041, 10.124],
    'uranus': [18.286, 20.097],
    'neptune': [29.81, 30.33],
    'pluto': [26.658, 49.305],
}


def delta_v_from_earth(x):
    return delta_v(earth_orbit_average_radius, x)


def delta_v(r_origin, x):
    return np.abs(math.sqrt(sun_planetary_parameter/r_origin)*(np.sqrt((2*r_origin)/np.array(r_origin+x))-1))


def round_to_multiple(x, multiple):
    return multiple * round(x / multiple)


plt.figure(figsize=(20,12))
ax = plt.subplot()

points = np.arange(0.0, 60, 0.005)
annotated_points = []
for _, values in points_of_interest.items():
    annotated_points.append(round_to_multiple((values[0]+values[1])/2, 0.005))


x = points
y =  delta_v_from_earth(points)
line, = plt.plot(x, y, '-gD', markevery=[i in annotated_points for i in x])
for point_name, values in points_of_interest.items():
    point_x = (values[0]+values[1])/2
    point_y = float(delta_v_from_earth(point_x))
    ax.annotate('{} ({})'.format(point_name, point_y), (point_x, point_y))
    #ax.annotate(point_name + '_min', (values[0], float(delta_v_from_earth(values[0]))))
    #ax.annotate(point_name + '_max', (values[1], float(delta_v_from_earth(values[1]))))
plt.ylabel('Delta V Required (m/s, approx)')
plt.show()