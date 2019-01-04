import select
import errno
import time
from datetime import datetime, timezone

from django.core.exceptions import ValidationError
from django.db import models, connection

from cinp.orm_django import DjangoCInP as CInP
from packrat.Attrib.models import Tag, DistroVersion
from packrat.fields import name_regex, MANAGER_TYPE_CHOICES, MANAGER_TYPE_LENGTH

"""
TODO:

snapshots:
  snapshot of curent tags
  ability to tweek tags for the snapshot

"""

cinp = CInP( 'Repo', '2.0' )


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
  - tag: tag that this repo includes
  - show_only_latest: if True to only expose the highest numberd versoin of each package,
  """
  name = models.CharField( max_length=50, primary_key=True )
  description = models.CharField( max_length=200 )
  filesystem_dir = models.CharField( max_length=50, unique=True )  # TODO: validate this, must be fs safe
  distroversion_list = models.ManyToManyField( DistroVersion )
  manager_type = models.CharField( max_length=MANAGER_TYPE_LENGTH, choices=MANAGER_TYPE_CHOICES )
  tag = models.ForeignKey( Tag, on_delete=models.PROTECT )
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
    cursor.execute( 'LISTEN "mirror_repo_{0}"'.format( self.pk ) )
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
      connection.cursor().execute( 'NOTIFY "mirror_repo_{0}"'.format( self.pk ) )
    else:
      connection.cursor().execute( 'NOTIFY "mirror_repo_{0}", \'{1}\''.format( self.pk, package.pk ) )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return cinp.basic_auth_check( user, verb, Repo )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if not name_regex.match( self.name ):
      errors[ 'name' ] = 'Invalid'

    if errors:
      raise ValidationError( errors )

  class Meta:
    default_permissions = ()

  def __str__( self ):
    return 'Repo "{0}"'.format( self.description )


@cinp.model( not_allowed_verb_list=( 'CREATE', 'DELETE', 'UPDATE' ) )
class Mirror( models.Model ):
  """
  Mirror groups a set of Repos togeather to provide for a client.  A PSK is
  required to help control access.

  - name: name of the mirror. also effectivly the username for the Mirror,
    ie: 'prod'
  - description: short description of the mirror, ie: 'Production'
  - last_heartbeat: DateTime stamp of when the mirror last checked in.  Can
    be used to detect Mirror client that have stopped checking in. This is
    updated when the client does a full sync.
  """
  name = models.CharField( max_length=50, primary_key=True )
  description = models.CharField( max_length=200 )
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
  def checkAuth( user, verb, id_list, action=None ):
    return cinp.basic_auth_check( user, verb, Mirror )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if not name_regex.match( self.name ):
      errors[ 'name' ] = 'Invalid'

    if errors:
      raise ValidationError( errors )

  class Meta:
    default_permissions = ()

  def __str__( self ):
    return 'Mirror "{0}"'.format( self.description )
