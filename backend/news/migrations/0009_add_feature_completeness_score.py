# Generated manually on 2025-10-19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0008_newsarticle_colombian_involvement_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsarticle',
            name='feature_completeness_score',
            field=models.FloatField(default=0.0, help_text='0.0-1.0: Porcentaje de campos ML extraídos vs total esperado', verbose_name='Completitud de extracción de features'),
        ),
    ]
