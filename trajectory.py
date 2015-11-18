#!/usr/bin/kivy
import math
import os

'''
' Berechnet die Flugkurve, und gibt eine Liste der Koordinaten aus, die der Planet 
' wahrscheinlich zurücklegt.
'
' coord_planet		Die Kooridnaten des Planets
' speed_planet		Die Geschwindigkeit des Planets, (Speed_X, Speed_Y)
' weight_planet		Das Gewicht des Planeten
' coord_sun			Die Koordinaten der Sonne
' weight_sun		Das Gewicht der Sonne
' interval			Der Abstand zwischen zwei Punkten
' count				Die Anzahl der Punkte
'''
def calc_trajectory (coord_planet, speed_planet, weight_planet, coord_sun, weight_sun, interval, count):
	# Print CSV
	printCsv = True
	# Gravitationskonstante
	gamma = 0.005#000000000000000000667408
	# list of tuples
	L = []
	
	coords = coord_planet
	speed = speed_planet
	
	if printCsv 
		os.remove('test.csv')
		fobjData = open('test.csv', 'w')
		fobjAll = open ('all.csv', 'w')
		fobjAll.write('X;Y;speedX;speedY;gx;gy;r\n')
		
	for i in range(count) :
		# distance between sun and planet
		r = calc_distance(coords, coord_sun) 
	
		# Fallbeschleunigung
		g = (-1 * gamma) * (weight_planet + weight_sun) / math.pow(r, 2.0) 
		gx = g * coords[0] / r
		gy = g * coords[1] / r
		
		# neue Geschwindigkeit und Kooridnaten berechnen
		speed = (speed[0] + (gx * interval), speed[1] + (gy * interval))
		coords = (coords[0] + (speed[0] * interval) + (0.5 * gx * math.pow(interval, 2.0)),coords[1] + (speed[1] * interval) + (0.5 * gy * math.pow(interval, 2.0)))
		
		if printCsv 
			fobjData.write(str(coords[0]) + ';' + str(coords[1]) + '\n')# + ';' + str(speed[0]) + ';' + str(speed[1]) + ';' + str(gx) + ';' + str(gy) + ';' + str(r) + '\n')
			fobjAll.write(str(coords[0]) + ';' + str(coords[1]) + ';' + str(speed[0]) + ';' + str(speed[1]) + ';' + str(gx) + ';' + str(gy) + ';' + str(r) + '\n')
	
		L.append(coords)
	
	if printCsv
		fobjData.close()
		fobjAll.close()
		
	return L
	
	
'''
' Berechnet den Abstand zwischen zwei Koordinatenpaaren
' 
' tuple1	Die erste Koordinate
' tuple2	Die zweite Koordinate
'''
def calc_distance(tuple1, tuple2):
	return math.sqrt(math.pow(tuple1[0] - tuple2[0], 2.0) + math.pow(tuple1[1] - tuple2[1], 2.0))
	
	
d = calc_trajectory((10,-50), (0.2, 0.5), 10, (0,0), 1500, .1, 2000)
# print d
print 'FINISHED'