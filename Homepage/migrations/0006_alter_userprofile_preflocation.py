# Generated by Django 4.1.7 on 2023-03-16 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Homepage', '0005_rename_userid_businessprofile_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='prefLocation',
            field=models.CharField(choices=[(' ', '---------'), ('1', 'North'), ('2', 'South'), ('3', 'East'), ('4', 'West'), ('5', 'Central')], max_length=30),
        ),
    ]