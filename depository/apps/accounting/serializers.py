from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy
from rest_framework import serializers

from depository.apps.accounting.models import Pilgrim


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password')


class PilgrimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pilgrim
        fields = '__all__'


class SignInSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        if all(data.values()):
            user = authenticate(username=data['username'], password=data['password'])
            if user:
                return {}
            else:
                msg = ugettext_lazy('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg)
        else:
            msg = ugettext_lazy('Must include "username" and "password".')
            raise serializers.ValidationError(msg)
