import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from packrat.Attrib.models import Tag


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

  t3 = Tag( name='t3' )
  t3.full_clean()
  t3.save()

  t1.required_list = [ t2 ]
  t1.full_clean()
  t1.save()

  t2.required_list = [ t1 ]
  with pytest.raises( ValidationError ):
    t2.full_clean()

  t2.required_list = [ t2 ]
  with pytest.raises( ValidationError ):
    t2.full_clean()

  t2.required_list = [ t3 ]
  t2.change_control_required = True
  t2.full_clean()
  t2.save()

  assert Tag.tagMap() == { 't1': { 'change_control': False, 'requred': [ 't2' ] }, 't2': { 'change_control': True, 'requred': [ 't3' ] }, 't3': { 'change_control': False, 'requred': [] } }

  t1.required_list = [ t2, t3 ]
  t1.full_clean()
  t1.save()

  t2.required_list = []
  t2.full_clean()
  t2.save()

  assert Tag.tagMap() == { 't1': { 'change_control': False, 'requred': [ 't2', 't3' ] }, 't2': { 'change_control': True, 'requred': [] }, 't3': { 'change_control': False, 'requred': [] } }

  assert [ i.codename for i in Permission.objects.filter( content_type=ContentType.objects.get_for_model( Tag ) ) ] == [ 'tag_t1', 'tag_t2', 'tag_t3' ]
