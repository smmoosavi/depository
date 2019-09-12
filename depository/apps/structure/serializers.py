from django.conf import settings
from django.utils import timezone
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from depository.apps.reception.models import Pack
from depository.apps.structure.helpers import CodeHelper, ConstantHelper
from depository.apps.structure.models import Cell, Cabinet, Row


class CabinetCreateSerializer(serializers.Serializer):
    code = serializers.IntegerField(required=False)
    num_of_rows = serializers.IntegerField()
    num_of_cols = serializers.IntegerField()
    size = serializers.ChoiceField(
        Cell.SIZE_CHOICES, default=Cell.SIZE_SMALL
    )
    first_row_size = serializers.ChoiceField(
        Cell.SIZE_CHOICES, default=Cell.SIZE_SMALL
    )

    def create(self, data):
        cabinet_code = data.get('code')
        if not cabinet_code:
            last_cabinet = Cabinet.objects.order_by('-code').first()
            if last_cabinet:
                cabinet_code = last_cabinet.code + 1
            else:
                cabinet_code = 10
        cabinet = Cabinet.objects.create(code=cabinet_code, depository_id=settings.DEFAULT_DEPOSITORY_ID)
        for row_idx in range(data['num_of_rows']):
            row = Row.objects.create(code=str(row_idx + 1), cabinet=cabinet)
            for col_idx in range(data['num_of_cols']):
                size = Cell.SIZE_SMALL
                if row_idx == 0 and data['first_row_size'] == Cell.SIZE_LARGE:
                    size = Cell.SIZE_LARGE
                Cell.objects.create(code=str(col_idx), row=row, size=size)
        return cabinet


class StatusSerializer(serializers.Serializer):
    code = serializers.CharField()
    is_healthy = serializers.BooleanField()

    def create(self, data):
        cabinet, row, cell = CodeHelper().to_code(data['code'])
        if cell:
            cell = get_object_or_404(Cell.objects.all(), code=cell, row__code=row, row__cabinet__code=cabinet)
            cell.is_healthy = data['is_healthy']
            cell.save()
        elif row:
            row = get_object_or_404(Row.objects.all(), code=row, cabinet__code=cabinet)
            row.cells.update(is_healthy=data['is_healthy'])
        elif cabinet:
            cabinet = get_object_or_404(Cabinet.objects.all(), code=cabinet)
            Cell.objects.filter(row__cabinet=cabinet).update(is_healthy=data['is_healthy'])
        return data


class CellSerializer(serializers.ModelSerializer):
    code = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()

    class Meta:
        model = Cell
        fields = '__all__'

    def get_code(self, obj):
        return CodeHelper().to_str(obj.row.cabinet.code, obj.row.code, obj.code)

    def get_age(self, obj):
        pack = Pack.objects.filter(cell=obj, exited_at__isnull=True).last()
        if not pack or pack.delivery.exited_at:
            return -1
        age = (timezone.now() - pack.delivery.entered_at).total_seconds() // 3600
        days = int(ConstantHelper().get(settings.CONST_KEY_STORE_THRESHOLD, "1"))
        if 0 <= age <= (days * 24):
            return 0
        else:
            return 1


class RowSerializer(serializers.ModelSerializer):
    cells = serializers.SerializerMethodField()

    class Meta:
        model = Row
        fields = '__all__'

    def get_cells(self, obj):
        return CellSerializer(obj.cells, many=True).data


class CabinetSerializer(serializers.ModelSerializer):
    rows = serializers.SerializerMethodField()

    class Meta:
        model = Cabinet
        fields = ('code', 'rows')

    def get_rows(self, obj):
        return RowSerializer(obj.rows, many=True).data
