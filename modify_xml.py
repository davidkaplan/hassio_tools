#!/usr/bin/env python3

import re
import argparse
#from xml.dom import minidom
import xml.etree.ElementTree as ET
#import lxml.etree as ET

NAMESPACE = "https://github.com/OpenZWave/open-zwave"
COMMANDCLASS38_FILENAME = 'CommandClass38.xml'
NS_RE = re.compile('''^(\{.*\})(.+)''')

def getCommandClass38():
	parser = ET.XMLParser(encoding='utf-8')
	return ET.parse(COMMANDCLASS38_FILENAME, parser=parser).getroot()[0]

COMMANDCLASS38 = getCommandClass38()

def splitns(elem):
	return NS_RE.match(elem.tag).group(1, 2)

def read_xml(filename):
	ET.register_namespace("", NAMESPACE)
	parser = ET.XMLParser(encoding='utf-8')
	tree = ET.parse(filename, parser=parser)
	return tree

def fixCommandClass38(element):
	for child in element:
		ns, tag = splitns(child)
		if tag == 'CommandClasses':
			for index, commandclass in enumerate(child):
				if commandclass.get('id') == '38':
					print('index ', index)
					child.remove(commandclass)
					child.insert(index, COMMANDCLASS38)

def modify_xml(tree, fix_commandclass=False):
	'''
	fix_commandclass: if True replaces CommandClass 38 with new values from this thread:
	https://community.home-assistant.io/t/new-device-zooz-rgbw-dimmer-zen31-only-partially-working-no-switches/178915 
	'''
	root = tree.getroot()
	for node in root:
		for child in node:
			ns, tag = splitns(child)
			if tag == 'Manufacturer' and child.get('name') == 'Zooz':
				for grandchild in child:
					ns, tag = splitns(grandchild)
					if tag == 'Product' and grandchild.get('name') == 'ZEN31 RGBW Dimmer':
						node.set('specific', '1')
						print('Found ZEN31, Node:', node.get('id'))
				if fix_commandclass == True:
					fixCommandClass38(node)
	return tree

def write_xml(tree, filename):
	tree.write(filename, encoding="utf-8", xml_declaration=True)
	with open(filename, "r") as fh:
		xml_txt = fh.read()
	foo = minidom.parseString(xml_txt)
	bar = foo.toprettyxml(indent='', newl='', encoding='utf-8') #indent="   ")
	#with open(filename, "wb") as fh:
	#	fh.write(bar)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Zen31 XML modifier')
	parser.add_argument('-i', '--input',  action='store', required=True, help='Input File')
	parser.add_argument('-o', '--output', action='store', help='Output File')
	args = parser.parse_args()
	fileout = args.input if args.output is None else args.output
	xml_in = read_xml(args.input)
	xml_modified = modify_xml(xml_in, fix_commandclass=True)
	write_xml(xml_modified, fileout)

