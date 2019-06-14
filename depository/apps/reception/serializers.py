from rest_framework import serializers


class ReceptionTakeSerializer(serializers.BaseSerializer):
    # TODO: add creation fields

    def save(self, **kwargs):
        # TODO: create user if needed & create Pack, Delivery
        pass


class ReceptionGiveSerializer(serializers.BaseSerializer):
    # TODO: add creation fields

    def save(self, **kwargs):
        # TODO: create user if needed & create Pack, Delivery
        pass
