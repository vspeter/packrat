import magic
import os
import re

from gzip import GzipFile
from tarfile import TarFile

from packrat.Attrib.models import DistroVersion
from packrat.fields import name_regex

PACKAGE_INFO_REGISTRY = []
TYPE_INFO_MAP = {}


def infoDetect( target_file, type ):
  magic_helper = magic.open( 0 )
  magic_helper.load()

  try:
    magic_type = magic_helper.descriptor( os.dup( target_file.file.fileno() ) )
  except Exception as e:
    raise Exception( 'Error getting magic: "{0}"'.format( e ) )

  if type is not None:
    if type in TYPE_INFO_MAP:
      return TYPE_INFO_MAP[ type ].detect( target_file, magic_type )

    else:
      return Other.detect( target_file, magic_type, type )

  for info in PACKAGE_INFO_REGISTRY:
    result = info.detect( target_file, magic_type )
    if result is not None:
      return result

  return None


class PackageInfo():
  def __init__( self, filename, package, arch, version, type ):
    super().__init__()
    self.filename = filename
    self.package = package
    self.arch = arch
    self.version = version
    self.type = type

  @property
  def distroversion_list( self ):
    full_list = []
    match_list = []
    for tmp in DistroVersion.objects.filter( file_type=self.type ):
      for name in tmp.release_names.split( '\t' ):
        full_list.append( name  )
        if name in self.version:
          match_list.append( tmp.pk )

    if match_list:
      return match_list
    else:
      return full_list


class Deb( PackageInfo ):
  @classmethod
  def detect( cls, target_file, magic_type ):
    ( filename, extension ) = os.path.splitext( os.path.basename( target_file.name ) )
    if extension != '.deb':
      return None

    if magic_type != 'Debian binary package (format 2.0)':
      return None

    # TODO: get the package, version, arch from the changelog
    try:
      ( package, version, arch ) = filename.split( '_' )
    except ValueError:
      raise ValueError( 'Unrecognized deb file name Format' )

    if arch == 'amd64':
      arch = 'x86_64'
    elif arch not in ( 'i386', 'all' ):
      raise ValueError( 'Unrecognized deb Arch' )

    return cls( filename, package, arch, version, 'deb' )


PACKAGE_INFO_REGISTRY.append( Deb )
TYPE_INFO_MAP[ 'deb' ] = Deb


class RPM( PackageInfo ):
  @classmethod
  def detect( cls, target_file, magic_type ):
    ( filename, extension ) = os.path.splitext( os.path.basename( target_file.name ) )

    if extension != '.rpm':
      return None

    if magic_type not in ( 'RPM v3.0 bin noarch', 'RPM v3.0 bin i386/x86_64' ):
      return None

    # <name>-<version>-<release>.<architecture>.rpm for binaries.
    # TODO: get these from the rpm file
    try:
      ( package, version, release, arch ) = re.match( '(.+)-([^-]+)-([^-]+)\.(\w+)', filename ).groups()
    except ValueError:
      raise ValueError( 'Unrecognized rpm file name Format' )

    if arch == 'src':
      raise ValueError( 'Source rpms are not supported' )

    if arch == 'noarch':
      arch = 'all'
    elif arch not in ( 'i386', 'x86_64' ):
      raise ValueError( 'Unrecognized rpm Arch' )

    return cls( filename, package, arch, '{0}-{1}'.format( version, release ), 'rpm' )


PACKAGE_INFO_REGISTRY.append( RPM )
TYPE_INFO_MAP[ 'rpm' ] = RPM


class Docker( PackageInfo ):
  @classmethod
  def detect( cls, target_file, magic_type ):
    ( filename, extension ) = os.path.splitext( os.path.basename( target_file.name ) )

    if extension != '.tar':
      return None

    if not magic_type.startswith( 'POSIX tar archive' ):
      return None

    # TODO: get the info from the manifest
    try:
      ( package, version ) = filename.split( '_' )
    except ValueError:
      raise ValueError( 'Unrecognized Docker Container file name Format' )

    tarfile = TarFile( fileobj=target_file.file, mode='r' )

    info = tarfile.extractfile( 'manifest.json' )
    tarfile.close()
    target_file.file.seek( 0 )

    if info is None:
      return None

    return cls( filename, package, 'all', version, 'docker' )


PACKAGE_INFO_REGISTRY.append( Docker )
TYPE_INFO_MAP[ 'docker' ] = Docker


class Python( PackageInfo ):
  @classmethod
  def detect( cls, target_file, magic_type ):
    filename = os.path.basename( target_file.name )

    if not filename.endswith( '.tar.gz'):
      return None

    if not magic_type.startswith( 'gzip compressed data' ):
      return None

    ( filename, _, _ ) = filename.rsplit( '.', 2 )

    try:
      ( package, version ) = filename.rsplit( '-', 1 )  # ie: cinp-0.9.2.tar.gz
    except ValueError:
      return None

    gzfile = GzipFile( fileobj=target_file.file, mode='r' )
    tarfile = TarFile( fileobj=gzfile, mode='r' )

    try:
      info = tarfile.extractfile( '{0}/PKG-INFO'.format( filename ) )
    except KeyError:
      return None

    tarfile.close()
    gzfile.close()
    target_file.file.seek( 0 )

    if info is None:
      return None

    return cls( filename, package, 'all', version, 'python' )


PACKAGE_INFO_REGISTRY.append( Python )
TYPE_INFO_MAP[ 'python' ] = Python


class OVA( PackageInfo ):
  @classmethod
  def detect( cls, target_file, magic_type ):
    ( filename, extension ) = os.path.splitext( os.path.basename( target_file.name ) )

    if extension != '.ova':
      return None

    if not magic_type.startswith( 'POSIX tar archive' ):
      return None

    # TODO: get the info from the ovf
    try:
      ( package, version ) = filename.split( '_' )
    except ValueError:
      raise ValueError( 'Unrecognized OVA file name Format' )

    return cls( filename, package, 'all', version, 'ova' )


PACKAGE_INFO_REGISTRY.append( OVA )
TYPE_INFO_MAP[ 'ova' ] = OVA


class Respkg( PackageInfo ):
  @classmethod
  def detect( cls, target_file, magic_type ):
    ( filename, extension ) = os.path.splitext( os.path.basename( target_file.name ) )

    if extension != '.respkg':
      return None

    if not magic_type.startswith( 'gzip compressed data' ):
      return None

    # TODO: get the info from the metadata
    try:
      ( package, version ) = filename.split( '_' )
    except ValueError:
      raise ValueError( 'Unrecognized OVA file name Format' )

    return cls( filename, package, 'all', version, 'respkg' )


PACKAGE_INFO_REGISTRY.append( Respkg )
TYPE_INFO_MAP[ 'respkg' ] = Respkg


COMPRESED_TYPE_LIST = ( 'tar', 'img' )
OTHER_TYPE_LIST = ( 'tar', 'img', 'appimage' )


# Must be last, being it will catch anything with a '_' in the filename
class Other( PackageInfo ):  # This will take *anything* that has one (and only one) "_" in the file name to delinitate the package and version,  we are not doing any type checking
  @classmethod
  def detect( cls, target_file, magic_helper, requested_type=None ):  # compare with packrat-agent/packratAgent/JsonManager.py -> _splitFileName
    filename = os.path.basename( target_file.name )

    parts = filename.split( '.' )

    if parts[ -2 ] in COMPRESED_TYPE_LIST:  # to deal with things like '.tar.??', 'img.??'
      ( filename, _, _ ) = filename.rsplit( '.', 2 )
      type = parts[ -2 ]

    else:
      ( filename, _ ) = filename.rsplit( '.', 1 )
      type = parts[ -1 ]

    try:
      ( package, version ) = filename.split( '_' )
    except ValueError:
      return None

    type = type.lower()

    if requested_type is not None:
      if not name_regex.match( requested_type ):
        raise ValueError( 'Invalid type' )

      type = requested_type

    elif type not in OTHER_TYPE_LIST:
      type = 'resource'

    return cls( filename, package, 'all', version, type )


PACKAGE_INFO_REGISTRY.append( Other )
for type in OTHER_TYPE_LIST:
  TYPE_INFO_MAP[ type ] = Other

TYPE_INFO_MAP[ 'resource' ] = Other
