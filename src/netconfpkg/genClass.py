#!/usr/bin/python
## 
## Local variables:
## mode: sgml
## tab-width: 3
## End:
#
__version__ = "1.4"
#

## Copyright (C) 2000,2001 Red Hat, Inc.
## Copyright (C) 2000,2001 Harald Hoyer <harald.hoyer@redhat.de>
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from Alchemist import *
from FileBlackBox import *
import sys
import string

true = (1==1)
false = not true

ClassesDone = {}
ImportClasses = []
BaseFile = None
ImplFile = None
OptLower = false
OptNoBase = false
OptCondBase = false
OptFunctions = false
ImplPrefix = None
Type2Str = {
	Data.ADM_TYPE_LIST : 'Data.ADM_TYPE_LIST',
	Data.ADM_TYPE_STRING : 'Data.ADM_TYPE_STRING',
	Data.ADM_TYPE_INT : 'Data.ADM_TYPE_INT',
	Data.ADM_TYPE_BOOL : 'Data.ADM_TYPE_BOOL',
	Data.ADM_TYPE_FLOAT: 'Data.ADM_TYPE_FLOAT',
	Data.ADM_TYPE_BASE64 : 'Data.ADM_TYPE_BASE64',
	Data.ADM_TYPE_COPY : 'Data.ADM_TYPE_COPY'
	}

#
# %classname
# %base
# %childname
# %childtype
# %InitList
# %UnlinkList
# %CommitList
# %RollbackList
# %BackupList
# %TestList
#

InitList = "# InitList\n"
UnlinkList = "# UnlinkList\n"
CommitList = "# CommitList\n"
CommitAList = "# CommitAList\n"
RollbackList = "# RollbackList\n"
TestList = "# TestList\n"
BackupList = "# BackupList\n"
ApplyList = "# ApplyList\n"

ClassHeader = """
class %classname%base:
	def __init__(self, list = None, parent = None):
		self.__parent = parent
		self.dead = 0

		self.__doUnlink()

		# Constructor with object
		if list and (not parent) and isinstance(list, %classname):
			self.apply(list)
			self.__list = None
			return

		self.setList(list)
		# initialize all variables with None
		self.rollback()
		
	#
	# @brief returns the parent of this object
	# @return the parent of this object
	#
	def getParent(self):
		return self.__parent

	def __doUnlink(self):
		%UnlinkList
		pass
	
	def setList(self, list):
		self.__list = list
		if not list:
			return
		%SetList

	#
	# @brief deletes this object from our parent and unlinks from the alchemist
	#
	def unlink(self):
		if self.dead:
			return
		self.dead = 1
		if self.__parent and self.__parent.dead:
			return
		parent = self.__parent
		del self.__parent
		if self.__list:
			ret = self.__list.unlink()
			del self.__list
		self.__doUnlink()
		if parent:
			parent.remove%classname(self)
			
	def test(self):
		%TestList
		pass

	def commit(self):
		if self.__list:
			%CommitAList
			pass
		%CommitList
	
	def rollback(self):
		if self.__list:
			%InitList
			pass
		%BackupList
		return

	def copy():
		n = %classname(None, None)
		n.apply(self)
		return n

	def apply(self, other):
		if not other:
			self.unlink()
			return
		%ApplyList
		pass
"""


ListOps = """
	def test%childname(self, value):
		return 0

	def get%childname(self):
		return self.%childname


	def remove%childname(self, child):
		if child == self.%childname:
			child = self.%childname
			self.%childname = None
			child.unlink()

	def del%childname(self):
		self.%childname = None
"""

ListCNLOps = """	
	def set%childname(self, value):
		self.%childname = value
"""

ListCLOps = """	
	def create%childname(self):
		if not self.%childname:
			self.%childname = %childname(None, self)
		return self.%childname
"""

AnonListOps = """
	def __len__ (self):
		return len(self.__%classname)

	def __getitem__(self, key):
		return self.__%classname[key]

	def __setitem__(self, key, value):
		self.__%classname[key] = value

	def __delitem__(self, key):
		del self.__%classname[key]

	def __getslice__(self, i, j):
		return self.__%classname[i:j]

	def __setslice__(self, i, j, s):
		self.__%classname[i:j] = s

	def __delslice__(self, i, j):
		del self.__%classname[i:j]

	def append (self, x):
		return self.__%classname.append(x)

	def extend (self, l):
		return self.__%classname.extend(l)

	def count(self, x):
		return self.__%classname.count(x)

	def index(self, x):
		return self.__%classname.index(x)

	def insert(self, i, x):
		return self.__%classname.insert(i, x)

	def pop(self, i = None):
		return self.__%classname.pop(i)

	def remove(self, x):
		return self.__%classname.remove(x)

	def reverse(self):
		return self.__%classname.reverse()

	def sort(self, cmpfunc = None):
		return self.__%classname.sort(cmpfunc)

	def get%childname(self, pos):
		return self.__%classname[pos]

	def del%childname(self, pos):
		self.__%classname.pop(pos)
		return 0

	def getNum%childname(self):
		return len(self.__%classname)

	def move%childname(self, pos1, pos2):
		direct = 0
		if pos2 > pos1: direct = 1
		obj = self.__%classname.pop(pos1)
		self.__%classname.insert(obj, pos2 - direct)
		return 0
"""
AnonListCLOps = """
	def add%childname(self):
		self.__%classname.append(%childname(None, self))
		return len(self.__%classname)
"""

AnonListCNLOps = """
	def add%childname(self):
		self.__%classname.append(None)
		return len(self.__%classname)

	# @brief set the value of %childname
	# @param pos the position in the list of the %childname object
	# @param value the value
	# @return @c 0 on success
	def set%childname(self, pos, value):
		self.__%classname[pos] = value
		return 0
"""

AnonListPKOps = """
	def __getitem__ (self, key):
		for i in xrange (len (self)):
			if self.__%classname.%childname[i].%childkey == key:
				return child
		return None

	def __setitem__ (self, key, value):
		raise 'TypeError', "Unable to explicitly set a %childname.  Use %classname::add instead"

	def __delitem__ (self, key):
		for i in xrange (len (self)):
			if self.__%classname.%childname[i].%childkey == key:

		raise KeyError, key

	def keys (self):
		if self.__%classname == []:
			return []

		retval = []
		for i in xrange (len (self)):
			retval.append (self.__virtualhosts.getvirtualhost (i).getVHName())
		return retval
"""


AnonCNList = """
"""

def printb(str):
	global BaseFile	
	BaseFile.write(str + "\n")


def printClass(list, basename, baseclass):
	global ClassesDone
	global ImportClasses
	global BaseFile
	global ImplFile
	global OptLower
	global ImplPrefix
	global OptNoBase
	global OptCondBase
	global InitList
	global UnlinkList
	global CommitList
	global CommitAList
	global RollbackList
	global TestList
	global BackupList

	try:
		done = ClassesDone[list.getName()]
		return
	except KeyError:
		pass

	ClassesDone[list.getName()] = true

	testlist = ""
	applylist= ApplyList
	base = ""
	methods = ""
	setlist = "#SetList\n"
	initlist = InitList
	unlinklist = UnlinkList
	commitlist = CommitList
	commitalist = CommitAList
	rollbacklist = RollbackList
	testlist = TestList
	backuplist = BackupList

	dobase = not (OptNoBase or OptCondBase)

	#
	# in case of the CondBase options
	# if the class file already exists, write _base classes
	#
	if OptCondBase and os.access(ImplPrefix + basename + '.py', os.R_OK):
		dobase = true

	num = list.getNumChildren()

	for i in xrange(num):
		child = list.getChildByIndex(i)

		if child.getType() == Data.ADM_TYPE_LIST:
			printClass(child,  child.getName(), baseclass)

	if dobase:
		base = "_base"
		ImportClasses.append(basename)
			
	initDone = {}
	for i in xrange(num):
		child = list.getChildByIndex(i)
		cname = child.getName()

		if OptLower: clname = string.OptLower(cname)
		else: clname = cname

		try: done = initDone[cname]				
		except KeyError:
			initDone[cname] = true
			done = false
			
		if done:	continue

		ctype = child.getType()
		cstype = Type2Str[ctype]

		if list.isAnonymous():
			setlist = setlist + "\t\tself.__list.setAnonymous(1)\n"
						
		if list.isAtomic():
			setlist = setlist + "\t\tself.__list.setAtomic(1)\n"
						
		if list.isProtected():
			setlist = setlist + "\t\tself.__list.setProtected(1)\n"
						
		if list.isAnonymous():
			#
			# List == Anonymous
			#

			methods = methods + AnonListOps

			unlinklist = unlinklist + '\t\tself.__%classname = []\n'
			unlinklist = unlinklist + '\t\tself.__%classname_bak = []\n'

			backuplist = backuplist \
						  + "\t\tself.__%classname = self.__%classname_bak[:]\n"
							
			commitlist = commitlist \
							 + '\t\tself.__%classname_bak = self.__%classname[:]\n'

			testlist = testlist \
					  + '\t\tfor pos in xrange(len(self.__%classname)):\n' \
					  + '\t\t\tself.test%childname(self.__%classname[pos])\n'
			
			
			if ctype != Data.ADM_TYPE_LIST:				
				#
				# Child != List
				#

				methods = methods + AnonListCNLOps
				
				applylist= applylist \
							  + '\t\tfor pos in xrange(self.getNum%childname()): ' \
							  + 'self.del%childname(0)\n' \
							  + '\t\tfor pos in xrange(other.getNum%childname' \
							  + '() ):\n' \
							  + '\t\t\tself.add%childname()\n' \
							  + '\t\t\tself.set%childname(pos, other.get' \
							  + '%childname(pos))\n'

				initlist = initlist \
							  + "\t\t\tfor i in xrange(self.__list.getNumChildren()):\n"\
							  + '\t\t\t\tself.__%classname_bak.append(' \
							  + 'self.__list.getChildByIndex(i).getValue())\n'

				commitalist = commitalist \
								  + '\t\t\tfor i in xrange(len(self.__%classname_bak)):\n' \
								  + '\t\t\t\tself.__%classname_bak.unlink()\n' \
								  + '\t\t\tfor i in xrange(len(self.__%classname)):\n' \
								  + '\t\t\t\tself.__list.addChild(%childtype, "%childname").setValue(self.__%classname[i])\n' 
				
				#########################				
			else:
				#
				# Child == List
				#

				methods = methods + AnonListCLOps

				applylist= applylist+ \
						'\t\tfor pos in xrange(self.getNum' + \
						'%childname() ):\n' + \
						'\t\t\tself.del%childname(0)\n' + \
						'\t\tfor pos in xrange(other.getNum' \
						+ '%childname() ):\n' + \
						'\t\t\tself.add%childname()\n' + \
						'\t\t\tself.get%childname(pos).apply(other.get' + \
						'%childname(pos))\n'

				initlist = initlist \
							  + "\t\t\tfor i in xrange(self.__list.getNumChildren()):\n"\
							  + '\t\t\t\tself.__%classname_bak.append(%childname(self.__list.getChildByIndex(i), self))\n'
				
				commitalist = commitalist + """
			for i in xrange(len(self.__%classname_bak)):
				self.__%classname_bak.unlink()
			for i in xrange(len(self.__%classname)):
				self.__%classname[i].setList(self.__list.addChild(%childtype, "%childname"))
				self.__%classname[i].commit()
"""							  
				#########################
			

			#########################
		else:
			#
			# List != Anonymous
			#
			methods = methods + ListOps
			
			initlist = initlist \
						  + '\t\t\ttry:\n' \
						  + '\t\t\t\tchild = self.__list.getChildByName("%childname")\n' \
						  + '\t\t\t\tif child.getType() != %childtype: raise TypeError\n'
			
			unlinklist = unlinklist + '\t\tself.%childname = None\n'
			unlinklist = unlinklist + '\t\tself.__%childname_bak = None\n'

			backuplist = backuplist \
							 + '\t\tself.%childname = self.__%childname_bak\n'
			
			commitlist = commitlist \
							 + '\t\tself.__%childname_bak = self.%childname\n'

			if ctype != Data.ADM_TYPE_LIST:
				#
				# Child != List
				#

				methods = methods + ListCNLOps

				testlist = testlist + \
						'\t\tself.test%childname(self.%childname)\n'
				
				applylist= applylist+ \
						'\t\tself.set%childname(other.get%childname())\n'

				commitalist = commitalist + """
			if self.%childname:
				if self.__%childname_bak:
					self.__list.getChildByName("%childname").setValue(self.%childname)
				else:
					self.__list.addChild(%childtype, "%childname").setValue(self.%childname)
			else:
				self.__list.getChildByName("%childname").unlink()
"""				

				initlist = initlist \
							  + '\t\t\t\tself.__%childname_bak = child.getValue()\n'
				
				#########################				
			else:
				#
				# Child == List
				#

				methods = methods + ListCLOps

				initlist = initlist \
							  + '\t\t\t\tself.__%childname_bak = %childname(child, self)\n'
				
				testlist = testlist + \
						'\t\tself.%childname.test()\n'
				
				applylist = applylist \
							  + '\t\tself.create%childname().apply(other.get%childname())\n'
				

				commitalist = commitalist + """
			if self.__%childname_bak: self.__%childname_bak.unlink()			
			if self.%childname:
				self.%childname.setList(self.__list.addChild(%childtype, "%childname"))
				self.%childname.commit()
"""
				
				#########################
				
			initlist = initlist \
						  + '\t\t\texcept (KeyError): pass\n' 


		testlist = string.replace(testlist, '%childname', clname)
		initlist = string.replace(initlist, '%childname', clname)
		initlist = string.replace(initlist, '%childtype', cstype)
		unlinklist = string.replace(unlinklist, '%childname', clname)
		backuplist = string.replace(backuplist, '%childname', clname)
		commitlist = string.replace(commitlist, '%childname', clname)
		commitlist = string.replace(commitlist, '%childtype', cstype)
		commitalist = string.replace(commitalist, '%childname', clname)
		commitalist = string.replace(commitalist, '%childtype', cstype)
		applylist= string.replace(applylist, '%childname', clname)
		methods = string.replace(methods, '%childname', clname)
		methods = string.replace(methods, '%childtype', cstype)
		
	methods = ClassHeader + methods		
	methods = string.replace(methods, '%SetList', setlist)
	methods = string.replace(methods, '%BackupList', backuplist)
	methods = string.replace(methods, '%ApplyList', applylist)
	methods = string.replace(methods, '%TestList', testlist)
	methods = string.replace(methods, '%CommitList', commitlist)
	methods = string.replace(methods, '%CommitAList', commitalist)
	methods = string.replace(methods, '%UnlinkList', unlinklist)
	methods = string.replace(methods, '%InitList', initlist)
	methods = string.replace(methods, '%TestList', testlist)
	methods = string.replace(methods, '%base', base)
	methods = string.replace(methods, '%classname', basename)

	printb(methods)

	if not (OptNoBase or OptCondBase):
		try:
			fd = os.open(ImplPrefix + basename + '.py', os.O_CREAT | os.O_WRONLY | os.O_EXCL, 0664)
			file = os.fdopen(fd, "w")
		except (IOError, OSError), msg:
			pass
		else:
			file.write("""## Copyright (C) 2000,2001 Red Hat, Inc.
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.



# Please extend this class and overload the methods from the base class
""")
			if bpath != None:
				file.write('from ' + bpath[:-3] + ' import *\n')
				file.write('\n')
			file.write('class ' + basename + '(' + basename + '_base):\n')
			file.write('\tdef __init__(self, list = None, parent = None):\n')
			file.write('\t\t' + basename + '_base.__init__(self, list, parent)\n')
			file.write('\n')
			file.close()




if __name__ == '__main__':
	basepath = ""
	argc = len(sys.argv)

	if argc < 2:
		print "Usage: " + sys.argv[0] + " [-l, --lower] [[-n, --no-base]|[-c, --cond-base]] [-f, --functions] <idl file> <base .py> <impl ImplPrefix>"
		sys.exit(10)

	n = 1

	while true:
		if sys.argv[n] == '-l' or sys.argv[n] == '--lower':
			OptLower = true
			n = n+1
			continue

		if sys.argv[n] == '-n' or sys.argv[n] == '--nobase':
			OptNoBase = true
			n = n+1
			continue

		if sys.argv[n] == '-c' or sys.argv[n] == '--cond-base':
			OptCondBase = true
			n = n+1
			continue

		if sys.argv[n] == '-f' or sys.argv[n] == '--functions':
			OptFunctions = true
			n = n+1
			continue

		break

	boxpath = sys.argv[n]
	n = n+1

	if argc > n:	
		bpath = sys.argv[n]
		if bpath[-3:] != '.py':
			print bpath + ' must end with .py'
			sys.exit(10)

		basepath = sys.argv[n]
		n = n+1		
		if argc > n:
			ImplPrefix = sys.argv[n]
			n = n+1			
	else:
		BaseFile = sys.stdout
		bpath = None

	bbc = Context(name = 'FileBlackBox', serial = 1)
	broot = bbc.getDataRoot()
	list = broot.addChild(Data.ADM_TYPE_LIST, 'box_cfg')
	list.addChild(Data.ADM_TYPE_STRING, 'path').setValue(boxpath)
	list.addChild(Data.ADM_TYPE_STRING, 'box_type').setValue('FileBlackBox')
	list.addChild(Data.ADM_TYPE_BOOL, 'readable').setValue(true)
	list.addChild(Data.ADM_TYPE_BOOL, 'writable').setValue(false)
	bb = FileBlackBox(list)

	if bb.errNo():
		print 'Error creating FileBlackBox: ' + bb.strError()
		sys.exit(10)

	if bb.isReadable():
		con = bb.read() 
		if con == None:
			if bb.errNo():
				print 'Error reading ' + boxpath +': ' + bb.strError()
				sys.exit(10)

	else:
		print 'Error: ' + boxpath + ' is not readable!'
		sys.exit(10)

	dr = con.getDataRoot().getChildByIndex(0)
	drname = dr.getName()

	if not BaseFile and basepath:
		BaseFile = open(basepath, "w")

	#
	# Print base class
	#
	printb('# autogenerated file by genClass version ' + __version__ \
			 + ' - DO NOT EDIT !')
	printb('# command line was:')

	cline = ''
	for i in xrange(len(sys.argv)):
		cline = cline + ' ' + sys.argv[i]
		
	printb('# ' + cline)
	printb("""#
# This file loads all the implementation classes
# for global functions edit """ \
		   + ImplPrefix + "_functions.py instead" \
		   + """

## Copyright (C) 2000,2001 Red Hat, Inc.
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

#

import sys
from Alchemist import *
import FileBlackBox
""")

	if OptFunctions:
		printb("""
from """ + ImplPrefix + """_functions import *

true = (1==1)
false = not true
""")

	printClass(dr, drname, ImplPrefix)

	for i in xrange(len(ImportClasses)):
		printb('from ' + ImplPrefix + ImportClasses[i] + ' import *')

	printb("""
if __name__ == '__main__':

	argc = len(sys.argv)

	if argc < 2:
		print \"Usage: \" + sys.argv[0] + \" <input file>\"
		sys.exit(10)

	boxpath = sys.argv[1]

	bbc = Context(name = 'FileBlackBox', serial = 1)
	broot = bbc.getDataRoot()
	list = broot.addChild(Data.ADM_TYPE_LIST, 'box_cfg')
	list.addChild(Data.ADM_TYPE_STRING, 'path').setValue(boxpath)
	list.addChild(Data.ADM_TYPE_STRING, 'box_type').setValue('FileBlackBox')
	list.addChild(Data.ADM_TYPE_BOOL, 'readable').setValue(1)
	list.addChild(Data.ADM_TYPE_BOOL, 'writable').setValue(0)
	bb = FileBlackBox.FileBlackBox(list)

	if bb.errNo():
		print 'Error creating FileBlackBox: ' + bb.strError()
		sys.exit(10)

	if bb.isReadable():
		con = bb.read() 
		if con == None:
			if bb.errNo():
				print 'Error reading ' + boxpath +': ' + bb.strError()
				sys.exit(10)

	else:
		print 'Error: ' + boxpath + ' is not readable!'
		sys.exit(10)

	dr = con.getDataRoot().getChildByIndex(0)

	config = """ + drname + '(dr)' + """
	config_copy = """ + drname + '()' + """
	config_copy.apply(config)
	print con.toXML()
	config.apply(config_copy)
	config_copy.unlink()
	print con.toXML()
	config.unlink()
	config_copy.apply(config)
""")

	#
	# Print functions file, if it not exists
	#
	if OptFunctions:
		try:
			fd = os.open(ImplPrefix + '_functions.py', os.O_CREAT | os.O_WRONLY | os.O_EXCL, 0664)
			file = os.fdopen(fd, "w")
		except (IOError, OSError), msg:
			pass
		else:		
			file.write("""## Copyright (C) 2000,2001 Red Hat, Inc.
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

# For global functions for all classes edit this file
""")
			file.close()

