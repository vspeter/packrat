import magic
import os

from django.core.exceptions import ValidationError

class Pdisk( object ):
  @classmethod
  def load( cls, file ):
    ( filename, extension ) = os.path.splitext( os.path.basename( file.name ) )

    if extension != '.tar.gz':
      return None

    m = magic.open( 0 )
    m.load()
    try:
      magic_type = m.descriptor( os.dup( file.file.fileno() ) )
    except Exception as e:
      raise Exception( 'Error getting magic: %s' % e)

    if magic_type != 'gzip compressed data':
      return None

    # TODO: get the package and version from manafest, also verifying that it is a Plato Disk tar.gz
    try:
      ( package, version ) = filename.split( '_' )
    except ValueError:
      raise ValidationError( 'Unrecognized Plato Disk file name Format' )

    return cls( package, version )

  def __init__( self, package, version ):
    self.package = package
    self.arch = 'all'
    self.version = version
    self.type = 'pdisk'
