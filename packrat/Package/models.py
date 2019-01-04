import hashlib
from datetime import datetime, timezone

from django.core.exceptions import ValidationError
from django.db import models

from cinp.orm_django import DjangoCInP as CInP
from cinp.server_common import NotAuthorized

from packrat.Attrib.models import Tag, DistroVersion
from packrat.Repo.models import Repo
from packrat.lib.info import infoDetect
from packrat.fields import name_regex, USERNAME_LENGTH, FILE_TYPE_CHOICES, FILE_ARCH_CHOICES, FILE_TYPE_LENGTH, FILE_ARCH_LENGTH

cinp = CInP( 'Package', '2.0' )


@cinp.model( not_allowed_verb_list=( 'DELETE', 'CALL' ) )
class Package( models.Model ):
  """
  A collection of PackageFiles

  - name: the common name of the PackageFiles
  - deprocated_count: the number of deprocated files to keep, oldest according to the deprocated_at field are removed first
  - failed_count: the number of failed files to keep, oldest according to the failed_at field are removed first
  """
  name = models.CharField( max_length=200, primary_key=True )
  deprocated_count = models.IntegerField( default=20 )
  failed_count = models.IntegerField( default=10 )
  created = models.DateTimeField( editable=False, auto_now_add=True )
  updated = models.DateTimeField( editable=False, auto_now=True )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return cinp.basic_auth_check( user, verb, Package )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if not name_regex.match( self.name ):
      errors[ 'name' ] = 'Invalid'

    if errors:
      raise ValidationError( errors )

  def __str__( self ):
    return 'Package "{0}"'.format( self.name )


@cinp.model( not_allowed_verb_list=( 'CREATE', 'UPDATE', 'DELETE' ), constant_set_map={ 'type': FILE_TYPE_CHOICES, 'arch': FILE_ARCH_CHOICES }, property_list=( 'tags', ) )
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
  - version: Version of the Package this PacageFile represents, ie: '1.2-5'
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
  distroversion = models.ForeignKey( DistroVersion, editable=False, on_delete=models.PROTECT )
  version = models.CharField( max_length=50, editable=False )
  type = models.CharField( max_length=FILE_TYPE_LENGTH, editable=False, choices=FILE_TYPE_CHOICES )
  arch = models.CharField( max_length=FILE_ARCH_LENGTH, editable=False, choices=FILE_ARCH_CHOICES )
  justification = models.TextField()
  provenance = models.TextField()
  file = models.FileField( editable=False )
  sha256 = models.CharField( max_length=64, editable=False )
  tag_list = models.ManyToManyField( Tag, through='PackageFileTag' )
  failed_at = models.DateTimeField( blank=True, null=True )
  failed_by = models.CharField( max_length=USERNAME_LENGTH, blank=True, null=True )
  deprocated_at = models.DateTimeField( blank=True, null=True )
  deprocated_by = models.CharField( max_length=USERNAME_LENGTH, blank=True, null=True )
  created_by = models.CharField( max_length=USERNAME_LENGTH )
  created = models.DateTimeField( editable=False, auto_now_add=True )
  updated = models.DateTimeField( editable=False, auto_now=True )

  @property
  def tags( self ):
    return [ i.name for i in self.tag_list.all() ]

  def notify( self, tag_list=None ):
    """
    notify repos that hold this tag
    """
    if tag_list is None:
      tag_list = self.tag_list

    repo_list = Repo.objects.filter( tag_list__in=tag_list, distroversion_list=self.distroversion )

    for repo in repo_list:
      repo.notify( self.package )

  def loadfile( self, target_file, distroversion ):
    info = infoDetect( target_file )

    if info is None:
      raise ValueError( 'Unable to Determine File Type' )

    try:
      package = Package.objects.get( pk=info.package )
    except Package.DoesNotExist:
      raise ValueError( 'Unable to find package "{0}"'.format( info.package ) )

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

  @cinp.action( paramater_type_list=[ { 'type': '_USER_' }, { 'type': 'Model', 'model': Tag }, { 'type': 'String' } ] )
  def tag( self, user, tag, change_control_id=None ):
    """
    Tag package file.  If to release Type requires change control,
    change_control_id must be specified.
    """
    if not user.has_perm( 'Attrib.tag_{0}'.format( tag ) ):
      raise NotAuthorized()

    cur_tags = [ i.name for i in self.tag_list ]

    for item in tag.required_list:
      if item.name not in cur_tags:
        raise ValueError( 'Required tag "{0}" missing'.format( item.name ) )

    if tag.change_control_required and change_control_id is None:
      raise ValueError( 'Change Control required to tag with "{0}"({1})'.format( tag.description, tag.name ) )

    pft = PackageFileTag()
    pft.package_file = self
    pft.tag = tag
    pft.by = user.username
    pft.at = datetime.now( timezone.utc )
    pft.change_control_id = change_control_id
    pft.full_clean()
    pft.save()

    self.notify( [ tag ] )

  @cinp.action( paramater_type_list=[ { 'type': '_USER_' } ] )
  def deprocate( self, user ):
    """
    Deprocate package file.
    """
    self.deprocated_at = datetime.now( timezone.utc )
    self.deprocated_by = user.username
    self.full_clean()
    self.save()

    self.notify()

  @cinp.action( paramater_type_list=[ { 'type': '_USER_' } ] )
  def fail( self, user ):
    """
    Fail package file.
    """
    self.failed_at = datetime.now( timezone.utc )
    self.failed_by = user.username
    self.full_clean()
    self.save()

    self.notify()

  @cinp.action( return_type={ 'type': 'String', 'is_array': True }, paramater_type_list=[ { 'type': 'File', 'allowed_scheme_list': [ 'djfh' ] } ] )
  @staticmethod
  def distroversionOptions( file ):
    """
    returns a list of possible DistroVersions for this filename
    """
    info = infoDetect( file )

    if info is None:
      raise ValueError( 'Unable to Determine File Type' )

    return info.distroversion_list

  @cinp.action( paramater_type_list=[ { 'type': '_USER_' }, { 'type': 'File', 'allowed_scheme_list': [ 'djfh' ] }, { 'type': 'String' }, { 'type': 'String' }, { 'type': 'String' } ] )
  @staticmethod
  def create( user, file, justification, provenance, distroversion ):
    """
    Create a new PackageFile
    """
    try:
     PackageFile.objects.get( file='./{0}'.format( file.name ) )  # TODO: Figure out where the ./ is comming from and get rid of it, make sure to update the clean up script
     raise ValueError( 'File name "{0}" allready used'.format( file.name ) )
    except PackageFile.DoesNotExist:
     pass

    result = PackageFile()
    result.justification = justification
    result.provenance = provenance
    result.created_by = user.username
    result.loadfile( file, distroversion )
    result.full_clean()
    result.save()

  @cinp.action( return_type={ 'type': 'Boolean' }, paramater_type_list=[ { 'type': 'String' } ] )
  @staticmethod
  def filenameInUse( file_name ):
    """
    returns true if the file_name has allready been used.  Good Idea to call this
    before uploading files to ensure the file name is unique.
    """
    try:
      PackageFile.objects.get( file='./{0}'.format( file_name ) )  # TODO: see ./ comment in create
      return True
    except PackageFile.DoesNotExist:
      pass

    return False

  @cinp.list_filter( name='package', paramater_type_list=[ { 'type': 'Model', 'model': Package } ] )
  @staticmethod
  def filterPackage( package ):
    return PackageFile.objects.filter( package=package )

  @cinp.list_filter( name='repo', paramater_type_list=[ { 'type': 'Model', 'model': Repo }, { 'type': 'String', 'is_array': True } ] )
  @staticmethod
  def filterRepo( repo, package_list ):
    queryset_parms = {}
    queryset_parms[ 'distroversion__in' ] = [ i.pk for i in repo.distroversion_list.all() ]
    queryset_parms[ 'tag_list__in' ] = [ i.pk for i in repo.tag_list.all() ]

    if package_list:  # not None, and not and empty string or empty list
      queryset_parms[ 'package_id__in' ] = package_list

    return PackageFile.objects.filter( **queryset_parms )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    if not cinp.basic_auth_check( user, verb, PackageFile ):
      return False

    if verb == 'CALL':
      if action in ( 'filenameInUse', 'distroversionOptions', 'create' ) and user.has_perm( 'Package.add_packagefile' ):
        return True

      if action == 'tag' and user.has_perm( 'Package.can_tag' ):
        return True

      if action == 'fail' and user.has_perm( 'Package.can_fail' ):
        return True

      if action == 'deprocate' and user.has_perm( 'Package.can_deprocate' ):
        return True

      return False

    else:
      return True

    return False

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if self.pk and self.file._file:
      self[ 'file' ] = 'Not Allowed to update the file'

      if errors:
        raise ValidationError( errors )

  class Meta:
    unique_together = ( 'package', 'distroversion', 'version', 'type', 'arch' )
    default_permissions = ( 'add', )
    permissions = (
                    ( 'can_tag', 'Can add Tag' ),
                    ( 'can_untag', 'Can remove a Tag' ),
                    ( 'can_fail', 'Can Mark a Package File as Failed' ),
                    ( 'can_unfail', 'Can Un-Mark a Package File as Failed' ),
                    ( 'can_deprocate', 'Can Mark a Package File as Deprocated' ),
                    ( 'can_undeprocate', 'Can Un-Mark a Package File as Deprocated' )
    )

  def __str__( self ):
    return 'PackageFile "{0}"'.format( self.file.name )


@cinp.model( not_allowed_verb_list=( 'CREATE', 'UPDATE', 'DELETE', 'CALL' ) )
class PackageFileTag( models.Model ):
  """
  This is a Helper Table to join PackageFile to Tag.  This stores when
  the package file was tagged and by whom
  """
  package_file = models.ForeignKey( PackageFile, on_delete=models.CASCADE )
  tag = models.ForeignKey( Tag, on_delete=models.CASCADE )
  by = models.CharField( max_length=USERNAME_LENGTH )
  at = models.DateTimeField( editable=False, auto_now_add=True )
  change_control_id = models.CharField( max_length=50, blank=True, null=True )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return cinp.basic_auth_check( user, verb, PackageFileTag )

  class Meta:
    unique_together = ( 'package_file', 'tag' )
    default_permissions = ()

  def __str__( self ):
    return 'PackageFileTag for PackageFile "{0}" Release Type "{1}" at "{2}"'.format( self.package_file, self.release_type, self.at )
