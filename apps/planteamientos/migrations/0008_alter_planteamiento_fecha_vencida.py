# Generated by Django 4.0.5 on 2022-07-02 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planteamientos', '0007_alter_planteamiento_fecha_vencida'),
    ]

    operations = [
        migrations.AlterField(
            model_name='planteamiento',
            name='fecha_vencida',
            field=models.DateField(),
        ),
    ]
