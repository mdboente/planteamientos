# Generated by Django 4.0.5 on 2022-07-02 20:59

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('planteamientos', '0006_alter_planteamiento_fecha_vencida'),
    ]

    operations = [
        migrations.AlterField(
            model_name='planteamiento',
            name='fecha_vencida',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
