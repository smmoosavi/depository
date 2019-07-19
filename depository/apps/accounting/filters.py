#!/usr/bin/env python
# vim: ts=4 sw=4 et

from django_filters import rest_framework as filters

from depository.apps.accounting.models import Pilgrim


class PilgrimFilter(filters.FilterSet):
    class Meta:
        model = Pilgrim
        fields = (
            'first_name', 'last_name', 'phone', 'country', 'city',
            'passport_id'
        )
