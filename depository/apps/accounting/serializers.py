import os
import tempfile

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy
from rest_framework import serializers

from depository.apps.accounting.helper import AccountHelper
from depository.apps.accounting.models import Pilgrim
from depository.apps.utils.excel import ExcelUtil


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password')


class ImportUserSerializer(serializers.Serializer):
    users = serializers.FileField()

    def create(self, validated_data):
        tup = tempfile.mkstemp(suffix='.xlsx')  # make a tmp file
        f = os.fdopen(tup[0], 'wb')  # open the tmp file for writing
        f.write(validated_data['users'].read())  # write the tmp file
        f.close()

        users_data = ExcelUtil().import_file(tup[1])
        for user_data in users_data[1:]:
            user = User.objects.create(username=user_data['username'])
            user.set_password(user_data['password'])
            user.save()
        return validated_data


class PilgrimSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Pilgrim
        fields = ('phone', 'country', 'name')

    def get_name(self, obj):
        return obj.get_full_name()


class SignInSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        if all(data.values()):
            user = authenticate(username=data['username'], password=data['password'])
            if user:
                return {
                    'token': AccountHelper().generate_jwt_token(user),
                    'user': user,
                }
            else:
                msg = ugettext_lazy('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg)
        else:
            msg = ugettext_lazy('Must include "email" and "password".')
            raise serializers.ValidationError(msg)
