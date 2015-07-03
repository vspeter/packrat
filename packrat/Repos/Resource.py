import os

class Resource( object ): # This will take anything that has one (and only one) "_" in the file name to delinitate the package and version
  @classmethod
  def load( cls, file ):
    ( filename, extension ) = os.path.splitext( os.path.basename( file.name ) )

    try:
      ( package, version ) = filename.split( '_' )
    except ValueError:
      return None

    return cls( package, version )

  def __init__( self, package, version ):
    self.package = package
    self.arch = 'all'
    self.version = version
    self.type = 'rsc'
