from django.core.exceptions import ValidationError
from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, post_delete

from cinp.orm_django import DjangoCInP as CInP
from packrat.fields import name_regex, DISTRO_CHOICES, DISTRO_LENGTH, FILE_TYPE_LENGTH

"""
tags -
  list of required tags
  flag for auto happening
  optional change control requirements
"""


cinp = CInP( 'Attrib', '2.0' )


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
  required_list = models.ManyToManyField( 'self', symmetrical=False, related_name='+' )
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
      todo += current.required_list.all()
      if self in todo:
        errors[ 'required' ] = 'required tags recursivly refer back to this tag'
        break

    if not name_regex.match( self.name ):
      errors[ 'name' ] = 'Invalid'

    if errors:
      raise ValidationError( errors )

  @cinp.action( return_type='Map' )
  @staticmethod
  def tagMap():
    result = {}
    for tag in Tag.objects.all():
      result[ tag.name ] = { 'requred': [ i.name for i in tag.required_list.all().order_by( 'name' ) ], 'change_control': tag.change_control_required }

    return result

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return cinp.basic_auth_check( user, verb, Tag )

  class Meta:
    default_permissions = ()

  def __str__( self ):
    return 'Tag "{0}"'.format( self.name )


@receiver( post_save, sender=Tag )
def tagPreSave( sender, instance, created, **kwargs ):
  if not created:
    return

  permission = Permission()
  permission.codename = 'tag_{0}'.format( instance.name )
  permission.name = 'Can add tag {0}'.format( instance.name )
  permission.content_type = ContentType.objects.get_for_model( Tag )
  permission.full_clean()
  permission.save()


@receiver( post_delete, sender=Tag )
def tagPostDelete( sender, instance, **kwargs ):
  try:
    permission = Permission.objects.get( codename='tag_{0}'.format( instance.name ) )
    permission.delete()
  except Permission.DoesNotExist:
    pass


@cinp.model( not_allowed_verb_list=( 'CREATE', 'DELETE', 'UPDATE' ), constant_set_map={ 'distro': DISTRO_CHOICES } )
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
  file_type = models.CharField( max_length=FILE_TYPE_LENGTH )
  release_names = models.CharField( max_length=100, blank=True, help_text='tab delimited list of things like el5, trusty, something that is in filename that tells what version it belongs to' )
  created = models.DateTimeField( editable=False, auto_now_add=True )
  updated = models.DateTimeField( editable=False, auto_now=True )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return cinp.basic_auth_check( user, verb, DistroVersion )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if not name_regex.match( self.name ):
      errors[ 'name' ] = 'Invalid'

    if errors:
      raise ValidationError( errors )

  class Meta:
    unique_together = ( 'distro', 'version', 'file_type' )
    default_permissions = ()

  def __str__( self ):
    return 'Version "{0}" of "{1}"'.format( self.version, self.distro )
