import magic
import os

from django.core.exceptions import ValidationError

class Deb( object ):
  @classmethod
  def load( cls, file ):
    ( filename, extension ) = os.path.splitext( os.path.basename( file.name ) )

    if extension != '.deb':
      return None

    m = magic.open( 0 )
    m.load()
    try:
      magic_type = m.descriptor( os.dup( file.file.fileno() ) )
    except Exception as e:
      raise Exception( 'Error getting magic: %s' % e)

    if magic_type != 'Debian binary package (format 2.0)':
      return None

    # TODO: get the package, version, arch from the changelog
    try:
      ( package, version, arch ) = filename.split( '_' )
    except ValueError:
      raise ValidationError( 'Unrecognized deb file name Format' )

    if arch == 'amd64':
      arch = 'x86_64'
    elif arch not in ( 'i386', 'all' ):
      raise ValidationError( 'Unrecognized deb Arch' )

    return cls( package, arch, version )

  def __init__( self, package, arch, version ):
    self.package = package
    self.arch = arch
    self.version = version
    self.type = 'deb'
