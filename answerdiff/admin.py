from django.contrib import admin
from .models import Question, Profile, Submission, Contest, AcceptedQuestion, Comment

admin.site.register(Question)
admin.site.register(Profile)
admin.site.register(Submission)
admin.site.register(Contest)
admin.site.register(AcceptedQuestion)
admin.site.register(Comment)
