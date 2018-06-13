import magic
import os
import re

from gzip import GzipFile
from tarfile import TarFile
from django.apps import apps

PACKAGE_INFO_REGISTRY = []


def infoDetect( target_file ):
  magic_helper = magic.open( 0 )
  magic_helper.load()

  for info in PACKAGE_INFO_REGISTRY:
    result = info.detect( target_file, magic_helper )
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
    DistroVersion = apps.get_model( 'Repos.DistroVersion' )

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
  def detect( cls, target_file, magic_helper ):
    ( filename, extension ) = os.path.splitext( os.path.basename( target_file.name ) )
    if extension != '.deb':
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

    try:
      magic_type = magic_helper.descriptor( os.dup( target_file.file.fileno() ) )
    except Exception as e:
      raise Exception( 'Error getting magic: %s' % e)

    if magic_type != b'Debian binary package (format 2.0)':
      return None

    return cls( filename, package, arch, version, 'deb' )

PACKAGE_INFO_REGISTRY.append( Deb )


class RPM( PackageInfo ):
  @classmethod
  def detect( cls, target_file, magic_helper ):
    ( filename, extension ) = os.path.splitext( os.path.basename( target_file.name ) )

    if extension != '.rpm':
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

    try:
      magic_type = magic_helper.descriptor( os.dup( target_file.file.fileno() ) )
    except Exception as e:
      raise Exception( 'Error getting magic: %s' % e)

    if magic_type not in ( b'RPM v3.0 bin noarch', b'RPM v3.0 bin i386/x86_64' ):
      return None

    return cls( filename, package, arch, '%s-%s' % ( version, release ), 'rpm' )

PACKAGE_INFO_REGISTRY.append( RPM )


class Docker( PackageInfo ):
  @classmethod
  def detect( cls, target_file, magic_helper ):
    ( filename, extension ) = os.path.splitext( os.path.basename( target_file.name ) )

    if extension != '.tar':
      return None

    # TODO: get the info from  the manifest
    try:
      ( package, version ) = filename.split( '_' )
    except ValueError:
      raise ValueError( 'Unrecognized Docker Container file name Format' )

    try:
      magic_type = magic_helper.descriptor( os.dup( target_file.file.fileno() ) )
    except Exception as e:
      raise Exception( 'Error getting magic: %s' % e)

    if not magic_type.startswith( b'POSIX tar archive' ):
      return None

    tarfile = TarFile( fileobj=target_file.file, mode='r' )

    info = tarfile.extractfile( 'manifest.json' )
    tarfile.close()
    target_file.file.seek( 0 )

    if info is None:
      return None

    return cls( filename, package, 'all', version, 'docker' )


PACKAGE_INFO_REGISTRY.append( Docker )


class Python( PackageInfo ):
  @classmethod
  def detect( cls, target_file, magic_helper ):
    filename = os.path.basename( target_file.name )

    if not filename.endswith( '.tar.gz'):
      return None

    ( filename, extension ) = os.path.splitext( filename )  # one for .gz
    ( filename, extension ) = os.path.splitext( filename )  # second for .tar

    try:
      ( package, version ) = filename.split( '-' )  # ie: cinp-0.9.2.tar.gz
    except ValueError:
      raise ValueError( 'Unrecognized Python Container file name Format' )

    try:
      magic_type = magic_helper.descriptor( os.dup( target_file.file.fileno() ) )
    except Exception as e:
      raise Exception( 'Error getting magic: %s' % e)

    if not magic_type.startswith( b'gzip compressed data' ):
      return None

    gzfile = GzipFile( fileobj=target_file.file, mode='r' )
    tarfile = TarFile( fileobj=gzfile, mode='r' )

    info = tarfile.extractfile( '{0}/PKG-INFO'.format( filename ) )
    tarfile.close()
    gzfile.close()
    target_file.file.seek( 0 )

    if info is None:
      return None

    return cls( filename, package, 'all', version, 'python' )

PACKAGE_INFO_REGISTRY.append( Python )


# Resource must be last, being it will catch anything with a '_' in the filename
class Resource( PackageInfo ):  # This will take *anything* that has one (and only one) "_" in the file name to delinitate the package and version,  we are not doing any type checking
  @classmethod
  def detect( cls, target_file, magic_helper ):  # compare with packrat-agent/packratAgent/Json.py -> _splitFileName
    filename = os.path.basename( target_file.name )

    if filename.endswith( ( '.tar.gz', '.tar.bz2', '.tar.xz', 'img.gz', 'img.bz2', 'img.xz' ) ):
      ( filename, _, _ ) = filename.rsplit( '.', 2 )
    else:
      try:
        ( filename, _ ) = filename.rsplit( '.', 1 )
      except ValueError:
        pass

    try:
      ( package, version ) = filename.split( '_' )
    except ValueError:
      return None

    return cls( filename, package, 'all', version, 'rsc' )

PACKAGE_INFO_REGISTRY.append( Resource )
