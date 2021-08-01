#!/usr/bin/python3
import serial
import math
import time
import sys
import re

from xml.dom import minidom

class PlotterDrawing:
	BLACK = 0
	RED = 1
	GREEN = 2
	BLUE = 3

	def __init__(self):
		self.output = bytearray(b'\x1bc\rI\r')

	def append(self, cmd):
		self.output.extend(bytes(cmd.encode('ascii')))

	def color(self, color):
		self.append(f'C{color}\r')

	def move(self, x, y):
		self.append(f'M{round(x)},{round(y)}\r')

	def line(self, x, y):
		self.append(f'D{round(x)},{round(y)}\r')

	def circle(self, radius):
		self.append(f'Y{round(radius)}\r')

	def sethome(self):
		self.append(f'I\r')

	def home(self):
		self.append(f'H\r')

def usage():
	print(f"usage: {sys.argv[0]} <input.svg> <com-port> [<width-in-steps>] [<debug>]")
	exit(0)

def SVG_to_plotter(draw, filename, scale):
	doc = minidom.parse(filename)
	viewbox = doc.getElementsByTagName('svg')[0].getAttribute('viewBox').split(' ')
	plot_scale = scale
	scale_side = float(viewbox[2])
	point_scale = 1 / scale_side * plot_scale

	groups = doc.getElementsByTagName('g')
	for group in groups:
		elements = group.childNodes
		for element in elements:
			if element.nodeName == 'polygon' or \
			   element.nodeName == 'polyline' or \
				 element.nodeName == 'line':

				if element.hasAttribute('style'):
					style = element.getAttribute('style')
					color = re.findall(r'(?:stroke:#)......', style)[0]
					
					if color == "stroke:#ff0000":
						draw.color(draw.RED)
					if color == "stroke:#00ff00":
						draw.color(draw.GREEN)
					if color == "stroke:#0000ff":
						draw.color(draw.BLUE)
					if color == "stroke:#000000":
						draw.color(draw.BLACK)
				else:
					draw.color(draw.BLACK)

				if element.tagName == 'polygon' or \
				   element.tagName == 'polyline':
					points = element.getAttribute('points').split(' ')

					lastx = -1
					lasty = -1
					point_idx = 0
					for point in points:
						if ',' in point:
							x,y = point.split(',')
							x = int(float(x) * point_scale)
							y = -int(float(y) * point_scale)
							if point_idx == 0:
								firstx = x
								firsty = y
								draw.move(x, y)
							else:
								draw.line(x,y)
							point_idx += 1
					if element.tagName == 'polygon':
						draw.line(firstx,firsty)
						
				elif element.tagName == 'line':
					x1 = int(float(element.getAttribute('x1')) * point_scale)
					y1 = -int(float(element.getAttribute('y1')) * point_scale)
					x2 = int(float(element.getAttribute('x2')) * point_scale)
					y2 = -int(float(element.getAttribute('y2')) * point_scale)
					draw.move(x1,y1)
					draw.line(x2,y2)

	draw.home()
	doc.unlink()

	# for debug
	#print(draw.output)

if __name__ == "__main__":
	if len(sys.argv) < 3:
		usage()
	
	if len(sys.argv) < 4:
		scale = 960
	else:
		scale = int(sys.argv[3])

	filename = sys.argv[1]
	com_port = sys.argv[2]

	draw = PlotterDrawing()

	SVG_to_plotter(draw, filename, scale)

	if len(sys.argv) < 5:
		with serial.Serial(com_port,2400,rtscts=True) as ser:
			for line in draw.output.split(b'\r'):
				ser.write(line + b':\r')
				ser.flush()
			ser.close()
	else:
		print(draw.output)