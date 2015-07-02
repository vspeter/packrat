import os

from django.core.exceptions import ValidationError

class Resource( object ):
  @classmethod
  def load( cls, file ):
    ( filename, extension ) = os.path.splitext( os.path.basename( file.name ) )

    if extension != '.tar.gz':
      return None

    try:
      ( package, version ) = filename.split( '_' )
    except ValueError:
      raise ValidationError( 'Unrecognized Resource file name Format' )

    return cls( package, version )

  def __init__( self, package, version ):
    self.package = package
    self.arch = 'all'
    self.version = version
    self.type = 'rsc'
