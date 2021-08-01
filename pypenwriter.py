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
		self.output = b'\x1bc\rI\r'
		self.lastcommand = ""
		self.thiscommand = ""
		self.lastcolor = -1

	def append(self, cmd):
		if self.lastcommand == "D" and self.thiscommand == "D":
			self.output = self.output[:-1]
		self.output += bytes(cmd.encode('ascii')) + b'\r'
		self.lastcommand = self.thiscommand

	def color(self, color):
		if self.lastcolor != color:
			self.thiscommand = "C"
			self.append(f'C{color}')
			self.lastcolor = color

	def move(self, x, y):
		self.thiscommand = "M"
		self.append(f'M{round(x)},{round(y)}')

	def line(self, x, y):
		self.thiscommand = "D"
		if self.lastcommand == "D":
			self.append(f',{round(x)},{round(y)}')
		else:
			self.append(f'D{round(x)},{round(y)}')

	def circle(self, radius):
		self.thiscommand = "Y"
		self.append(f'Y{round(radius)}')

	def sethome(self):
		self.thiscommand = "I"
		self.append(f'I')

	def home(self):
		self.thiscommand = "H"
		self.append(f'H')

def usage():
	print(f"usage: {sys.argv[0]} <input.svg> <com-port> [<width-in-steps>] [<debug>]")
	exit(0)

def SVG_to_plotter(draw, filename, scale):
	doc = minidom.parse(filename)
	viewbox = doc.getElementsByTagName('svg')[0].getAttribute('viewBox').split(' ')
	plot_scale = scale
	scale_side = float(viewbox[2])
	point_scale = 1 / scale_side * plot_scale
	halfway_down = int(float(viewbox[3]) * point_scale / 2)

	draw.move(0,-halfway_down)
	draw.sethome()

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
							y = halfway_down-int(float(y) * point_scale)
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
					y1 = halfway_down-int(float(element.getAttribute('y1')) * point_scale)
					x2 = int(float(element.getAttribute('x2')) * point_scale)
					y2 = halfway_down-int(float(element.getAttribute('y2')) * point_scale)
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
			commands = draw.output.split(b'\r')
			idx = 0
			for command in commands:
				ser.write(command + b':\r')
				ser.flush()
				idx += 1;
				print(f"\rprogress: {int(idx / len(commands) * 100)}%", end="")
			ser.close()
	else:
		print(draw.output)