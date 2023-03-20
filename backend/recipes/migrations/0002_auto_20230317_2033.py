# Generated by Django 2.2.16 on 2023-03-17 17:33

import colorfield.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=colorfield.fields.ColorField(default='#FF0000', help_text='Введите цвет в HEX-формате', image_field=None, max_length=18, samples=None, verbose_name='HEX-код'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(help_text='Введите название тэга.', max_length=200, unique=True, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(help_text='Укажите уникальный адрес для тэга. Используйте только латиницу, цифры, дефисы и знаки подчёркивания', max_length=200, unique=True, verbose_name='Короткое название'),
        ),
    ]
