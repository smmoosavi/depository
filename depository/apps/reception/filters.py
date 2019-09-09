#!/usr/bin/env python
# vim: ts=4 sw=4 et

from django_filters import rest_framework as filters

from depository.apps.reception.models import Delivery


class DeliveryFilter(filters.FilterSet):
    first_name = filters.CharFilter(method='filter_first_name')
    last_name = filters.CharFilter(method='filter_last_name')
    country = filters.CharFilter(method='filter_country')
    phone = filters.CharFilter(method='filter_phone')
    passport_id = filters.CharFilter(method='filter_passport_id')

    class Meta:
        model = Delivery
        fields = ()

    def filter_first_name(self, qs, name, value):
        return qs.filter(pilgrim__first_name__icontains=value)

    def filter_last_name(self, qs, name, value):
        return qs.filter(pilgrim__last_name__icontains=value)

    def filter_country(self, qs, name, value):
        return qs.filter(pilgrim__country__icontains=value)

    def filter_phone(self, qs, name, value):
        return qs.filter(pilgrim__phone__icontains=value)

    def filter_passport_id(self, qs, name, value):
        return qs.filter(pilgrim__passport_id__icontains=value)
