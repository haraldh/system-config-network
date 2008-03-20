"""
Generates classes with useful methods from xml data structure definition
file (alchemist style).
"""
## Copyright (C) 2001 - 2007 Red Hat, Inc.
## Copyright (C) 2001 - 2007 Harald Hoyer <harald@redhat.com>

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

__author__ = "Harald Hoyer"

import new
import sys
import types

from netconfpkg.NC_functions import log

Alchemist = None
LIST = "LIST"
STRING = "STRING"
INT = "INT"
BOOL = "BOOL"
FLOAT = "FLOAT"
BASE64 = "BASE64"
ANONYMOUS = "ANONYMOUS"
PROTECTED = "PROTECTED"
ATOMIC = "ATOMIC"
TYPE = "TYPE"
FLAGS = "FLAGS"
SELF = "SELF"
NAME = "NAME"
PARENT = "PARENT"
CHILDKEYS = "CHILDKEYS"
##PRIMARYKEY = "PRIMARYKEY"
##TYPEKEY = "TYPEKEY"
_STRICTTYPE = None

class ParseError(Exception):
    "ParseError exception"
    pass
NOCHILDATTR = ParseError

# pylint: disable-msg=W0212

class GenClass:
    """
    Basic class common for all genClass generated classes
    and imported from a seperate module
    """
    def __init__(self, clist = None, parent = None):
        'Constructor with the parent list and optional the Alchemist list.'
        self._attributes = getattr(self.__class__, "_Attributes", None)
        self._parent = parent
        self.changed = False
        self._dead = False

        # initialize all variables with None
        self._doClear()

        # Constructor with object
        if clist != None and (parent == None) and isinstance(clist, GenClass):
            self.apply(clist)
            return

        if isinstance(clist, Alchemist.Context):
            self.fromContext(clist.getDataRoot().getChildByIndex(0))
            self.commit(changed = False)
            self.setChanged(False)

        if isinstance(clist, Alchemist.Data):
            self.fromContext(clist)
            self.commit(changed = False)
            self.setChanged(False)

    def commit(self, changed=True):
        'Stub'
        raise NotImplementedError

    def apply(self, other):
        'Stub'
        raise NotImplementedError

    def _doClear(self):
        'Stub'
        raise NotImplementedError

    def _newClass(self, *args, **kwargs):
        "return new instance of this class"
        classname = args[0]
        if len(args) >= 2:
            clist = args[1]
        else:
            clist = kwargs.get("clist")
        if len(args) >= 3:
            parent = args[2]
        else:
            parent = kwargs.get("parent")
        klass = self.__class__._Globals[classname] # pylint: disable-msg=E1101

        if klass:
            return klass(clist, parent)
        else: 
            return None

    def checkType(self, child, value):
        'Check the type of the value passed to an assignment'
        if not _STRICTTYPE:
            return

        ctype = self._attributes[child][TYPE]

        tdict = {
            STRING: types.StringType,
            BASE64: types.StringType,
            INT: types.IntType,
            FLOAT: types.FloatType,
            }


        if ctype == BOOL:
            if value != None and not isinstance(value, bool):
                raise TypeError

        elif value == None:
            return

        elif tdict.has_key(ctype):
            if not isinstance(value, tdict[ctype]):
                raise TypeError

        elif ctype == LIST:
            if (ANONYMOUS in self._attributes[child][FLAGS]) \
               and not isinstance(value, GenClassAList):
                raise TypeError
            elif not isinstance(value, GenClassList):
                raise TypeError

    def getParent(self):
        'Get the parent list'
        return self._parent

    def _setParent(self, parent):
        'Set the parent list (private)'
        self._parent = parent

    def toContext(self, clist):
        'Convert this list to the internal Alchemist representation.'
        if clist == None:
            return
        if isinstance(clist, Alchemist.Context):
            dr = clist.getDataRoot()
            if dr.getNumChildren() == 0:
                dr.addChild(self._attributes[SELF][TYPE],
                            self._attributes[SELF][NAME])
            clist = clist.getDataRoot().getChildByIndex(0)

        if ANONYMOUS in self._attributes[SELF][FLAGS]:
            clist.setAnonymous(1)
        if ATOMIC in self._attributes[SELF][FLAGS]:
            clist.setAtomic(1)
        if PROTECTED in self._attributes[SELF][FLAGS]:
            clist.setProtected(1)

        return clist

    def __str__(self):
        'String representation.'
        parentStr = self._attributes[SELF][NAME]
        return self._objToStr(parentStr)

    def _objToStr(self, parentStr = None):
        'Stub'
        raise NotImplementedError

    def _parseLine(self, vals, value):
        'Stub'
        raise NotImplementedError

    def _load(self, *args, **kwargs):
        """
        load(filename=None)
        load the object from stdin or filename
        """
        filename = None
        if len(args) >= 1:
            filename = args[0]
        else:
            filename = kwargs.get("filename")
            
        if filename:
            mfile = open(filename, "r")
        else:
            mfile = sys.stdin

        lines = mfile.readlines()

        for line in lines:
            try:
                line = line[:-1]
                vals = line.split("=")
                if len(vals) <= 1:
                    continue
                key = vals[0]
                value = "=".join(vals[1:])

                vals = key.split(".")
                self._parseLine(vals, value)
            except Exception, e:
                pe = ParseError(line)
                pe.args += e.args
                raise pe

        if filename:
            mfile.close()

    def save(self, *args, **kwargs):
        """
        save(filename=None)
        save the object to stdout or filename
        """
        filename = None
        if len(args) >= 1:
            filename = args[0]
        else:
            filename = kwargs.get("filename")
            
        if filename:
            mfile = open(filename, "w")
        else:
            mfile = sys.stdout
        mfile.write(str(self))
        if kwargs.has_key('filename'):
            mfile.close()

    def fromContext(self, clist):
        'Stub'
        raise NotImplementedError

    def unlink(self):
        "deletes this object"
        if self._dead:
            return
        self._dead = True
        if self._parent != None and self._parent._dead:
            return
        parent = self._parent
        del self._parent

        self._doClear()
        if parent and hasattr(parent, "remove" + self._attributes[SELF][NAME]):
            getattr(parent, "remove" + self._attributes[SELF][NAME])(self)

    def modified(self):
        "returns state of the object's modification since last commit"
        return self.changed

    def setChanged(self, val):
        "set the object's modification state"
        self.changed = val

    def copy(self):
        "create a new instance of ourselves"
        n = self._newClass(self._attributes[SELF][NAME], None, None)
        n.apply(self)
        return n

def _installFuncs(baseclass):
    "install basic functions to a generated class"
    for i in baseclass._Attributes[SELF][CHILDKEYS]:
        val = baseclass._Attributes[i]
        funcs = baseclass._Attributes[SELF]['install_func'](baseclass,
                                                                     val)
        for func in funcs:
            f = getattr(baseclass, '_%sAttr' % func)
            f = f.im_func
            defArgs = f.func_defaults[:-1]
            if defArgs != None and defArgs != ():
                defArgs = defArgs + (i,)
            else:
                defArgs = (i,)
            nfunc = new.function(f.func_code, f.func_globals,
                                 func + i, defArgs)
            setattr(baseclass, func + i,
                    new.instancemethod(nfunc, None, baseclass))

        # speedup get and set by using properties
        setattr(baseclass, i, property(fget = getattr(baseclass, 
                                                      "get"+i, None), 
                                       fset = getattr(baseclass, 
                                                      "set"+i, None),
                                       fdel = getattr(baseclass, 
                                                      "del"+i, None)))
                
    #install_funcs = classmethod(install_funcs)

def __GenClassList_get_install_funcs(klass, val): # pylint: disable-msg=W0613
    "returns all functions to install"
    funcs = [ "get", "del", "test", "commit", "rollback" ]
    if val[TYPE] != LIST:
        funcs.append("set")
    else:
        funcs.extend(["create" , "remove"])

    return funcs

class GenClassList(GenClass):
    """
    Non-Anonymous List
    """
    def __init__(self, clist = None, parent = None):
        GenClass.__init__(self, clist, parent)

    def _doClear(self):
        "clear this list"
        for i in self._attributes[SELF][CHILDKEYS]:
            #val = self._attributes[i]
            self.__dict__[i] = None
            self.__dict__['__' + i + '_bak'] = None

    def test(self):
        "checks the objects validity"
        for i in self._attributes[SELF][CHILDKEYS]:
            val = self._attributes[i]
            if val[TYPE] == LIST:
                if self.__dict__[i]:
                    self.__dict__[i].test()
            else:
                getattr(self, "test" + i)(self.__dict__[i])

    def commit(self, changed=True):
        "commit the object, setting modified state to False"
        for i in self._attributes[SELF][CHILDKEYS]:
            if hasattr(self, "commit" + i):
                getattr(self, "commit" + i)(changed=changed, child=i)

    def setChanged(self, changed):
        "set the object's modification state"
        GenClass.setChanged(self, changed)
        if not changed:
            for i in self._attributes[SELF][CHILDKEYS]:
                val = self._attributes[i]
                if val[TYPE] == LIST:
                    child = getattr(self, i)
                    if hasattr(child, "setChanged"):
                        child.setChanged(changed)

    def _commitAttr(self, changed=True, child=None):
        "commit an attribute"
        if not child:
            return

        cd = getattr(self, child)

        if self._attributes[child][TYPE] == LIST:
            if hasattr(cd, "commit"):
                cd.commit(changed)
                if changed and hasattr(cd, "changed") and cd.changed:
                    self.setChanged(changed)

        if changed and getattr(self, '__' + child + '_bak') != cd:
            log.log(5, "%s changed %s" % (self._attributes[SELF][NAME] + \
                                              '.' + child, str(changed)))
            self.setChanged(changed)

        setattr(self, '__' + child + '_bak', cd)    

    def rollback(self):
        "rollback this list"
        #print "----------- rollback %s -------" % self._attributes[SELF][NAME]
        for i in self._attributes[SELF][CHILDKEYS]:
            getattr(self, "rollback" + i)()

    def __str__(self):
        return GenClass.__str__(self)

    def _objToStr(self, parentStr = None):
        'Internal recursive object to string method.'
        retstr = ""

        for child, attr in self._attributes.items():
            if child == SELF: 
                continue

            val = None

            if hasattr(self, child):
                val = getattr(self, child)

            if attr[TYPE] != LIST:
                if val != None:
                    if attr[TYPE] != BOOL:
                        retstr += "%s.%s=%s\n" % (parentStr, child, str(val))
                    else:
                        if val: 
                            retstr += "%s.%s=True\n" % (parentStr, child)
                        else: 
                            retstr += "%s.%s=False\n" % (parentStr, child)

            else:
                if val != None:
                    retstr += val._objToStr("%s.%s" % (parentStr, child))

        return retstr


    def _parseLine(self, vals, value):
        'Internal import method, which parses an snmp style assignment.'
        if len(vals) == 0:
            return

        key = vals[0]
        try:
            key = int(key)
        except ValueError:
            pass

        if len(vals) == 1:
            if self._attributes[key][TYPE] == INT:
                setattr(self, key, int(value))
            elif self._attributes[key][TYPE] == BOOL:
                if value == "True":
                    setattr(self, key, True)
                elif value == "False":
                    setattr(self, key, False)
            else:
                setattr(self, key, value)
            return
        else:
            if key == self._attributes[SELF][NAME]:
                self._parseLine(vals[1:], value)
                return

            if hasattr(self, key) and getattr(self, key):
                getattr(self, key)._parseLine(vals[1:], value)
                return
            else:
                self._createAttr(key)._parseLine(vals[1:], value)

    def apply(self, other):
        "apply another object to this one (copy)"
        if other == None:
            self.unlink()
            return

        #if not isinstance(other, GenClass):
        #    return

        for i in self._attributes[SELF][CHILDKEYS]:
            val = self._attributes[i]
            if val[TYPE] != LIST:
                getattr(self, "set" + i)(getattr(other, "get" + i)())
            else:
                child = getattr(self, "create" + i)()
                if child != None:
                    child.apply(getattr(other, "get" + i)())

    def _testAttr(self, value, child=None): # pylint: disable-msg=W0613
        "test an attribute"
        return True

    def _getAttr(self, child=None):
        "get an attribute"
        return self.__dict__[child]

    def _delAttr(self, child=None):
        "delete an attribute"
        self.__dict__[child] = None

#    def __setattr__(self, name, value):
#        if hasattr(self, "set" + name):
#            getattr(self, "set" + name)(value)
#        else:
#            self.__dict__[name] = value

    def toContext(self, clist):
        "deepcopy"
        clist = GenClass.toContext(self, clist)
        if clist == None: 
            return

        for child in self._attributes[SELF][CHILDKEYS]:
            val = getattr(self, child)
            if self._attributes[child][TYPE] == LIST:
                if val != None:
                    achild = clist.addChild(self._attributes[child][TYPE],
                                           self._attributes[child][NAME])
                    val.toContext(achild)
            else:
                if val != None:
                    try:
                        achild = clist.getChildByName(\
                            self._attributes[child][NAME])
                    except KeyError:
                        achild = clist.addChild(self._attributes[child][TYPE],
                                                self._attributes[child][NAME])
                        achild.setValue(val)
                else:
                    if clist.hasChildNamed(self._attributes[child][NAME]):
                        clist.getChildByName(\
                            self._attributes[child][NAME]).unlink()

    def fromContext(self, clist):
        "deepcopy"
        if not clist: 
            return
        if isinstance(clist, Alchemist.Context):
            clist = clist.getDataRoot().getChildByIndex(0)

        for child in self._attributes[SELF][CHILDKEYS]:
            if self._attributes[child][TYPE] != LIST:
                setattr(self, child,
                        clist.getChildByName(\
                        self._attributes[child][NAME]).getValue())
            else:
                achild = clist.getChildByName(self._attributes[child][NAME])
                nchild = self._newClass(self._attributes[child][NAME],
                                       achild, self)
                setattr(self, child, nchild)

    def _rollbackAttr(self, child=None):
        "rollback an attribute"
        if hasattr(self, '__' + child + '_bak'):
            setattr(self, child, getattr(self, '__' + child + '_bak'))

            if self._attributes[child][TYPE] == LIST:
                co = getattr(self, child)
                if hasattr(co, "rollback"):
                    co.rollback()
        else:
            setattr(self, child, None)

    #
    # Non-List-Child functions
    #
    def _setAttr(self, value, child=None):
        "set an attribute"
        self.checkType(child, value)
        self.__dict__[child] = value
        if isinstance(value, GenClass):
            value.setParent(self)

    #
    # List-Child functions
    #
    def _createAttr(self, child=None):
        "create an attribute"
        val = getattr(self, child)
        if val == None:
            val = self._newClass(self._attributes[child][NAME], None, self)
            setattr(self, child, val)
        return val

    def _removeAttr(self, child, childname=None):
        "remove an attribute"
        val = getattr(self, childname)
        if child == val:
            child = val
            setattr(self, childname, None)
            child.unlink()

class GenClassAList(GenClass, list):
    """
    Anonymous List
    """
    def __init__(self, clist = None, parent = None):
        list.__init__(self)
        GenClass.__init__(self, clist, parent)
        self.data_bak = []

    def _doClear(self):
        "clear this list"
        self.data_bak = []

    def test(self):
        "checks the objects validity"
        for child in self:
            if hasattr(child, 'test'):
                child.test()

    def __str__(self):
        return GenClass.__str__(self)

    def _objToStr(self, parentStr = None):
        'Internal recursive object to string method.'
        retstr = ""
        if len(self):
            # print numbers
            num = 1
            ckey = self._attributes[SELF][CHILDKEYS][0]
            attr = self._attributes[ckey]
            if attr[TYPE] == LIST:
                for child in self:
                    if hasattr(child, '_objToStr'):
                        retstr += child._objToStr("%s.%d" % (parentStr, num))
                        num += 1
            else:
                for val in self:
                    if val:
                        if attr[TYPE] != BOOL:
                            retstr += "%s.%d=%s\n" % (parentStr, num, str(val))
                        else:
                            if val: 
                                retstr += "%s.%d=True\n" % (parentStr, num)
                            else: 
                                retstr += "%s.%d=False\n" % (parentStr, num)
                        num += 1

        return retstr


    def _parseLine(self, vals, value):
        'Internal import method, which parses an snmp style assignment.'
        if len(vals) == 0:
            return

        key = vals[0]
        try:
            key = int(key)
        except ValueError:
            pass

        if len(vals) == 1:
            cname = self._attributes[SELF][CHILDKEYS][0]
            if isinstance(key, int) and len(self) >= int(key) :
                self[int(key)-1] = value
                return
            else:
                num = self._addAttr(cname)
                self[num] = value
                return
        else:
            if key == self._attributes[SELF][NAME]:
                self._parseLine(vals[1:], value)
                return

            cname = self._attributes[SELF][CHILDKEYS][0]
            if isinstance(key, int) and len(self) >= int(key) :
                self[int(key)-1]._parseLine(vals[1:], value)
                return
            else:
                num = self._addAttr(cname)
                self[num]._parseLine(vals[1:], value)
                return

    def toContext(self, clist):
        "deepcopy"
        clist = GenClass.toContext(self, clist)
        if clist == None: 
            return

        for i in xrange(clist.getNumChildren()):
            clist.getChildByIndex(0).unlink()

        for i in self._attributes[SELF][CHILDKEYS]:
            val = self._attributes[i]
            for child in self:
                if not isinstance(child, GenClass):
                    continue
                nchild = clist.addChild(self._attributes[i][TYPE],
                                       self._attributes[i][NAME])
                if val[TYPE] == LIST:
                    child.toContext(nchild)
                else:
                    nchild.setValue(child)

    def commit(self, changed=True):
        "commit the list"
        if changed:
            if len(self.data_bak) != len(self):
                log.log(5, "3 %s changed %s" % (self._attributes[SELF][NAME],
                                                str(changed)))
                self.setChanged(changed)
            else:
                for i in xrange(0, len(self.data_bak)):
                    if self.data_bak[i] != self[i]:
                        log.log(5, "4 %s changed %s" % (\
                                self._attributes[SELF][NAME], str(changed)))
                        self.setChanged(changed)
                        break

        for child in self:
            if hasattr(child, 'commit'):
                child.commit(changed)
            if changed and hasattr(child, "changed") and child.changed:
                log.log(5, "5 %s changed %s" % (child._attributes[SELF][NAME],
                                                str(changed)))
                self.setChanged(changed)

        self.data_bak = self[:]


    def setChanged(self, changed):
        "set the object's modification state"
        GenClass.setChanged(self, changed)
        if not changed:
            for child in self:
                if hasattr(child, 'setChanged'):
                    child.setChanged(changed)

    def fromContext(self, clist):
        "deepcopy"
        if not clist: 
            return

        if isinstance(clist, Alchemist.Context):
            clist = clist.getDataRoot().getChildByIndex(0)

        for i in self._attributes[SELF][CHILDKEYS]:
            val = self._attributes[i]
            # pylint: disable-msg=W0612
            for pos in xrange(getattr(self, "getNum" + i)()):
                getattr(self, "del" + i)(0)

            if val[TYPE] == LIST:
                for j in xrange(clist.getNumChildren()):
                    child = self._newClass(self._attributes[i][NAME],
                                          clist.getChildByIndex(j), self)
                    self.append(child)
            else:
                for i in xrange(clist.getNumChildren()):
                    child = clist.getChildByIndex(i)
                    self.append(child.getValue())

    def rollback(self):
        "rollback this list"
        for childkey in self._attributes[SELF][CHILDKEYS]:
            val = self._attributes[childkey]
            if val[TYPE] == LIST:
                for child in self.data_bak:
                    child.rollback()
        self = self.data_bak[:]

    def apply(self, other):
        "apply another object to this one (copy)"
        if other == None:
            self.unlink()
            return

        for child in self._attributes[SELF][CHILDKEYS]:
            val = self._attributes[child]
            if not hasattr(self, "getNum" + child):
                return
            for pos in xrange(getattr(self, "getNum" + child)()):
                getattr(self, "del" + child)(0)

            if val[TYPE] != LIST:
                for pos in xrange(getattr(other, "getNum" + child)()):
                    getattr(self, "add" + child)()
                    getattr(self, "set" + child)(pos, \
                                                 getattr(other, 
                                                         "get" + child)(pos))
            else:                
                for pos in xrange(getattr(other, "getNum" + child)()):
                    getattr(self, "add" + child)()
                    c1 = getattr(self, "get" + child)(pos)
                    c2 = getattr(other, "get" + child)(pos)
                    if isinstance(c2, GenClass):
                        c1.apply(c2)
                    else:
                        self[pos] = c2
                    

    def _getAttr(self, pos, child = None): # pylint: disable-msg=W0613
        "get an atttribute at position pos"
        return self[pos]

    def _delAttr(self, pos, child = None): # pylint: disable-msg=W0613
        "delete an atttribute at position pos"
        self.pop(pos)
        return 0

    def _getNumAttr(self, child = None): # pylint: disable-msg=W0613
        "get the number of atttributes"
        return len(self)

    def _moveAttr(self, pos1, pos2, child = None): # pylint: disable-msg=W0613
        "move an atttribute from pos1 to pos2"
        direct = 0
        if pos2 > pos1:
            direct = 1
        obj = self.pop(pos1)
        self.insert(obj, pos2 - direct)
        return 0

    def __setitem__(self, pos, item):
        "set item at position pos"
        #print "------- %s::__setitem__  -------" % self._attributes[SELF][NAME]
        child = self._attributes[SELF][CHILDKEYS][0]
        self.checkType(child, item)
        if isinstance(item, GenClass):
            item._setParent(self)
        list.__setitem__(self, pos, item)

    def _addAttr(self, child = None):
        "add an attribute and return the position"
        if self._attributes[child][TYPE] == LIST:
            nchild = self._newClass(self._attributes[child][NAME], None, self)
            self.append(nchild)
        else:
            self.append(None)
        return len(self)-1

    #
    # List-Child functions
    #
    def _removeAttr(self, val, child = None): # pylint: disable-msg=W0613
        "remove an attribute"
        try: 
            self.remove(val)
        except ValueError: 
            pass

    def append(self, item):
        "append an item"
        #print "------- %s::append()  -------" % self._attributes[SELF][NAME]
        list.append(self, item)
        if isinstance(item, GenClass):
            item._setParent(self)

    def insert(self, pos, item):
        "insert an item at position pos"
        list.insert(self, pos, item)
        item._setParent(self)

    #
    # Non-List-Child functions
    #
    def _setAttr(self, pos, value, child = None):
        "set an attribute"
        #print "_setAttr"
        self.checkType(child, value)
        self[pos] = value
        return 0

def __GenClassAList_get_install_funcs(klass, val): # pylint: disable-msg=W0613
    "returns all functions to install"
    funcs = [ "get", "del", "move", "getNum" , "add", "set" ]
    return funcs

def __GenClass_init_func(selfklass, clist=None, parent=None):
    "__init__ method of genClass classes"
    if hasattr(selfklass.__class__, "_ListClass"):
        selfklass.__class__._ListClass.__init__(selfklass, clist, parent)

def __GenClass_new_class(attributes, myglobals):
    "generate a new class with attributes and myglobals"
    classname = attributes[SELF][NAME]
    if attributes[SELF][TYPE] != LIST:
        raise AttributeError

    if ANONYMOUS in attributes[SELF][FLAGS]:
        listtype = GenClassAList
        attributes[SELF]['install_func'] = __GenClassAList_get_install_funcs
    else:
        listtype = GenClassList
        attributes[SELF]['install_func'] = __GenClassList_get_install_funcs

    newclass = new.classobj(classname + '_base', (listtype,),
                            {'_Attributes' : attributes,
                             '__init__' : __GenClass_init_func,
                             '_ListClass' : listtype,
                             '_Globals' : myglobals,
                             })

    _installFuncs(newclass)


    implclass = new.classobj(classname, (newclass,),
                             {})
    return (newclass, implclass)

def __generateClassAlchemist(clist, parent = None, optlower = False,
                             myglobals = None):
    "generate a genClass with underlying Alchemist"
    #import Alchemist

    if myglobals.has_key(clist.getName()):
        return

    myglobals[clist.getName()] = None

    attributes = { SELF: { NAME : clist.getName(),
                           TYPE : LIST,
                           FLAGS : [],
                           PARENT : parent,
                           CHILDKEYS : []}}

    if clist.isAnonymous():
        attributes[SELF][FLAGS].append(ANONYMOUS)

    if clist.isAtomic():
        attributes[SELF][FLAGS].append(ATOMIC)

    if clist.isProtected():
        attributes[SELF][FLAGS].append(PROTECTED)

    num = clist.getNumChildren()

    if parent:
        pname = parent + "." + attributes[SELF][NAME]
    else:
        pname = attributes[SELF][NAME]

    for i in xrange(num):
        child = clist.getChildByIndex(i)

        if child.getType() == Alchemist.Data.ADM_TYPE_LIST:
            __generateClassAlchemist(child, pname, myglobals = myglobals)

    for i in xrange(num):
        child = clist.getChildByIndex(i)
        cname = child.getName()
        if cname in attributes[SELF][CHILDKEYS]:
            continue

        if optlower: clname = str.lower(cname)
        else: clname = cname

        ctype = child.getType()

        attributes[cname] = { NAME : clname, TYPE : ctype, FLAGS : [] }
        attributes[SELF][CHILDKEYS].append(cname)

        if child.getType() == Alchemist.Data.ADM_TYPE_LIST:
            if child.isAnonymous():
                attributes[cname][FLAGS].append(ANONYMOUS)

            if child.isAtomic():
                attributes[cname][FLAGS].append(ATOMIC)

            if child.isProtected():
                attributes[cname][FLAGS].append(PROTECTED)

    baseclass, implclass = __GenClass_new_class(attributes, myglobals)
    myglobals[clist.getName() + '_base' ] = baseclass
    myglobals[clist.getName() ] = implclass

def __readClassfileAlchemist(boxpath, mod = None, optlower = False):
    "read an idl classfile with Alchemist"
    try:
        # pylint: disable-msg=F0401
        from Alchemist import FileBlackBox
    except ImportError:
        return
    bbc = Alchemist.Context(name = 'FileBlackBox', serial = 1)
    broot = bbc.getDataRoot()
    clist = broot.addChild(Alchemist.Data.ADM_TYPE_LIST, 'box_cfg')
    clist.addChild(Alchemist.Data.ADM_TYPE_STRING, 'path').setValue(boxpath)
    clist.addChild(Alchemist.Data.ADM_TYPE_STRING,
                  'box_type').setValue('FileBlackBox')
    clist.addChild(Alchemist.Data.ADM_TYPE_BOOL, 'readable').setValue(True)
    clist.addChild(Alchemist.Data.ADM_TYPE_BOOL, 'writable').setValue(False)
    bb = FileBlackBox.FileBlackBox(clist)

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

    __generateClassAlchemist(dr, myglobals = mod.__dict__, optlower = optlower)

def __generateClass(clist, parent = None, optlower = False, myglobals = None):
    "generate a class"
    listname = clist.nodeName.encode()
    if myglobals.has_key(listname):
        return

    myglobals[listname] = None

    attributes = { SELF: { NAME : listname,
                           TYPE : LIST,
                           FLAGS : [],
                           PARENT : parent,
                           CHILDKEYS : []}}

    if "ANONYMOUS" in clist.attributes.keys() and \
           unicode.upper(clist.attributes["ANONYMOUS"].value) == "TRUE":
        attributes[SELF][FLAGS].append(ANONYMOUS)

    if "ATOMIC" in clist.attributes.keys() and \
           unicode.upper(clist.attributes["ATOMIC"].value) == "TRUE":
        attributes[SELF][FLAGS].append(ATOMIC)

    if "PROTECTED" in clist.attributes.keys() and \
           unicode.upper(clist.attributes["PROTECTED"].value) == "TRUE":
        attributes[SELF][FLAGS].append(PROTECTED)

    if parent:
        pname = parent + "." + attributes[SELF][NAME]
    else:
        pname = attributes[SELF][NAME]

    for child in clist.childNodes:
        if child.nodeType != child.ELEMENT_NODE:
            continue

        if "TYPE" in child.attributes.keys() and \
               unicode.upper(child.attributes["TYPE"].value) == "LIST":
            __generateClass(child, pname, myglobals = myglobals)

    childnum = 0

    for child in clist.childNodes:
        if child.nodeType != child.ELEMENT_NODE:
            continue

        cname = child.nodeName.encode()
        if cname in attributes[SELF][CHILDKEYS]:
            continue

        childnum += 1

        if optlower: 
            clname = cname.lower()
        else: 
            clname = cname

        if "TYPE" in child.attributes.keys():
            ctype = unicode.upper(child.attributes["TYPE"].value)
            if ctype == "LIST": ctype = Alchemist.Data.ADM_TYPE_LIST
            elif ctype == "STRING": ctype = Alchemist.Data.ADM_TYPE_STRING
            elif ctype == "INT": ctype = Alchemist.Data.ADM_TYPE_INT
            elif ctype == "BOOL": ctype = Alchemist.Data.ADM_TYPE_BOOL
            elif ctype == "FLOAT": ctype = Alchemist.Data.ADM_TYPE_FLOAT
            elif ctype == "BASE64": ctype = Alchemist.Data.ADM_TYPE_BASE64
        else: 
            raise NOCHILDATTR

        attributes[cname] = { NAME : clname, TYPE : ctype, FLAGS : [] }
        attributes[SELF][CHILDKEYS].append(cname)

        if ctype == Alchemist.Data.ADM_TYPE_LIST:
            if "ANONYMOUS" in child.attributes.keys() and \
                   unicode.upper(child.attributes["ANONYMOUS"].value) == "TRUE":
                attributes[cname][FLAGS].append(ANONYMOUS)

            if "ATOMIC" in child.attributes.keys() and \
                   unicode.upper(child.attributes["ATOMIC"].value) == "TRUE":
                attributes[cname][FLAGS].append(ATOMIC)

            if "PROTECTED" in child.attributes.keys() and \
                   unicode.upper(child.attributes["PROTECTED"].value) == "TRUE":
                attributes[cname][FLAGS].append(PROTECTED)
##       else:
##          if "PRIMARYKEY" in child.attributes.keys():
##             attributes[cname][FLAGS].append(PRIMARYKEY)
##          if "TYPEKEY" in child.attributes.keys():
##             attributes[cname][FLAGS].append(TYPEKEY)

    baseclass, implclass = __GenClass_new_class(attributes, myglobals)
    myglobals[listname + '_base' ] = baseclass
    myglobals[listname] = implclass

def __readClassfile(boxpath, mod = None, optlower = False): # pylint: disable-msg=W0613
    "read an idl classfile with xml.dom"
    import xml.dom.minidom

    doc = xml.dom.minidom.parse(boxpath)
    dt = doc.childNodes[0].getElementsByTagName("datatree")[0]
    dr = None
    for e in dt.childNodes:
        if e.nodeType != e.ELEMENT_NODE:
            continue
        dr = e
        break

    __generateClass(dr, myglobals = mod.__dict__)

def readClassfile(boxpath, mod, optlower = False):
    """
    Load the classfile and use the Alchemist, if Use_Alchemist is 
    set in the module.
    """
    global LIST
    global STRING
    global INT
    global BOOL
    global FLOAT
    global BASE64
    global Alchemist
    useAlchemist = None
    if hasattr(mod, "Use_Alchemist"):
        useAlchemist = getattr(mod, "Use_Alchemist")

    if useAlchemist:
        import Alchemist # pylint: disable-msg=W0621
        LIST = Alchemist.Data.ADM_TYPE_LIST
        STRING = Alchemist.Data.ADM_TYPE_STRING
        INT = Alchemist.Data.ADM_TYPE_INT
        BOOL = Alchemist.Data.ADM_TYPE_BOOL
        FLOAT = Alchemist.Data.ADM_TYPE_FLOAT
        BASE64 = Alchemist.Data.ADM_TYPE_BASE64
        __readClassfileAlchemist(boxpath, mod, optlower)
    else:
        class Alchemist: # pylint: disable-msg=W0232
            "stub"
            class Data: # pylint: disable-msg=W0232
                "stub"
                ADM_TYPE_LIST = LIST
                ADM_TYPE_STRING = STRING
                ADM_TYPE_INT = INT
                ADM_TYPE_BOOL = BOOL
                ADM_TYPE_FLOAT = FLOAT
                ADM_TYPE_BASE64 = BASE64

            class Context: # pylint: disable-msg=W0232
                "stub"
                pass

        __readClassfile(boxpath, mod)
