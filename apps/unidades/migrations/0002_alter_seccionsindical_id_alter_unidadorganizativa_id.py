# Generated by Django 4.0.5 on 2022-06-26 04:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('unidades', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seccionsindical',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='unidadorganizativa',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
