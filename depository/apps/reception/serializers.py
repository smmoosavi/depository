from rest_framework import serializers

from depository.apps.reception.models import Delivery


class ReceptionTakeSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.CharField()
    country = serializers.CharField()
    bag_count = serializers.IntegerField()
    suitcase_count = serializers.IntegerField()
    pram_count = serializers.IntegerField()

    def save(self, **kwargs):
        # TODO: create user if needed & create Pack, Delivery
        pass


class ReceptionGiveSerializer(serializers.BaseSerializer):
    hash_id = serializers.CharField()

    def save(self, **kwargs):
        # TODO: create user if needed & create Pack, Delivery
        pass


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
