import pytest
from django.core.exceptions import ValidationError

from packrat.Repos.models import ReleaseType


@pytest.mark.django_db
def test_releasetype():
  r = ReleaseType()
  with pytest.raises( ValidationError ):
    r.full_clean()

  r = ReleaseType( name='test' )
  with pytest.raises( ValidationError ):
    r.full_clean()

  r = ReleaseType( name='test', level=10 )
  with pytest.raises( ValidationError ):
    r.full_clean()

  r = ReleaseType( name='test', level=10, description='test' )
  r.full_clean()

  r = ReleaseType( name='new', level=10, description='test' )
  with pytest.raises( ValidationError ):
    r.full_clean()

  r = ReleaseType( name='depr', level=10, description='test' )
  with pytest.raises( ValidationError ):
    r.full_clean()

  # yhese two will fail b/c the preloaded data in the migration allready loaded them
  # r = ReleaseType( name='new', level=1, description='test' )
  # r.full_clean()
  #
  # r = ReleaseType( name='depr', level=100, description='test' )
  # r.full_clean()

  r = ReleaseType( name='test', level=1, description='test' )
  with pytest.raises( ValidationError ):
    r.full_clean()

  r = ReleaseType( name='test', level=100, description='test' )
  with pytest.raises( ValidationError ):
    r.full_clean()

  for level in ( 0, -2, 101, 1000, 1234 ):
    r = ReleaseType( name='test', level=level, description='test' )
    with pytest.raises( ValidationError ):
      r.full_clean()

  for name in ( 'test*', '*', '' ):
    r = ReleaseType( name=name, level=10, description='test' )
    with pytest.raises( ValidationError ):
      r.full_clean()
