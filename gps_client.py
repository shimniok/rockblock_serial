#!/usr/bin/env python

from gps import *
import time
import threading
import math

gpsd = None

class GpsPoller(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		global gpsd
		gpsd = gps(mode=WATCH_ENABLE)
		self.current_value = None
		self.running = True

	def run(self):
		global gpsd
		while gpsp.running:
			gpsd.next()

if __name__ == '__main__':
	gpsp = GpsPoller()
	try:
		gpsp.start()
		while True:
			if not math.isnan(float(gpsd.fix.speed)):
				print "Lat = ", gpsd.fix.latitude
				print "Lon = ", gpsd.fix.longitude
				print "Alt = ", gpsd.fix.altitude
				print "Speed = ", gpsd.fix.speed
				print "Track = ", gpsd.fix.track
				print
			time.sleep(5)
	except (KeyboardInterrupt, SystemExit):
		print "\nKilling thread..."
		gpsp.running = False
		gpsp.join()
	print "Done.\nExiting."
