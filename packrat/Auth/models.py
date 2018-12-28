from django.contrib.auth import authenticate, login, logout

from cinp.orm_django import DjangoCInP as CInP

from packrat.Attrib.models import Tag


def getUser( auth_id, auth_token ):
  if auth_id is None or auth_token is None:
    return None

  try:
    session = Session.objects.get( user=auth_id, token=auth_token )
  except ( Session.DoesNotExist, User.DoesNotExist ):
    return None

  if not session.user.isActive:
    return None

  if not session.isActive:
    return None

  return session.user


"""

TODO:
  add tracking logging, or some place to send tracking info

"""


cinp = CInP( 'Auth', '2.0' )


@cinp.staticModel( not_allowed_verb_list=[ 'LIST', 'DELETE', 'CREATE' ] )
class User():

  @property
  def isActive( self ):
    return self.is_active

  @property
  def isSuperuser( self ):
    return self.is_superuser

  @property
  def isAnonymouse( self ):
    return self.is_anonymouse

  @cinp.action( paramater_type_list=[ 'String', 'String' ] )
  @staticmethod
  def login( username, password ):
    user = authenticate( username=username, password=password )
    if user is not None:
      pass
    else:
      raise ValueError( 'Invalid Login' )

  @cinp.action( paramater_type_list=[ 'String' ] )
  def set_password( self, password ):
    self.set_password( password )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    if id_list is not None and len( id_list ) >= 1 and id_list[0] != user.username:
      return False

    return True

  def __str__( self ):
    return 'User "{0}"'.format( self.username )
