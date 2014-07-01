from django import forms
import json

from app.models import *
from abc import abstractmethod

# Category management forms
class CategoryForm(forms.Form):
	cat_id = forms.IntegerField(required=True)
	
	def is_allowed(self, user):
		category = Category.objects.get(id=self.cleaned_data['cat_id'])
		if category is not None:
			return user in category.get_all_admins()
		else:
			return False
	
	@abstractmethod
	def execute_action(self):
		pass

class EditCategoryForm(CategoryForm):
    name = forms.CharField(required=True, max_length=150)
    def execute_action(self):
   		category = Category.objects.get(id=self.cleaned_data['cat_id'])
   		return_dict = {}
   		if category is not None:
   			category.name = self.cleaned_data['name']
   			category.save()
   			return_dict['status'] = 'OK'
   			return_dict['message'] = 'Saved <b>%s</b>.' % self.cleaned_data['name']
   			return_dict['data'] = { 
   				'cat_id': self.cleaned_data['cat_id'],
   				'new_name': self.cleaned_data['name'] 
   			}
   		else:
   			return_dict['status'] = 'Error'
   			return_dict['message'] = 'Something went wrong. Please refresh \
   			the page and try again.'

   		return json.dumps(return_dict)

class RemoveAdminForm(CategoryForm):
	admin_id = forms.IntegerField(required=True)
	

	def execute_action(self):
		admin = jUser.objects.get(id = self.cleaned_data['admin_id'])
		category = Category.objects.get(id = self.cleaned_data['cat_id'])
		return_dict = {}
		if admin is not None and category is not None:
			if admin in category.admins.all():
				category.admins.remove(admin)
				return_dict['status'] = 'OK'
				return_dict['message'] = 'Removed <b>%s %s</b>.' %\
										  (admin.first_name, admin.last_name)
				return_dict['data'] = { 
					'cat_id': self.cleaned_data['cat_id'],
					'admin_id': self.cleaned_data['admin_id'] 
				}

			else:
				return_dict['status'] = 'Error'
				return_dict['message'] = 'Something went wrong. Please refresh the page and try again.'

		else:
			return_dict['status'] = 'Error'
			return_dict['message'] = 'Something went wrong. Please refresh the page and try again.'

		return json.dumps(return_dict)




class NewAdminForm(CategoryForm):
	admin_id = forms.IntegerField(required=True)

	def is_allowed(self, user):
		condition_1 = super(NewAdminForm,self).is_allowed(user)
		admin = jUser.objects.get(id=self.cleaned_data['admin_id'])
		if admin is not None:
			return condition_1 and admin.user_type > USER_TYPE_STUDENT
		else:
			return False
		

	def execute_action(self):
		category = Category.objects.get(id=self.cleaned_data['cat_id'])
		admin = jUser.objects.get(id=self.cleaned_data['admin_id'])
		return_dict = {}
		if category is not None and admin is not None:
			if not admin in category.get_all_admins():
				admin.categories_managed.add(category)
				return_dict['status'] = 'OK'
				return_dict['message'] = "Successfully added <b>%s %s</b>" %\
										 (admin.first_name, admin.last_name)
				return_dict['data'] = { 
					'cat_id': self.cleaned_data['cat_id'],
					'admin_id': self.cleaned_data['admin_id'],
					'admin_fname': admin.first_name,
					'admin_lname': admin.last_name,
					'admin_username': admin.username 
				}
			else:
				return_dict['status'] = "Error"
				return_dict['message'] = "<b>%s %s</b> is already an admin of <b>%s</b>" %\
									     (admin.first_name, admin.last_name, category.name)
		else:
			return_dict['status'] = "Error"
			return_dict['message'] = "User or category does not exist."
		return json.dumps(return_dict)



class DeleteCategoryForm(CategoryForm):
	# delete_all determines whether all subcategories should also be deleted
	delete_all = forms.BooleanField(required=False)
	def execute_action(self):
		category = Category.objects.get(id=self.cleaned_data['cat_id'])
		return_dict = {}
		if category is not None:
			if self.cleaned_data['delete_all']:
				descendants = category.get_descendants()
				courses = category.get_all_courses()
				for course in courses:
					course.category = None
					course.save()
				for desc in descendants:
					desc.delete()
				category.delete()
			else:
				parent = category.parent
				for course in category.courses.all():
					course.category = parent
					course.save()
				for child in category.children.all():
					child.parent = parent
					child.save()
				category.delete()

			return_dict['status'] = 'OK'
			return_dict['message'] = 'Successfully deleted category. Please refresh\
			the page to see the changes in the category tree'
			return_dict['data'] = { 
				'cat_id': self.cleaned_data['cat_id'],
				'delete_all': self.cleaned_data['delete_all'] 
			}
		else:
			return_dict['status'] = 'Error'
			return_dict['message'] = 'Category does not exist'
		return json.dumps(return_dict)

class NewSubcatForm(CategoryForm):
	name = forms.CharField(required=True, max_length=150)
	abbrev = forms.CharField(required=True, max_length=10)

	def execute_action(self):
		parent_cat = Category.objects.get(id=self.cleaned_data['cat_id'])
		new_cat = Category.objects.create(name=self.cleaned_data['name'],
										  abbreviation=self.cleaned_data['abbrev'],
										  parent=parent_cat)
		return_dict = {}
		if new_cat is not None:
			new_cat.save()
			return_dict['status'] = 'OK'
			return_dict['message'] = 'Added <b>%s</b>.' % new_cat.name
			return_dict['data'] = { 
				'parent_id': self.cleaned_data['cat_id'],
				'cat_id': new_cat.id,
				'cat_name': new_cat.name
			}
		else:
			return_dict['status'] = 'Error'
			return_dict['message'] = 'Could not create the category'

		return json.dumps(return_dict)

class MoveCategoryForm(CategoryForm):
	parent_id = forms.IntegerField(required=True)

	def is_allowed(self, user):
		parent_cat = Category.objects.get(id = self.cleaned_data['parent_id'])
		category = Category.objects.get(id = self.cleaned_data['cat_id'])
		condition_1 = super(MoveCategoryForm,self).is_allowed(user)
		condition_2 = parent_cat is not None and user in parent_cat.get_all_admins()
		return condition_1 and condition_2

	def execute_action(self):
		parent_id = self.cleaned_data['parent_id']
		parent = Category.objects.get(id = self.cleaned_data['parent_id'])
		category = Category.objects.get(id = self.cleaned_data['cat_id'])
		old_parent = category.parent
		return_dict = {}
		if category is not None and parent is not None:
			if parent in category.get_descendants():
				# if the category is moving to one of it's descendants,
				# avoid a cycle by moving all of its children to the old_parent
				for child in category.children.all():
					child.parent = old_parent
					child.save()
				category.parent = parent
				category.save()
				return_dict = {
					'status': "OK",
					'message': "Moved <b>%s</b>" % category.name,
				}
				return_dict['data'] = {
					'descendant': True,
					'cat_id': category.id,
					'parent_id': parent.id
				}
			elif parent == category:
				return_dict = {
					'status': "Error",
					'message': "You cannot make any category the parent of itself."
				}
			else:
				category.parent = parent
				category.save()
				return_dict = {
					'status': "OK",
					'message': "Moved <b>%s</b>" % category.name,
				}
				return_dict['data'] = {
					'descendant': False,
					'cat_id': category.id,
					'parent_id': parent.id
				}
		else:
			return_dict = {
				'status': "Error",
				'message': "Something went wrong. Please refresh the page and try again."
			}
		return json.dumps(return_dict)



class MoveCourseForm(CategoryForm):
	course_id = forms.IntegerField(required=True)
	
	def is_allowed(self,user):
		condition_1 = super(MoveCourseForm,self).is_allowed(user)
		course = Course.objects.get(id=self.cleaned_data['course_id'])
		if course is None:
			return False

		condition_2 = False
		for category in user.categories_managed.all():
			if course in category.get_all_courses():
				condition_2 = True
		return condition_1 and condition_2
	
	def execute_action(self):
		course = Course.objects.get(id=self.cleaned_data['course_id'])
		
		category = Category.objects.get(id=self.cleaned_data['cat_id'])
		return_dict={}
		if course is not None and category is not None:			
			course.category = category
			course.save()
			return_dict['status'] = 'OK'
			return_dict['message'] = 'The course <b>%s</b> was successfully moved' % course.name
			return_dict['data'] = {
				'cat_id': category.id,
				'course_id' : course.id,
				'course_name': course.name
			}

		else:
			return_dict['status'] = 'Error'
			return_dict['message'] = 'The selected course or category does not exist'
		return json.dumps(return_dict)


class AddCourseForm(CategoryForm):
	name = forms.CharField(required=True, max_length=200)
	credits = forms.IntegerField(required=True)
	abbrev = forms.CharField(required=True, max_length=50)
	description = forms.CharField(required=5000)

	def execute_action(self):
		parent_cat = Category.objects.get(id = self.cleaned_data['cat_id'])
		course = Course.objects.create(name = self.cleaned_data['name'],
									   abbreviation = self.cleaned_data['abbrev'],
									   category = parent_cat, 
									   credits = self.cleaned_data['credits'],
									   description = self.cleaned_data['description'])
		return_dict = {}
		if course is not None:
			course.save()
			return_dict['status'] = "OK"
			return_dict['message'] = "Added <b>%s</b>. Please refresh\
			the page to see the changes in the category tree" % course.name
			return_dict['data'] = {
				'course_id' : course.id,
				'cat_id' : self.cleaned_data['cat_id'],
				'course_name' : course.name
			}
		else:
			return_dict['status'] = 'Error'
			return_dict['message'] = 'Could not create the course'

		return json.dumps(return_dict)

# Course management forms
class CourseForm(forms.Form):
	course_id = forms.IntegerField(required=True)
	
	def is_allowed(self,user):
		course = Course.objects.get(id=self.cleaned_data['course_id'])
		category = course.category
		if course is not None and category is not None:
			return user in category.get_all_admins()
		else:
			return category is None

class NewProfessorForm(CourseForm):
	professor_id = forms.IntegerField(required=True)

	def execute_action(self):

		professor = jUser.objects.get(id=self.cleaned_data['professor_id'])
		course = Course.objects.get(id=self.cleaned_data['course_id'])
		return_dict = {}
		if professor is not None and course is not None:
			if not professor in course.professors.all():
				reg = ProfessorCourseRegistration(course=course,professor=professor, is_approved=True)
				reg.save()
				return_dict['status'] = "OK"
				return_dict['message'] = "Successfully addedd <b>%s %s</b>" %\
											(professor.first_name,professor.last_name)
				return_dict['data'] = {
					'professor_id' : professor.id,
					'professor_fname': professor.first_name, 
					'professor_lname': professor.last_name,
					'professor_username': professor.username,
					'course_id': course.id
				}
			else: # professor already exists
				return_dict['status'] = "Error"
				return_dict['message'] = "<b>%s %s</b> already is a professor of <b>%s</b>" %\
				 						 (professor.first_name,professor.last_name,course.name)

		else:
			return_dict['status'] = "OK"
			return_dict['message'] = "Something went wrong. Please refresh the page and try again."
		return json.dumps(return_dict)

class RemoveProfessorForm(CourseForm):
	professor_id = forms.IntegerField(required=True)

	def execute_action(self):
		professor = jUser.objects.get(id=self.cleaned_data['professor_id'])
		course = Course.objects.get(id=self.cleaned_data['course_id'])
		return_dict = {}
		if professor is not None and course is not None:
			if course in professor.courses_managed.all():
				ProfessorCourseRegistration.objects.filter(professor=professor, course=course).delete()
				return_dict['status'] = 'OK'
				return_dict['message'] = 'Successfully unassigned professor from course'
				return_dict['data'] = {
					'professor_id' : professor.id,
					'course_id': course.id
				}
			else:
				return_dict['status'] = 'Error'
				return_dict['message'] = '<b>%s %s</b> is not a professor of <b>%s</b>' %\
										  (professor.first_name, professor.last_name,
										  	course.name)
			
		else:
			return_dict['status'] = 'Error'
			return_dict['message'] = 'Something went wrong. Please refresh the page and try again'

		return json.dumps(return_dict)

class MoveToCategoryForm(CourseForm):
	cat_id = forms.IntegerField(required=True)

	def is_allowed(self,user):
		category = Category.objects.get(id=self.cleaned_data['cat_id'])
		course = Course.objects.get(id=self.cleaned_data['course_id'])
		if course is not None:
			old_cat = course.category
			if category and course and old_cat:
				condition_1 = user in category.get_all_admins()
				condition_2 = super(MoveToCategoryForm,self).is_allowed(user)
				condition_3 = user in old_cat.get_all_admins()
				return condition_1 and condition_2 and condition_3
		
		return False
		
	def execute_action(self):
		course = Course.objects.get(id=self.cleaned_data['course_id'])
		category = Category.objects.get(id=self.cleaned_data['cat_id'])
		result_dict = {}
		# make sure the course is not in a parent category
		# of the user's categories_managed
		if course is not None and category is not None:
			old_cat = course.category
			course.category = category
			course.save()
			result_dict['status'] = "OK"
			result_dict['message'] = "Course category changed successfully."
			result_dict['data'] = {
				'cat_id': category.id,
				'course_id': course.id,
			}
			
		else:
			result_dict['status'] = "Error"
			result_dict['message'] = "Something went wrong. Please refresh the\
			page and try again"

		return json.dumps(result_dict)

class EditCourseForm(CourseForm):
	name = forms.CharField(required=True, max_length=200)

	def execute_action(self):
		course = Course.objects.get(id=self.cleaned_data['course_id'])
		return_dict = {}
		if course is not None:
			course.name = self.cleaned_data['name']
			course.save()
			return_dict['status'] = "OK"
			return_dict['message'] = "aved <b>%s</b>" % course.name
			return_dict['data'] = {
				'course_id': course.id,
				'course_name': course.name
			}
		else:
			return_dict['status'] = "Error"
			return_dict['message'] = "Something went wrong. Please refresh the \
			page and try again."

		return json.dumps(return_dict)

class DeleteCourseForm(CourseForm):
	
	def execute_action(self):
		course = Course.objects.get(id=self.cleaned_data['course_id'])
		return_dict = {}
		if course is not None:
			course_id = course.id;
			course.delete()
			return_dict['status'] = "OK"
			return_dict['message'] = "Course successully deleted."
			return_dict['data'] = {
				'course_id' : course_id
			}
		else:
			return_dict['status'] = "Error"
			return_dict['message'] = "Something went wrong. Please refresh the \
			page and try again."
		return json.dumps(return_dict)
