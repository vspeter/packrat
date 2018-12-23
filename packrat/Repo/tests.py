import pytest
from django.core.exceptions import ValidationError

from packrat.Repos.models import Tag


@pytest.mark.django_db
def test_tag():
  t = Tag()
  with pytest.raises( ValidationError ):
    t.full_clean()

  t = Tag( name='test' )
  t.full_clean()

  for name in ( 'test*', '*', '' ):
    t = Tag( name=name )
    with pytest.raises( ValidationError ):
      t.full_clean()

  t1 = Tag( name='t1' )
  t1.full_clean()
  t1.save()

  t2 = Tag( name='t2' )
  t2.full_clean()
  t2.save()

  t2.allowed_tags += t1
  t2.full_clean()
  t2.save()

  t1.allowed_tags += t2
  with pytest.raises( ValidationError ):
    t1.full_clean()
