import re

name_regex = re.compile( '^[0-9a-zA-Z\-_]+$' )  # possible to be using in a filesystem, must be filesystem safe, also don't allow chars that are used to delimit version and other info
filename_regex = re.compile( '^[0-9a-zA-Z\-_\.]+$' )  # same as name_regex, but include version stuff

USERNAME_LENGTH = 40

FILE_ARCH_CHOICES = ( ( 'x86_64', 'x86_64' ), ( 'i386', 'i386' ), ( 'arm64', 'ARM64' ), ( 'all', 'All' ) )  # these names follow the Debian arch names
DISTRO_CHOICES = ( ( 'debian', 'Debian' ), ( 'rhel', 'RHEL' ), ( 'sles', 'SLES' ), ( 'none', 'None' ) )  # there is no ubuntu, it shares the same version space as debian
MANAGER_TYPE_CHOICES = ( ( 'apt', 'APT' ), ( 'yum', 'YUM' ), ( 'json', 'JSON' ), ( 'docker', 'Docker' ), ( 'pypi', 'PyPi' ) )


# if these are changed (or any other field length), make sure to update the sqlite db in packrat-agent
MANAGER_TYPE_LENGTH = 6
FILE_TYPE_LENGTH = 20
FILE_ARCH_LENGTH = 6
DISTRO_LENGTH = 6
