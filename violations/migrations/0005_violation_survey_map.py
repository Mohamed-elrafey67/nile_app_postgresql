from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('violations', '0004_violation_geometry'),
    ]

    operations = [
        migrations.AddField(
            model_name='violation',
            name='survey_map',
            field=models.FileField(
                blank=True, null=True,
                upload_to='survey_maps/',
                verbose_name='الخريطة المساحية المعتمدة (PDF)'
            ),
        ),
    ]
