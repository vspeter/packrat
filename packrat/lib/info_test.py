import pytest
import os
from packrat.lib.info import infoDetect
import importlib.util


def load_resources():
  path = os.path.realpath( os.path.join( os.path.dirname( __file__ ), '..', '..', 'lib/setup/setupHelper.py' ) )
  spec = importlib.util.spec_from_file_location( 'setupHelper', path )
  helper = importlib.util.module_from_spec( spec )
  spec.loader.exec_module( helper )
  helper.load()


class FakeFile:
  def __init__( self, filename ):
    super().__init__()
    self.name = filename
    self.filepath = os.path.join( 'test_resources', filename )
    self.file = open( self.filepath, 'rb' )


def info_dump( info ):
  return ( info.filename, info.package, info.arch, info.version, info.type )


def test_detect( mocker ):
  assert info_dump( infoDetect( FakeFile( 'test_0.1-2_all.deb' ), None ) ) == ( 'test_0.1-2_all', 'test', 'all', '0.1-2', 'deb' )
  assert info_dump( infoDetect( FakeFile( 'docker-test_0.0.tar' ), None ) ) == ( 'docker-test_0.0', 'docker-test', 'all', '0.0', 'docker' )
  assert info_dump( infoDetect( FakeFile( 'thevm_2.3.ova' ), None ) ) == ( 'thevm_2.3', 'thevm', 'all', '2.3', 'ova' )
  assert info_dump( infoDetect( FakeFile( 'package1_1.2.3.tar.gz' ), None ) ) == ( 'package1_1.2.3', 'package1', 'all', '1.2.3', 'tar' )
  assert info_dump( infoDetect( FakeFile( 'pytest-0.0.0.tar.gz' ), None ) ) == ( 'pytest-0.0.0', 'pytest', 'all', '0.0.0', 'python' )
  assert info_dump( infoDetect( FakeFile( 'bob_1.1.respkg' ), None ) ) == ( 'bob_1.1', 'bob', 'all', '1.1', 'respkg' )
  assert info_dump( infoDetect( FakeFile( 'jane_0.9.appimage' ), None ) ) == ( 'jane_0.9', 'jane', 'all', '0.9', 'appimage' )

  assert info_dump( infoDetect( FakeFile( 'test_0.1-2_all.deb' ), 'deb' ) ) == ( 'test_0.1-2_all', 'test', 'all', '0.1-2', 'deb' )
  assert info_dump( infoDetect( FakeFile( 'docker-test_0.0.tar' ), 'docker' ) ) == ( 'docker-test_0.0', 'docker-test', 'all', '0.0', 'docker' )
  assert info_dump( infoDetect( FakeFile( 'thevm_2.3.ova' ), 'ova' ) ) == ( 'thevm_2.3', 'thevm', 'all', '2.3', 'ova' )
  assert info_dump( infoDetect( FakeFile( 'package1_1.2.3.tar.gz' ), 'tar' ) ) == ( 'package1_1.2.3', 'package1', 'all', '1.2.3', 'tar' )
  assert info_dump( infoDetect( FakeFile( 'pytest-0.0.0.tar.gz' ), 'python' ) ) == ( 'pytest-0.0.0', 'pytest', 'all', '0.0.0', 'python' )
  assert info_dump( infoDetect( FakeFile( 'bob_1.1.respkg' ), 'respkg' ) ) == ( 'bob_1.1', 'bob', 'all', '1.1', 'respkg' )
  assert info_dump( infoDetect( FakeFile( 'jane_0.9.appimage' ), 'appimage' ) ) == ( 'jane_0.9', 'jane', 'all', '0.9', 'appimage' )

  assert info_dump( infoDetect( FakeFile( 'jane_0.9.AppImage' ), None ) ) == ( 'jane_0.9', 'jane', 'all', '0.9', 'appimage' )
  assert info_dump( infoDetect( FakeFile( 'jane_0.9.AppImage' ), 'appimage' ) ) == ( 'jane_0.9', 'jane', 'all', '0.9', 'appimage' )

  assert info_dump( infoDetect( FakeFile( 'package1_1.2.3.tar.gz' ), 'bob' ) ) == ( 'package1_1.2.3', 'package1', 'all', '1.2.3', 'bob' )

  assert info_dump( infoDetect( FakeFile( 'bogusfile_0.0.bob.stuff' ), None ) ) == ( 'bogusfile_0.0.bob', 'bogusfile', 'all', '0.0.bob', 'resource' )
  assert info_dump( infoDetect( FakeFile( 'bogusfile_0.0.bob.stuff' ), 'sally' ) ) == ( 'bogusfile_0.0.bob', 'bogusfile', 'all', '0.0.bob', 'sally' )

  assert infoDetect( FakeFile( 'bogusfile.noversion.stuff' ), None ) is None
  assert infoDetect( FakeFile( 'bogusfile.noversion.stuff' ), 'resource' ) is None

  with pytest.raises( ValueError ):
    infoDetect( FakeFile( 'bogusfile_0.0.bob.stuff' ), 'in val id' )


@pytest.mark.django_db
def test_distroversion_list( mocker ):
  load_resources()

  infoDetect( FakeFile( 'test_0.1-2_all.deb' ), None ).distroversion_list == [ 'trusty', 'xenial', 'bionic' ]
  infoDetect( FakeFile( 'docker-test_0.0.tar' ), None ).distroversion_list == [ 'docker' ]
  infoDetect( FakeFile( 'package1_1.2.3.tar.gz' ), None ).distroversion_list == [ 'tar' ]
  infoDetect( FakeFile( 'pytest-0.0.0.tar.gz' ), None ).distroversion_list == [ 'pypy' ]
  infoDetect( FakeFile( 'thevm_2.3.ova' ), None ).distroversion_list == [ 'ova' ]
  infoDetect( FakeFile( 'bob_1.1.respkg' ), None ).distroversion_list == [ 'respkg' ]
  infoDetect( FakeFile( 'bogusfile_0.0.bob.stuff' ), None ).distroversion_list == [ 'resource' ]

  infoDetect( FakeFile( 'bogusfile_0.0.bob.stuff' ), 'something' ).distroversion_list == []
