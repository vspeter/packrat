import hashlib
from datetime import datetime, timezone

from django.core.exceptions import ValidationError
from django.db import models

from cinp.orm_django import DjangoCInP as CInP
from packrat.Repos.PackageInfo import infoDetect


"""
tags -
  list of required tags
  flag for auto happening
  optional change control requirements
"""

cinp = CInP( 'Package', '2.0' )


@cinp.model( not_allowed_verb_list=( 'DELETE', 'CALL' ) )
class Package( models.Model ):
  """
  A collection of PackageFiles

  - name: the common name of the PackageFiles
  - deprocated_count: the number of deprocated files to keep, oldest according to the created field are removed first
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
    return [ i.name for i in self.tag_list ]

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

  @cinp.action( paramater_type_list=[ { 'type': '_USER_' }, { 'type': 'Model', 'model': 'packrat.Repos.models.Tag' }, { 'type': 'String' } ] )
  def tag( self, user, tag, change_control_id=None ):
    """
    Tag package file.  If to release Type requires change control,
    change_control_id must be specified.
    """
    cur_tags = [ i.name for i in self.tag_list ]

    for tag in tag.required:
      if tag.name not in cur_tags:
        raise ValueError( 'Required tag "{0}" missing'.format( tag.name ) )

    if tag.change_control_required and change_control_id is None:
      raise ValueError( 'Change Control required to tag with "%s"(%s)' % ( tag.description, tag.name ) )

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
  def distroversion_options( file ):
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
     PackageFile.objects.get( file='./%s' % file.name )  # TODO: Figure out where the ./ is comming from and get rid of it, make sure to update the clean up script
     raise ValueError( 'File name "%s" allready used' % file.name )
    except PackageFile.DoesNotExist:
     pass

    result = PackageFile()
    result.justification = justification
    result.provenance = provenance
    result.create_by = user.username
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
    queryset_parms = {}
    queryset_parms[ 'distroversion__in' ] = [ i.pk for i in repo.distroversion_list.all() ]
    queryset_parms[ 'tag_list__in' ] = [ i.pk for i in repo.tag_list.all() ]

    if package_list:  # not None, and not and empty string or empty list
      queryset_parms[ 'package_id__in' ] = package_list

    return PackageFile.objects.filter( **queryset_parms )

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
class PackageFileTag( models.Model ):
  """
  This is a Helper Table to join PackageFile to Tag.  This stores when
  the package file was tagged and by whom
  """
  package_file = models.ForeignKey( PackageFile, on_delete=models.CASCADE )
  release_type = models.ForeignKey( Tag, on_delete=models.CASCADE )
  by = models.CharField( max_length=USERNAME_LENGTH )
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
