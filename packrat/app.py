from cinp.server_werkzeug import WerkzeugServer
from cinp.django_file_handler import upload_handler

from packrat.Auth.models import getUser
# from packrat.files_handler import files_handler

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


def get_app( debug ):
  app = WerkzeugServer( root_path='/api/v1/', root_version='2.0', debug=debug, get_user=getUser, cors_allow_list=[ '*' ] )
  app.root_namespace.doc == __doc__

  app.registerNamespace( '/', 'packrat.Auth' )
  app.registerNamespace( '/', 'packrat.Attrib' )
  app.registerNamespace( '/', 'packrat.Package' )
  app.registerNamespace( '/', 'packrat.Repo' )

  app.registerPathHandler( '/api/upload', upload_handler )
  # app.registerPathHandler( '/files', files_handler )  # TODO: In prod  this should be handeled by the static web server

  app.validate()

  return app
