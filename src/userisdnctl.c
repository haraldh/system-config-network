#include <alloca.h>
#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include "isdn.h"
#include "isdnif.h"

typedef union {
  isdn_net_ioctl_phone_6 phone_6;
  isdn_net_ioctl_phone_5 phone_5;
} isdn_net_ioctl_phone;

static int data_version;

#define FOUND_FALSE -1
#define NOT_FOUND 0
#define FOUND_TRUE 1

static void
usage(void) {
  fprintf(stderr, "usage: userisdnctl <hangup|dial|status> <interface>\n");
  exit(1);
}

static size_t
testSafe(char *ifaceConfig) {
  struct stat sb;

  /* These shouldn't be symbolic links -- anal, but that's fine w/ mkj. */
  if (lstat(ifaceConfig, &sb)) {
    fprintf(stderr, "failed to stat %s: %s\n", ifaceConfig, 
	    strerror(errno));
    exit(1);
  }

  /* Safety/sanity checks. */
  if (!S_ISREG(sb.st_mode)) {
    fprintf(stderr, "%s is not a normal file\n", ifaceConfig);
    exit(1);
  }
  
  if (sb.st_uid) {
    fprintf(stderr, "%s should be owned by root\n", ifaceConfig);
    exit(1);
  }
  
  if (sb.st_mode & S_IWOTH) {
    fprintf(stderr, "%s should not be world writeable\n", ifaceConfig);
    exit(1);
  }
  
  return sb.st_size;
}

static int
userCtl(char *file) {
  char *buf;
  char *contents = NULL;
  char *chptr = NULL;
  char *next = NULL;
  int fd = -1, retval = NOT_FOUND;
  size_t size = 0;
  
  size = testSafe(file);
  
  buf = contents = malloc(size + 2);
  
  if ((fd = open(file, O_RDONLY)) == -1) {
    fprintf(stderr, "failed to open %s: %s\n", file, strerror(errno));
    exit(1);
  }
  
  if (read(fd, contents, size) != size) {
    perror("error reading device configuration");
    exit(1);
  }
  close(fd);
  
  contents[size] = '\n';
  contents[size + 1] = '\0';
  
  /* Each pass parses a single line (until an answer is found),  The contents
     pointer itself points to the beginning of the current line. */
  while (*contents) {
    chptr = contents;
    while (*chptr != '\n') chptr++;
    next = chptr + 1;
    while (chptr >= contents && isspace(*chptr)) chptr--;
    *(++chptr) = '\0';
    
    if (!strncmp(contents, "USERCTL=", 8)) {
      contents += 8;
      if ((contents[0] == '"' &&
	   contents[strlen(contents) - 1] == '"') ||
	  (contents[0] == '\'' &&
	   contents[strlen(contents) - 1] == '\''))
	{
	  contents++;
	  contents[strlen(contents) - 1] = '\0';
	}
      
      if (!strcmp(contents, "yes") || !strcmp(contents, "true")) 
	retval = FOUND_TRUE;
      else 
	retval = FOUND_FALSE;
      
      break;
    }
    
    contents = next;
  }
  
  free(buf);
  
  return retval;
}

static int
set_isdn_net_ioctl_phone(isdn_net_ioctl_phone *ph, char *name,
			 char *phone, int outflag) {
  switch(data_version) {
  case 0x04:
  case 0x05:
    if (strlen(phone) > 19) {
      fprintf(stderr, "phone-number must not exceed %d characters\n", 19);
      return -1;
    }
    /*
     * null termination happens automatically because
     * we clear the entire struct first
     */
    strncpy(ph->phone_5.name, name, sizeof(ph->phone_5.name)-1);
    strncpy(ph->phone_5.phone, phone, sizeof(ph->phone_5.phone)-1);
    ph->phone_5.outgoing = outflag;
    break;
  case 0x06:
    if (strlen(phone) > 31) {
      fprintf(stderr, "phone-number must not exceed %d characters\n", 31);
      return -1;
    }
    strncpy(ph->phone_6.name, name, sizeof(ph->phone_6.name)-1);
    strncpy(ph->phone_6.phone, phone, sizeof(ph->phone_6.phone)-1);
    ph->phone_6.outgoing = outflag;
  }
  return 0;
}


static int
status(char *name) {
  isdn_net_ioctl_phone phone;
  int rc;
  int isdninfo = open("/dev/isdninfo", O_RDONLY);
  if (isdninfo < 0) {
    isdninfo = open("/dev/isdn/isdninfo", O_RDONLY);
    if (isdninfo < 0) {
      perror("Can't open /dev/isdninfo or /dev/isdn/isdninfo");
      exit(-1);
    }
  }

  data_version = ioctl(isdninfo, IIOCGETDVR, 0);
  if (data_version < 0) {
    fprintf(stderr, "Could not get version of kernel ioctl structs!\n");
    fprintf(stderr, "Make sure that you are using the correct version.\n");
    fprintf(stderr, "(Try recompiling isdnctrl).\n");
    close(isdninfo);
    exit(-1);
  }
  data_version = (data_version >> 8) & 0xff;
  
  if (data_version < 4) {
    fprintf(stderr, "Kernel-version too old, terminating.\n");
    fprintf(stderr, "UPDATE YOUR KERNEL.\n");
    close(isdninfo);
    exit(-1);
  }
  if (data_version > 6) {
    fprintf(stderr, "Kernel-version newer than isdnctrl-version, terminating.\n");
    fprintf(stderr, "GET A NEW VERSION OF isdn4k-utils.\n");
    close(isdninfo);
    exit(-1);
  }

  memset(&phone, 0, sizeof phone);
  set_isdn_net_ioctl_phone(&phone, name, "", 0);

  rc = ioctl(isdninfo, IIOCNETGPN, &phone);
  if (rc < 0) {
    if (errno == ENOTCONN) {
      printf("%s is not connected\n", name);
      close(isdninfo);
      return 1;
    }
    perror(name);
    close(isdninfo);
    return -1;
  }

  switch(data_version) {
  case 0x04:
  case 0x05:
    printf("%s connected %s %s\n",
	   name, phone.phone_5.outgoing ? "to" : "from",
	   phone.phone_5.phone);
    break;
  case 0x06:
    printf("%s connected %s %s\n",
	   name, phone.phone_6.outgoing ? "to" : "from",
	   phone.phone_6.phone);
  }

  close(isdninfo);
  return 0;
}

static int
hangup(int fd, char *name) {
  int result;

  if ((result = ioctl(fd, IIOCNETHUP, name)) < 0) {
    perror(name);
    return -1;
  }
  if (result)
    printf("%s not connected\n", name);
  else
    printf("%s hung up\n", name);

  return 0;
}

static int
dial(int fd, char *name) {
  int result;

  if ((result = ioctl(fd, IIOCNETDIL, name)) < 0) {
    perror(name);
    return -1;
  }
  printf("Dialing of %s triggered\n", name);
  return 0;
}

static int
isdnctrl(char *name, char *opt) {
  int ret = 0;
  int fd;

  fd = open("/dev/isdn/isdnctrl", O_RDWR);
  if (fd < 0)
    fd = open("/dev/isdnctrl", O_RDWR);
  if (fd < 0) {
    perror("Can't open /dev/isdnctrl or /dev/isdn/isdnctrl");
    exit(-1);
  }

  if (!strcmp(opt, "dial")) {
    ret = dial(fd, name);
  } else if (!strcmp(opt, "hangup")) {
    ret = hangup(fd, name);
  } else if (!strcmp(opt, "status")) {
    ret = status(name);
  }

  close(fd);
  return ret;
}

int
main(int argc, char ** argv) {
  char * ifaceConfig;
  char * chptr;
  char * interface;
  char tmp;
  char *opt = NULL;
  int ret = 0;

  if (argc != 3) usage();

  if (!strcmp(argv[1], "hangup")) {
    opt = "hangup";
  } else if (!strcmp(argv[1], "dial")) {
    opt = "dial";
  } else if  (!strcmp(argv[1], "status")) {
    opt = "status";
  } else {
    usage();
  }
  
  if (chdir("/etc/sysconfig/network-scripts")) {
    fprintf(stderr, "error switching to /etc/sysconfig/network-scripts: "
	    "%s\n", strerror(errno));
    exit(1);
  }

  /* force the interface configuration to be in the current directory */
  interface = chptr = ifaceConfig = argv[2];
  while (*chptr) {
    if (*chptr == '/')
      ifaceConfig = chptr + 1;
    chptr++;
  }

  /* automatically prepend "ifcfg-" if it is not specified */
  if (strncmp(ifaceConfig, "ifcfg-", 6)) {
    char *temp;
    
    temp = (char *) alloca(strlen(ifaceConfig) + 7);
    strcpy(temp, "ifcfg-");
    /* strcat is safe because we got the length from strlen */
    strcat(temp, ifaceConfig);
    ifaceConfig = temp;
  }
    
  if(getuid() != 0)
    switch (userCtl(ifaceConfig)) {
      char *dash;
      
    case NOT_FOUND:
      /* a `-' will be found at least in "ifcfg-" */
      dash = strrchr(ifaceConfig, '-');
      if (*(dash-1) != 'g') {
	/* This was a clone configuration; ask the parent config */
	tmp = *dash;
	*dash = '\0';
	if (userCtl(ifaceConfig) == FOUND_TRUE) {
	  /* exit the switch; users are allowed to control */
	  *dash = tmp;
	  break;
	}
	*dash = tmp;
      }
      /* else fall through */
    case FOUND_FALSE:
      fprintf(stderr,
	      "Users are not allowed to control this interface.\n");
      exit(1);
      break;
    }

  ret = isdnctrl(interface, opt);

  exit(ret);
}
