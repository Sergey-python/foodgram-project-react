from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from rest_framework.exceptions import ValidationError


class SerializerPasswordValidation:
    @staticmethod
    def validate_user_password(password_value, password_field, user):
        try:
            validate_password(password_value, user)
        except django_exceptions.ValidationError as e:
            raise ValidationError({password_field: list(e.messages)})
