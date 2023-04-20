# Generated by Django 4.1.7 on 2023-04-19 15:10

from django.db import migrations, models
from datetime import date

def populate_birthdate(apps, schema_editor):
    UserProfile = apps.get_model('Homepage', 'UserProfile')
    for profile in UserProfile.objects.all():
        birthyear = date.today().year - profile.age
        birthdate = date(birthyear, 1, 1)
        profile.birthdate = birthdate
        profile.save()

class Migration(migrations.Migration):

    dependencies = [
        ('Homepage', '0017_promotion'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='birthdate',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.RunPython(populate_birthdate),
    ]