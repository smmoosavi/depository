# Generated by Django 2.2.4 on 2019-08-20 07:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('reception', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delivery',
            name='exit_type',
            field=models.IntegerField(
                blank=True,
                choices=[(0, 'delivered to customer'), (1, 'delivered to store'), (2, 'Missed')],
                null=True),
        ),
    ]
