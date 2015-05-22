from datetime import datetime

from django.core.exceptions import ValidationError, PermissionDenied
from django.db import models
from django.utils.timezone import utc

from Deb import Deb
from Rpm import Rpm
from Pdisk import Pdisk

DISTRO_CHOICES = ( ( 'debian', 'Debian' ), ( 'centos', 'Centos' ), ( 'rhel', 'RHEL' ), ( 'sles', 'SLES' ) ) # there is no ubuntu, it shares the same version space as debian
MANAGER_TYPE_CHOICES = ( ( 'apt', 'APT' ), ( 'yum', 'YUM' ), ( 'zypper', 'Zypper' ) )
FILE_TYPE_CHOICES = ( ( 'deb', 'deb' ), ( 'rpm', 'RPM' ), ( 'pdisk', 'Plato Disk' ) )
FILE_ARCH_CHOICES = ( ( 'x86_64', 'x86_64' ), ( 'i386', 'i386' ), ( 'all', 'All' ) )
RELEASE_TYPE_CHOICES = ( ( 'ci', 'CI' ), ( 'dev', 'Development' ), ( 'stage', 'Staging' ), ( 'prod', 'Production' ), ( 'depr', 'Deprocated' ) )

MANAGER_TYPE_LENGTH = 6
FILE_TYPE_LENGTH = 3
FILE_ARCH_LENGTH = 6
RELEASE_TYPE_LENGTH = 5
DISTRO_LENGTH = 6


class DistroVersion( models.Model ):
  """
This is a type of Distro, ie Centos 6 or Ubuntu 14.04(Trusty)
  """
  # TODO: make the release_names another model
  DISTROS = DISTRO_CHOICES
  FILE_TYPES = FILE_TYPE_CHOICES
  name = models.CharField( max_length=20, primary_key=True )
  distro = models.CharField( max_length=DISTRO_LENGTH, choices=DISTRO_CHOICES ) # TODO: convert into another model
  version = models.CharField( max_length=10 )
  file_type = models.CharField( max_length=FILE_TYPE_LENGTH, choices=FILE_TYPE_CHOICES )
  release_names = models.CharField( max_length=100, blank=True ) # '\t' delimited, things like el5, trusty, something that is in filename that tells what version it belongs to
  created = models.DateTimeField( editable=False, auto_now_add=True )
  updated = models.DateTimeField( editable=False, auto_now=True )

  def __unicode__( self ):
    return 'Version "%s" of "%s"' % ( self.version, self.distro )

  class Meta:
    unique_together = ( 'distro', 'version', 'file_type' )

  class API:
    constants = ( 'DISTROS', 'FILE_TYPES' )


class Repo( models.Model ):
  """
This is a Collection of PackageFiles that meant certian requrements, ie: distro, repo manager, and release type.
  """
  MANAGER_TYPES = MANAGER_TYPE_CHOICES
  RELEASE_TYPES = RELEASE_TYPE_CHOICES
  distroversion_list = models.ManyToManyField( DistroVersion )
  manager_type = models.CharField( max_length=MANAGER_TYPE_LENGTH, choices=MANAGER_TYPE_CHOICES )
  description = models.CharField( max_length=200 )
  release_type = models.CharField( max_length=RELEASE_TYPE_LENGTH, choices=RELEASE_TYPE_CHOICES )
  created = models.DateTimeField( editable=False, auto_now_add=True )
  updated = models.DateTimeField( editable=False, auto_now=True )

  @property
  def package_queryset_parms( self ):
    qs = { 'packagefile__distroversion__in': [ i.pk for i in self.distroversion_list.all() ] }

    if self.release_type == 'ci':
      qs[ 'packagefile__ci_at__isnull' ] = False
      qs[ 'packagefile__dev_at__isnull' ] = True
      qs[ 'packagefile__stage_at__isnull' ] = True
      qs[ 'packagefile__prod_at__isnull' ] = True
      qs[ 'packagefile__depr_at__isnull' ] = True

    elif self.release_type == 'dev':
      qs[ 'packagefile__ci_at__isnull' ] = False
      qs[ 'packagefile__dev_at__isnull' ] = False
      qs[ 'packagefile__stage_at__isnull' ] = True
      qs[ 'packagefile__prod_at__isnull' ] = True
      qs[ 'packagefile__depr_at__isnull' ] = True

    elif self.release_type == 'stage':
      qs[ 'packagefile__ci_at__isnull' ] = False
      qs[ 'packagefile__dev_at__isnull' ] = False
      qs[ 'packagefile__stage_at__isnull' ] = False
      qs[ 'packagefile__prod_at__isnull' ] = True
      qs[ 'packagefile__depr_at__isnull' ] = True

    elif self.release_type == 'prod':
      qs[ 'packagefile__ci_at__isnull' ] = False
      qs[ 'packagefile__dev_at__isnull' ] = False
      qs[ 'packagefile__stage_at__isnull' ] = False
      qs[ 'packagefile__prod_at__isnull' ] = False
      qs[ 'packagefile__depr_at__isnull' ] = True

    elif self.release_type == 'depr':
      qs[ 'packagefile__depr_at__isnull' ] = False

    return qs

  def __unicode__( self ):
    return 'Repo "%s"' % self.description

  class API:
    constants = ( 'MANAGER_TYPES', 'RELEASE_TYPES' )


class Mirror( models.Model ):
  """
This is will authorize a remote server to get a listing of package files.  That list is generated via the repo_list.
NOTE: this dosen't prevent the remote server from downloading an indivvidual file if it allready knows the url, this just controlls the list of files sent.
  """
  name = models.CharField( max_length=50, primary_key=True )
  description = models.CharField( max_length=200 )
  psk = models.CharField( max_length=100 )
  repo_list = models.ManyToManyField( Repo )
  last_sync_start = models.DateTimeField( editable=False, blank=True, null=True )
  last_sync_complete = models.DateTimeField( editable=False, blank=True, null=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )
  updated = models.DateTimeField( editable=False, auto_now=True )

  def __unicode__( self ):
    return 'Mirror "%s"' % self.description

  def syncStart( self ):
    self.last_sync_start = datetime.utcnow().replace( tzinfo=utc )
    self.save()

  def syncComplete( self ):
    self.last_sync_complete = datetime.utcnow().replace( tzinfo=utc )
    self.save()

  class API:
    actions = { 'syncStart': [],
                'syncComplete': [],
              }


class Package( models.Model ):
  """
This is a Collection of PacageFiles, they share a name.
  """
  name = models.CharField( max_length=200, primary_key=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )
  updated = models.DateTimeField( editable=False, auto_now=True )

  def __unicode__( self ):
    return 'Package "%s"' % self.name

  class API:
    list_filters = { 'repo-sync': { 'repo': Repo } }

    @staticmethod
    def buildQS( qs, filter, values ):
      if filter == 'repo-sync':
        return qs.filter( **values[ 'repo' ].package_queryset_parms )

      raise Exception( 'Invalid filter "%s"' % filter )


class PackageFile( models.Model ): # TODO: add delete to cleanup the file, django no longer does this for us
  """
This is the Individual package "file", they can indivdually belong to any type, arch, package, this is the thing that is actually sent to the remote repos
  """
  RELEASE_LEVELS = ( 'new', 'ci', 'dev', 'stage', 'prod', 'depr' )
  FILE_TYPES = FILE_TYPE_CHOICES
  FILE_ARCHS = FILE_ARCH_CHOICES
  package = models.ForeignKey( Package, editable=False )
  distroversion = models.ForeignKey( DistroVersion, editable=False )
  version = models.CharField( max_length=50, editable=False )
  type = models.CharField( max_length=FILE_TYPE_LENGTH, editable=False, choices=FILE_TYPE_CHOICES )
  arch = models.CharField( max_length=FILE_ARCH_LENGTH, editable=False, choices=FILE_ARCH_CHOICES )
  justification = models.TextField()
  provenance = models.TextField()
  file = models.FileField( editable=False )
  prod_changecontrol_id = models.CharField( max_length=20, blank=True )
  ci_at = models.DateTimeField( editable=False, blank=True, null=True )
  dev_at = models.DateTimeField( editable=False, blank=True, null=True )
  stage_at = models.DateTimeField( editable=False, blank=True, null=True )
  prod_at = models.DateTimeField( editable=False, blank=True, null=True )
  depr_at = models.DateTimeField( editable=False, blank=True, null=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )
  updated = models.DateTimeField( editable=False, auto_now=True )

  @property
  def release( self ):
    if self.depr_at:
      return 'depr'

    elif self.prod_at and self.stage_at and self.dev_at and self.ci_at:
      return 'prod'

    elif self.stage_at and self.dev_at and self.ci_at:
      return 'stage'

    elif self.dev_at and self.ci_at:
      return 'dev'

    elif self.ci_at:
      return 'ci'

    else:
      return 'new'

  def loadfile( self, file, request_distro ):
    file.file.seek( 0 ) # some upstream process might of left the cursor at the end of the file

    pkgFile = None
    for loader in ( Deb, Rpm, Pdisk ):
      pkgFile = loader.load( file )
      if pkgFile is not None:
        break

    if not pkgFile:
      raise ValidationError( 'Unable to Determine File Type' )

    try:
      package = Package.objects.get( pk=pkgFile.package )
    except Package.DoesNotExist:
      raise ValidationError( 'Unable to find package "%s"' % pkgFile.package )

    distroversion = None
    distroversion_list = []
    full_distroversion_list = []
    for tmp in DistroVersion.objects.filter( file_type=pkgFile.type ):
      full_distroversion_list.append( tmp.pk )
      for name in tmp.release_names.split( '\t' ):
        if name in pkgFile.version:
          distroversion_list.append( tmp.pk )

    if request_distro:
      if request_distro in full_distroversion_list:
        distroversion = request_distro

    elif len( distroversion_list ) == 1:
      distroversion = distroversion_list[0]

    elif len( full_distroversion_list ) == 1:
      distroversion = full_distroversion_list[0]

    if not distroversion:  # confused, punt to the caller
      if distroversion_list:
        return distroversion_list
      else:
        return full_distroversion_list

    # we found one and only one disto, we are taking it
    self.file = file
    self.distroversion_id = distroversion
    self.package = package
    self.type = pkgFile.type
    self.arch = pkgFile.arch
    self.version = pkgFile.version
    return True

  def promote( self, _user_, to ):
    """
Promote package file to the next release level, to must be one of RELEASE_LEVELS
    """
    if not _user_.has_perm( 'Repos.promote_packagefile' ):
      raise PermissionDenied()

    if to not in self.RELEASE_LEVELS:
      raise Exception( 'Release level "%s" is Invalid' % to )

    if self.release == 'new' and to == 'ci':
      self.ci_at = datetime.utcnow().replace( tzinfo=utc )

    elif self.release == 'ci' and to == 'dev':
      self.dev_at = datetime.utcnow().replace( tzinfo=utc )

    elif self.release == 'dev' and to == 'stage':
      self.stage_at = datetime.utcnow().replace( tzinfo=utc )

    elif self.release == 'stage' and to == 'prod':
      if not self.prod_changecontrol_id:
        raise Exception( 'Change Control ID Requred to promote to prod' )
      self.prod_at = datetime.utcnow().replace( tzinfo=utc )

    else:
      raise Exception( 'Unable to promote from "%s" to "%s"' % ( self.release, to ) )

    self.save()

  def deprocate( self, _user_ ):
    """
Deprocate package file.
    """

    if not _user_.has_perm( 'Repos.promote_packagefile' ):
      raise PermissionDenied()

    self.depr_at = datetime.utcnow().replace( tzinfo=utc )

    self.save()

  @staticmethod
  def create( _user_, file, justification, provenance, version=None, ):
    """
Create a new PackageFile, note version is the distro version and is only required if it
can't be automatically detected, in which case the return value of created will be a list of
possible versions
    """

    if not _user_.has_perm( 'Repos.create_packagefile' ):
      raise PermissionDenied()

    if not version or not version.strip():
      version = None

    try:
      PackageFile.objects.get( file='./%s' % file.name ) #TODO: Figure out where the ./ is comming from and get rid of it, make sure to update the clean up script
      raise Exception( 'File name "%s" allready used' % file.name )
    except PackageFile.DoesNotExist:
      pass

    result = PackageFile()
    result.justification = justification
    result.provenance = provenance
    options = result.loadfile( file, version )

    if options is True:
      result.save()
      return True

    else:
      return options

  def save( self, *args, **kwargs ):
    if self.pk and self.file._file:
      raise ValidationError( 'Not Allowed to update the file.' )

    super( PackageFile, self ).save( *args, **kwargs )

  def __unicode__( self ):
    return 'PackageFile "%s"' % ( self.file.name )

  class Meta:
    unique_together = ( 'package', 'distroversion', 'version', 'type', 'arch' )

    default_permissions = ( 'change', 'promote', 'create' )

  class API:
    not_allowed_methods = ( 'CREATE', 'DELETE' )
    constants = ( 'RELEASE_LEVELS', 'FILE_TYPES', 'FILE_ARCHS' )
    actions = {
               'promote': [ { 'type': 'String', 'choices': dict( RELEASE_TYPE_CHOICES ) } ],
               'deprocate': [],
               'create': [ { 'type': 'File' }, { 'type': 'String' }, { 'type': 'String' }, { 'type': 'String' } ]
              }
    properties = [ 'release' ]
    list_filters = {
                      'package': { 'package': Package },
                      'repo-sync': { 'repo': Repo, 'package': Package }
                   }

    @staticmethod
    def buildQS( qs, filter, values ):
      if filter == 'package':
        return qs.filter( package=values[ 'package' ] )

      if filter == 'repo-sync':
        repo_parms = values[ 'repo' ].package_queryset_parms
        repo_parms = dict( zip( [ i[13:] for i in repo_parms.keys() ], repo_parms.values() ) ) # take off the "packagefile__" prefix
        return qs.filter( package=values[ 'package'], **repo_parms )

      raise Exception( 'Invalid filter "%s"' % filter )
