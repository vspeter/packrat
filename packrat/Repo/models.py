import select
import errno
import time
from datetime import datetime, timezone

from django.core.exceptions import ValidationError
from django.db import models, connection

from cinp.orm_django import DjangoCInP as CInP
from packrat.fields import name_regex

__doc__ = """
Packrat Class Relationships

From the Mirror prespective::

               +--------+
               | Mirror |
               +--------+
                 |    |
 +----------------+  +----------------+
 |     Repo 1     |  |      Repo N    |
 +----------------+  +----------------+
 | List of        |  | List of        |
 | ReleaseTypes   |  | ReleaseTypes   |
 |                |  |                |
 | List of        |  | List of        |
 | DistroVersions |  | DistroVersions |
 +----------------+  +----------------+
         |                    |
 +----------------+  +----------------+
 | View of        |  | View of        |
 | PackageFiles as|  | PackageFiles as|
 | Filterd by the |  | Filterd by the |
 | Release/Distro |  | Release/Distro |
 | Constraints of |  | Constraints of |
 | the repo       |  | the repo       |
 +----------------+  +----------------+


From the Package perspective::

              +---------+
              | Package |
              +---------+
                |      |
  +---------------+  +---------------+
  | PackageFile 1 |  | PackageFile 2 |
  +---------------+  +---------------+
  | Verion 1      |  | Version 2     |
  | DistroVersion |  | DistroVersion |
  | Arch / Type   |  | Arch / Type   |
  |               |  |               |
  | List of       |  | List of       |
  | ReleaseTypes  |  | ReleaseTypes  |
  | through       |  | through       |
  | PackageFile-  |  | PackageFile-  |
  | ReleaseType   |  | ReleaseType   |
  +---------------+  +---------------+

"""

"""
TODO:



snapshots:
  snapshot of curent tags
  ability to tweek tags for the snapshot

"""



cinp = CInP( 'Repo', '2.0' )


@cinp.model( not_allowed_verb_list=( 'CREATE', 'DELETE', 'UPDATE' ) )
class Tag( models.Model ):
  """
  Tags are ...

  - name: name of the release, ie: 'prod'
  - description: short description of the release type, ie: 'Production'
  - change_control_required: if True, inorder to be promoted to this Release
    a Change Control ID is required and must check out before being allowed to
    promote to this level.
  """
  name = models.CharField( max_length=10, primary_key=True )
  required_list = models.ManyToManyField( 'self', related_name='+' )
  change_control_required = models.BooleanField( default=False )
  created = models.DateTimeField( editable=False, auto_now_add=True )
  updated = models.DateTimeField( editable=False, auto_now=True )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    todo = [ self ]
    visited = []
    while todo:
      current = todo.pop( 0 )
      if current in visited:
        continue

      visited.append( current )
      todo += current.required_list
      if self in todo:
        errors[ 'required' ] = 'required tags recursivly refer back to this tag'
        break

    if not name_regex.match( self.name ):
      errors[ 'name' ] = 'Invalid'

    if errors:
      raise ValidationError( errors )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'Tag "%s"(%s)' % ( self.description, self.name )


@cinp.model( not_allowed_verb_list=( 'CREATE', 'DELETE', 'UPDATE' ), constant_set_map={ 'distro': DISTRO_CHOICES, 'file_type': FILE_TYPE_CHOICES } )
class DistroVersion( models.Model ):
  """
  This is a type of Distro, ie Centos 6 or Ubuntu 14.04(Trusty)

  - name: name of the distro version, ie: 'precise', 'sels12'
  - distro: the distro family this version belongs to, ie 'debian'
  - version: version identifier, ie: 'precise', '12'
  - file_type: the type of file expected for this DistroVersion, ie: 'deb', 'rpm'
  - release_names: a tab delemited list of strings that apear in the file name
    to help packrat auto detect which DistroVersion a PackageFile belongs to, ie:
    'xenial', 'rel6'
  """
  name = models.CharField( max_length=20, primary_key=True )
  distro = models.CharField( max_length=DISTRO_LENGTH, choices=DISTRO_CHOICES )  # TODO: convert into another model
  version = models.CharField( max_length=10, null=True, blank=True )
  file_type = models.CharField( max_length=FILE_TYPE_LENGTH, choices=FILE_TYPE_CHOICES )
  release_names = models.CharField( max_length=100, blank=True, help_text='tab delimited list of things like el5, trusty, something that is in filename that tells what version it belongs to' )
  created = models.DateTimeField( editable=False, auto_now_add=True )
  updated = models.DateTimeField( editable=False, auto_now=True )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if not name_regex.match( self.name ):
      errors[ 'name' ] = 'Invalid'

    if errors:
      raise ValidationError( errors )

  class Meta:
    unique_together = ( 'distro', 'version', 'file_type' )

  def __str__( self ):
    return 'Version "%s" of "%s"' % ( self.version, self.distro )


@cinp.model( not_allowed_verb_list=( 'CREATE', 'DELETE', 'UPDATE' ), constant_set_map={ 'manager_type': MANAGER_TYPE_CHOICES } )
class Repo( models.Model ):
  """
  This is a Collection of PackageFiles that meant certian requrements, ie:
  distro, repo manager, and release type. This is will authorize any mirrors
  including this Repo to get a listing of package files.

  NOTE: this dosen't prevent the remote server from downloading an individual
  file if it allready knows the url, this just controlls the list of files sent.

  - name: name of the repo, ie: 'prod-apt'
  - filesystem_dir: the name of the directory to put the the PackageFiles belonging
    to this repo into, ie: 'prod-apt'
  - distroversion_list: list of the distro versions this repos includes
  - manager_type: what repo manager to use for this repo, ie: 'apt'
  - description: short description of the Repo, ie: 'Production Apt'
  - tag_list: list of the tags that this repo includes
  - show_only_latest: if True to only expose the highest numberd versoin of each package,
  """
  name = models.CharField( max_length=50, primary_key=True )
  description = models.CharField( max_length=200 )
  filesystem_dir = models.CharField( max_length=50, unique=True )  # TODO: validate this, must be fs safe
  distroversion_list = models.ManyToManyField( DistroVersion )
  manager_type = models.CharField( max_length=MANAGER_TYPE_LENGTH, choices=MANAGER_TYPE_CHOICES )
  tag_list = models.ManyToManyField( Tag )
  show_only_latest = models.BooleanField( default=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )
  updated = models.DateTimeField( editable=False, auto_now=True )

  @cinp.action( return_type={ 'type': 'String', 'is_array': True }, paramater_type_list=[ { 'type': 'Integer' } ] )
  def poll( self, timeout ):
    """
    this function will block for up to timeout seconds waiting for notification
    that PackageFile change that affects this Repo.  If not change happend
    returns empty array, otherwise an array of Package names that changed
    """
    cursor = connection.cursor()
    cursor.execute( 'LISTEN "mirror_repo_%s"' % self.pk )
    conn = cursor.cursor.connection
    conn.commit()
    try:
      select.select( [ conn ], [], [], timeout )
    except select.error as e:
      if e[0] == errno.EINTR:
        time.sleep( timeout )  # Self DOS Preventor
      else:
        raise e

    conn.poll()

    result = []
    while conn.notifies:
      notify = conn.notifies.pop()  # hopfully notify.channel = the LISTEN name, can't do anything about it if it isn't at this point
      if notify.payload:  # is '' if there is not a payload
        result.append( notify.payload )

    return result

  def notify( self, package=None ):
    """
    send the notify event to anything blocked in the poll
    """
    if package is None:
      connection.cursor().execute( 'NOTIFY "mirror_repo_%s"' % self.pk )
    else:
      connection.cursor().execute( 'NOTIFY "mirror_repo_%s", \'%s\'' % ( self.pk, package.pk ) )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if not name_regex.match( self.name ):
      errors[ 'name' ] = 'Invalid'

    if errors:
      raise ValidationError( errors )

  def __str__( self ):
    return 'Repo "%s"' % self.description


@cinp.model( not_allowed_verb_list=( 'CREATE', 'DELETE', 'UPDATE' ) )
class Mirror( models.Model ):
  """
  Mirror groups a set of Repos togeather to provide for a client.  A PSK is
  required to help control access.

  - name: name of the mirror. also effectivly the username for the Mirror,
    ie: 'prod'
  - description: short description of the mirror, ie: 'Production'
  - psk: Preshared Key used for controlling mirror access
  - last_heartbeat: DateTime stamp of when the mirror last checked in.  Can
    be used to detect Mirror client that have stopped checking in. This is
    updated when the client does a full sync.
  """
  name = models.CharField( max_length=50, primary_key=True )
  description = models.CharField( max_length=200 )
  psk = models.CharField( max_length=100 )
  repo_list = models.ManyToManyField( Repo )
  last_heartbeat = models.DateTimeField( editable=False, blank=True, null=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )
  updated = models.DateTimeField( editable=False, auto_now=True )

  @cinp.action()
  def heartbeat( self ):  # TODO: make sure it's the right user for the Mirror
    self.last_heartbeat = datetime.now( timezone.utc )
    self.full_clean()
    self.save()

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if not name_regex.match( self.name ):
      errors[ 'name' ] = 'Invalid'

    if errors:
      raise ValidationError( errors )

  def __str__( self ):
    return 'Mirror "%s"' % self.description
