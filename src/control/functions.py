## Copyright (C) 2002 Red Hat, Inc.
## Copyright (C) 2002 Than Ngo <than@redhat.com>

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

PROGNAME = 'switchmail'
SWITCHMAILDIR = '/usr/share/switchmail/'
VERSION = '0.1.0'
GLADEPATH = ''

import re
import traceback
import sys
import os
import os.path
import shutil

true = (1==1)
false = not true

SENDMAIL =  0 
POSTFIX = 1
EXIM =  2

def switch(i):
    print i, 'mta is switched'

def detect():
    return ('Sendmail', 'Postfix', 'Exim')
