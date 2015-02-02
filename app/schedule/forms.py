from django import forms
from app.models import *
from django.utils import timezone
import pytz

class AppointmentForm(forms.Form):
	title = forms.CharField(max_length=50, required=False)
	body = forms.CharField(max_length=250, required=False)
	start = forms.DateTimeField(input_formats = settings.VALID_TIME_INPUTS)
	end = forms.DateTimeField(input_formats = settings.VALID_TIME_INPUTS)
	timezone_minutes = forms.IntegerField()
	eventId = forms.IntegerField(required=False)
	copy = forms.BooleanField(required=False)
	num_weeks = forms.IntegerField(required=False)

	def clean(self):
		super(AppointmentForm,self).clean()
		
		start_val = self.cleaned_data['start']
		end_val = self.cleaned_data['end']
		local_timezone = timezone.get_current_timezone()
		if timezone.is_aware(start_val):
			start_val = timezone.make_naive(start_val,start_val.tzinfo)
		if timezone.is_aware(end_val):
			end_val = timezone.make_naive(end_val,end_val.tzinfo)
		timezone_minutes = self.cleaned_data['timezone_minutes']
		
		start_val = start_val + timedelta(minutes=timezone_minutes)
		end_val = end_val + timedelta(minutes=timezone_minutes)


		start_utc = timezone.make_aware(start_val,pytz.utc)
		end_utc = timezone.make_aware(end_val,pytz.utc)
		self.cleaned_data['start'] = start_utc
		self.cleaned_data['end'] = end_utc

		return self.cleaned_data


class PersonalAppointmentForm(AppointmentForm):
	pass

class CalendarImportForm(forms.Form):
	calFile = forms.FileField()

	def clean(self):
		cleaned_data = super(CalendarImportForm, self).clean()
		return self.cleaned_data


class CourseAppointmentForm(AppointmentForm):
	course_id = forms.CharField()

	def clean(self):
		super(CourseAppointmentForm,self).clean()
		course = Course.objects.get(id=self.cleaned_data['course_id'])
		self.cleaned_data['course'] = course
		return self.cleaned_data
