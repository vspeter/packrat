import magic
import os
import re

from django.apps import apps

PACKAGE_INFO_REGISTRY = []


def infoDetect( filename ):
  for info in PACKAGE_INFO_REGISTRY:
    result = info.detect( filename )
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

  def validate( self, file ):
    pass


class Deb( PackageInfo ):
  @classmethod
  def detect( cls, filename ):
    ( filename, extension ) = os.path.splitext( os.path.basename( filename ) )
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

    return cls( filename, package, arch, version, 'deb' )

  def validate( self, file ):
    m = magic.open( 0 )
    m.load()
    try:
      magic_type = m.descriptor( os.dup( file.file.fileno() ) )
    except Exception as e:
      raise Exception( 'Error getting magic: %s' % e)

    if magic_type != 'Debian binary package (format 2.0)':
      raise ValueError( 'Invalid Debian Package' )

PACKAGE_INFO_REGISTRY.append( Deb )


class RPM( PackageInfo ):
  @classmethod
  def detect( cls, filename ):
    ( filename, extension ) = os.path.splitext( os.path.basename( filename ) )

    if extension != '.rpm':
      return None

    # TODO: get these from the rpm file
    try:
      ( package, version, release, arch ) = re.match( '(.+)-([^-]+)-([^-]+)\.(\w+)', filename ).groups()
    except ValueError:
      raise ValueError( 'Unrecognized rpm file name Format' )

    if arch == 'noarch':
      arch = 'all'
    elif arch not in ( 'i386', 'x86_64' ):
      raise ValueError( 'Unrecognized rpm Arch' )

    return cls( filename, package, arch, '%s-%s' % ( version, release ), 'rpm' )

  def validate( self, file ):
    m = magic.open( 0 )
    m.load()
    try:
      magic_type = m.descriptor( os.dup( file.file.fileno() ) )
    except Exception as e:
      raise Exception( 'Error getting magic: %s' % e)

    if magic_type not in ( 'RPM v3.0 bin noarch', 'RPM v3.0 bin i386/x86_64' ):
      raise ValueError( 'Not Valid RPM type' )

PACKAGE_INFO_REGISTRY.append( RPM )


# Resource must be last, being it will catch anything with a '_' in the filename
class Resource( PackageInfo ):  # This will take *anything* that has one (and only one) "_" in the file name to delinitate the package and version,  we are not doing any type checking
  @classmethod
  def detect( cls, filename ):  # compare with packrat-agent/packratAgent/Json.py -> _splitFileName
    filename = os.path.basename( filename )

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
