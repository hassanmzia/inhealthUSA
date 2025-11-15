# Generated manually for profile picture upload feature
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('healthcare', '0010_add_email_verification'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, help_text='User profile picture', null=True, upload_to='profile_pictures/'),
        ),
    ]
