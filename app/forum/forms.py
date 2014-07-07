from django import forms
from app.models import *


class SubmitForumPost(forms.Form):
    forum_id = forms.CharField()
    title = forms.CharField()
    description = forms.CharField(required=False)
    anonymous = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super(SubmitForumPost, self).clean()

        forums = Forum.objects.filter(id=cleaned_data.get("forum_id"))
        if len(forums) != 1:
            raise forms.ValidationError("Not a valid number of forums with this forum_id!")
        cleaned_data['forum'] = forums[0]

        return cleaned_data

class SubmitForumAnswer(forms.Form):
    forum_id = forms.CharField()
    text = forms.CharField()
    post_id = forms.CharField()
    parent_answer_id = forms.CharField(required=False)

    anonymous = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super(SubmitForumAnswer, self).clean()

        forums = Forum.objects.filter(id=cleaned_data.get("forum_id"))
        if len(forums) != 1:
            raise forms.ValidationError("Not a valid number of forums with this forum_id!")
        cleaned_data['forum'] = forums[0]

        posts = ForumPost.objects.filter(id=cleaned_data.get("post_id"))
        if len(posts) != 1:
            raise forms.ValidationError("Not a valid number of posts with this post_id!")
        cleaned_data['post'] = posts[0]

        if posts[0].forum != forums[0]:
            raise forms.ValidationError("The post is not part of the correct forum!")

        answer_id = cleaned_data.get("parent_answer_id")
        if answer_id:
            answers = ForumAnswer.objects.filter(id=answer_id)
            if len(answers) != 1:
                raise forms.ValidationError("Not a valid number of answers with this post_id!")
            cleaned_data['parent_answer'] = answers[0]

            if answers[0].post != posts[0]:
                raise forms.ValidationError("The answer you are replying to is not part of the correct post!")

        return cleaned_data