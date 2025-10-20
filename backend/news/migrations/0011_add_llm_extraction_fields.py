# Generated manually for task-9.6: Ollama LLM integration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0010_backfill_feature_completeness_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsarticle',
            name='llm_features_extracted',
            field=models.BooleanField(
                default=False,
                help_text='Indica si el LLM (Ollama) procesó este artículo',
                verbose_name='Features extraídas por LLM'
            ),
        ),
        migrations.AddField(
            model_name='newsarticle',
            name='llm_extraction_results',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='Diccionario con todas las features extraídas por el LLM',
                verbose_name='Resultados de extracción LLM'
            ),
        ),
        migrations.AddField(
            model_name='newsarticle',
            name='llm_extraction_date',
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name='Fecha de extracción LLM'
            ),
        ),
        migrations.AddField(
            model_name='newsarticle',
            name='extraction_comparison',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='Comparación entre resultados de spaCy y LLM',
                verbose_name='Comparación de extracciones'
            ),
        ),
    ]
