from django.test import TestCase

import datetime

from django.utils import timezone
from .models import Question
from django.urls import reverse


def create_question(question_text, days, choices = []):
    """
    Create a question with the given 'question_text' and published the given number of 'days' offset to now (negative
    for questions published in the past, positive for question that have yet to be published
    :param question_text:
    :param days:
    :return:
    """
    time = timezone.now() + datetime.timedelta(days=days)
    q = Question.objects.create(question_text=question_text, pub_date=time)
    for particular_choice in choices:
        q.choice_set.create(choice_text=particular_choice, votes = 0)
    return q

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future returns a 404 not found.
        :return:
        """
        generic_choices = ['Choice 1', 'Choice 2']
        future_question = create_question(question_text='Future question.', days=5, choices=generic_choices)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past displays the question's text.
        :return:
        """
        generic_choices = ['Choice 1', 'Choice 2']
        past_question = create_question(question_text='Past Question.', days=-5, choices=generic_choices)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_no_choice_question(self):
        """
        The detail view should not display questions which does not have any choice
        :return:
        """
        question_with_no_choices = create_question(question_text="Question with no choices 1", days=0)
        url = reverse('polls:detail', args=(question_with_no_choices.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_question_with_choice(self):
        """
        The detail view should display questions which have choice/choices
        :return:
        """
        generic_choices = ['Choice 1', 'Choice 2']
        question_with_choices = create_question(question_text="Question with choices 1", days=0,
                                                  choices=generic_choices)
        url = reverse('polls:detail', args=(question_with_choices.id,))
        response = self.client.get(url)
        self.assertContains(response, question_with_choices.question_text)

    # def test_both_question_with_choice_and_question_with_no_choice(self):
    #     """
    #     The detail view should not display question with no choice and display question with choice
    #     :return:
    #     """
    #     generic_choices = ['Choice 1', 'Choice 2']
    #     question_with_no_choices = create_question(question_text="Question with no choices 1", days=0)
    #     question_with_choices = create_question(question_text="Question with choices 2", days=0,
    #                                             choices=generic_choices))
    #     url1 = reverse('polls:detail', args=(question_with_no_choices))
    #     response = self.client.get(url1)
    #     self.assertEqual(response.status_code, 404)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no question exist, an appropriate message is displsyed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in thw past are diaplayed on the index page.
        :return:
        """
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on the index page.
        :return:
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'],[])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future question exist, only past questions are displayed.
        :return:
        """
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_two_past_question(self):
        """
        The questions index page may display multiple questions.
        :return:
        """
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )

class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        time=timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours = 23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


