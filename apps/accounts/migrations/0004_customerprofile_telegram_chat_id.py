# Generated migration for Telegram integration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_stylistprofile_salon'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerprofile',
            name='telegram_chat_id',
            field=models.CharField(blank=True, help_text='Chat ID برای ارسال اعلان\u200cهای تلگرام', max_length=50, null=True, unique=True, verbose_name='شناسه چت تلگرام'),
        ),
    ]
