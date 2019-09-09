from django.utils import timezone
from khayyam.jalali_datetime import JalaliDatetime
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from depository.apps.accounting.models import Pilgrim
from depository.apps.reception.models import Delivery, Pack
from depository.apps.reception.services import ReceptionHelper
from depository.apps.structure.models import Cell
from django.utils.translation import ugettext as _

from depository.apps.utils.utils import sub_dict


class ReceptionTakeSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.CharField(required=False)
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
        if attrs.get('bag_count', 0) and (attrs.get('pram_count', 0) or attrs.get('suitcase_count', 0)):
            raise ValidationError(
                _("The given combination of packs isn't valid, because size of bag and para/suitcase isn't equal.")
            )
        return attrs

    def get_pilgrim(self, data):
        pilgrim_data = sub_dict(data, ['first_name', 'last_name', 'phone', 'country', 'passport_id'])
        pilgrim, is_created = Pilgrim.objects.get_or_create(**pilgrim_data)
        return pilgrim

    def create(self, data):
        pilgrim = self.get_pilgrim(data)
        size = Cell.SIZE_LARGE if data.get('pram_count') else Cell.SIZE_SMALL
        free_cell = ReceptionHelper().assign_cell(size)
        if not free_cell:
            raise ValidationError(_("All spaces are busy"))
        delivery_data = {'pilgrim': pilgrim, 'taker': self.context['request'].user}
        delivery = Delivery.objects.create(**delivery_data)
        pack_data = sub_dict(data, ['bag_count', 'suitcase_count', 'pram_count'])
        pack_data['delivery'] = delivery
        pack_data['cell'] = free_cell
        pack = Pack.objects.create(**pack_data)
        rh = ReceptionHelper()
        rh.print(pack)

        return data


class ReceptionGiveSerializer(serializers.Serializer):
    hash_id = serializers.CharField()
    exited_at = serializers.SerializerMethodField()
    pilgrim = serializers.SerializerMethodField()

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

    def get_exited_at(self, obj):
        if obj.exited_at:
            return JalaliDatetime(obj.exited_at).strftime("%A %d %B %H:%M")

    def get_pilgrim(self, obj):
        return obj.pilgrim.get_full_name()


class PackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pack
        fields = '__all__'


class DeliverySerializer(serializers.ModelSerializer):
    pack = serializers.SerializerMethodField()
    pilgrim = serializers.SerializerMethodField()
    entered_at = serializers.SerializerMethodField()
    exited_at = serializers.SerializerMethodField()

    class Meta:
        model = Delivery
        fields = (
            'pilgrim', 'taker', 'giver', 'hash_id', 'entered_at', 'exited_at',
            'exit_type', 'pack'
        )

    def get_pack(self, obj):
        return PackSerializer(obj.packs, many=True).data

    def get_pilgrim(self, obj):
        return obj.pilgrim.get_full_name()

    def get_entered_at(self, obj):
        if obj.entered_at:
            return JalaliDatetime(obj.entered_at).strftime("%A %d %B %H:%M")

    def get_exited_at(self, obj):
        if obj.exited_at:
            return JalaliDatetime(obj.exited_at).strftime("%A %d %B %H:%M")
