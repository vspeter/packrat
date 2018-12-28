#!/usr/bin/python3
import os

os.environ.setdefault( "DJANGO_SETTINGS_MODULE", "packrat.settings" )

import django
django.setup()

from django.contrib.auth.models import User
from packrat.Repo.models import Repo, Mirror
from packrat.Attrib.models import DistroVersion, Tag


def load_superuser():
  u = User.objects.get( username__exact='root' )
  u.set_password( 'root' )
  u.save()


def load_repos( app, schema_editor ):
  release_list = ( ( 'dev', [ 'dev', 'stage', 'prod' ] ), ( 'stage', [ 'stage', 'prod' ] ), ( 'prod', [ 'prod' ] ) )

  for release, release_type_list in release_list:
    r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', description='APT - {0}'.format( release.title() ), manager_type='apt', name='apt-{0}'.format( release ), filesystem_dir='apt-{0}'.format( release ) )
    r.distroversion_list = [ 'trusty', 'xenial', 'bionic' ]
    r.release_type_list = release_type_list
    r.full_clean()
    r.save()

  for release, release_type_list in release_list:
    r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', description='YUM - {0}'.format( release.title() ), manager_type='yum', name='yum-{0}'.format( release ), filesystem_dir='yum-{0}'.format( release ) )
    r.distroversion_list = [ 'centos6', 'centos7', 'sles11', 'sles12' ]
    r.release_type_list = release_type_list
    r.full_clean()
    r.save()

  for release, release_type_list in release_list:
    r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', description='JSON - {0}'.format( release.title() ), manager_type='json', name='json-{0}'.format( release ), filesystem_dir='json-{0}'.format( release ), show_only_latest=False )
    r.distroversion_list = [ 'resource' ]
    r.release_type_list = release_type_list
    r.full_clean()
    r.save()

  for release, release_type_list in release_list:
    r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', description='Docker - {0}'.format( release.title() ), manager_type='docker', name='docker-{0}'.format( release ), filesystem_dir='docker-{0}'.format( release ), show_only_latest=False )
    r.distroversion_list = [ 'docker' ]
    r.release_type_list = release_type_list
    r.full_clean()
    r.save()

  for release, release_type_list in release_list:
    r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', description='PYPI - {0}'.format( release.title() ), manager_type='pypi', name='pypi-{0}'.format( release ), filesystem_dir='pypi-{0}'.format( release ), show_only_latest=False )
    r.distroversion_list = [ 'pypi' ]
    r.release_type_list = release_type_list
    r.full_clean()
    r.save()

  for release, release_type_list in release_list:
    r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', description='OVA - {0}'.format( release.title() ), manager_type='ova', name='ova-{0}'.format( release ), filesystem_dir='ova-{0}'.format( release ), show_only_latest=False )
    r.distroversion_list = [ 'ova' ]
    r.release_type_list = release_type_list
    r.full_clean()
    r.save()


def load_distro_versions( app, schema_editor ):
  for version in ( 'trusty', 'xenial', 'bionic' ):
    d = DistroVersion( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', name=version, file_type='deb', version=version, release_names=version, distro='debian' )
    d.full_clean()
    d.save()

  for version, release_name, name in ( ( '6', 'el6', 'centos6' ), ( '7', 'el7', 'centos7' ) ):
    d = DistroVersion( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', name=name, file_type='rpm', version=version, release_names=release_name, distro='centos' )
    d.full_clean()
    d.save()

  for version, name in ( ( 'sles11', '11' ), ( 'sles12', '12' ) ):
    d = DistroVersion( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', name=version, file_type='rpm', version=version, release_names=name, distro='sles' )
    d.full_clean()
    d.save()

  d = DistroVersion( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', name='resource', file_type='rsc', distro='none' )
  d.full_clean()
  d.save()

  d = DistroVersion( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', name='docker', file_type='docker', distro='none' )
  d.full_clean()
  d.save()

  d = DistroVersion( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', name='pypi', file_type='python', distro='none' )
  d.full_clean()
  d.save()

  d = DistroVersion( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', name='ova', file_type='ova', distro='none' )
  d.full_clean()
  d.save()


def load_tags( app, schema_editor ):
  type_list = (  )

  for name, description, level in type_list:
    t = Tag( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', name=name, level=level, change_control_required=( name == 'prod' ), description=description )
    t.full_clean()
    t.save()


def load_mirrors( app, schema_editor ):
  m = Mirror( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', name='prod', description='Production', psk='prod' )
  repo_list = []
  for release in ( 'prod', ):
    repo_list += [ 'apt-{0}'.format( release ), 'yum-{0}'.format( release ), 'json-{0}'.format( release ), 'docker-{0}'.format( release ), 'pypi-{0}'.format( release ) ]
  m.repo_list = repo_list
  m.full_clean()
  m.save()

  m = Mirror( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', name='stage', description='Staging', psk='stage' )
  repo_list = []
  for release in ( 'stage', ):
    repo_list += [ 'apt-{0}'.format( release ), 'yum-{0}'.format( release ), 'json-{0}'.format( release ), 'docker-{0}'.format( release ), 'pypi-{0}'.format( release ) ]
  m.repo_list = repo_list
  m.full_clean()
  m.save()

  m = Mirror( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', name='dev', description='Developent', psk='dev' )
  repo_list = []
  for release in ( 'dev', ):
    repo_list += [ 'apt-{0}'.format( release ), 'yum-{0}'.format( release ), 'json-{0}'.format( release ), 'docker-{0}'.format( release ), 'pypi-{0}'.format( release ) ]
  m.repo_list = repo_list
  m.full_clean()
  m.save()


load_superuser()
load_repos()
load_distro_versions()
load_tags()
load_mirrors()
