import new
from UserList import UserList
import Alchemist
import FileBlackBox
import sys
import traceback
from types import *
# first some defines
true = (1==1)
false = not true

LIST = Alchemist.Data.ADM_TYPE_LIST
STRING = Alchemist.Data.ADM_TYPE_STRING
INT = Alchemist.Data.ADM_TYPE_INT
BOOL = Alchemist.Data.ADM_TYPE_BOOL
FLOAT = Alchemist.Data.ADM_TYPE_FLOAT
BASE64 = Alchemist.Data.ADM_TYPE_BASE64

ANONYMOUS = "ANONYMOUS"
PROTECTED = "PROTECTED"
ATOMIC = "ATOMIC"
TYPE = "TYPE"
FLAGS = "FLAGS"
SELF = "SELF"
NAME= "NAME"
CHILDKEYS = "CHILDKEYS"
        
# this basic class will be common for all genClass generated classes
# and imported from a seperate module
class GenClass:
   def __init__(self, list = None, parent = None):
      self._attributes = self.__class__.Attributes
      self._parent = parent
      self.changed = false
      self._dead = 0

      # initialize all variables with None
      self._doClear()

      # Constructor with object
      if list != None and (parent == None) and isinstance(list, GenClass):
         self.apply(list)
         return

      if isinstance(list, Alchemist.Context):
         self.fromContext(list.getDataRoot().getChildByIndex(0))
         self.commit(changed = false)
         
      if isinstance(list, Alchemist.Data):
         self.fromContext(list)
         self.commit(changed = false)
      
   def _doClear(self):
      raise NotImplemented

   def checkType(self, child, value):
      type = self._attributes[child][TYPE]

      if type == BOOL:
         if value != None and value != true and value != false:
            raise ValueError

      elif value == None:
         return
      
      elif type == LIST:
         if (ANONYMOUS in self._attributes[child][FLAGS]) \
            and not isinstance(value, GenAClassList):
            raise ValueError
         elif not isinstance(value, GenClassList):
            raise ValueError
         
      elif type == STRING:
         if not isinstance(value, StringType) and not isinstance(value, unicode):
            raise ValueError
         
      elif type == BASE64:
         if not isinstance(value, StringType) and not isinstance(value, unicode):
            raise ValueError
         
      elif type == INT:
         if not isinstance(value, IntType):
            raise ValueError

      elif type == FLOAT:
         if not isinstance(value, FloatType):
            raise ValueError
      
   
   #
   # @brief returns the parent of this object
   # @return the parent of this object
   #
   def getParent(self):
      return self._parent

   def _setParent(self, parent):
      self._parent = parent			
      
   def toContext(self, list):
      if list == None:
         return
      if ANONYMOUS in self._attributes[SELF][FLAGS]:
         list.setAnonymous(1)
      if ATOMIC in self._attributes[SELF][FLAGS]:
         list.setAtomic(1)
      if PROTECTED in self._attributes[SELF][FLAGS]:
         list.setProtected(1)      

   def fromContext(self, list):
      pass

   def save(self):
      raise NotImplemented

   def load(self):
      raise NotImplemented
   
   #
   # @brief deletes this object
   #
   def unlink(self):
      if self._dead:
         return
      self._dead = 1
      if self._parent != None and self._parent._dead:
         return
      parent = self._parent
      del self._parent
         
      self._doClear()
      if parent and hasattr(parent, "remove" + self._attributes[SELF][NAME]):
         getattr(parent, "remove" + self._attributes[SELF][NAME])(self)

   def modified(self):
      return self.changed
			
   def setChanged(self, val):
      self.changed = val
      if self._parent != None and val:
         self._parent.setChanged(val)		

   def copy(self):
      # create new instance of ourselves
      n = self.newClass(self._attributes[SELF][NAME], None, None)
      n.apply(self)
      return n

def _install_funcs(baseclass):
   for i in baseclass.Attributes[SELF][CHILDKEYS]:
      val = baseclass.Attributes[i]
      funcs, allfuncs = baseclass.Attributes[SELF]['install_func'](baseclass, val)
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

   #install_funcs = classmethod(install_funcs)

#
# Non-Anonymous List
#
class GenClassList(GenClass):
   def __init__(self, list = None, parent = None):
      GenClass.__init__(self, list, parent)

   def _doClear(self):
      for i in self._attributes[SELF][CHILDKEYS]:
         val = self._attributes[i]
         self.__dict__[i] = None
         self.__dict__['__' + i + '_bak'] = None
			      
   def test(self):
      for i in self._attributes[SELF][CHILDKEYS]:
         val = self._attributes[i]
         if val[TYPE] == LIST:
            if self.__dict__[i]:
               self.__dict__[i].test()
         else:
            getattr(self, "test" + i)(self.__dict__[i])

   def commit(self, changed=true):
      for i in self._attributes[SELF][CHILDKEYS]:
         val = self._attributes[i]
         if hasattr(self, "commit" + i):
            getattr(self, "commit" + i)(changed)
	
   def rollback(self):
      #print "----------- rollback %s -------" % self._attributes[SELF][NAME]
      for i in self._attributes[SELF][CHILDKEYS]:
         getattr(self, "rollback" + i)()

   def apply(self, other):
      if other == None:
         self.unlink()
         return

      for i in self._attributes[SELF][CHILDKEYS]:
         val = self._attributes[i]
         if val[TYPE] != LIST:
            getattr(self, "set" + i)(getattr(other, "get" + i)())
         else:
            child = getattr(self, "create" + i)()
            if child != None:
               child.apply(getattr(other, "get" + i)())            
            
   def _testAttr(self, value, child=None):
      return 0

   def _getAttr(self, child=None):
      return self.__dict__[child]

   def _delAttr(self, child=None):
      self.__dict__[child] = None
	
   def __setattr__(self, name, value):
      if hasattr(self, "set" + name):
         getattr(self, "set" + name)(value)
      else:
         self.__dict__[name] = value

   def toContext(self, list):
      if not list: return      
      if isinstance(list, Alchemist.Context):
         list = list.getDataRoot().getChildByIndex(0)

      GenClass.toContext(self, list)
      for child in self._attributes[SELF][CHILDKEYS]:
         val = getattr(self, child)
         if self._attributes[child][TYPE] == LIST:
            if val != None:
               achild = list.addChild(self._attributes[child][TYPE],
                                      self._attributes[child][NAME])
               val.toContext(achild)
         else:
            if val != None:
               try:
                  achild = list.getChildByName(self._attributes[child][NAME])
               except KeyError:                  
                  achild = list.addChild(self._attributes[child][TYPE],
                                                self._attributes[child][NAME])
                  achild.setValue(val)
            else:
               if list.hasChildNamed(self._attributes[child][NAME]):
                  list.getChildByName(self._attributes[child][NAME]).unlink()

   def fromContext(self, list):
      if not list: return      
      if isinstance(list, Alchemist.Context):
         list = list.getDataRoot().getChildByIndex(0)

      GenClass.fromContext(self, list)
         
      for child in self._attributes[SELF][CHILDKEYS]:
         if self._attributes[child][TYPE] != LIST:
            setattr(self, child,
                    list.getChildByName(self._attributes[child][NAME]).getValue())
         else:
            achild = list.getChildByName(self._attributes[child][NAME])
            nchild = self.newClass(self._attributes[child][NAME],
                                   achild, self)
            setattr(self, child, nchild)

   def _commitAttr(self, changed=true, child=None):
      cd = getattr(self, child)
      
      if self._attributes[child][TYPE] == LIST:
         if hasattr(cd, "commit"):
            getattr(cd, "commit")(changed)

      if getattr(self, '__' + child + '_bak') != cd:
         #print "%s changed" % child
         self.setChanged(changed)			

      setattr(self, '__' + child + '_bak', cd)      

   def _rollbackAttr(self, child=None):      
      if hasattr(self, '__' + child + '_bak'):
         setattr(self, child, getattr(self, '__' + child + '_bak'))

         if self._attributes[child][TYPE] == LIST:
            co = getattr(self, child)
            if hasattr(co, "rollback"):
               getattr(co, "rollback")()            
      else:
         setattr(self, child, None)
      
   #
   # Non-List-Child functions
   #
   def _setAttr(self, value, child=None):
      self.checkType(child, value)
      self.__dict__[child] = value
      if isinstance(list, GenClass):
         value.setParent(self)

   #
   # List-Child functions
   #
   def _createAttr(self, child=None):
      val = getattr(self, child)
      if val == None:
         val = self.newClass(self._attributes[child][NAME], None, self)
         setattr(self, child, val)
      return val

   def _removeAttr(self, child, childname=None):
      val = getattr(self, childname)
      if child == val:
         child = val
         setattr(self, childname, None)
         child.unlink()

def GenClassList_get_install_funcs(klass, val):
   funcs = [ "get", "del", "test", "commit", "rollback" ]
   if val[TYPE] != LIST:
      funcs.append("set")
   else: 
      funcs.extend(["create" , "remove"])

   allfuncs = [ "get", "del", "test", "commit", "rollback",
                "set", "create" , "remove" ]

   return funcs, allfuncs
   #get_install_funcs = classmethod(get_install_funcs)

#
# Anonymous List
#
class GenClassAList(GenClass, UserList):
   def __init__(self, list = None, parent = None):
      UserList.__init__(self)
      GenClass.__init__(self, list, parent)

   def _doClear(self):
      self.data = []
      self.data_bak = []
			
   def test(self):
      for child in self.data:
         child.test()


   def toContext(self, list):
      if not list: return      
      if isinstance(list, Alchemist.Context):
         dr = list.getDataRoot()
         if dr.getNumChildren() == 0:
            dr.addChild(self._attributes[SELF][TYPE],
                        self._attributes[SELF][NAME])
         list = list.getDataRoot().getChildByIndex(0)

      GenClass.toContext(self, list)
      
      for i in xrange(list.getNumChildren()):
         list.getChildByIndex(0).unlink()
         
      for i in self._attributes[SELF][CHILDKEYS]:
         val = self._attributes[i]         
         for child in self.data:
            nchild = list.addChild(self._attributes[i][TYPE],
                                   self._attributes[i][NAME])
            if val[TYPE] == LIST:
               child.toContext(nchild)
            else:
               nchild.setValue(child)
               
   def commit(self, changed=true):
      if self.data_bak != None and self.data == None:
         #print "%s changed" % self._attributes[SELF][NAME]
         self.setChanged(changed)
      elif self.data_bak == None and self.data != None:
         #print "%s changed" % self._attributes[SELF][NAME]
         self.setChanged(changed)
      elif len(self.data_bak) != len(self.data):
         #print "%s changed" % self._attributes[SELF][NAME]
         self.setChanged(changed)
      else:
         for i in xrange(0, len(self.data_bak)):
            if self.data_bak[i] != self.data[i]:
               #print "%s changed" % self._attributes[SELF][NAME]
               self.setChanged(changed)
            
      for i in self._attributes[SELF][CHILDKEYS]:
         val = self._attributes[i]
               
         if val[TYPE] == LIST:
            for child in self.data:
               child.commit(changed)
         
      self.data_bak = self.data[:]
	
   def fromContext(self, list):
      if not list: return      
      if isinstance(list, Alchemist.Context):
         list = list.getDataRoot().getChildByIndex(0)

      GenClass.fromContext(self, list)
      for i in self._attributes[SELF][CHILDKEYS]:
         val = self._attributes[i]
         for pos in xrange(getattr(self, "getNum" + i)()):
            getattr(self, "del" + i)(0)

         if val[TYPE] == LIST:
            for j in xrange(list.getNumChildren()):
               child = self.newClass(self._attributes[i][NAME],
                                     list.getChildByIndex(j), self)
               self.data.append(child)
         else:
            for i in xrange(list.getNumChildren()):
               child = list.getChildByIndex(i)
               self.data.append(child.getValue())

   def rollback(self):
      for childkey in self._attributes[SELF][CHILDKEYS]:
         val = self._attributes[childkey]
         if val[TYPE] == LIST:               
            for child in self.data_bak:
               child.rollback()
      self.data = self.data_bak[:]
      
   def apply(self, other):
      if other == None:
         self.unlink()
         return

      for child in self._attributes[SELF][CHILDKEYS]:
         val = self._attributes[child]
         for pos in xrange(getattr(self, "getNum" + child)()):
            getattr(self, "del" + child)(0)

         if val[TYPE] != LIST:               
            for pos in xrange(getattr(other, "getNum" + child)()):
               getattr(self, "add" + child)()
               getattr(self, "set" + child)(pos,\
                                            getattr(other, "get" + child)(pos))
         else:
            for pos in xrange(getattr(other, "getNum" + child)()):
               getattr(self, "add" + child)()
               getattr(self, "get" + child)(pos).apply(\
                     getattr(other, "get" + child)(pos))

   def _getAttr(self, pos, child = None):
      return self.data[pos]

   def _delAttr(self, pos, child = None):
      self.data.pop(pos)
      return 0

   def _getNumAttr(self, child = None):
      return len(self.data)
   
   def _moveAttr(self, pos1, pos2, child = None):
      direct = 0
      if pos2 > pos1: direct = 1
      obj = self.data.pop(pos1)
      self.data.insert(obj, pos2 - direct)
      return 0

   def __setitem__(self, i, item):
      child = self._attributes[SELF][CHILDKEYS][0]
      self.checkType(child, item)
      UserList.__setitem__(self, i, item)

   def _addAttr(self, child = None):
      if self._attributes[child][TYPE] == LIST:
         nchild = self.newClass(self._attributes[child][NAME], None, self)
         self.data.append(nchild)
      else:
         self.data.append(None)         
      return len(self.data)-1

   #
   # List-Child functions
   #
   def _removeAttr(self, val, child = None):
      try: self.remove(val)
      except ValueError: pass

   def append(self, item):
      UserList.append(self, item)
      if isinstance(item, GenClass):
         item._setParent(self)
		
   def insert(self, i, item):
      UserList.insert(self, i, item)
      item._setParent(self)

   #
   # Non-List-Child functions
   #
   def _setAttr(self, pos, value, child = None):
      self.checkType(child, value)
      self.data[pos] = value
      return 0
         
def GenClassAList_get_install_funcs(klass, val):
   funcs = [ "get", "del", "move", "getNum" , "add", "set" ]

   allfuncs = [ "get", "del", "move", "getNum" , "add",
                "set", "remove" ]

   return funcs, allfuncs
   #get_install_funcs = classmethod(get_install_funcs)

def GenClass_new_class(attributes, myglobals):
   classname = attributes[SELF][NAME]
   if attributes[SELF][TYPE] != LIST:
      raise AttributeError
   
   if ANONYMOUS in attributes[SELF][FLAGS]:
      listtype = GenClassAList
      attributes[SELF]['install_func'] = GenClassAList_get_install_funcs
   else:
      listtype = GenClassList
      attributes[SELF]['install_func'] = GenClassList_get_install_funcs

   def GenClass_init_func(self, list=None, parent=None):
      if hasattr(self.__class__, "_ListClass"):
         self.__class__._ListClass.__init__(self, list, parent)

   def GenClass_newClass_func(self, classname, list=None, parent=None):
      klass = self.__class__._Globals[classname]
      if klass:
         return klass(list, parent)
      else: return None

   newclass = new.classobj(classname + '_base', (listtype,),
                           {'Attributes':attributes,
                            '__init__':GenClass_init_func,
                            '_ListClass':listtype,
                            '_Globals':myglobals,
                            'newClass':GenClass_newClass_func})
   
   _install_funcs(newclass)


   implclass = new.classobj(classname, (newclass,),
                            {})
   return (newclass, implclass)


def _printClass(list, optlower = false, myglobals = None):
   if myglobals.has_key(list.getName()):
      return 

   myglobals[list.getName()] = None

   attributes = { SELF: { NAME : list.getName(),
                          TYPE : LIST,                          
                          FLAGS : [],
                          CHILDKEYS : []}}
   if list.isAnonymous():
      attributes[SELF][FLAGS].append(ANONYMOUS)
      
   if list.isAtomic():
      attributes[SELF][FLAGS].append(ATOMIC)
						
   if list.isProtected():
      attributes[SELF][FLAGS].append(PROTECTED)
	
   num = list.getNumChildren()
   retval = {}
   for i in xrange(num):
      child = list.getChildByIndex(i)
      
      if child.getType() == Alchemist.Data.ADM_TYPE_LIST:
	 _printClass(child, myglobals = myglobals)
	
   for i in xrange(num):
      child = list.getChildByIndex(i)
      cname = child.getName()
      if cname in attributes[SELF][CHILDKEYS]:
         continue
      
      if optlower: clname = str.OptLower(cname)
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
      
   baseclass, implclass = GenClass_new_class(attributes, myglobals)
   myglobals[list.getName() + '_base' ] = baseclass
   myglobals[list.getName() ] = implclass

def GenClass_read_classfile(boxpath, mod = None, OptLower = false):
   bbc = Alchemist.Context(name = 'FileBlackBox', serial = 1)
   broot = bbc.getDataRoot()
   list = broot.addChild(Alchemist.Data.ADM_TYPE_LIST, 'box_cfg')
   list.addChild(Alchemist.Data.ADM_TYPE_STRING, 'path').setValue(boxpath)
   list.addChild(Alchemist.Data.ADM_TYPE_STRING,
                 'box_type').setValue('FileBlackBox')
   list.addChild(Alchemist.Data.ADM_TYPE_BOOL, 'readable').setValue(true)
   list.addChild(Alchemist.Data.ADM_TYPE_BOOL, 'writable').setValue(false)
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

   _printClass(dr, myglobals = mod.__dict__)
