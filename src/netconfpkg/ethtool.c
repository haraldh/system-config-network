#include <sys/types.h>
#include <string.h>
#include <stdlib.h>
#include <sys/ioctl.h>
#include <stdio.h>
#include <net/if.h>

typedef __uint32_t u32;	/* hack, so we may include kernel's ethtool.h */
typedef __uint16_t u16;	/* ditto */
typedef __uint8_t u8;	/* ditto */
#include <linux/ethtool.h>
#include <linux/sockios.h>

#include <Python.h>

static PyObject *
get_module (PyObject * self, PyObject * args)
{
  struct ethtool_cmd ecmd;
  struct ifreq ifr;
  int fd, err;
  char buf[1024];
  char *devname;
    
  if (!PyArg_ParseTuple(args, "s", &devname)) {
    return NULL;
  }

  /* Setup our control structures. */
  memset(&ecmd, 0, sizeof(ecmd));
  memset(&ifr, 0, sizeof(ifr));
  strcpy(&ifr.ifr_name[0], devname);
  ifr.ifr_data = (caddr_t) &buf;
  ecmd.cmd = ETHTOOL_GDRVINFO;
  memcpy(&buf, &ecmd, sizeof(ecmd));
  
  /* Open control socket. */
  fd = socket(AF_INET, SOCK_DGRAM, 0);
  if(fd < 0) {
    PyErr_SetString(PyExc_OSError, strerror(errno));
    return NULL;
  }
  
  /* Get current settings. */
  err = ioctl(fd, SIOCETHTOOL, &ifr);
  if(err < 0) {
    PyErr_SetString(PyExc_OSError, strerror(errno));
    close(fd);
    return NULL;
  }

  close(fd);
  return PyString_FromString (((struct ethtool_drvinfo *)buf)->driver);
}

static struct PyMethodDef PyEthModuleMethods[] = {
    	{ "get_module",
          (PyCFunction) get_module, METH_VARARGS, NULL },
	{ NULL, NULL, 0, NULL }	
};

void initethtool(void) {
  PyObject *m, *d, *o;
  PyMethodDef *def;
  
  m = Py_InitModule("ethtool", PyEthModuleMethods);
  d = PyModule_GetDict(m);
}
