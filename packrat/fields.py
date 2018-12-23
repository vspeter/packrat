import re

name_regex = re.compile( '^[0-9a-zA-Z\-_]+$' )  # possible to be using in a filesystem, must be filesystem safe, also don't allow chars that are used to delimit version and other info

USERNAME_LENGTH = 40

FILE_ARCH_CHOICES = ( ( 'x86_64', 'x86_64' ), ( 'i386', 'i386' ), ( 'all', 'All' ) )
FILE_TYPE_CHOICES = ( ( 'deb', 'deb' ), ( 'rpm', 'RPM' ), ( 'rsc', 'Resource' ), ( 'ova', 'OVA' ), ( 'docker', 'Docker' ), ( 'python', 'Python' ) )
DISTRO_CHOICES = ( ( 'debian', 'Debian' ), ( 'centos', 'Centos' ), ( 'rhel', 'RHEL' ), ( 'sles', 'SLES' ), ( 'core', 'CoreOS' ), ( 'none', 'None' ) )  # there is no ubuntu, it shares the same version space as debian
MANAGER_TYPE_CHOICES = ( ( 'apt', 'APT' ), ( 'yum', 'YUM' ), ( 'yast', 'YaST' ), ( 'json', 'JSON' ), ( 'docker', 'Docker' ), ( 'pypi', 'PyPi' ) )


# if these are changed (or any other field length), make sure to update the sqlite db in packrat-agent
MANAGER_TYPE_LENGTH = 6
FILE_TYPE_LENGTH = 6
FILE_ARCH_LENGTH = 6
DISTRO_LENGTH = 6
