# Interface to crypt and md5_crypt
# Copyright (C) 1996,2000 Red Hat, Inc
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import string
import crypt
import rand

def _mk_crypt_salt():
    ret = ['','']
    for i in [0,1]:
        j = rand.choice(range(0,64))
        if (j < 26):
            ret[i] = string.lowercase[j]
        elif (j < 52):
            ret[i] = string.uppercase[j-26]
        elif (j < 62):
            ret[i] = string.digits[j-52]
        elif (j == 63):
            ret[i] = '.'
        else:
            ret[i] = '/'
    return ret[0]+ret[1]

def crypt_passwd(password):
    return crypt.crypt(password, _mk_crypt_salt())

def md5_passwd(password):
    # FIXME
    return 'this needs to be fixed'
