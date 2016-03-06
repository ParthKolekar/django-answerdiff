"""
    Module DocString
"""

import binascii
import datetime
import os

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

def question_image_filepath(instance, filename):
    """
        Function DocString
    """
    return '/'.join(['images', str(instance.question_level), str(instance.question_level_id), binascii.b2a_hex(os.urandom(15)), filename])

def question_input_file_upload(instance, filename):
    """
        Function DocString
    """
    return '/'.join(['input', str(instance.question_level), str(instance.question_level_id), binascii.b2a_hex(os.urandom(15)), filename])

def question_gold_file_upload(instance, filename):
    """
        Function DocString
    """
    return '/'.join(['gold', str(instance.question_level), str(instance.question_level_id), binascii.b2a_hex(os.urandom(15)), filename])


def question_checker_upload(instance, filename):
    """
        Function DocString
    """
    return '/'.join(['checker', str(instance.question_level), str(instance.question_level_id), binascii.b2a_hex(os.urandom(15)), 'checker', filename])

def question_preprocess_upload(instance, filename):
    """
        Function DocString
    """
    return '/'.join(['checker', str(instance.question_level), str(instance.question_level_id), binascii.b2a_hex(os.urandom(15)), 'preprocess', filename])

def submission_storage_path(instance, filename):
    """
        Function DocString
    """
    string = '/'.join(['submissions', instance.submission_user.user_nick, str(instance.submission_question.question_level), str(instance.submission_question.question_level_id)])
    string += '/'+datetime.datetime.now().strftime("%I:%M%p-%m-%d-%Y")
    string += filename
    return string


FILE = "FL"
STRING = "ST"
UPLOAD_CHOICES = (
    (FILE, "File"),
    (STRING, "String"),
)

USER_LEVEL_INCREMENT_TYPE_CHOICES = (
    ("TYPE1", "TYPE1"),  #Gordian knot type level increment
    ("TYPE2", "TYPE2"),  #Cache-in type level increment
)

WA = 'WA'
AC = 'AC'
PR = 'PR'
SUBMISSION_STATE_CHOICES = (
    (WA, "Wrong Answer"),
    (AC, "Accepted"),
    (PR, "Processing"),
)

class Contest(models.Model):
    """
        Give Contest Details.
    """

    def __str__(self):
        return str(self.contest_name)

    contest_name = models.CharField(
        max_length = 255,
        default = '',
        unique = True,
    )
    contest_description = models.TextField(
        blank = True,
        default = '',
    )
    contest_rules = models.TextField(
        blank = False,
        default = '',
    )
    contest_start_time = models.DateTimeField(
        blank = False,
    )
    contest_end_time = models.DateTimeField(
        blank = False,
    )
    contest_consecutive_submission_halt_time = models.DurationField(default = datetime.timedelta(0,30))
    contest_number_of_level = models.PositiveIntegerField()
    contest_questions_in_each_level = models.PositiveIntegerField()
    contest_user_level_increment_type = models.CharField(
        max_length = 6,
        choices = USER_LEVEL_INCREMENT_TYPE_CHOICES,
    )
    contest_number_to_increment_level_at = models.PositiveIntegerField() 
    contest_question_type = models.CharField(
        max_length = 6,
        choices = UPLOAD_CHOICES,
    )

class Language(models.Model):
    """
        Gives the Languages which can be compiled on the system for FILE type submissions.
    """

    def __str__(self):
        return str(self.language_name)

    language_compile_arguments = models.CharField(
        max_length = 255,
        blank = True,
        default = '',
        unique = False,
    )
    language_runtime_arguments = models.CharField(
        max_length = 255,
        blank = True,
        default = '',
        unique = False
    )
    language_file_extension = models.CharField(
        max_length = 16,
        blank = False,
        default = '',
        unique = True,
    )
    language_is_preprocessed = models.BooleanField(
        default = False,
    )
    language_is_sandboxed = models.BooleanField(
        default = False,
    )
    language_is_compiled = models.BooleanField(
        default = False,
    )
    language_is_checked = models.BooleanField(
        default = False,
    )
    language_is_executed = models.BooleanField(
        default = False,
    )
    language_name = models.CharField(
        max_length = 255,
        blank = False,
        default = '',
        unique = False,
    )


class Question(models.Model):
    """
        This Database stores the questions that are to be rendered.
        Also provides descriptive functions which provide easy rendering abilities.
    """

#    class Meta:
#        abstract = True

    def __str__(self):
        return " ".join([str(self.question_level), str(self.question_number) , str(self.question_title)])
    # Example: 4_1_{{title}} means question_number 1 of level 4 with title
    # Sets the question level and the identifier inside the level.
    # Level can also be designated as question type.
    # Example - Question 4 of Level 3.
    # ===> question_number = 4, question_level = 3
    question_level = models.IntegerField()

    question_number = models.IntegerField()

    # Question Details
    question_title = models.CharField(
        max_length = 255,
        unique = True,
    )
    question_desc = models.TextField()
    question_image = models.ImageField(
        blank = True,
        upload_to = question_image_filepath,
    )

    # However use is_question_valid till then.
    # question upload details.
    # Keep these fields in mind when you derive from base.
    question_upload_type = models.CharField(
        max_length = 2,
        choices = UPLOAD_CHOICES,
        default = STRING,
    )

    # If ST then answer string is to be provided
    question_answer_string = models.CharField(
        blank = True,
        max_length = 255,
        default = '',
    )

    # If not ST then the upload file is the file to be compared to
    # and checker script is the one which checks the submission.
    question_upload_file = models.FileField(
        blank = True,
        upload_to = question_input_file_upload,
    ) # if upload_type == ST, ignore.
    question_gold_upload_file = models.FileField(
        blank = True,
        upload_to = question_gold_file_upload,
    )
    question_checker_script = models.FileField(
        blank = True,
        upload_to = question_checker_upload,
    )
    question_preprocess_script = models.FileField(
        blank = True,
        upload_to = question_preprocess_upload,
    )
    question_restrict_language_to = models.ForeignKey(
            Language,
            blank=True,
            null=True,
            default=None,
        )
    # In Kilobytes and seconds
    question_time_limit = models.CharField(
       blank = True,
       max_length = 16,
       default = '',
    )
    question_memory_limit = models.CharField(
       blank = True,
       max_length = 16,
       default = '',
    )
    question_output_limit = models.CharField(
       blank = True,
       max_length = 16,
       default = '',
    )
    def is_question_accessible(self, level):
        """
            Function DocString
        """
        if level >= self.question_level:
            return True
        return False

    def is_question_valid(self):
        """
            Function DocString
        """
        if self.question_upload_type == STRING:
            return self.question_answer_string and True
        else:
            return self.question_upload_file and self.question_checker_script

    def check_submission(self, submission_string, submission_id):
        """
            Function DocString
        """
        if self.question_upload_type == STRING:
            return self.question_answer_string.lower().replace(' ', '') == submission_string.lower().replace(' ', '')
        else:
            raise Exception("Question not String Type.")

class Profile(models.Model):
    """
        This Database stores the other User Information.
        The comments on the side refer to the
        CAS login creds for reference.
    """

    def __str__(self):
        return "    ".join([str(self.user_nick), str(self.user.username)])

    user = models.OneToOneField(User)

    user_nick = models.CharField(
        max_length=255,
    ) # displayName

    user_last_ip = models.GenericIPAddressField(
        editable = True,
        default = '0.0.0.0',
    )

    # This is the highest level of questions that one can access.
    user_access_level = models.PositiveIntegerField(
        default = 1,
        editable = True,
    )
    # ======================================================
    user_score = models.FloatField(
        default = 0,
        editable = True,
    )

    def level_up(self):
        """
           Increments User level. Call with care.
        """
        self.user_access_level += 1

    def score_up(self, increment_by):
        """
           Score Up by parameter increment_by
        """
        self.user_score += increment_by


    # flash message
#    user_notification_flash = models.BooleanField(
#        default = False,
#    )

class Submission(models.Model):
    """
        This Database stores the Submissions Information.
    """

#    class Meta:
#        abstract = True

    def __str__(self):
        return "    ".join([str(self.submission_question.question_title),  str(self.submission_user.profile.user_nick), str(self.submission_score)])

    submission_user = models.ForeignKey(User)

    submission_question = models.ForeignKey(Question)

    submission_timestamp = models.DateTimeField(
        auto_now_add = True,
    )
    submission_string = models.CharField(
        blank = True,
        editable = True,
        default = '',
        max_length = 255,
    )
    submission_storage = models.FileField(
        editable = True,
        upload_to = submission_storage_path,
        blank = True,
    )
    submission_state = models.CharField(
        max_length = 2,
        choices = SUBMISSION_STATE_CHOICES,
        default = PR,
    )
    #================================================================
    submission_score = models.FloatField(
        default = 0,
    )

    submission_runtime_log = models.CharField(
        max_length = 255,
        default = "",
        blank = True,
    )

    def __check_ans__(self):
        if(self.submission_question.question_upload_type == FILE):
            raise Exception("Wrong Method Called.Question not String Type.")
        elif self.submission_question.check_submission(self.submission_string,self.id):
            self.submission_state = AC
            self.submission_score = settings.CONTEST_QUESTION_SCORE
        else:
            self.submission_state = WA
        return self.submission_state

    """
        def get_team_name(self):
            return self.submission_user.get_team_name()

        def get_team_score(self):
            return self.submission_user.get_team_score()
    """

# class ClarificationMessages(models.Model):
#     """
#         Clarification Messages to display on Index Page.
#     """
#
#     def __str__(self):
#         return str(self.clarification_messages_message)
#
#     clarification_messages_message = models.CharField(
#         max_length = 255,
#     )
#
class Comment(models.Model):
     """
         Comments of user. Needs approval from admins.
     """

#     class Meta:
#         abstract = True

     def __str__(self):
         return "    ".join([str(self.comment_is_approved), str(self.comment_user.profile.user_nick), str(self.comment_message)])

     comment_timestamp = models.DateTimeField(
         auto_now_add = True,
     )

     comment_message = models.CharField(
         max_length = 255,
         default = '',
     )

     comment_user = models.ForeignKey(User)

     comment_question = models.ForeignKey(Question)

     comment_is_approved = models.BooleanField(
         default = False,
     )

class AcceptedQuestion(models.Model):
    """
    Questions Accepted by each user
    """

    def __str__(self):
        return "User %s has solved %s" % (self.user.username, self.question.id)

    record_user = models.ForeignKey(User)
    record_question = models.ForeignKey(Question)

    score = models.FloatField(
        default=0.0,
    )

    tries = models.IntegerField(
        default=0,
    )

    accepted = models.BooleanField(
        default=False,
    )
