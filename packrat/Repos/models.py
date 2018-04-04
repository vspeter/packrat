import select
import errno
import time
import hashlib
import re
from datetime import datetime, timezone

from django.core.exceptions import ValidationError
from django.db import models, connection

from cinp.orm_django import DjangoCInP as CInP
from packrat.Repos.PackageInfo import infoDetect

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

name_regex = re.compile( '^[0-9a-zA-Z\-_]+$' )  # possible to be using in a filesystem, must be filesystem safe, also don't allow chars that are used to delimit version and other info

DISTRO_CHOICES = ( ( 'debian', 'Debian' ), ( 'centos', 'Centos' ), ( 'rhel', 'RHEL' ), ( 'sles', 'SLES' ), ( 'core', 'CoreOS' ), ( 'none', 'None' ) )  # there is no ubuntu, it shares the same version space as debian
MANAGER_TYPE_CHOICES = ( ( 'apt', 'APT' ), ( 'yum', 'YUM' ), ( 'yast', 'YaST' ), ( 'json', 'JSON' ), ( 'docker', 'Docker' ), ( 'pypi', 'PyPi' ) )
FILE_TYPE_CHOICES = ( ( 'deb', 'deb' ), ( 'rpm', 'RPM' ), ( 'rsc', 'Resource' ), ( 'docker', 'Docker' ), ( 'python', 'Python' ) )
FILE_ARCH_CHOICES = ( ( 'x86_64', 'x86_64' ), ( 'i386', 'i386' ), ( 'all', 'All' ) )

# if these are changed (or any other field length), make sure to update the sqlite db in packrat-agent
MANAGER_TYPE_LENGTH = 6
FILE_TYPE_LENGTH = 6
FILE_ARCH_LENGTH = 6
DISTRO_LENGTH = 6

cinp = CInP( 'Repo', '1.5' )


@cinp.model( not_allowed_verb_list=( 'CREATE', 'DELETE', 'UPDATE' ) )
class ReleaseType( models.Model ):
  """
  Releases are stages a PackageFile can exist in, for example prod or stage.
  PackageFiles are promoted from one stage to the next.  At a minnimum you should
  have a ReleaseType with a name 'depr' with level = 100 and 'new' with
  level = 1, change_control_required is ignored for 'new' and 'depr'.

  - name: name of the release, ie: 'prod'
  - description: short description of the release type, ie: 'Production'
  - level: a numeric value to help packrat know the direction of promotion.
    The highest level ReleasetType a Package file is attached to is that
    PackageFiles curent release level.  Min value is 1, Max value is 100
  - change_control_required: if True, inorder to be promoted to this Release
    a Change Control ID is required and must check out before being allowed to
    promote to this level.
  """
  name = models.CharField( max_length=10, primary_key=True )
  description = models.CharField( max_length=100 )
  level = models.IntegerField( unique=True )
  change_control_required = models.BooleanField( default=False )
  created = models.DateTimeField( editable=False, auto_now_add=True )
  updated = models.DateTimeField( editable=False, auto_now=True )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if self.level is None or self.level < 2 or self.level > 99:
      if not( ( self.level == 1 and self.name == 'new' ) or ( self.level == 100 and self.name == 'depr' ) ):
        errors[ 'level' ] = 'Must be from 2 to 99'

    if ( self.name == 'new' and self.level != 1 ) or ( self.name == 'depr' and self.level != 100 ):
      errors[ 'name' ] = '"new" must be level 1 and "depr" must be level 100'

    if not name_regex.match( self.name ):
      errors[ 'name' ] = 'Invalid'

    if errors:
      raise ValidationError( errors )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'ReleaseType "%s"(%s)' % ( self.description, self.name )


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
  - release_type_list: list of the release types that this repo includes
  - show_only_latest: if True to only expose the highest numberd versoin of each package,
  """
  name = models.CharField( max_length=50, primary_key=True )
  description = models.CharField( max_length=200 )
  filesystem_dir = models.CharField( max_length=50, unique=True )  # TODO: validate this, must be fs safe
  distroversion_list = models.ManyToManyField( DistroVersion )
  manager_type = models.CharField( max_length=MANAGER_TYPE_LENGTH, choices=MANAGER_TYPE_CHOICES )
  release_type_list = models.ManyToManyField( ReleaseType )
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


@cinp.model( not_allowed_verb_list=( 'DELETE', 'CALL' ) )
class Package( models.Model ):
  """
  A collection of PackageFiles

  - name: the common name of the PackageFiles
  - deprocated_count: the number of deprocated versions to keep
  """
  name = models.CharField( max_length=200, primary_key=True )
  deprocated_count = models.IntegerField( default=10 )
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

  def __str__( self ):
    return 'Package "%s"' % self.name


@cinp.model( not_allowed_verb_list=( 'CREATE', 'DELETE' ), constant_set_map={ 'type': FILE_TYPE_CHOICES, 'arch': FILE_ARCH_CHOICES }, property_list=( 'release', ) )
class PackageFile( models.Model ):  # TODO: add delete to cleanup the file, django no longer does this for us
  """
  This is the Individual package "file", they can indivdually belong to any
  type, arch, package, this is the thing that is actually sent to the remote repos
  PackageFile records should only be created with the create static function,
  this will insure the releations ships with Package, Version, Type, Arch are
  detectored correctly.  See the create function for more detail. Records
  should also not have their file links updated, instead create a new record.
  Updating existing records is blocked.

  - package: The PackageFile group this package belongs to
  - distroversion: The DistroVersion this PackageFile is associated with.
  - version: Version of the Package this PacageFile represents, ie '1.2-5'
  - type: Type of file
  - arch: Archetuture of the file
  - justification: User provided field used when auditing package files.  This
    should detail the justification for this PackageFile's inclusion
  - provenance: User provided field used when auditing package files.  This
    should describe the provenance (where the PackageFile and/or it's sources)
    came from
  - sha256: hash of the file, given to the client so it can verify package file
    integrety
  - release_type_list: which release levels this package has been promoted to
  """
  package = models.ForeignKey( Package, editable=False, on_delete=models.CASCADE )
  distroversion = models.ForeignKey( DistroVersion, editable=False, on_delete=models.CASCADE )
  version = models.CharField( max_length=50, editable=False )
  type = models.CharField( max_length=FILE_TYPE_LENGTH, editable=False, choices=FILE_TYPE_CHOICES )
  arch = models.CharField( max_length=FILE_ARCH_LENGTH, editable=False, choices=FILE_ARCH_CHOICES )
  justification = models.TextField()
  provenance = models.TextField()
  file = models.FileField( editable=False )
  sha256 = models.CharField( max_length=64, editable=False )
  release_type_list = models.ManyToManyField( ReleaseType, through='PackageFileReleaseType' )
  created = models.DateTimeField( editable=False, auto_now_add=True )
  updated = models.DateTimeField( editable=False, auto_now=True )

  @property
  def release( self ):
    try:
      return self.release_type_list.order_by( '-level' )[0].name
    except IndexError:
      return None

  def notify( self, previous_release ):
    """
    notify repos that hold this PakcageFile's curent and previous release
    """
    repo_list = Repo.objects.filter( release_type_list__in=( previous_release, self.release ), distroversion_list=self.distroversion )

    for repo in repo_list:
      repo.notify( self.package )

  def loadfile( self, target_file, distroversion ):
    info = infoDetect( target_file )

    if info is None:
      raise ValueError( 'Unable to Determine File Type' )

    try:
      package = Package.objects.get( pk=info.package )
    except Package.DoesNotExist:
      raise ValueError( 'Unable to find package "%s"' % info.package )

    if distroversion not in info.distroversion_list:
      raise ValueError( 'DistroVersion "{0}" is not an option for this file'.format( distroversion ) )

    target_file.file.seek( 0 )
    sha256 = hashlib.sha256()
    while True:
      buf = target_file.file.read( 4096 )
      if not buf:
        break
      sha256.update( buf )

    self.file = target_file
    self.distroversion_id = distroversion
    self.package = package
    self.type = info.type
    self.arch = info.arch
    self.version = info.version
    self.sha256 = sha256.hexdigest()

  @cinp.action( paramater_type_list=[ { 'type': 'Model', 'model': 'packrat.Repos.models.ReleaseType' }, { 'type': 'String' } ] )
  def promote( self, to, change_control_id=None ):
    """
    Promote package file to the next release level.  Promotions must go to a
    higher ReleaseType.level.  If to release Type requires change control,
    change_control_id must be specified.
    """
    cur_release = None
    try:
      cur_release = self.release_type_list.order_by( '-level' )[0]
    except IndexError:
      pass

    if cur_release is not None and ( cur_release.level == to.level or cur_release.level >= to.level ):
      raise Exception( 'Unable to promote from "%s"(%s) to "%s"(%s)' % ( cur_release.description, cur_release.name, to.description, to.name ) )

    if to.change_control_required and change_control_id is None:
      raise Exception( 'Change Control required to promote to "%s"(%s)' % ( to.description, to.name ) )

    pfrt = PackageFileReleaseType()
    pfrt.package_file = self
    pfrt.release_type = to
    pfrt.at = datetime.now( timezone.utc )
    pfrt.change_control_id = change_control_id
    pfrt.full_clean()
    pfrt.save()

    self.notify( cur_release )

  @cinp.action()
  def deprocate( self ):
    """
    Deprocate package file.  Forces the target Release type to 'depr'.
    """
    previous_release = self.release

    pfrt = PackageFileReleaseType()
    pfrt.package_file = self
    pfrt.release_type = ReleaseType.objects.get( name='depr' )
    pfrt.at = datetime.now( timezone.utc )
    pfrt.full_clean()
    pfrt.save()

    self.notify( previous_release )

  @cinp.action( return_type={ 'type': 'String', 'is_array': True }, paramater_type_list=[ { 'type': 'File', 'allowed_scheme_list': [ 'djfh' ] } ] )
  @staticmethod
  def distroversion_options( file ):
    """
    returns a list of possible DistroVersions for this filename
    """
    info = infoDetect( file )

    if info is None:
      raise ValueError( 'Unable to Determine File Type' )

    return info.distroversion_list

  @cinp.action( paramater_type_list=[ { 'type': 'File', 'allowed_scheme_list': [ 'djfh' ] }, { 'type': 'String' }, { 'type': 'String' }, { 'type': 'String' } ] )
  @staticmethod
  def create( file, justification, provenance, distroversion ):
    """
    Create a new PackageFile
    """
    try:
     PackageFile.objects.get( file='./%s' % file.name )  # TODO: Figure out where the ./ is comming from and get rid of it, make sure to update the clean up script
     raise ValueError( 'File name "%s" allready used' % file.name )
    except PackageFile.DoesNotExist:
     pass

    result = PackageFile()
    result.justification = justification
    result.provenance = provenance
    result.loadfile( file, distroversion )
    result.full_clean()
    result.save()
    pfrt = PackageFileReleaseType()
    pfrt.package_file = result
    pfrt.release_type = ReleaseType.objects.get( name='new' )
    pfrt.at = datetime.now( timezone.utc )
    pfrt.full_clean()
    pfrt.save()

  @cinp.action( return_type={ 'type': 'Boolean' }, paramater_type_list=[ { 'type': 'String' } ] )
  @staticmethod
  def filenameInUse( file_name ):
    """
    returns true if the file_name has allready been used.  Good Idea to call this
    before uploading files to ensure the file name is unique.
    """
    try:
      PackageFile.objects.get( file='./%s' % file_name )  # TODO: see ./ comment in create
      return True
    except PackageFile.DoesNotExist:
      pass

    return False

  @cinp.list_filter( name='package', paramater_type_list=[ { 'type': 'Model', 'model': 'packrat.Repos.models.Package' } ] )
  @staticmethod
  def filter_package( package ):
    return PackageFile.objects.filter( package=package )

  @cinp.list_filter( name='repo', paramater_type_list=[ { 'type': 'Model', 'model': 'packrat.Repos.models.Repo' }, { 'type': 'String', 'is_array': True } ] )
  @staticmethod
  def filter_repo( repo, package_list ):
    # NOTE: the release type filter is not 100% right, it will work find for most cases, but there are times when this dosen't work, ie a repo that omits a middle level, but that should not happen very often, and until someone comes up with a clever way to fix it, we will have to be happy with this for now
    #   instead of filtering for just the packagefiles with the last releasttype in the list, we are taking the next highest releasetype and removing anything from there up.
    queryset_parms = {}
    queryset_parms[ 'distroversion__in' ] = [ i.pk for i in repo.distroversion_list.all() ]
    queryset_parms[ 'release_type_list__in' ] = [ i.pk for i in repo.release_type_list.all() ]

    if package_list:  # not None, and not and empty string or empty list
      queryset_parms[ 'package_id__in' ] = package_list

    highest_level = max( [ i.level for i in repo.release_type_list.all() ] )

    return PackageFile.objects.filter( **queryset_parms ).exclude( release_type_list__in=[ i.pk for i in ReleaseType.objects.filter( level__gt=highest_level ) ] ).distinct()

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    # promote
    # deprocate
    # if not user.has_perm( 'Repos.promote_packagefile' ):
    #   raise PermissionDenied()

    # create
    # if not user.has_perm( 'Repos.create_packagefile' ):
    #   raise PermissionDenied()

    return True

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if self.pk and self.file._file:
      self[ 'file' ] = 'Not Allowed to update the file'

      if errors:
        raise ValidationError( errors )

  class Meta:
    unique_together = ( 'package', 'distroversion', 'version', 'type', 'arch' )

  def __str__( self ):
    return 'PackageFile "%s"' % ( self.file.name )


@cinp.model( )
class PackageFileReleaseType( models.Model ):
  """
  This is a Helper Table to join PackageFile to ReleaseType.  This stores when
  the package file was promoted to the ReleaseType
  """
  package_file = models.ForeignKey( PackageFile, on_delete=models.CASCADE )
  release_type = models.ForeignKey( ReleaseType, on_delete=models.CASCADE )
  at = models.DateTimeField( editable=False, auto_now_add=True )
  change_control_id = models.CharField( max_length=50, blank=True, null=True )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  class Meta:
    unique_together = ( 'package_file', 'release_type' )

  def __str__( self ):
    return 'PackageFileReleaseType for PackageFile "%s" Release Type "%s" at "%s"' % ( self.package_file, self.release_type, self.at )
