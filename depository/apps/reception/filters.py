#!/usr/bin/env python
# vim: ts=4 sw=4 et

from django_filters import rest_framework as filters

from depository.apps.reception.models import Delivery


class DeliveryFilter(filters.FilterSet):
    class Meta:
        model = Delivery
        fields = ('pilgrim', 'taker', 'giver', 'hash_id',)
