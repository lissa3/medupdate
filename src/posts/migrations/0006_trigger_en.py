# Generated by Django 4.2.1 on 2023-08-22 21:10
from django.contrib.postgres.search import SearchVector
from django.db import migrations


def compute_search_vector_en(apps, schema_editor):
    Post = apps.get_model("posts", "Post")
    vector_en = SearchVector("title_en", weight="A", config="english") + SearchVector(
        "content_en", weight="B", config="english"
    )

    Post.objects.update(vector_en=vector_en)


class Migration(migrations.Migration):
    dependencies = [
        ("posts", "0005_trigger_ru"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE TRIGGER vector_en_trigger
            BEFORE INSERT OR UPDATE OF title_en, content_en, vector_en
            ON posts_post
            FOR EACH ROW EXECUTE PROCEDURE
            tsvector_update_trigger(
                vector_en, 'pg_catalog.english', title_en, content_en
            );
            UPDATE posts_post SET vector_en = NULL;
            """,
            reverse_sql="""
            DROP TRIGGER IF EXISTS vector_en_trigger
            ON posts_post;
            """,
        ),
        migrations.RunPython(
            compute_search_vector_en, reverse_code=migrations.RunPython.noop
        ),
    ]
