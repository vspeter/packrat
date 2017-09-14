import os


class Resource( object ):  # This will take anything that has one (and only one) "_" in the file name to delinitate the package and version
  @classmethod
  def load( cls, file ):  # compare with packrat-agent/packratAgent/Json.py -> _splitFileName
    filename = os.path.basename( file.name )

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

    return cls( package, version )

  def __init__( self, package, version ):
    self.package = package
    self.arch = 'all'
    self.version = version
    self.type = 'rsc'
