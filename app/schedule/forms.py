from django import forms
from app.models import *
from django.utils import timezone
import pytz

class CreatePersonalAppointmentForm(forms.Form):
	title = forms.CharField(max_length=50, required=False)
	body = forms.CharField(max_length=250, required=False)
	start = forms.DateTimeField(input_formats = settings.VALID_TIME_INPUTS)
	end = forms.DateTimeField(input_formats = settings.VALID_TIME_INPUTS)

	def clean(self):
		super(CreatePersonalAppointmentForm,self).clean()
		print self.cleaned_data
		start_val = self.cleaned_data['start']
		end_val = self.cleaned_data['end']
		local_timezone = timezone.get_current_timezone()
		if timezone.is_naive(start_val):
			start_val = timezone.make_aware(start_val,local_timezone)
		if timezone.is_naive(end_val):
			end_val = timezone.make_aware(end_val,local_timezone)
		start_utc = timezone.localtime(start_val,pytz.utc)
		end_utc = timezone.localtime(end_val,pytz.utc)
		self.cleaned_data['start'] = start_utc
		self.cleaned_data['end'] = end_utc

		return self.cleaned_data