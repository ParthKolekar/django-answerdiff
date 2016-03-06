import datetime

from django.http import Http404
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import Question, Submission, Comment, Contest, AcceptedQuestion, Profile
from .serializers import QuestionSerializer, SubmissionSerializer, ScoreboardSerializer, CommentSerializer, SubmissionSerializerforMySubmission

from .task import checker_queue

FILE = "FL"
STRING = "ST"
SUBMISSION_STATE_CHOICES = { 'WA': 'Wrong Answer', 'AC': 'Accepted', 'PR': 'Processing', 'NA': 'Not Attempted' }

class ListProblems(APIView):
    """
        List all question according to user i.e user can be Admin or normal user.
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    # renderer_classes = (JSONRenderer, )  # uncomment this to send "only" json response
    def get(self, request, format=None):
        user = User.objects.get(username = request.user.username)
        profile = user.profile
        if request.user.is_staff:
            questions = Question.objects.all().order_by('question_level').order_by('question_number')
        else:
            questions = Question.objects.filter(question_level__lte=profile.user_access_level).order_by('question_level').order_by('question_number')
        success_sub = Submission.objects.filter(submission_user__username = user.username)
        problem_data = []
        for question in questions:
            acc = success_sub.filter(submission_question=question).filter(submission_state='AC')
            wan = success_sub.filter(submission_question=question).filter(submission_state='WA')
            prr = success_sub.filter(submission_question=question).filter(submission_state='PR')
            if acc:
                sta = SUBMISSION_STATE_CHOICES['AC']
            elif wan:
                sta = SUBMISSION_STATE_CHOICES['WA']
            elif prr:
                sta = SUBMISSION_STATE_CHOICES['PR']
            else:
                sta = SUBMISSION_STATE_CHOICES['NA']
            problem_data.append([question.question_level, question.question_number, question.question_title, sta ])

            context = {'user_nick':profile.user_nick, 'problem_data':problem_data }

        return Response(context)

class LevelDetails(APIView):
    """
    List all questions according to level of user, admin can access all level
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    # renderer_classes = (JSONRenderer, )  # uncomment this to send "only" json response
    def get_object(self, level):
        try:
            return Question.objects.filter(question_level = level).order_by('question_number')
        except Question.DoesNotExist:
            raise Http404

    def get(self, request, level, format=None):
        user = User.objects.get(username = request.user.username)
        profile = user.profile
        print profile.user_access_level
        if request.user.is_staff:
            questions = self.get_object(level)
        else:
            if int(level) <= profile.user_access_level:
                questions = self.get_object(level)
            else:
                content = {'user_nick':profile.user_nick, 'please move along': 'Nothing to see here' }
                return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)

        success_sub = Submission.objects.filter(submission_user__username = user.username)
        problem_data = []
        for question in questions:
            acc = success_sub.filter(submission_question=question).filter(submission_state='AC')
            wan = success_sub.filter(submission_question=question).filter(submission_state='WA')
            prr = success_sub.filter(submission_question=question).filter(submission_state='PR')
            if acc:
                sta = SUBMISSION_STATE_CHOICES['AC']
            elif wan:
                sta = SUBMISSION_STATE_CHOICES['WA']
            elif prr:
                sta = SUBMISSION_STATE_CHOICES['PR']
            else:
                sta = SUBMISSION_STATE_CHOICES['NA']

            problem_data.append([question.question_level, question.question_number, question.question_title, sta ])
        context = {'user_nick':profile.user_nick, 'problem_data':problem_data }
        return Response(context)


class QuestionDetails(APIView):
    """
    Show the question corresponding to level and number.
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    # renderer_classes = (JSONRenderer, )  # uncomment this to send "only" json response
    def get_object(self, question_level, question_number):
        try:
            return Question.objects.filter(question_level = question_level).filter(question_number = question_number )
        except Question.DoesNotExist:
            raise Http404

    def get_contest_type(self):
        contest_type = Contest.objects.all().first().contest_user_level_increment_type
        return str(contest_type)

    def get_question_type(self):
        contest_upload_type = Contest.objects.all().first().contest_question_type
        return str(contest_upload_type)

    def get_contest_consecutive_submission_halt_time(self):
        contest_consecutive_submission_halt_time = Contest.objects.all().first().contest_consecutive_submission_halt_time
        return contest_consecutive_submission_halt_time

    def get(self, request, question_level, question_number, format=None):
        question = self.get_object(question_level, question_number)
        user = User.objects.get(username = request.user.username)
        profile = user.profile

        if len(question):
            question_comments = Comment.objects.filter(comment_question=question).filter(comment_is_approved=True).order_by('comment_timestamp')

            if int(question_level) <= profile.user_access_level or request.user.is_staff :
                question_details = question[0]
                print type(question_details)
                serializer = QuestionSerializer(question_details)
                context = {'question_data':serializer.data, 'user_nick':profile.user_nick, 'question_comments':question_comments}
                return Response(context)
            else:
                content = {'user_nick':profile.user_nick, 'please move along': 'Nothing to see here' }
                return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)

        else:
            content = { 'user_nick':profile.user_nick, 'please move along': 'Question Not Available'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, question_level, question_number, format=None):
        """
        Use this Function to submit.
        """

        user = User.objects.get(username=request.user.username)
        question = Question.objects.filter(question_level=question_level).filter(question_number=question_number)
        if int(user.profile.user_access_level) < int(question_level):
            content = {'user_nick':profile.user_nick, 'please move along': 'Nothing to see here' }
            return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)

        time_last = None
        time_last_query = Submission.objects.filter(submission_user__username=request.user.username).filter(submission_question__question_level=question_level).filter(submission_question__question_number=question_number).filter(submission_state='WA').order_by('submission_timestamp').last()
        check_resubmission = AcceptedQuestion.objects.filter(record_user=request.user).filter(record_question=question)
        if check_resubmission:
            content = {'user_nick':profile.user_nick, 'Do not try to resubmit': 'Already Accepted' }
            return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)
        if time_last_query:
            time_last = time_last_query.submission_timestamp
        time_limit = self.get_contest_consecutive_submission_halt_time()

#        print time_last, time_limit, datetime.datetime.now(), time_limit <= datetime.datetime.now()

        if(time_last is None or time_last + time_limit <= datetime.datetime.now()):

            type_of_contest =  self.get_contest_type()
            type_of_submission = self.get_question_type()
            if type_of_submission != STRING:
                content = { 'user_nick':profile.user_nick, 'please move along': 'WRONG TYPE SUBMISSION'}
                return Response(content, status=status.HTTP_405_METHOD_NOT_ALLOWED)

            serializer = SubmissionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(submission_user = request.user,
                                submission_question = self.get_object(question_level,question_number)[0],
                )
                # checker_queue.delay(int(serializer.data['id']))
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            content = {'user_nick':profile.user_nick, 'Try to submit after some time': 'Nothing to see here' }
            return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)

class Scoreboard(APIView):
    """
    Class for displaying score board
    """

    def get(self, request, format=None):
        scoreboard = Profile.objects.all().order_by('user_score')
        # If you dont want to show admin in scoreboard, then remove it on frontend. NO extra computation here
        serializer = ScoreboardSerializer(scoreboard, many=True)
        return Response(serializer.data)

class CommentDetails(APIView):
    """
    Class for posting comments
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get_contest_consecutive_submission_halt_time(self):
        contest_consecutive_submission_halt_time = Contest.objects.all().first().contest_consecutive_submission_halt_time
        return contest_consecutive_submission_halt_time

    def post(self, request, question_level, question_number, format=None):
        """
        Use this Function to submit Comment.
        """
        user = User.objects.get(username=request.user.username)
        question = Question.objects.filter(question_level=question_level).filter(question_number=question_number)
        if int(user.profile.user_access_level) < int(question_level):
            content = {'user_nick':profile.user_nick, 'please move along': 'Nothing to see here' }
            return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)

        time_last = None
        time_last_query = Comment.objects.filter(comment_user__username=request.user.username).order_by('comment_timestamp').last()
        if time_last_query:
            time_last = time_last_query.comment_timestamp
        time_limit = self.get_contest_consecutive_submission_halt_time() # the halt time for submission is kept same as submission halt time

#        print time_last, time_limit, datetime.datetime.now(), time_limit <= datetime.datetime.now()

        if(time_last is None or time_last + time_limit <= datetime.datetime.now()):

            serializer = CommentSerializer(data=request.data)
            if not request.data['comment_message'] or len(str(request.data['comment_message'])) >= 255:
                content = {'user_nick':profile.user_nick, 'Try to submit something small': 'Like your Dick' }
                return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)
            if serializer.is_valid():
                serializer.save(comment_user = request.user,
                                comment_question = question[0],
                )
                checker_queue.delay(int(serializer.data['id']))
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            content = {'user_nick':profile.user_nick, 'Try to submit after some time': 'Nothing to see here' }
            return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)

class ListSubmissions(APIView):
    """
    List all Submissions of logged in user of return all submissions if user is admin
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    # renderer_classes = (JSONRenderer, )  # uncomment this to send "only" json response
    def get(self, request, format=None):
        user = User.objects.get(username = request.user.username)
        profile = user.profile
        if request.user.is_staff:
            submissions = Submission.objects.all().order_by('submission_timestamp')
        else:
            submissions = Submission.objects.filter(submission_user=user).order_by('submission_timestamp')
        serializer = SubmissionSerializerforMySubmission(submissions, many=True)
        return Response(serializer.data)
