# Generated by Django 2.2.6 on 2021-07-10 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_auto_20210707_2233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, help_text='Добавьте картинку', null=True, upload_to='posts/', verbose_name='Изображение'),
        ),
    ]
