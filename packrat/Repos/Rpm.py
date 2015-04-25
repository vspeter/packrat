import magic
import os
import re

from django.core.exceptions import ValidationError

class Rpm( object ):
  @classmethod
  def load( cls, file ):
    ( _, extension ) = os.path.splitext( os.path.basename( file.name ) )

    if extension != '.rpm':
      return None

    m = magic.open( 0 )
    m.load()
    try:
      magic_type = m.descriptor( os.dup( file.file.fileno() ) )
    except Exception as e:
      raise Exception( 'Error getting magic: %s' % e)

    if magic_type not in ( 'RPM v3.0 bin noarch', 'RPM v3.0 bin i386/x86_64' ):
      return None

    # TODO: get these from the rpm file
    try:
      ( package, version, release, arch ) = re.match( '(.+)-([^-]+)-([^-]+)\.(\w+)', file.name ).groups()
    except ValueError:
      raise ValidationError( 'Unrecognized rpm file name Format' )

    if arch == 'noarch':
      arch = 'all'
    elif arch not in ( 'i386', 'x86_64' ):
      raise ValidationError( 'Unrecognized rpm Arch' )

    return cls( package, arch, '%s-%s' % ( version, release ) )

  def __init__( self, package, arch, version ):
    self.package = package
    self.arch = arch
    self.version = version
    self.type = 'rpm'
