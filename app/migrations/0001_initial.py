# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'jUser'
        db.create_table(u'app_juser', (
            (u'user_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, primary_key=True)),
            ('department', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'app', ['jUser'])

        # Adding model 'Professor'
        db.create_table(u'app_professor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('department', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal(u'app', ['Professor'])

        # Adding model 'Rating'
        db.create_table(u'app_rating', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.jUser'])),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.Course'])),
            ('rating', self.gf('django.db.models.fields.FloatField')()),
            ('rating_type', self.gf('django.db.models.fields.CharField')(default='ALL', max_length=3)),
        ))
        db.send_create_signal(u'app', ['Rating'])

        # Adding model 'Professor_Rating'
        db.create_table(u'app_professor_rating', (
            (u'rating_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['app.Rating'], unique=True, primary_key=True)),
            ('prof', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.Professor'])),
        ))
        db.send_create_signal(u'app', ['Professor_Rating'])

        # Adding model 'Course'
        db.create_table(u'app_course', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('course_id', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('course_type', self.gf('django.db.models.fields.CharField')(default='LEC', max_length=3)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('credits', self.gf('django.db.models.fields.FloatField')()),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=5000, null=True, blank=True)),
            ('additional_info', self.gf('django.db.models.fields.CharField')(max_length=5000, null=True, blank=True)),
            ('sections_info', self.gf('django.db.models.fields.CharField')(max_length=5000, null=True, blank=True)),
            ('catalogue', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('grades', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('grades_info', self.gf('django.db.models.fields.CharField')(max_length=5000, null=True, blank=True)),
            ('abbreviation', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('participants', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('hours_per_week', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=200)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal(u'app', ['Course'])

        # Adding M2M table for field instructors on 'Course'
        m2m_table_name = db.shorten_name(u'app_course_instructors')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('course', models.ForeignKey(orm[u'app.course'], null=False)),
            ('professor', models.ForeignKey(orm[u'app.professor'], null=False))
        ))
        db.create_unique(m2m_table_name, ['course_id', 'professor_id'])

        # Adding model 'Comment'
        db.create_table(u'app_comment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.Course'])),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'app', ['Comment'])


    def backwards(self, orm):
        # Deleting model 'jUser'
        db.delete_table(u'app_juser')

        # Deleting model 'Professor'
        db.delete_table(u'app_professor')

        # Deleting model 'Rating'
        db.delete_table(u'app_rating')

        # Deleting model 'Professor_Rating'
        db.delete_table(u'app_professor_rating')

        # Deleting model 'Course'
        db.delete_table(u'app_course')

        # Removing M2M table for field instructors on 'Course'
        db.delete_table(db.shorten_name(u'app_course_instructors'))

        # Deleting model 'Comment'
        db.delete_table(u'app_comment')


    models = {
        u'app.comment': {
            'Meta': {'object_name': 'Comment'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app.Course']"}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'app.course': {
            'Meta': {'object_name': 'Course'},
            'abbreviation': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'additional_info': ('django.db.models.fields.CharField', [], {'max_length': '5000', 'null': 'True', 'blank': 'True'}),
            'catalogue': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'course_id': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'course_type': ('django.db.models.fields.CharField', [], {'default': "'LEC'", 'max_length': '3'}),
            'credits': ('django.db.models.fields.FloatField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '5000', 'null': 'True', 'blank': 'True'}),
            'grades': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'grades_info': ('django.db.models.fields.CharField', [], {'max_length': '5000', 'null': 'True', 'blank': 'True'}),
            'hours_per_week': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'instructors': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['app.Professor']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'participants': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'sections_info': ('django.db.models.fields.CharField', [], {'max_length': '5000', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200'})
        },
        u'app.juser': {
            'Meta': {'object_name': 'jUser', '_ormbases': [u'auth.User']},
            'department': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'app.professor': {
            'Meta': {'object_name': 'Professor'},
            'department': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'app.professor_rating': {
            'Meta': {'object_name': 'Professor_Rating', '_ormbases': [u'app.Rating']},
            'prof': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app.Professor']"}),
            u'rating_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['app.Rating']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'app.rating': {
            'Meta': {'object_name': 'Rating'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app.Course']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rating': ('django.db.models.fields.FloatField', [], {}),
            'rating_type': ('django.db.models.fields.CharField', [], {'default': "'ALL'", 'max_length': '3'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app.jUser']"})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['app']