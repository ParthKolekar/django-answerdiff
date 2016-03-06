from __future__ import absolute_import

import commands
import imp
import os

from celery import shared_task
from some.celery import app

from .models import Submission, AcceptedQuestion, Contest


@shared_task
def test(param):
    return "The test tak executed with argument '%s' " % param


@app.task()
def checker_queue(submission_id):
    try:
        submission = Submission.objects.get(id=submission_id)
    except: # TODO See the error that comes up and update it here
        return 1

    user = submission.submission_user
    question = submission.submission_question
    input_type = question.question_upload_type

    records = AcceptedQuestion.objects.filter(record_user=user).filter(record_question=question)
    try:
        record = records[0]
        if record.accepted:
            return 1

    except IndexError:
        record = AcceptedQuestion.create(record_user=user, record_question=question)

    record.tries += 1

    ans_correct = False
    if input_type == "STRING":
        ans = submission.__check_ans__()
        ans_correct = ans == "AC"

    # TODO Else for file, update submission in that else

    record.accepted = ans_correct
    if record.accepted:
        record.score = question.question_score / (0.5 ** (record.tries - 1))
    record.save()

    contest = Contest.objects.all().first()
    user_records = AcceptedQuestion.objects.filter(record_user=user).filter(accepted=True)
    profile = user.profile

    if contest.contest_user_level_increment_type == "TYPE1":
        profile.user_access_level = max(profile.user_access_level,
                                        len(user_records)/contest.contest_number_to_increment_level_at)

    elif contest.contest_user_level_increment_type == "TYPE2":
        accepted_level = [0 for i in range(1, profile.user_access_level+1)]
        for user_record in user_records:
            accepted_level[user_record.question.question_level] += 1

        flag = True
        for i in accepted_level:
            if i < contest.contest_number_to_increment_level_at:
                flag = False
                break

        if flag:
            profile.user_access_level += 1

    profile.save()  # Level Increase
    return 0
