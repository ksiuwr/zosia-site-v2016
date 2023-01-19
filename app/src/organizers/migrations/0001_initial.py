# Generated by Django 3.2.16 on 2023-01-19 20:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('conferences', '0004_zosia_registration_suspended'),
        ('users', '0006_alter_user_person_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizerContact',
            fields=[
                ('phone_number', models.CharField(max_length=9, verbose_name='Phone number')),
                ('user', models.OneToOneField(limit_choices_to={'is_staff': True}, on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='users.user', verbose_name='User')),
                ('zosia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='conferences.zosia', verbose_name='ZOSIA')),
            ],
        ),
    ]