from django.contrib.auth import hashers
from django.contrib.auth.models import User
from django.core import exceptions as django_exceptions
from django import db
from django.db.models import signals
from tastypie import authentication
from tastypie import authorization
from tastypie import exceptions as api_exceptions
from tastypie import models as auth_models
from tastypie.resources import ModelResource


# auto create and api_key when a user is added
signals.post_save.connect(auth_models.create_api_key, sender=User)


class UserResource(ModelResource):
    """Resource for managing user accounts"""
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        # allow user to be retrieved by username instead of id
        detail_uri_name = 'username'

        # use basic auth for the django user to authenticate
        authentication = authentication.BasicAuthentication()
        # DjangoAuthorization will limit user api use to superuser accounts
        authorization = authorization.DjangoAuthorization()

        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'put', 'delete']

        # excludes fields from all resources
        excludes = ['is_superuser', 'is_staff', 'is_active']

        exclude_from_reads = ['password']

    def full_dehydrate(self, bundle, for_list=False):
        """Override the `full_dehydrate` method to remove fields that should
        not be returned in GET requests.

        The `excludes` attribute will exclude fields for both read
        and write requests.  There are some fields, such as a password
        field, where it i snot desirable to exclude from an update, but
        should be excluded from a GET request.

        This implementation will take any field listed in the
        `exclude_from_reads` attribute and remove that field from
        data returned in a GET request.
        """

        bundle = super(UserResource, self).full_dehydrate(
            bundle, for_list=False)
        for field in self._meta.exclude_from_reads:
            if field in bundle.data.keys():
                del bundle.data[field]
        return bundle

    def hydrate_password(self, bundle):
        """Custom hydrate method to correctly hash a raw password
        sent it in by a client request."""

        raw_password = bundle.data['password']
        bundle.data['password'] = hashers.make_password(raw_password)
        return bundle

    def obj_create(self, bundle, request=None, **kwargs):
        """Implement custom object create method
        to handle the hashing of the password"""

        req_data = bundle.data
        username = req_data['username']
        email = req_data.get('email', '')
        password = req_data.get('password')
        first_name = req_data.get('first_name', '')
        last_name = req_data.get('last_name', '')

        try:
            bundle.obj = User.objects.create_user(
                username=username, email=email, password=password,
                first_name=first_name, last_name=last_name)

        except db.IntegrityError:
            raise api_exceptions.BadRequest('That username already exists')

        return bundle

    def obj_delete(self, bundle, **kwargs):
        """
        Implements custom delete method that performs a
        "soft delete" by setting `is_active` to False.
        """
        if not hasattr(bundle.obj, 'delete'):
            try:
                bundle.obj = self.obj_get(bundle=bundle, **kwargs)
            except django_exceptions.ObjectDoesNotExist:
                raise api_exceptions.NotFound(
                    "A model instance matching the provided "
                    "arguments could not be found.")

        self.authorized_delete_detail(
            self.get_object_list(bundle.request), bundle)
        bundle.obj.is_active = False
        bundle.obj.save()
