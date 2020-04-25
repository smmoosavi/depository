from django.conf import settings
from django.db.models import QuerySet
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from django.utils.translation import ugettext as _
from depository.apps.accounting.serializers import PilgrimSerializer
from depository.apps.reception.models import Pack
from depository.apps.structure.helpers import CodeHelper, ConstantHelper
from depository.apps.structure.models import Cell, Cabinet, Row


class CabinetCreateSerializer(serializers.Serializer):
    code = serializers.CharField(required=False)
    num_of_rows = serializers.IntegerField(max_value=9, min_value=1)
    num_of_cols = serializers.IntegerField(max_value=9, min_value=1)
    size = serializers.ChoiceField(
        Cell.SIZE_CHOICES, default=Cell.SIZE_SMALL
    )
    first_row_size = serializers.ChoiceField(
        Cell.SIZE_CHOICES, default=Cell.SIZE_SMALL
    )

    def create(self, data):
        cabinet_code = data.get('code')
        if not cabinet_code:
            codes = list(map(
                lambda x: settings.FARSI_CHARS.index(x), Cabinet.objects.values_list('code', flat=True)
            ))

            if codes:
                cabinet_code = settings.FARSI_CHARS[max(codes) + 1]
            else:
                cabinet_code = 'آ'
        cabinet = Cabinet.objects.create(code=cabinet_code, depository_id=settings.DEFAULT_DEPOSITORY_ID)
        for row_idx in range(data['num_of_rows']):
            row = Row.objects.create(code=str(row_idx), cabinet=cabinet)
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
    pilgrim = serializers.SerializerMethodField()

    class Meta:
        model = Cell
        fields = '__all__'

    def get_code(self, obj):
        return CodeHelper().to_str(obj.row.cabinet.code, obj.row.code, obj.code)

    def get_age(self, obj):
        pack = Pack.objects.filter(cell=obj, delivery__exited_at__isnull=True).last()
        if not pack or pack.delivery.exited_at:
            return -1
        age = (timezone.now() - pack.delivery.entered_at).total_seconds() // 3600
        days = int(ConstantHelper().get(settings.CONST_KEY_STORE_THRESHOLD, "1"))
        if 0 <= age <= (days * 24):
            return 0
        else:
            return 1

    def get_pilgrim(self, obj):
        if not obj.pack or obj.pack.delivery.exited_at:
            return {}
        return PilgrimSerializer(obj.pack.delivery.pilgrim).data


class CabinetExtendSerializer(serializers.Serializer):
    num_of_rows = serializers.IntegerField()
    num_of_cols = serializers.IntegerField()

    def __init__(self, *args, **kwargs):
        self.cabinet = kwargs.pop('cabinet', None)
        super(CabinetExtendSerializer, self).__init__(*args, **kwargs)

    def validate_num_of_rows(self, data):
        if self.cabinet.rows.count() + data > 9:
            raise ValidationError(_('num_of_rows should be lower than %s') % (9 - data))
        return data

    def validate_num_of_cols(self, data):
        if self.cabinet.rows.count() + data > 9:
            raise ValidationError(_('num_of_cols should be lower than %s') % (9 - data))
        return data

    def create(self, data):
        if self.validated_data['num_of_cols']:
            cell = Cell.objects.filter(row__cabinet=self.cabinet).order_by('-code').first()
            first_index = 0
            if cell:
                first_index = cell.code + 1
            for row in self.cabinet.rows.all():
                size = row.cells.all()[0].size
                for index in range(self.validated_data['num_of_cols']):
                    Cell.objects.create(row=row, code=index + first_index, size=size)
        if self.validated_data['num_of_rows']:
            cells_count = self.cabinet.rows.all()[0].cells.count()
            first_index = 0
            one_row = self.cabinet.rows.order_by('-code').first()
            if one_row:
                first_index = one_row.code + 1
            for index in range(self.validated_data['num_of_rows']):
                row = Row.objects.create(cabinet=self.cabinet, code=index + first_index)
                for i in range(cells_count):
                    Cell.objects.create(row=row, code=i)
        self.cabinet.refresh_from_db()
        return self.cabinet


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
