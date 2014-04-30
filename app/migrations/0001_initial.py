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
            ('user_type', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('university', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.University'], null=True)),
            ('is_confirmed', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
        ))
        db.send_create_signal(u'app', ['jUser'])

        # Adding M2M table for field majors on 'jUser'
        m2m_table_name = db.shorten_name(u'app_juser_majors')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('juser', models.ForeignKey(orm[u'app.juser'], null=False)),
            ('major', models.ForeignKey(orm[u'app.major'], null=False))
        ))
        db.create_unique(m2m_table_name, ['juser_id', 'major_id'])

        # Adding model 'StudentCourseRegistration'
        db.create_table(u'app_studentcourseregistration', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.jUser'])),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.Course'])),
            ('is_approved', self.gf('django.db.models.fields.BooleanField')()),
        ))
        db.send_create_signal(u'app', ['StudentCourseRegistration'])

        # Adding model 'InstructorCourseRegistration'
        db.create_table(u'app_instructorcourseregistration', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('instructor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.jUser'])),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.Course'])),
            ('is_approved', self.gf('django.db.models.fields.BooleanField')()),
        ))
        db.send_create_signal(u'app', ['InstructorCourseRegistration'])

        # Adding model 'Major'
        db.create_table(u'app_major', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('abbreviation', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
        ))
        db.send_create_signal(u'app', ['Major'])

        # Adding model 'Course'
        db.create_table(u'app_course', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('course_id', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('course_type', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('credits', self.gf('django.db.models.fields.FloatField')()),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=5000, null=True, blank=True)),
            ('additional_info', self.gf('django.db.models.fields.CharField')(max_length=5000, null=True, blank=True)),
            ('abbreviation', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=200)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('university', self.gf('django.db.models.fields.related.ForeignKey')(related_name='courses', to=orm['app.University'])),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(related_name='courses', to=orm['app.Category'])),
        ))
        db.send_create_signal(u'app', ['Course'])

        # Adding M2M table for field tags on 'Course'
        m2m_table_name = db.shorten_name(u'app_course_tags')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('course', models.ForeignKey(orm[u'app.course'], null=False)),
            ('tag', models.ForeignKey(orm[u'app.tag'], null=False))
        ))
        db.create_unique(m2m_table_name, ['course_id', 'tag_id'])

        # Adding M2M table for field majors on 'Course'
        m2m_table_name = db.shorten_name(u'app_course_majors')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('course', models.ForeignKey(orm[u'app.course'], null=False)),
            ('major', models.ForeignKey(orm[u'app.major'], null=False))
        ))
        db.create_unique(m2m_table_name, ['course_id', 'major_id'])

        # Adding model 'Tag'
        db.create_table(u'app_tag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'app', ['Tag'])

        # Adding model 'University'
        db.create_table(u'app_university', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal(u'app', ['University'])

        # Adding model 'Category'
        db.create_table(u'app_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.Category'], null=True)),
            ('level', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('abbreviation', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal(u'app', ['Category'])

        # Adding M2M table for field admins on 'Category'
        m2m_table_name = db.shorten_name(u'app_category_admins')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('category', models.ForeignKey(orm[u'app.category'], null=False)),
            ('juser', models.ForeignKey(orm[u'app.juser'], null=False))
        ))
        db.create_unique(m2m_table_name, ['category_id', 'juser_id'])

        # Adding model 'Domain'
        db.create_table(u'app_domain', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('university', self.gf('django.db.models.fields.related.ForeignKey')(related_name='domains', to=orm['app.University'])),
        ))
        db.send_create_signal(u'app', ['Domain'])

        # Adding model 'WikiPage'
        db.create_table(u'app_wikipage', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, primary_key=True)),
            ('content', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'app', ['WikiPage'])

        # Adding model 'Rating'
        db.create_table(u'app_rating', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.jUser'])),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.Course'])),
            ('rating', self.gf('django.db.models.fields.FloatField')()),
            ('rating_type', self.gf('django.db.models.fields.CharField')(default='ALL', max_length=3)),
        ))
        db.send_create_signal(u'app', ['Rating'])

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

        # Removing M2M table for field majors on 'jUser'
        db.delete_table(db.shorten_name(u'app_juser_majors'))

        # Deleting model 'StudentCourseRegistration'
        db.delete_table(u'app_studentcourseregistration')

        # Deleting model 'InstructorCourseRegistration'
        db.delete_table(u'app_instructorcourseregistration')

        # Deleting model 'Major'
        db.delete_table(u'app_major')

        # Deleting model 'Course'
        db.delete_table(u'app_course')

        # Removing M2M table for field tags on 'Course'
        db.delete_table(db.shorten_name(u'app_course_tags'))

        # Removing M2M table for field majors on 'Course'
        db.delete_table(db.shorten_name(u'app_course_majors'))

        # Deleting model 'Tag'
        db.delete_table(u'app_tag')

        # Deleting model 'University'
        db.delete_table(u'app_university')

        # Deleting model 'Category'
        db.delete_table(u'app_category')

        # Removing M2M table for field admins on 'Category'
        db.delete_table(db.shorten_name(u'app_category_admins'))

        # Deleting model 'Domain'
        db.delete_table(u'app_domain')

        # Deleting model 'WikiPage'
        db.delete_table(u'app_wikipage')

        # Deleting model 'Rating'
        db.delete_table(u'app_rating')

        # Deleting model 'Comment'
        db.delete_table(u'app_comment')


    models = {
        u'app.category': {
            'Meta': {'object_name': 'Category'},
            'abbreviation': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'categories_managed'", 'symmetrical': 'False', 'to': u"orm['app.jUser']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app.Category']", 'null': 'True'})
        },
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
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'courses'", 'to': u"orm['app.Category']"}),
            'course_id': ('django.db.models.fields.IntegerField', [], {}),
            'course_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'credits': ('django.db.models.fields.FloatField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '5000', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'majors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'courses'", 'symmetrical': 'False', 'to': u"orm['app.Major']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'courses'", 'symmetrical': 'False', 'to': u"orm['app.Tag']"}),
            'university': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'courses'", 'to': u"orm['app.University']"})
        },
        u'app.domain': {
            'Meta': {'object_name': 'Domain'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'university': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'domains'", 'to': u"orm['app.University']"})
        },
        u'app.instructorcourseregistration': {
            'Meta': {'object_name': 'InstructorCourseRegistration'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app.Course']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app.jUser']"}),
            'is_approved': ('django.db.models.fields.BooleanField', [], {})
        },
        u'app.juser': {
            'Meta': {'object_name': 'jUser', '_ormbases': [u'auth.User']},
            'courses_enrolled': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'students'", 'symmetrical': 'False', 'through': u"orm['app.StudentCourseRegistration']", 'to': u"orm['app.Course']"}),
            'courses_managed': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'instructors'", 'symmetrical': 'False', 'through': u"orm['app.InstructorCourseRegistration']", 'to': u"orm['app.Course']"}),
            'is_confirmed': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'majors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'students'", 'symmetrical': 'False', 'to': u"orm['app.Major']"}),
            'university': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app.University']", 'null': 'True'}),
            u'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'}),
            'user_type': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'app.major': {
            'Meta': {'object_name': 'Major'},
            'abbreviation': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'app.rating': {
            'Meta': {'object_name': 'Rating'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app.Course']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rating': ('django.db.models.fields.FloatField', [], {}),
            'rating_type': ('django.db.models.fields.CharField', [], {'default': "'ALL'", 'max_length': '3'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app.jUser']"})
        },
        u'app.studentcourseregistration': {
            'Meta': {'object_name': 'StudentCourseRegistration'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app.Course']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_approved': ('django.db.models.fields.BooleanField', [], {}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app.jUser']"})
        },
        u'app.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'app.university': {
            'Meta': {'object_name': 'University'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'app.wikipage': {
            'Meta': {'object_name': 'WikiPage'},
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'})
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