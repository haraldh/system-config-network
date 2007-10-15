#
# log.py - debugging log service
#
# Alexander Larsson <alexl@redhat.com>
# Matt Wilson <msw@redhat.com>
#
# Copyright 2002 Red Hat, Inc.
#
# This software may be freely redistributed under the terms of the GNU
# library public license.
#
# You should have received a copy of the GNU Library Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

# FIXME: use pythons logging handlers
# FIXME: [183066] DeprecationWarning: rhpl.log is deprecated
import sys
import syslog

class LogFile:
    def __init__ (self, progname, level = 0, filename = None):
        if filename == None:
            import syslog
            self.syslog = syslog.openlog(progname, syslog.LOG_PID)

            self.handler = self.syslog_handler
            self.logFile = sys.stderr
        else:
            self.handler = self.file_handler
            self.open(filename)

        self.level = level

    def close (self):
        try:
            self.logFile.close ()
        except:
            pass

    def open (self, file = None):
        if type(file) == type("hello"):
            try:
                self.logFile = open(file, "w")
            except:
                self.logFile = sys.stderr
        elif file:
            self.logFile = file
        else:
            self.logFile = sys.stderr

    def getFile (self):
        return self.logFile.fileno ()

    def __call__(self, format, *args):
        self.handler (format % args)

    def file_handler (self, string, level = 0):
        import time
        self.logFile.write ("[%d] %s: %s\n" % (level, time.ctime(), string))

    def syslog_handler (self, string, level = syslog.LOG_INFO):
        import syslog
        syslog.syslog(level, string)

    def set_loglevel(self, level):
        self.level = level

    def log(self, level, message):
        if self.level >= level:
            self.handler(message, level = level)

    def ladd(self, level, file, message):
        if self.level >= level:
            self.handler("++ %s \t%s" % (file, message))

    def ldel(self, level, file, message):
        if self.level >= level:
            self.handler("-- %s \t%s" % (file, message))

    def lch(self, level, file, message):
        if self.level >= level:
            self.handler("-+ %s \t%s" % (file, message))

