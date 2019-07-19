from rest_framework import serializers

from depository.apps.structure.models import Cell, Cabinet, Row


class CabinetCreateSerializer(serializers.Serializer):
    name = serializers.CharField()
    num_of_rows = serializers.IntegerField()
    num_of_cols = serializers.IntegerField()
    size = serializers.ChoiceField(
        Cell.SIZE_CHOICES, default=Cell.SIZE_SMALL
    )
    first_row_size = serializers.ChoiceField(
        Cell.SIZE_CHOICES, default=Cell.SIZE_SMALL
    )

    def create(self, validated_data):
        # TODO: create cabinet
        pass


class StatusSerializer(serializers.Serializer):
    code = serializers.CharField()
    is_healthy = serializers.BooleanField()


class CellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cell
        fields = '__all__'


class RowSerializer(serializers.ModelSerializer):
    cells = serializers.SerializerMethodField()

    class Meta:
        model = Row
        fields = '__all__'

    def get_cells(self, obj):
        return CellSerializer(obj.cells, many=True)


class CabinetSerializer(serializers.ModelSerializer):
    rows = serializers.SerializerMethodField()

    class Meta:
        model = Cabinet
        fields = ('code', 'rows')

    def get_rows(self, obj):
        return RowSerializer(obj.rows, many=True)
