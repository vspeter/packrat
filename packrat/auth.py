from django.contrib.auth.models import User
from django import db
from django.db.models import signals
from tastypie import authentication
from tastypie import authorization
from tastypie import exceptions
from tastypie import models as auth_models
from tastypie.resources import ModelResource


# auto create and api_key when a user is added
signals.post_save.connect(auth_models.create_api_key, sender=User)


class UserResource(ModelResource):
    """Resource for managing user accounts"""
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        detail_uri_name = 'username'

        # use basic auth for the django user to authenticate
        authentication = authentication.BasicAuthentication()
        # DjangoAuthorization will limit user api use to superuser accounts
        authorization = authorization.DjangoAuthorization()

        # fieds that can be
        allowed_update_fields = [
            'password', 'first_name', 'last_name',
            'is_active', 'is_staff', 'is_superuser'
        ]

    def obj_create(self, bundle, request=None, **kwargs):
        """Implement custom object create method
        to handle the hashing of the password"""

        req_data = bundle.data
        username = req_data['username']
        email = req_data.get('email', '')
        password = req_data.get('password')

        try:
            bundle.obj = User.objects.create_user(
                username=username, email=email, password=password)
        except db.IntegrityError:
            raise exceptions.BadRequest('That username already exists')

        return bundle

    def obj_update(self, bundle, request=None, **kwargs):
        """Implement custom update method to restrict the fields
        that are updated and to correctly set the hashed password"""

        req_data = bundle.data

        # settable fields are all fields included in the request
        # data that are also specified in allowed_update_fields.
        # "password" is not directly settable as it has to be
        # hashed before saving.
        settable_fields = [
            field for field in req_data
            if field in self._meta.allowed_update_fields
            and field != 'password'
        ]

        for field in settable_fields:
            setattr(bundle.obj, field, req_data[field])

        # if a new password is supplied in the request, hash the
        # password with the built-in set_password method and
        # update the request data
        password = req_data.get('password')
        if password:
            bundle.obj.set_password(password)
            bundle.data['password'] = bundle.obj.password

        return super(UserResource, self).obj_update(bundle, **kwargs)
