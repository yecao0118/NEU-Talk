from django.db import migrations, models
import uuid

def gen_uuid(apps, schema_editor):
    Comment = apps.get_model('accounts', 'Comment')
    for comment in Comment.objects.all():
        comment.unique_id = uuid.uuid4()
        comment.save()
    
class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_rename_post_comment_post_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='unique_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
    ]