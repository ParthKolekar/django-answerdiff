from rest_framework import serializers
from .models import Question, Submission, Profile, Comment


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('question_level', 'question_number', 'question_title', 'question_desc', 'question_image')

class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ('id','submission_string','submission_storage')

class ScoreboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('user_nick','user_score')

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('comment_message',)

class SubmissionSerializerforMySubmission(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ('submission_user',
                  'submission_question',
                  'submission_question',
                  'submission_state'
        )
        depth = 2
