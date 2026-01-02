#!/usr/bin/env python
import os
import binascii
import xml.etree.cElementTree as ET
from xml.etree import ElementTree
from xml.dom import minidom
import re

import hashlib
def md5sum(filename, blocksize=65536):
    h = hashlib.md5()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(blocksize), b""):
            h.update(block)
    return h.hexdigest()

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def search_sec_level(filename):
    with open(filename, "rb") as file:
        try:
            while True:
	       line = file.readline()
               if line:
		  a = re.match(".*PLATFORM_SECURITY_PATCH :=",line)
		  if a != None:
		     break
               else:
	          break
        finally:
            file.close()
    return line[6:43]


def gen_md5_xml():
	root_path = os.path.dirname(__file__)
	path = os.path.join(root_path, 'images')
	files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        xml = os.path.join(root_path, "md5sum.xml")
	root = ET.Element("root")
	digests = ET.SubElement(root, "digests")
	for file in files:
		file = os.path.join(root_path, file)
		digest = ET.SubElement(digests, "digest", name=os.path.basename(file), hash="md5")
		digest.text = md5sum(file)

	sec_patch_level = ET.SubElement(root, "security-patch-level")
	security = ET.SubElement(sec_patch_level, "level")
	source_path = os.popen('echo $ANDROID_BUILD_TOP').read()
	sec_path = os.path.join(source_path[:-1],'build/core/version_defaults.mk')
	security.text = search_sec_level(sec_path)
	xml_str = prettify(root)

	with open(xml,"w") as f:
		f.write(xml_str)

#------------------------------------------------------------------------------
if __name__ == "__main__":
	gen_md5_xml()
