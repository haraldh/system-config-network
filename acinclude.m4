dnl
dnl AC_PROG_RPM([ACTION-IF-FOUND [, ACTION-IF-NOT-FOUND])
dnl
AC_DEFUN(AC_PROG_RPM,
[dnl
dnl Check if the rpm program is available
dnl
	ac_rpm_bin=''
	AC_PATH_PROG(ac_rpm_bin, rpm)
	if	test -n "$ac_rpm_bin"; then
		ifelse([$1], , :, [$1])
	else    
		ifelse([$2], , :, [$2])       
   fi  
])

dnl
dnl AC_CHECK_RPM([PACKAGE [, MINIMAL-VERSION [ACTION-IF-FOUND [, ACTION-IF-NOT-FOUND ]]])
dnl
AC_DEFUN(AC_CHECK_RPM,
[dnl
	failed="true"
	package=$1
	vers=$2

	AC_PROG_RPM([], [ AC_MSG_ERROR( [no rpm system] ) ] ) 
	AC_MSG_CHECKING( [for rpm package $package] )

	version=$(rpm -q --queryformat '%{VERSION}' "$package" 2>/dev/null)
	release=$(rpm -q --queryformat '%{RELEASE}' "$package" 2>/dev/null)

	if test -n "$version" -a -n "$release"; then
		AC_MSG_RESULT( [found $version-$release] )
		if test -n "$vers"; then
			AC_MSG_CHECKING([checking, if version is newer or equal to $package-$vers])
			mversion="$vers"
			mrelease=$(echo $mversion|cut -d '-' -f 2)
			mversion=$(echo $mversion|cut -d '-' -f 1)
			mmajor=$(echo $mversion|cut -d '.' -f 1)
			mminor=$(echo $mversion|cut -d '.' -f 2)
			msubminor=$(echo $mversion|cut -d '.' -f 3)
			major=$(echo $version|cut -d '.' -f 1)
			minor=$(echo $version|cut -d '.' -f 2)
			subminor=$(echo $version|cut -d '.' -f 3)

			test -z "$major" && major=0
			test -z "$minor" && minor=0
			test -z "$subminor" && subminor=0
			test -z "$release" && release=0

			test -z "$mmajor" && mmajor=0
			test -z "$mminor" && mminor=0
			test -z "$msubminor" && msubminor=0
			test -z "$mrelease" && mrelease=0

			if test "$mmajor" = "$major"; then
				if test "$mminor" = "$minor"; then
					if test "$msubminor" = "$subminor"; then
						if test "$mrelease" -le "$release"; then
							failed="false"
						else
							failed="true"
						fi
					elif test "$msubminor" -le "$subminor"; then
						failed="false"
					fi
				elif test "$mminor" -le "$minor"; then
					failed="false"
				fi
			elif test "$mmajor" -le "$major"; then
				failed="false"
			fi

			if test "$failed" != "true"; then
				AC_MSG_RESULT( [yes] )
			else
				AC_MSG_RESULT( [failed] )
			fi
		fi
	else
		AC_MSG_RESULT( [failed] )
	fi

	if test "$failed" != "true"; then
		ifelse([$3], , :, [$3])
	else    
		ifelse([$4], , :, [$4])
   fi  
])
