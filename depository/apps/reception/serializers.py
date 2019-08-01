from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from depository.apps.accounting.models import Pilgrim
from depository.apps.reception.models import Delivery, Pack
from depository.apps.reception.services import CellAssigner
from depository.apps.structure.models import Cell
from django.utils.translation import ugettext as _

from depository.apps.utils.utils import sub_dict


class ReceptionTakeSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.CharField()
    country = serializers.CharField()
    passport_id = serializers.CharField(required=False)
    bag_count = serializers.IntegerField(required=False)
    suitcase_count = serializers.IntegerField(required=False)
    pram_count = serializers.IntegerField(required=False)

    def validate(self, attrs):
        if not {'bag_count', 'pram_count', 'suitcase_count'}.intersection(attrs):
            raise ValidationError(
                _("At least one of following fields is required: bag_count,'pram_count, suitcase_count")
            )
        return attrs

    def get_pilgrim(self, data):
        pilgrim_data = sub_dict(data, ['first_name', 'last_name', 'phone', 'country', 'passport_id'])
        pilgrim, is_created = Pilgrim.objects.get_or_create(**pilgrim_data)
        return pilgrim

    def create(self, data):
        pilgrim = self.get_pilgrim(data)
        size = Cell.SIZE_LARGE if data.get('pram_count') else Cell.SIZE_SMALL
        free_cell = CellAssigner().assign_cell(size)
        if not free_cell:
            raise ValidationError(_("All spaces are busy"))
        delivery_data = {'pilgrim': pilgrim, 'taker': self.context['request'].user}
        delivery = Delivery.objects.create(**delivery_data)
        pack_data = sub_dict(data, ['bag_count', 'suitcase_count', 'pram_count'])
        pack_data['delivery'] = delivery
        pack_data['cell'] = free_cell
        Pack.objects.create(**pack_data)
        return data


class ReceptionGiveSerializer(serializers.Serializer):
    hash_id = serializers.CharField()

    def validate(self, attrs):
        delivery = get_object_or_404(Delivery.objects.all(), hash_id=attrs['hash_id'])
        if delivery.giver or delivery.exited_at:
            raise ValidationError(_("This pack has been given to the owner"))
        return attrs

    def create(self, data):
        delivery = get_object_or_404(Delivery.objects.all(), hash_id=data['hash_id'])
        delivery.giver = self.context['request'].user
        delivery.exit_type = Delivery.DELIVERED_TO_CUSTOMER
        delivery.exited_at = timezone.now()
        delivery.save()
        return data


class DeliverySerializer(serializers.ModelSerializer):
    pack = serializers.SerializerMethodField()

    class Meta:
        model = Delivery
        fields = (
            'pilgrim', 'taker', 'giver', 'hash_id', 'entered_at', 'exited_at',
            'exit_type', 'pack'
        )

    def get_pack(self, obj):
        return obj.packs
