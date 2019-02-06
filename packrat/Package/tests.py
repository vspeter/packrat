import pytest

from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.storage import Storage
from django.core.exceptions import ValidationError

from cinp.server_common import NotAuthorized

from packrat.Package.models import Package, PackageFile
from packrat.Attrib.models import Tag, DistroVersion
from packrat.lib.info_test import FakeFile, load_resources, infoDetect


def load_test_package( mocker, user, filename, dv, type=None ):
  f = FakeFile( filename )
  file_mock = mocker.MagicMock( spec=File, name='FileMock' )
  file_mock.name = f.name
  file_mock.file = f.file
  storage_mock = mocker.MagicMock( spec=Storage, name='StorageMock' )
  storage_mock.url = mocker.MagicMock( name='url' )
  storage_mock.url.return_value = f.filepath

  PackageFile.create( user, file_mock, 'testing', 'testing', dv, type )


@pytest.mark.django_db
def test_distroversion_list( mocker ):
  load_resources()

  f = FakeFile( 'test_0.1-2_all.deb' )
  file_mock = mocker.MagicMock( spec=File, name='FileMock' )
  file_mock.name = f.name
  file_mock.file = f.file
  assert PackageFile.distroversionOptions( f ) == [ 'trusty', 'xenial', 'bionic' ]

  print( infoDetect( FakeFile( 'bogusfile_0.0.bob.stuff' ), None ).distroversion_list )

  f = FakeFile( 'bogusfile_0.0.bob.stuff' )
  file_mock = mocker.MagicMock( spec=File, name='FileMock' )
  file_mock.name = f.name
  file_mock.file = f.file
  assert PackageFile.distroversionOptions( f ) == [ 'resource' ]

  f = FakeFile( 'bogusfile_0.0.bob.stuff' )
  file_mock = mocker.MagicMock( spec=File, name='FileMock' )
  file_mock.name = f.name
  file_mock.file = f.file
  assert PackageFile.distroversionOptions( f, 'asdf' ) == []


@pytest.mark.django_db
def test_load_file( mocker ):
  load_resources()

  root = User.objects.get( username='root' )
  p = Package( name='test' )
  p.full_clean()
  p.save()
  p = Package( name='bogusfile' )
  p.full_clean()
  p.save()

  with pytest.raises( ValueError ):
    load_test_package( mocker, root, 'test_0.1-2_all.deb', 'bionic', 'sdf e' )
  load_test_package( mocker, root, 'test_0.1-2_all.deb', 'bionic' )

  load_test_package( mocker, root, 'bogusfile_0.0.bob.stuff', 'resource' )

  # TODO more?


@pytest.mark.django_db
def test_tagging_requirements( mocker ):
  load_resources()

  dev = Tag.objects.get( name='dev' )
  stage = Tag.objects.get( name='stage' )
  prod = Tag.objects.get( name='prod' )

  root = User.objects.get( username='root' )
  p = Package( name='test' )
  p.full_clean()
  p.save()

  load_test_package( mocker, root, 'test_0.1-2_all.deb', 'bionic' )
  pf = p.packagefile_set.get()

  assert pf.tags == ''

  with pytest.raises( ValueError ):
    pf.tag( root, stage )
  with pytest.raises( ValueError ):
    pf.tag( root, prod )
  pf.tag( root, dev )
  assert pf.tags == 'dev'
  with pytest.raises( ValidationError ):
    pf.tag( root, dev )
  assert pf.tags == 'dev'

  with pytest.raises( ValueError ):
    pf.tag( root, prod )
  pf.tag( root, stage )
  assert pf.tags == 'dev, stage'
  with pytest.raises( ValidationError ):
    pf.tag( root, stage )
  assert pf.tags == 'dev, stage'

  with pytest.raises( ValueError ):
    pf.tag( root, prod )
  pf.tag( root, prod, 'test' )
  assert pf.tags == 'dev, prod, stage'
  with pytest.raises( ValidationError ):
    pf.tag( root, prod, 'test' )
  assert pf.tags == 'dev, prod, stage'


@pytest.mark.django_db
def test_tagging_users( mocker ):
  load_resources()

  dev = Tag.objects.get( name='dev' )
  stage = Tag.objects.get( name='stage' )
  prod = Tag.objects.get( name='prod' )

  root = User.objects.get( username='root' )
  mcp = User.objects.get( username='mcp' )
  nullunit = User.objects.get( username='nullunit' )
  manager = User.objects.get( username='manager' )

  p = Package( name='test' )
  p.full_clean()
  p.save()

  load_test_package( mocker, root, 'test_0.1-2_all.deb', 'bionic' )
  pf = p.packagefile_set.get()

  assert pf.tags == ''

  with pytest.raises( NotAuthorized ):
    pf.tag( nullunit, dev )
  pf.tag( mcp, dev )
  assert pf.tags == 'dev'

  with pytest.raises( NotAuthorized ):
    pf.tag( nullunit, stage )
  pf.tag( manager, stage )
  assert pf.tags == 'dev, stage'

  with pytest.raises( NotAuthorized ):
    pf.tag( nullunit, prod )
  with pytest.raises( NotAuthorized ):
    pf.tag( mcp, prod )
  pf.tag( manager, prod, 'test' )
  assert pf.tags == 'dev, prod, stage'


@pytest.mark.django_db
def test_package_deprocate( mocker ):
  load_resources()

  dev = Tag.objects.get( name='dev' )

  root = User.objects.get( username='root' )

  p = Package( name='test' )
  p.full_clean()
  p.save()

  load_test_package( mocker, root, 'test_0.1-2_all.deb', 'bionic' )
  pf = p.packagefile_set.get()

  assert pf.deprocated_by is None
  assert pf.deprocated_at is None
  assert pf.failed_by is None
  assert pf.failed_at is None
  assert pf.tags == ''

  pf.deprocate( root )
  assert pf.deprocated_by == 'root'
  assert pf.deprocated_at is not None
  assert pf.failed_by is None
  assert pf.failed_at is None
  with pytest.raises( ValueError ):
    pf.tag( root, dev )
  with pytest.raises( ValueError ):
    pf.fail( root )
  assert pf.tags == ''
  pf.deprocate( root )
  assert pf.deprocated_by == 'root'
  assert pf.deprocated_at is not None
  assert pf.failed_by is None
  assert pf.failed_at is None
  assert pf.tags == ''

  pf.deprocated_at = None
  pf.deprocated_by = None
  pf.full_clean()
  pf.save()

  assert pf.deprocated_by is None
  assert pf.deprocated_at is None
  assert pf.failed_by is None
  assert pf.failed_at is None

  pf.fail( root )
  assert pf.deprocated_by is None
  assert pf.deprocated_at is None
  assert pf.failed_by == 'root'
  assert pf.failed_at is not None
  with pytest.raises( ValueError ):
    pf.tag( root, dev )
  with pytest.raises( ValueError ):
    pf.deprocate( root )
  assert pf.tags == ''
  pf.fail( root )
  assert pf.deprocated_by is None
  assert pf.deprocated_at is None
  assert pf.failed_by == 'root'
  assert pf.failed_at is not None
  assert pf.tags == ''

  pf.failed_at = None
  pf.failed_by = None
  pf.full_clean()
  pf.save()

  pf.tag( root, dev )
  assert pf.tags == 'dev'


@pytest.mark.django_db
def test_package_filters():
  pass
  # TODO


@pytest.mark.django_db
def test_failing_users( mocker ):
  load_resources()

  root = User.objects.get( username='root' )
  mcp = User.objects.get( username='mcp' )
  nullunit = User.objects.get( username='nullunit' )
  manager = User.objects.get( username='manager' )

  p = Package( name='test' )
  p.full_clean()
  p.save()

  load_test_package( mocker, root, 'test_0.1-2_all.deb', 'bionic' )
  pf = p.packagefile_set.get()

  # TODO
