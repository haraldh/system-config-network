#!/usr/bin/python
## 
## Local variables:
## mode: sgml
## tab-width: 3
## End:
#
__version__ = "2.0"
#

## Copyright (C) 2000-2002 Red Hat, Inc.
## Copyright (C) 2000-2002 Harald Hoyer <harald.hoyer@redhat.de>
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
ImportClasses = {}
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
class %classname%base%baseclass:
	def __init__(self, list = None, parent = None):
		%BaseInit
		self.__parent = parent
		self.changed = false
		self.dead = 0
		self.doClear()

		self.setList(list)
		# initialize all variables with None
		self.rollback()
		
	#
	# @brief returns the parent of this object
	# @return the parent of this object
	#
	def getParent(self):
		return self.__parent

	def setParent(self, parent):
		self.__parent = parent

	def doClear(self):
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
		self.doClear()
		if parent:
			parent.remove%classname(self)
			
	def test(self):
		%TestList
		pass

	def setChanged(self, val):
		self.changed = val
		if self.__parent and val:
			self.__parent.setChanged(val)
		
	def commit(self, changed=true):
		%CommitList
	
	def rollback(self):
		%BackupList
		return

	def copy(self):
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

	def del%childname(self):
		self.%childname = None
"""

SListCNLOps = """	
		
"""

SListCLOps = """	
"""

ListCNLOps = """	
	def set%childname(self, value):
		self.%childname = value

	def commit%childname(self, changed=true):
		if self.__%childname_bak != self.%childname:
			self.setChanged(changed)			
		self.__%childname_bak = self.%childname
"""


ListCLOps = """	
	def create%childname(self):
		if self.%childname == None:
			self.%childname = %childclassname(None, self)
		return self.%childname

	def remove%childname(self, child):
		if child == self.%childname:
			child = self.%childname
			self.%childname = None
			child.unlink()

	def commit%childname(self, changed=true):
		if hasattr(self.%childname, "commit"):
			self.%childname.commit(changed)
		if self.__%childname_bak != self.%childname:
			self.setChanged(changed)
		self.__%childname_bak = self.%childname
"""

AnonListOps = """
	def get%childname(self, pos):
		return self.data[pos]

	def del%childname(self, pos):
		self.data.pop(pos)
		return 0

	def getNum%childname(self):
		return len(self.data)

	def move%childname(self, pos1, pos2):
		direct = 0
		if pos2 > pos1: direct = 1
		obj = self.data.pop(pos1)
		self.data.insert(obj, pos2 - direct)
		return 0
"""
AnonListCLOps = """
	def add%childname(self):
		self.data.append(%childclassname(None, self))
		return len(self.data)-1

	def remove%childname(self, child):
		try: self.remove(child)
		except ValueError: pass

	def __setitem__(self, i, item):
		UserList.UserList.__setitem__(self, i, item)
		item.setParent(self)

	def append(self, item):
		UserList.UserList.append(self, item)
		item.setParent(self)
		
	def insert(self, i, item):
		UserList.UserList.insert(self, i, item)
		item.setParent(self)
		
"""

AnonListCNLOps = """
	def add%childname(self):
		self.data.append(None)
		return len(self.data)-1

	# @brief set the value of %childname
	# @param pos the position in the list of the %childname object
	# @param value the value
	# @return @c 0 on success
	def set%childname(self, pos, value):
		self.data[pos] = value
		return 0
"""

#  AnonListPKOps = """
#  	def __getitem__ (self, key):
#  		for i in xrange (len (self)):
#  			if self.data.%childname[i].%childkey == key:
#  				return child
#  		return None

#  	def __setitem__ (self, key, value):
#  		raise 'TypeError', "Unable to explicitly set a %childname.  Use %classname::add instead"

#  	def __delitem__ (self, key):
#  		for i in xrange (len (self)):
#  			if self.data.%childname[i].%childkey == key:

#  		raise KeyError, key

#  	def keys (self):
#  		if self.data == []:
#  			return []

#  		retval = []
#  		for i in xrange (len (self)):
#  			retval.append (self.__virtualhosts.getvirtualhost (i).getVHName())
#  		return retval
#  """


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
	baseclass = ""
	setlist = "#SetList\n"
	initlist = InitList
	unlinklist = UnlinkList
	commitlist = CommitList
	commitalist = CommitAList
	rollbacklist = RollbackList
	testlist = TestList
	backuplist = BackupList
	baseinit = ""
	scnl = false
	scl = false
	
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
		ImportClasses[basename] = true
			
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

		if ImportClasses.has_key(cname):
			cclassname = ImplPrefix + cname + '.' + cname
		else:
			cclassname = cname

		ctype = child.getType()
		cstype = Type2Str[ctype]

		if list.isAnonymous():
			#setlist = setlist + "\t\tself.__list.setAnonymous(1)\n"
			baseclass = "(UserList.UserList)"
			baseinit = "UserList.UserList.__init__(self)"
			
		if list.isAtomic():
			#setlist = setlist + "\t\tself.__list.setAtomic(1)\n"
			pass
						
		if list.isProtected():
			#setlist = setlist + "\t\tself.__list.setProtected(1)\n"
			pass
						
		if list.isAnonymous():
			#
			# List == Anonymous
			#

			methods = methods + AnonListOps

			unlinklist = unlinklist + '\t\tself.data = []\n'
			unlinklist = unlinklist + '\t\tself.data_bak = []\n'

			backuplist = backuplist \
				     + "\t\tself.data = self.data_bak[:]\n"
							
			commitlist = commitlist \
				     + '\t\tif self.data_bak and not self.data: self.setChanged(changed)\n' \
				     + '\t\telif not self.data_bak and self.data: self.setChanged(changed)\n' \
				     + '\t\telif len(self.data_bak) != len(self.data): self.setChanged(changed)\n' \
				     + '\t\telse:\n\t\t\tfor i in xrange(0, len(self.data_bak)):\n\t\t\t\tif self.data_bak[i] != self.data[i]: self.setChanged(changed)\n'

			commitlist = commitlist \
				     + '\t\tself.data_bak = self.data[:]\n'

			testlist = testlist \
				   + '\t\tfor pos in xrange(len(self.data)):\n' \
				   + '\t\t\tself.data[pos].test()\n'
			
			
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

				
				#########################				
			else:
				#
				# Child == List
				#

				methods = methods + AnonListCLOps

				applylist= applylist \
					   + '\t\tfor pos in xrange(self.getNum' \
					   + '%childname() ):\n' \
					   + '\t\t\tself.del%childname(0)\n' \
					   + '\t\tfor pos in xrange(other.getNum' \
					   + '%childname() ):\n' \
					   + '\t\t\tself.add%childname()\n' \
					   + '\t\t\tself.get%childname(pos).apply(other.get' \
					   + '%childname(pos))\n'

				commitlist = commitlist \
					     + '\t\tfor child in self.data:\n' \
					     + '\t\t\tchild.commit(changed)\n'

				backuplist = backuplist \
					     + '\t\tfor child in self.data:\n' \
					     + '\t\t\tchild.rollback()\n'
				#########################
			

			#########################
		else:
			#
			# List != Anonymous
			#
			methods = methods + ListOps
						
			unlinklist = unlinklist \
				     + '\t\tself.%childname = None\n'
			unlinklist = unlinklist \
				     + '\t\tself.__%childname_bak = None\n'

			backuplist = backuplist \
				     + '\t\tself.%childname = self.__%childname_bak\n'
			
			commitlist = commitlist \
				     + '\t\tself.commit%childname(changed)\n'

			if ctype != Data.ADM_TYPE_LIST:
				#
				# Child != List
				#
				methods = methods + ListCNLOps

				testlist = testlist \
					   + '\t\tself.test%childname(self.%childname)\n'
				
				applylist= applylist \
					   + '\t\tself.set%childname(other.get%childname())\n'

				initlist = initlist \
					   + '\t\t\t\tself.__%childname_bak = child.getValue()\n'
				
				#########################				
			else:
				#
				# Child == List
				#
				methods = methods + ListCLOps

				
				testlist = testlist \
					   + '\t\tif self.%childname: self.%childname.test()\n'
				
				applylist = applylist \
					    + '\t\tchild = self.create%childname()\n' \
					    + '\t\tif child: child.apply(other.get%childname())\n'

				backuplist = backuplist \
					     + '\t\tif self.%childname: self.%childname.rollback()\n'
				
				
				#########################
				
			initlist = initlist \
				   + '\t\t\texcept (KeyError): pass\n' 


		testlist = string.replace(testlist, '%childname', clname)
		initlist = string.replace(initlist, '%childname', clname)
		unlinklist = string.replace(unlinklist, '%childname', clname)
		backuplist = string.replace(backuplist, '%childname', clname)
		commitlist = string.replace(commitlist, '%childname', clname)
		commitalist = string.replace(commitalist, '%childname', clname)
		applylist= string.replace(applylist, '%childname', clname)
		methods = string.replace(methods, '%childname', clname)


		testlist = string.replace(testlist, '%childclassname', cclassname)
		initlist = string.replace(initlist, '%childclassname', cclassname)
		unlinklist = string.replace(unlinklist, '%childclassname', cclassname)
		backuplist = string.replace(backuplist, '%childclassname', cclassname)
		commitlist = string.replace(commitlist, '%childclassname', cclassname)
		commitalist = string.replace(commitalist, '%childclassname', cclassname)
		applylist= string.replace(applylist, '%childclassname', cclassname)
		methods = string.replace(methods, '%childclassname', cclassname)

		commitlist = string.replace(commitlist, '%childtype', cstype)
		initlist = string.replace(initlist, '%childtype', cstype)
		commitalist = string.replace(commitalist, '%childtype', cstype)
		methods = string.replace(methods, '%childtype', cstype)
		
	methods = ClassHeader + methods		
	methods = string.replace(methods, '%SetList', setlist)
	methods = string.replace(methods, '%baseclass', baseclass)
	methods = string.replace(methods, '%BaseInit', baseinit)
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

	if dobase:
		printb('import ' + ImplPrefix + basename)

	if not (OptNoBase or OptCondBase):
		try:
			fd = os.open(ImplPrefix + basename + '.py', os.O_CREAT | os.O_WRONLY | os.O_EXCL, 0664)
			file = os.fdopen(fd, "w")
		except (IOError, OSError), msg:
			pass
		else:
			file.write("""## Copyright (C) 2000-2002 Red Hat, Inc.
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

## Copyright (C) 2000-2002 Red Hat, Inc.
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
import UserList
from Alchemist import *
import FileBlackBox

true = (1==1)
false = not true
""")

	if OptFunctions:
		printb("""
from """ + ImplPrefix + """_functions import *
""")

	printClass(dr, drname, ImplPrefix)

	for key in ImportClasses.keys():
		printb('from ' + ImplPrefix + key + ' import *')

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
			file.write("""## Copyright (C) 2000-2002 Red Hat, Inc.
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

