#!/usr/bin/env python
# vim: ts=4 sw=4 et
import logging

logger = logging.getLogger(__name__)
from django_filters import rest_framework as filters

from depository.apps.reception.models import Delivery


class DeliveryFilter(filters.FilterSet):
    first_name = filters.CharFilter(method='filter_field')
    last_name = filters.CharFilter(method='filter_field')
    country = filters.CharFilter(method='filter_field')
    phone = filters.CharFilter(method='filter_field')
    passport_id = filters.CharFilter(method='filter_field')
    in_house = filters.BooleanFilter(method='filter_in_house')
    in_store = filters.BooleanFilter(method='filter_in_store')

    class Meta:
        model = Delivery
        fields = ()

    def filter_field(self, qs, name, value):
        query = {f"pilgrim__{name}__icontains":value}
        return qs.filter(**query)

    def filter_in_house(self, qs, name, value):
        if value:
            return qs.filter(exited_at__isnull=True)
        else:
            return qs.filter(exited_at__isnull=False)

    def filter_in_store(self, qs, name, value):
        if value:
            return qs.filter(exit_type=Delivery.DELIVERED_TO_STORE)
        else:
            return qs.exclude(exit_type=Delivery.DELIVERED_TO_STORE)
