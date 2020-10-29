import requests
from datetime import datetime as dt
from math import *
from matplotlib import pyplot as plt
from matplotlib import colors

print(dt.now(),'|', 'Network Scan Begin')
I = requests.get('http://172.0.0.199/scan.php')
II = requests.get('http://172.0.0.198/scan.php')
III = requests.get('http://172.0.0.197/scan.php')
print(dt.now(),'|', 'Network Scan End')
def parse_iwlist(iwlist_output):
    iwlist_output = iwlist_output.split('\n')
    devices = []
    for line in iwlist_output:
        if line.find('Address') != -1:
            devices.append([line.split(' ')[-1]])
        elif line.find('Channel:') != -1:
            devices[-1].append(int(line.split(':')[-1]))
        elif line.find('Frequency:') != -1:
            frequency_and_unit = line.split(':')[-1].split(' ')
            devices[-1].append(float(frequency_and_unit[0]))
            devices[-1].append(frequency_and_unit[1])
        elif line.find(' Signal level=') != -1:
            devices[-1].append(int(line.split('=')[-1].split(' ')[0]))
        elif line.find('ESSID:') != -1:
            devices[-1].append(line.split('"')[1])
    return devices

devices = []
print(dt.now(),'|', 'Network Parse Begin')
I = parse_iwlist(I.text)
II = parse_iwlist(II.text)
III = parse_iwlist(III.text)


class device_info:
    address = ""
    channel = 0
    frequency = 1.0
    frequency_unit = ""
    strengths = []
    ssid = ""


for device_list1 in I:
    for device_list2 in II:
        for device_list3 in III:
            if device_list1[0] == device_list2[0] and device_list2[0] == device_list3[0]:
                device = device_info()
                device.address = device_list1[0]
                device.channel = device_list1[1]
                device.frequency = device_list1[2]
                device.frequency_unit = device_list1[3]
                device.strengths = [device_list1[4], device_list2[4], device_list3[4]]
                device.ssid = device_list1[-1]
                devices.append(device)
print(dt.now(),'|', 'Network Parse End')
print(dt.now(),'|', 'Found', len(devices), 'Network Devices')

def Circle(radius, center):
    circle=plt.Circle(center,radius,facecolor='none', edgecolor='blue',linestyle='solid',linewidth='1')
    plt.gca().add_patch(circle)
    plt.plot()


def generate_points(radius, number_of_points, center_x, center_y):
    points = []
    i = 0
    while i < pi * 2:
        points.append([radius * cos(i) + center_x, radius * sin(i) + center_y])
        i += pi / number_of_points * 2
    return points



def find_closest_cluster(circle1_points, circle2_points, circle3_points):
    cluster = [[0,0],[0,0],[0,0],9999999]
    for point1 in circle1_points:
        for point2 in circle2_points:
            for point3 in circle3_points:
                perimeter = ((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
                perimeter += ((point3[0] - point2[0])**2 + (point3[1] - point2[1])**2)
                perimeter += ((point1[0] - point3[0])**2 + (point1[1] - point3[1])**2)
                if perimeter < cluster[3]:
                    cluster = [[point1[0],point1[1]],[point2[0],point2[1]],[point3[0],point3[1]],perimeter]
    return cluster

absolute_farthest = 0

print(dt.now(),'|', 'Device Plot Begin')

device_i = 0
for device in devices:
    device_i += 1
    number_of_points = 64
    smallest_cluster = [[0,0],[0,0],[0,0],9999999]
    for i in range(1,100):
        scale = -i
        piZeroAPoints = generate_points(device.strengths[0] / scale, number_of_points, -1, -1)
        piZeroBPoints = generate_points(device.strengths[1] / scale, number_of_points, 1, -1)
        piZeroCPoints = generate_points(device.strengths[2] / scale, number_of_points, 1, 1)
        cluster = find_closest_cluster(piZeroAPoints, piZeroBPoints, piZeroCPoints)

        if i == 1:
            smallest_cluster = cluster
        elif cluster[3] < smallest_cluster[3]:
            smallest_cluster = cluster
        elif cluster[3] > smallest_cluster[3]:
            break

    avg_point = [0,0]
    avg_point[0] = (smallest_cluster[0][0] + smallest_cluster[1][0] + smallest_cluster[2][0]) / 3
    avg_point[1] = (smallest_cluster[0][1] + smallest_cluster[1][1] + smallest_cluster[2][1]) / 3
    plt.plot(avg_point[0], avg_point[1], marker='*', color='blue')
    plt.text(avg_point[0] + 1, avg_point[1] + 1, device.address + ' ' + device.ssid)
    avg_farthest = avg_point[0]
    if avg_point[1] > avg_point[0]:
        avg_farthest = avg_point[1]
    if avg_farthest > absolute_farthest:
        absolute_farthest = avg_farthest
    print(dt.now(),'|', 'Located Device', device_i, '/', len(devices), ':', device.ssid)

print(dt.now(),'|', 'Device Plot End')

plt.plot(-1,-1, marker='*', color='lightgray')
plt.plot(1,-1, marker='*', color='lightgray')
plt.plot(1,1, marker='*', color='lightgray')

absolute_farthest *= 2

outer_bounds = generate_points(absolute_farthest, 10, 0, 0)
for point in outer_bounds:
    plt.plot(point[0], point[1])

plt.axis('equal')

plt.show()