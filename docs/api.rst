==================================
CInP API Documentation for Packrat
==================================

------------
Namespace - 
------------
URL: /api/v1/

API Version: v1


Model - Auth
------------

URL: /api/v1/Auth







Action - login
~~~~~~~~~~~~~~

URL: /api/v1/Auth(login)

Static: True



Return Type::

  None(String)(Req)

Paramaters::

  - username(String)(Req)
  - password(String)(Req)



Action - logout
~~~~~~~~~~~~~~~

URL: /api/v1/Auth(logout)

Static: True



Return Type::

  None(String)(Req)

Paramaters::

  - username(String)(Req)
  - token(String)(Req)



Action - keepalive
~~~~~~~~~~~~~~~~~~

URL: /api/v1/Auth(keepalive)

Static: True



Return Type::

  None(String)(Req)




------------------
Namespace - .Repos
------------------
URL: /api/v1/Repos

API Version: v1


Model - Repo
------------

URL: /api/v1/Repos/Repo


::

  This is a Collection of PackageFiles that meant certian requrements, ie: distro, repo manager, and release type.




Fields
~~~~~~

::

  - updated(DateTime)(R)
  - description(String)(RW)(Req)
  - created(DateTime)(R)
  - manager_type(String)(RW)(Req)
  - distroversion_list(ModelList)(RW)(Req) uri: /api/v1/Repos/DistroVersion
  - release_type(String)(RW)(Req)



Action - poll
~~~~~~~~~~~~~

URL: /api/v1/Repos/Repo(poll)

Static: False



Return Type::

  None(String)(Req)

Paramaters::

  - timeout(Integer)(Req)



Model - PackageFile
-------------------

URL: /api/v1/Repos/PackageFile


::

  This is the Individual package "file", they can indivdually belong to any type, arch, package, this is the thing that is actually sent to the remote repos



List Filters
~~~~~~~~~~~~

::

  - repo-sync - repo(Model)(Req) uri: /api/v1/Repos/Repo, package(Model)(Req) uri: /api/v1/Repos/Package
  - package - package(Model)(Req) uri: /api/v1/Repos/Package

Fields
~~~~~~

::

  - updated(DateTime)(R)
  - justification(String)(RW)(Req)
  - ci_at(DateTime)(R)
  - prod_at(DateTime)(R)
  - package(Model)(R)(Req) uri: /api/v1/Repos/Package
  - type(String)(R)(Req)
  - stage_at(DateTime)(R)
  - provenance(String)(RW)(Req)
  - created(DateTime)(R)
  - prod_changecontrol_id(String)(RW)
  - version(String)(R)(Req)
  - file(File)(R)(Req)
  - dev_at(DateTime)(R)
  - release(String)(R)
  - distroversion(Model)(R)(Req) uri: /api/v1/Repos/DistroVersion
  - arch(String)(R)(Req)
  - depr_at(DateTime)(R)



Action - deprocate
~~~~~~~~~~~~~~~~~~

URL: /api/v1/Repos/PackageFile(deprocate)

Static: False


::

  Deprocate package file.



Return Type::

  None(String)(Req)




Action - promote
~~~~~~~~~~~~~~~~

URL: /api/v1/Repos/PackageFile(promote)

Static: False


::

  Promote package file to the next release level, to must be one of RELEASE_LEVELS



Return Type::

  None(String)(Req)

Paramaters::

  - to(String)(Req)



Action - create
~~~~~~~~~~~~~~~

URL: /api/v1/Repos/PackageFile(create)

Static: True


::

  Create a new PackageFile, note version is the distro version and is only required if it
  can't be automatically detected, in which case the return value of created will be a list of
  possible versions



Return Type::

  None(String)(Req)

Paramaters::

  - version(String)
  - provenance(String)(Req)
  - justification(String)(Req)
  - file(File)(Req)



Action - filenameInUse
~~~~~~~~~~~~~~~~~~~~~~

URL: /api/v1/Repos/PackageFile(filenameInUse)

Static: True



Return Type::

  None(String)(Req)

Paramaters::

  - file_name(String)(Req)



Model - DistroVersion
---------------------

URL: /api/v1/Repos/DistroVersion


::

  This is a type of Distro, ie Centos 6 or Ubuntu 14.04(Trusty)




Fields
~~~~~~

::

  - updated(DateTime)(R)
  - name(String)(RC)(Req)
  - created(DateTime)(R)
  - file_type(String)(RW)(Req)
  - version(String)(RW)(Req)
  - release_names(String)(RW)
  - distro(String)(RW)(Req)



Model - Package
---------------

URL: /api/v1/Repos/Package


::

  This is a Collection of PacageFiles, they share a name.



List Filters
~~~~~~~~~~~~

::

  - repo-sync - repo(Model)(Req) uri: /api/v1/Repos/Repo

Fields
~~~~~~

::

  - updated(DateTime)(R)
  - name(String)(RC)(Req)
  - created(DateTime)(R)



Model - Mirror
--------------

URL: /api/v1/Repos/Mirror


::

  This is will authorize a remote server to get a listing of package files.  That list is generated via the repo_list.
  NOTE: this dosen't prevent the remote server from downloading an indivvidual file if it allready knows the url, this just controlls the list of files sent.




Fields
~~~~~~

::

  - psk(String)(RW)(Req)
  - updated(DateTime)(R)
  - name(String)(RC)(Req)
  - created(DateTime)(R)
  - last_sync_complete(DateTime)(R)
  - last_sync_start(DateTime)(R)
  - repo_list(ModelList)(RW)(Req) uri: /api/v1/Repos/Repo
  - description(String)(RW)(Req)



Action - syncStart
~~~~~~~~~~~~~~~~~~

URL: /api/v1/Repos/Mirror(syncStart)

Static: False



Return Type::

  None(String)(Req)




Action - syncComplete
~~~~~~~~~~~~~~~~~~~~~

URL: /api/v1/Repos/Mirror(syncComplete)

Static: False



Return Type::

  None(String)(Req)




Generated by CInP autodoc
*************************
