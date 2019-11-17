# Generated by Django 2.2.6 on 2019-11-14 23:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lectures', '0004_add_fields_events_and_requests'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lecture',
            name='events',
            field=models.CharField(blank=True, help_text="Are you planning any event after your lecture or workshop (e.g. pizza, drinks, games, recruitment)? <b>TELL US ABOUT IT!</b> Beware that organizers <u>WON'T ALLOW</u> you to arrange your event if you don't announce it here!", max_length=800, null=True, verbose_name='Additional events'),
        ),
    ]
