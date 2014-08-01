from django import forms
from app.models import *


class SubmitForumPost(forms.Form):
    forum_pk = forms.CharField()
    title = forms.CharField()
    description = forms.CharField(required=False)
    anonymous = forms.BooleanField(required=False)
    tagsRadios = forms.CharField(required=False)

    def clean(self):
        cleaned_data = super(SubmitForumPost, self).clean()

        forums = Forum.objects.filter(pk=cleaned_data.get("forum_pk"))
        if len(forums) != 1:
            raise forms.ValidationError("Not a valid number of forums with this forum_pk!")
        forum = forums[0]
        cleaned_data['forum'] = forum

        if 'tagsRadios' in cleaned_data:
            tag = cleaned_data['tagsRadios']
            possibleTags = forum.get_tags()
            if tag not in possibleTags:
                cleaned_data['tagsRadios'] = None

        return cleaned_data

class SubmitForumAnswer(forms.Form):
    forum_pk = forms.CharField()
    text = forms.CharField()
    post_id = forms.CharField()
    parent_answer_id = forms.CharField(required=False)

    anonymous = forms.BooleanField(required=False)

    discussion_answer_id = forms.CharField(required=False)

    def clean(self):
        cleaned_data = super(SubmitForumAnswer, self).clean()

        forums = Forum.objects.filter(pk=cleaned_data.get("forum_pk"))
        if len(forums) != 1:
            raise forms.ValidationError("Not a valid number of forums with this forum_pk!")
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

        discussion_answer_id = cleaned_data.get("discussion_answer_id")
        if discussion_answer_id:
            discussion_answers = ForumAnswer.objects.filter(id=discussion_answer_id)
            if len(discussion_answers) != 1:
                raise forms.ValidationError("Not a valid number of discussion answers with this discussion_answer_id!")
            discussion_answer = discussion_answers[0]
            cleaned_data['discussion_answer'] = discussion_answer

            if discussion_answer.post != posts[0]:
                raise forms.ValidationError("The answer you are discussing about is not part of the correct post!")

            parent_answer = discussion_answer.parent_answer
            if not parent_answer or parent_answer.parent_answer:
                raise forms.ValidationError("The discussion answer is not an answer that should have its discussion page!")

        return cleaned_data

class UpvotePost(forms.Form):
    post_id = forms.CharField()

    def clean(self):
        cleaned_data = super(UpvotePost, self).clean()

        posts = ForumPost.objects.filter(id=cleaned_data.get("post_id"))
        if len(posts) != 1:
            raise forms.ValidationError("Not a valid number of posts with this post_id!")
        cleaned_data['post'] = posts[0]

        return cleaned_data


class UpvoteAnswer(forms.Form):
    answer_id = forms.CharField()

    def clean(self):
        cleaned_data = super(UpvoteAnswer, self).clean()

        answers = ForumAnswer.objects.filter(id=cleaned_data.get("answer_id"))
        if len(answers) != 1:
            raise forms.ValidationError("Not a valid number of answers with this answer_id!")
        cleaned_data['answer'] = answers[0]

        return cleaned_data
