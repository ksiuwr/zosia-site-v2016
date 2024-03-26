# Generated by Django 3.2.16 on 2023-01-17 23:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conferences', '0004_zosia_registration_suspended'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='town',
            field=models.CharField(default='', help_text='Town displayed in terms and conditions', max_length=60),
        ),
    ]