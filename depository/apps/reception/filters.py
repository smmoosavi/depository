#!/usr/bin/env python
# vim: ts=4 sw=4 et

from django_filters import rest_framework as filters

from depository.apps.reception.models import Delivery


class DeliveryFilter(filters.FilterSet):
    first_name = filters.CharFilter()
    last_name = filters.CharFilter()
    country = filters.CharFilter()
    phone = filters.CharFilter()
    passport_id = filters.CharFilter()

    class Meta:
        model = Delivery
        fields = ()

    def filter_first_name(self, qs, name, value):
        return qs.filter(pilgrim__first_name=value)

    def filter_last_name(self, qs, name, value):
        return qs.filter(pilgrim__last_name=value)

    def filter_country(self, qs, name, value):
        return qs.filter(pilgrim__country=value)

    def filter_phone(self, qs, name, value):
        return qs.filter(pilgrim__phone=value)

    def filter_passport_id(self, qs, name, value):
        return qs.filter(pilgrim__passport_id=value)
