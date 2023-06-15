"""
Test /v1/auth/subscribe
"""
import hashlib
from datetime import datetime
from unittest.mock import MagicMock, call, patch

from django.urls.base import reverse_lazy
from django.utils import timezone
from rest_framework import status

from breathecode.notify import actions as notify_actions
from breathecode.authenticate.models import Token

from ..mixins.new_auth_test_case import AuthTestCase

now = timezone.now()


def plan_db_item(plan, data={}):
    return {
        'id': plan.id,
        'cohort_pattern': plan.cohort_pattern,
        'event_type_set_id': plan.event_type_set.id if plan.event_type_set else None,
        'mentorship_service_set_id': plan.mentorship_service_set.id if plan.mentorship_service_set else None,
        'currency_id': plan.currency.id,
        'slug': plan.slug,
        'status': plan.status,
        'has_waiting_list': plan.has_waiting_list,
        'is_onboarding': plan.is_onboarding,
        'time_of_life': plan.time_of_life,
        'time_of_life_unit': plan.time_of_life_unit,
        'trial_duration': plan.trial_duration,
        'trial_duration_unit': plan.trial_duration_unit,
        'is_renewable': plan.is_renewable,
        'owner_id': plan.owner.id if plan.owner else None,
        'price_per_half': plan.price_per_half,
        'price_per_month': plan.price_per_month,
        'price_per_quarter': plan.price_per_quarter,
        'price_per_year': plan.price_per_year,
        **data,
    }


def plan_serializer(plan):
    return {
        'financing_options': [],
        'service_items': [],
        'has_available_cohorts': plan.available_cohorts.exists(),
        'slug': plan.slug,
        'status': plan.status,
        'time_of_life': plan.time_of_life,
        'time_of_life_unit': plan.time_of_life_unit,
        'trial_duration': plan.trial_duration,
        'trial_duration_unit': plan.trial_duration_unit,
    }


def post_serializer(plans=[], data={}):
    return {
        'id': 0,
        'access_token': None,
        'cohort': None,
        'syllabus': None,
        'email': '',
        'first_name': '',
        'last_name': '',
        'phone': '',
        'plans': [plan_serializer(plan) for plan in plans],
        **data,
    }


def put_serializer(user_invite, cohort=None, syllabus=None, plans=[], data={}):
    return {
        'id': user_invite.id,
        'access_token': None,
        'cohort': cohort.id if cohort else None,
        'syllabus': syllabus.id if syllabus else None,
        'email': user_invite.email,
        'first_name': user_invite.first_name,
        'last_name': user_invite.last_name,
        'phone': user_invite.phone,
        'plans': [plan_serializer(plan) for plan in plans],
        **data,
    }


class SubscribeTestSuite(AuthTestCase):
    """Test /v1/auth/subscribe"""
    """
    🔽🔽🔽 Post without email
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=now))
    def test_task__post__without_email(self):
        url = reverse_lazy('authenticate:subscribe')
        response = self.client.post(url)

        json = response.json()
        expected = {'detail': 'without-email', 'status_code': 400}

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.bc.database.list_of('authenticate.UserInvite'), [])
        self.assertEqual(self.bc.database.list_of('payments.Plan'), [])

    """
    🔽🔽🔽 Post without UserInvite
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=now))
    def test_task__post__without_user_invite(self):
        url = reverse_lazy('authenticate:subscribe')
        data = {
            'email': 'pokemon@potato.io',
            'first_name': 'lord',
            'last_name': 'valdomero',
            'phone': '+123123123'
        }

        access_token = self.bc.random.string(lower=True, upper=True, number=True, size=40)
        with patch('binascii.hexlify', MagicMock(return_value=bytes(access_token, 'utf-8'))):
            response = self.client.post(url, data, format='json')

        json = response.json()
        expected = post_serializer(data={
            'id': 1,
            'access_token': access_token,
            **data,
        })

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.bc.database.list_of('authenticate.UserInvite'),
                         [{
                             'academy_id': None,
                             'author_id': None,
                             'cohort_id': None,
                             'id': 1,
                             'role_id': None,
                             'sent_at': None,
                             'status': 'ACCEPTED',
                             'token': hashlib.sha1(
                                 (str(now) + 'pokemon@potato.io').encode('UTF-8')).hexdigest(),
                             'process_message': '',
                             'process_status': 'DONE',
                             'syllabus_id': None,
                             **data,
                         }])

        self.assertEqual(self.bc.database.list_of('payments.Plan'), [])

    """
    🔽🔽🔽 Post with UserInvite
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=now))
    def test_task__post__with_user_invite__already_exists__status_waiting_list(self):
        """
        Descriptions of models are being generated:

          UserInvite(id=1): {}
        """

        user_invite = {'email': 'pokemon@potato.io', 'status': 'WAITING_LIST'}
        model = self.bc.database.create(user_invite=user_invite)

        url = reverse_lazy('authenticate:subscribe')
        data = {'email': 'pokemon@potato.io'}
        response = self.client.post(url, data, format='json')

        json = response.json()
        expected = {'detail': 'user-invite-exists', 'status_code': 400}

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.bc.database.list_of('authenticate.UserInvite'), [
            self.bc.format.to_dict(model.user_invite),
        ])

        self.assertEqual(self.bc.database.list_of('payments.Plan'), [])

    @patch('django.utils.timezone.now', MagicMock(return_value=now))
    def test_task__post__with_user_invite__already_exists__status_pending(self):
        """
        Descriptions of models are being generated:

          UserInvite(id=1): {}
        """

        user_invite = {'email': 'pokemon@potato.io', 'status': 'PENDING'}
        model = self.bc.database.create(user_invite=user_invite)

        url = reverse_lazy('authenticate:subscribe')
        data = {'email': 'pokemon@potato.io'}
        response = self.client.post(url, data, format='json')

        json = response.json()
        expected = {'detail': 'user-invite-exists-status-pending', 'status_code': 400}

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.bc.database.list_of('authenticate.UserInvite'), [
            self.bc.format.to_dict(model.user_invite),
        ])

        self.assertEqual(self.bc.database.list_of('payments.Plan'), [])

    @patch('django.utils.timezone.now', MagicMock(return_value=now))
    def test_task__post__with_user_invite__already_exists__status_accepted(self):
        """
        Descriptions of models are being generated:

          UserInvite(id=1): {}
        """

        user_invite = {'email': 'pokemon@potato.io', 'status': 'ACCEPTED'}
        model = self.bc.database.create(user_invite=user_invite)

        url = reverse_lazy('authenticate:subscribe')
        data = {'email': 'pokemon@potato.io'}
        response = self.client.post(url, data, format='json')

        json = response.json()
        expected = {'detail': 'user-invite-exists-status-accepted', 'status_code': 400}

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.bc.database.list_of('authenticate.UserInvite'), [
            self.bc.format.to_dict(model.user_invite),
        ])

        self.assertEqual(self.bc.database.list_of('payments.Plan'), [])

    """
    🔽🔽🔽 Post with UserInvite
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=now))
    def test_task__post__with_user_invite__user_exists(self):
        """
        Descriptions of models are being generated:

          User(id=1):
            groups: []
            user_permissions: []
        """

        user = {'email': 'pokemon@potato.io'}
        model = self.bc.database.create(user=user)

        url = reverse_lazy('authenticate:subscribe')
        data = {'email': 'pokemon@potato.io'}
        response = self.client.post(url, data, format='json')

        json = response.json()
        expected = {'detail': 'user-exists', 'status_code': 400}

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.bc.database.list_of('authenticate.UserInvite'), [])
        self.assertEqual(self.bc.database.list_of('payments.Plan'), [])

    """
    🔽🔽🔽 Post with UserInvite with other email
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=now))
    @patch('breathecode.notify.actions.send_email_message', MagicMock(return_value=None))
    @patch('breathecode.authenticate.models.Token.get_or_create', MagicMock(wraps=Token.get_or_create))
    def test_task__post__with_user_invite(self):
        """
        Descriptions of models are being generated:

          UserInvite(id=1): {}
        """

        user_invite = {'email': 'henrrieta@horseman.io', 'status': 'WAITING_LIST'}
        model = self.bc.database.create(user_invite=user_invite)

        url = reverse_lazy('authenticate:subscribe')
        data = {
            'email': 'pokemon@potato.io',
            'first_name': 'lord',
            'last_name': 'valdomero',
            'phone': '+123123123'
        }

        access_token = self.bc.random.string(lower=True, upper=True, number=True, size=40)
        with patch('binascii.hexlify', MagicMock(return_value=bytes(access_token, 'utf-8'))):
            response = self.client.post(url, data, format='json')

        json = response.json()
        expected = post_serializer(data={
            'id': 2,
            'access_token': access_token,
            **data,
        })

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.bc.database.list_of('authenticate.UserInvite'), [
            self.bc.format.to_dict(model.user_invite), {
                'academy_id': None,
                'author_id': None,
                'cohort_id': None,
                'id': 2,
                'role_id': None,
                'sent_at': None,
                'status': 'ACCEPTED',
                'token': hashlib.sha1((str(now) + 'pokemon@potato.io').encode('UTF-8')).hexdigest(),
                'process_message': '',
                'process_status': 'DONE',
                'syllabus_id': None,
                **data,
            }
        ])

        user_db = self.bc.database.list_of('auth.User')
        for item in user_db:
            self.assertTrue(isinstance(item['date_joined'], datetime))
            del item['date_joined']

        self.assertEqual(user_db, [{
            'email': 'pokemon@potato.io',
            'first_name': 'lord',
            'id': 1,
            'is_active': True,
            'is_staff': False,
            'is_superuser': False,
            'last_login': None,
            'last_name': 'valdomero',
            'password': '',
            'username': 'pokemon@potato.io',
        }])

        self.assertEqual(self.bc.database.list_of('payments.Plan'), [])

        self.assertEqual(notify_actions.send_email_message.call_args_list, [
            call(
                'pick_password', 'pokemon@potato.io', {
                    'SUBJECT':
                    'Set your password at 4Geeks',
                    'LINK': ('http://localhost:8000/v1/auth/password/' + hashlib.sha1(
                        (str(now) + 'pokemon@potato.io').encode('UTF-8')).hexdigest())
                })
        ])

        user = self.bc.database.get('auth.User', 1, dict=False)
        self.assertEqual(Token.get_or_create.call_args_list, [
            call(user=user, token_type='login'),
        ])

    """
    🔽🔽🔽 Post does not get in waiting list using a plan
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=now))
    @patch('breathecode.notify.actions.send_email_message', MagicMock(return_value=None))
    @patch('breathecode.authenticate.models.Token.get_or_create', MagicMock(wraps=Token.get_or_create))
    def test_task__post__does_not_get_in_waiting_list_using_a_plan(self):
        """
        Descriptions of models are being generated:

          UserInvite(id=1): {}
        """

        user_invite = {'email': 'henrrieta@horseman.io', 'status': 'WAITING_LIST'}
        plan = {'time_of_life': None, 'time_of_life_unit': None, 'has_waiting_list': True, 'invites': []}
        model = self.bc.database.create(user_invite=user_invite, plan=plan)

        url = reverse_lazy('authenticate:subscribe')
        data = {
            'email': 'pokemon@potato.io',
            'first_name': 'lord',
            'last_name': 'valdomero',
            'phone': '+123123123',
            'plan': 1,
        }
        access_token = self.bc.random.string(lower=True, upper=True, number=True, size=40)
        with patch('binascii.hexlify', MagicMock(return_value=bytes(access_token, 'utf-8'))):
            response = self.client.post(url, data, format='json')

        del data['plan']
        json = response.json()
        expected = put_serializer(model.user_invite, plans=[model.plan], data={
            'id': 2,
            **data,
        })

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.bc.database.list_of('authenticate.UserInvite'), [
            self.bc.format.to_dict(model.user_invite), {
                'academy_id': None,
                'author_id': None,
                'cohort_id': None,
                'id': 2,
                'role_id': None,
                'sent_at': None,
                'status': 'WAITING_LIST',
                'process_message': '',
                'process_status': 'PENDING',
                'token': hashlib.sha1((str(now) + 'pokemon@potato.io').encode('UTF-8')).hexdigest(),
                'syllabus_id': None,
                **data,
            }
        ])

        self.assertEqual(self.bc.database.list_of('auth.User'), [])
        self.assertEqual(self.bc.database.list_of('payments.Plan'), [plan_db_item(model.plan, data={})])
        self.bc.check.queryset_with_pks(model.plan.invites.all(), [2])
        self.bc.check.calls(notify_actions.send_email_message.call_args_list, [])
        self.bc.check.calls(Token.get_or_create.call_args_list, [])

    """
    🔽🔽🔽 Post get in waiting list using a plan
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=now))
    @patch('breathecode.notify.actions.send_email_message', MagicMock(return_value=None))
    @patch('breathecode.authenticate.models.Token.get_or_create', MagicMock(wraps=Token.get_or_create))
    def test_task__post__get_in_waiting_list_using_a_plan(self):
        """
        Descriptions of models are being generated:

          UserInvite(id=1): {}
        """

        user_invite = {'email': 'henrrieta@horseman.io', 'status': 'WAITING_LIST'}
        plan = {'time_of_life': None, 'time_of_life_unit': None, 'has_waiting_list': False, 'invites': []}
        model = self.bc.database.create(user_invite=user_invite, plan=plan)

        url = reverse_lazy('authenticate:subscribe')
        data = {
            'email': 'pokemon@potato.io',
            'first_name': 'lord',
            'last_name': 'valdomero',
            'phone': '+123123123',
            'plan': 1,
        }
        access_token = self.bc.random.string(lower=True, upper=True, number=True, size=40)
        with patch('binascii.hexlify', MagicMock(return_value=bytes(access_token, 'utf-8'))):
            response = self.client.post(url, data, format='json')

        del data['plan']
        json = response.json()
        expected = post_serializer(plans=[model.plan], data={
            'id': 2,
            'access_token': access_token,
            **data,
        })

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.bc.database.list_of('authenticate.UserInvite'), [
            self.bc.format.to_dict(model.user_invite), {
                'academy_id': None,
                'author_id': None,
                'cohort_id': None,
                'id': 2,
                'role_id': None,
                'sent_at': None,
                'status': 'ACCEPTED',
                'token': hashlib.sha1((str(now) + 'pokemon@potato.io').encode('UTF-8')).hexdigest(),
                'process_message': '',
                'process_status': 'DONE',
                'syllabus_id': None,
                **data,
            }
        ])

        self.assertEqual(self.bc.database.list_of('payments.Plan'), [plan_db_item(model.plan, data={})])
        self.bc.check.queryset_with_pks(model.plan.invites.all(), [2])

        token = hashlib.sha1((str(now) + data['email']).encode('UTF-8')).hexdigest()

        self.bc.check.calls(notify_actions.send_email_message.call_args_list, [
            call(
                'pick_password', 'pokemon@potato.io', {
                    'SUBJECT': 'Set your password at 4Geeks',
                    'LINK': f'http://localhost:8000/v1/auth/password/{token}'
                })
        ])

        User = self.bc.database.get_model('auth.User')
        user = User.objects.get(email=data['email'])

        self.bc.check.calls(Token.get_or_create.call_args_list, [
            call(user=user, token_type='login'),
        ])

    """
    🔽🔽🔽 Put without email
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=now))
    @patch('breathecode.notify.actions.send_email_message', MagicMock(return_value=None))
    @patch('breathecode.authenticate.models.Token.get_or_create', MagicMock(wraps=Token.get_or_create))
    def test_task__put__without_email(self):
        url = reverse_lazy('authenticate:subscribe')
        response = self.client.put(url)

        json = response.json()
        expected = {'detail': 'not-found', 'status_code': 404}

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.bc.database.list_of('authenticate.UserInvite'), [])
        self.assertEqual(self.bc.database.list_of('auth.User'), [])
        self.assertEqual(self.bc.database.list_of('payments.Plan'), [])

        self.assertEqual(notify_actions.send_email_message.call_args_list, [])
        self.assertEqual(Token.get_or_create.call_args_list, [])

    """
    🔽🔽🔽 Put with UserInvite, passing Cohort as None
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=now))
    @patch('breathecode.notify.actions.send_email_message', MagicMock(return_value=None))
    @patch('breathecode.authenticate.models.Token.get_or_create', MagicMock(wraps=Token.get_or_create))
    def test_task__put__with_user_invite__cohort_as_none(self):
        token = self.bc.random.string(lower=True, upper=True, number=True, size=40)
        user_invite = {
            'email': 'pokemon@potato.io',
            'status': 'WAITING_LIST',
            'token': token,
        }
        model = self.bc.database.create(user_invite=user_invite)
        url = reverse_lazy('authenticate:subscribe')
        data = {
            'email': 'pokemon@potato.io',
            'first_name': 'lord',
            'last_name': 'valdomero',
            'phone': '+123123123',
            'token': token,
        }

        access_token = self.bc.random.string(lower=True, upper=True, number=True, size=40)
        with patch('binascii.hexlify', MagicMock(return_value=bytes(access_token, 'utf-8'))):
            response = self.client.put(url, data, format='json')

        del data['token']

        json = response.json()

        expected = put_serializer(model.user_invite, data={
            'id': 1,
            'access_token': access_token,
            **data,
        })

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.bc.database.list_of('authenticate.UserInvite'),
                         [{
                             'academy_id': None,
                             'author_id': None,
                             'cohort_id': None,
                             'id': 1,
                             'role_id': None,
                             'sent_at': None,
                             'status': 'ACCEPTED',
                             'token': hashlib.sha1(
                                 (str(now) + 'pokemon@potato.io').encode('UTF-8')).hexdigest(),
                             'process_message': '',
                             'process_status': 'DONE',
                             'token': token,
                             'syllabus_id': None,
                             **data,
                         }])

        user_db = self.bc.database.list_of('auth.User')
        for item in user_db:
            self.assertTrue(isinstance(item['date_joined'], datetime))
            del item['date_joined']

        self.assertEqual(user_db, [{
            'email': 'pokemon@potato.io',
            'first_name': 'lord',
            'id': 1,
            'is_active': True,
            'is_staff': False,
            'is_superuser': False,
            'last_login': None,
            'last_name': 'valdomero',
            'password': '',
            'username': 'pokemon@potato.io',
        }])

        self.assertEqual(self.bc.database.list_of('payments.Plan'), [])

        self.assertEqual(notify_actions.send_email_message.call_args_list, [
            call(
                'pick_password', 'pokemon@potato.io', {
                    'SUBJECT': 'Set your password at 4Geeks',
                    'LINK': f'http://localhost:8000/v1/auth/password/{token}'
                })
        ])

        user = self.bc.database.get('auth.User', 1, dict=False)
        self.assertEqual(Token.get_or_create.call_args_list, [
            call(user=user, token_type='login'),
        ])

    """
    🔽🔽🔽 Put with UserInvite, passing Cohort not found
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=now))
    @patch('breathecode.notify.actions.send_email_message', MagicMock(return_value=None))
    @patch('breathecode.authenticate.models.Token.get_or_create', MagicMock(wraps=Token.get_or_create))
    def test_task__put__with_user_invite__cohort_not_found(self):
        token = self.bc.random.string(lower=True, upper=True, number=True, size=40)
        user_invite = {
            'email': 'pokemon@potato.io',
            'status': 'WAITING_LIST',
            'token': token,
        }
        self.bc.database.create(user_invite=user_invite)
        url = reverse_lazy('authenticate:subscribe')
        data = {
            'email': 'pokemon@potato.io',
            'first_name': 'lord',
            'last_name': 'valdomero',
            'phone': '+123123123',
            'cohort': 1,
            'token': token,
        }
        response = self.client.put(url, data, format='json')

        del data['token']

        json = response.json()
        expected = {'cohort': ['Invalid pk "1" - object does not exist.']}

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.bc.database.list_of('authenticate.UserInvite'),
                         [{
                             'academy_id': None,
                             'author_id': None,
                             'cohort_id': None,
                             'id': 1,
                             'role_id': None,
                             'sent_at': None,
                             'status': 'WAITING_LIST',
                             'token': hashlib.sha1(
                                 (str(now) + 'pokemon@potato.io').encode('UTF-8')).hexdigest(),
                             'process_message': '',
                             'process_status': 'PENDING',
                             'token': token,
                             'email': 'pokemon@potato.io',
                             'first_name': None,
                             'last_name': None,
                             'phone': '',
                             'syllabus_id': None,
                         }])

        self.assertEqual(self.bc.database.list_of('payments.Plan'), [])
        self.assertEqual(self.bc.database.list_of('auth.User'), [])

        self.assertEqual(notify_actions.send_email_message.call_args_list, [])
        self.assertEqual(Token.get_or_create.call_args_list, [])

    """
    🔽🔽🔽 Put with UserInvite, passing Cohort and it found
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=now))
    @patch('breathecode.notify.actions.send_email_message', MagicMock(return_value=None))
    @patch('breathecode.authenticate.models.Token.get_or_create', MagicMock(wraps=Token.get_or_create))
    def test_task__put__with_user_invite__cohort_found(self):
        token = self.bc.random.string(lower=True, upper=True, number=True, size=40)
        user_invite = {
            'email': 'pokemon@potato.io',
            'status': 'WAITING_LIST',
            'token': token,
        }
        model = self.bc.database.create(user_invite=user_invite, cohort=1)
        url = reverse_lazy('authenticate:subscribe')
        data = {
            'email': 'pokemon@potato.io',
            'first_name': 'lord',
            'last_name': 'valdomero',
            'phone': '+123123123',
            'cohort': 1,
            'token': token,
        }

        access_token = self.bc.random.string(lower=True, upper=True, number=True, size=40)
        with patch('binascii.hexlify', MagicMock(return_value=bytes(access_token, 'utf-8'))):
            response = self.client.put(url, data, format='json')

        del data['token']

        json = response.json()
        expected = put_serializer(model.user_invite, data={
            'id': 1,
            'access_token': access_token,
            **data,
        })

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        del data['cohort']
        self.assertEqual(self.bc.database.list_of('authenticate.UserInvite'),
                         [{
                             'academy_id': 1,
                             'author_id': None,
                             'cohort_id': 1,
                             'id': 1,
                             'role_id': None,
                             'sent_at': None,
                             'status': 'ACCEPTED',
                             'token': hashlib.sha1(
                                 (str(now) + 'pokemon@potato.io').encode('UTF-8')).hexdigest(),
                             'process_message': '',
                             'process_status': 'DONE',
                             'token': token,
                             'syllabus_id': None,
                             **data,
                         }])

        self.assertEqual(self.bc.database.list_of('payments.Plan'), [])

        user_db = self.bc.database.list_of('auth.User')
        for item in user_db:
            self.assertTrue(isinstance(item['date_joined'], datetime))
            del item['date_joined']

        self.assertEqual(user_db, [{
            'email': 'pokemon@potato.io',
            'first_name': 'lord',
            'id': 1,
            'is_active': True,
            'is_staff': False,
            'is_superuser': False,
            'last_login': None,
            'last_name': 'valdomero',
            'password': '',
            'username': 'pokemon@potato.io',
        }])

        self.assertEqual(notify_actions.send_email_message.call_args_list, [
            call(
                'pick_password', 'pokemon@potato.io', {
                    'SUBJECT': 'Set your password at 4Geeks',
                    'LINK': f'http://localhost:8000/v1/auth/password/{token}'
                })
        ])

        user = self.bc.database.get('auth.User', 1, dict=False)
        self.assertEqual(Token.get_or_create.call_args_list, [
            call(user=user, token_type='login'),
        ])

    """
    🔽🔽🔽 Put with UserInvite, passing Cohort and it found, Academy available as saas, User does not exists
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=now))
    @patch('breathecode.notify.actions.send_email_message', MagicMock(return_value=None))
    @patch('breathecode.authenticate.models.Token.get_or_create', MagicMock(wraps=Token.get_or_create))
    def test_task__put__with_user_invite__cohort_found__academy_available_as_saas__user_does_not_exists(self):
        token = self.bc.random.string(lower=True, upper=True, number=True, size=40)
        user_invite = {
            'email': 'pokemon@potato.io',
            'status': 'WAITING_LIST',
            'token': token,
        }
        academy = {'available_as_saas': True}
        model = self.bc.database.create(user_invite=user_invite, cohort=1, academy=academy)
        url = reverse_lazy('authenticate:subscribe')
        data = {
            'email': 'pokemon@potato.io',
            'first_name': 'lord',
            'last_name': 'valdomero',
            'phone': '+123123123',
            'cohort': 1,
            'token': token,
        }
        access_token = self.bc.random.string(lower=True, upper=True, number=True, size=40)
        with patch('binascii.hexlify', MagicMock(return_value=bytes(access_token, 'utf-8'))):
            response = self.client.put(url, data, format='json')

        del data['token']

        json = response.json()
        expected = put_serializer(model.user_invite, data={
            'id': 1,
            'access_token': access_token,
            **data,
        })

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        del data['cohort']
        self.assertEqual(self.bc.database.list_of('authenticate.UserInvite'),
                         [{
                             'academy_id': 1,
                             'author_id': None,
                             'cohort_id': 1,
                             'id': 1,
                             'role_id': None,
                             'sent_at': None,
                             'status': 'ACCEPTED',
                             'token': hashlib.sha1(
                                 (str(now) + 'pokemon@potato.io').encode('UTF-8')).hexdigest(),
                             'process_message': '',
                             'process_status': 'DONE',
                             'token': token,
                             'syllabus_id': None,
                             **data,
                         }])

        user_db = self.bc.database.list_of('auth.User')
        for item in user_db:
            self.assertTrue(isinstance(item['date_joined'], datetime))
            del item['date_joined']

        self.assertEqual(user_db, [{
            'email': 'pokemon@potato.io',
            'first_name': 'lord',
            'id': 1,
            'is_active': True,
            'is_staff': False,
            'is_superuser': False,
            'last_login': None,
            'last_name': 'valdomero',
            'password': '',
            'username': 'pokemon@potato.io',
        }])

        self.assertEqual(self.bc.database.list_of('payments.Plan'), [])

        self.assertEqual(notify_actions.send_email_message.call_args_list, [
            call(
                'pick_password', 'pokemon@potato.io', {
                    'SUBJECT': 'Set your password at 4Geeks',
                    'LINK': f'http://localhost:8000/v1/auth/password/{token}'
                })
        ])

        user = self.bc.database.get('auth.User', 1, dict=False)
        self.assertEqual(Token.get_or_create.call_args_list, [
            call(user=user, token_type='login'),
        ])

    """
    🔽🔽🔽 Put with UserInvite, passing Cohort and it found, Academy available as saas, User exists
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=now))
    @patch('breathecode.notify.actions.send_email_message', MagicMock(return_value=None))
    @patch('breathecode.authenticate.models.Token.get_or_create', MagicMock(wraps=Token.get_or_create))
    def test_task__put__with_user_invite__cohort_found__academy_available_as_saas__user_exists(self):
        token = self.bc.random.string(lower=True, upper=True, number=True, size=40)
        user_invite = {
            'email': 'pokemon@potato.io',
            'status': 'WAITING_LIST',
            'token': token,
        }
        academy = {'available_as_saas': True}
        user = {'email': 'pokemon@potato.io'}
        model = self.bc.database.create(user_invite=user_invite, cohort=1, academy=academy, user=user)
        url = reverse_lazy('authenticate:subscribe')
        data = {
            'email': 'pokemon@potato.io',
            'first_name': 'lord',
            'last_name': 'valdomero',
            'phone': '+123123123',
            'cohort': 1,
            'token': token,
        }
        access_token = self.bc.random.string(lower=True, upper=True, number=True, size=40)
        with patch('binascii.hexlify', MagicMock(return_value=bytes(access_token, 'utf-8'))):
            response = self.client.put(url, data, format='json')

        del data['token']

        json = response.json()
        expected = put_serializer(model.user_invite, data={
            'id': 1,
            'access_token': access_token,
            **data,
        })

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        del data['cohort']
        self.assertEqual(self.bc.database.list_of('authenticate.UserInvite'),
                         [{
                             'academy_id': 1,
                             'author_id': 1,
                             'cohort_id': 1,
                             'id': 1,
                             'role_id': None,
                             'sent_at': None,
                             'status': 'ACCEPTED',
                             'token': hashlib.sha1(
                                 (str(now) + 'pokemon@potato.io').encode('UTF-8')).hexdigest(),
                             'process_message': '',
                             'process_status': 'DONE',
                             'token': token,
                             'syllabus_id': None,
                             **data,
                         }])

        self.assertEqual(self.bc.database.list_of('payments.Plan'), [])
        self.assertEqual(self.bc.database.list_of('auth.User'), [self.bc.format.to_dict(model.user)])

        self.assertEqual(notify_actions.send_email_message.call_args_list, [])
        self.assertEqual(Token.get_or_create.call_args_list, [
            call(user=model.user, token_type='login'),
        ])

    """
    🔽🔽🔽 Put with UserInvite, passing Syllabus not found
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=now))
    @patch('breathecode.notify.actions.send_email_message', MagicMock(return_value=None))
    @patch('breathecode.authenticate.models.Token.get_or_create', MagicMock(wraps=Token.get_or_create))
    def test_task__put__with_user_invite__syllabus_not_found(self):
        token = self.bc.random.string(lower=True, upper=True, number=True, size=40)
        user_invite = {
            'email': 'pokemon@potato.io',
            'status': 'WAITING_LIST',
            'token': token,
        }
        self.bc.database.create(user_invite=user_invite)
        url = reverse_lazy('authenticate:subscribe')
        data = {
            'email': 'pokemon@potato.io',
            'first_name': 'lord',
            'last_name': 'valdomero',
            'phone': '+123123123',
            'syllabus': 1,
            'token': token,
        }
        response = self.client.put(url, data, format='json')

        del data['token']

        json = response.json()
        expected = {'syllabus': ['Invalid pk "1" - object does not exist.']}

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.bc.database.list_of('authenticate.UserInvite'),
                         [{
                             'academy_id': None,
                             'author_id': None,
                             'cohort_id': None,
                             'id': 1,
                             'role_id': None,
                             'sent_at': None,
                             'status': 'WAITING_LIST',
                             'token': hashlib.sha1(
                                 (str(now) + 'pokemon@potato.io').encode('UTF-8')).hexdigest(),
                             'process_message': '',
                             'process_status': 'PENDING',
                             'token': token,
                             'email': 'pokemon@potato.io',
                             'first_name': None,
                             'last_name': None,
                             'phone': '',
                             'syllabus_id': None,
                         }])

        self.assertEqual(self.bc.database.list_of('payments.Plan'), [])
        self.assertEqual(self.bc.database.list_of('auth.User'), [])

        self.assertEqual(notify_actions.send_email_message.call_args_list, [])
        self.assertEqual(Token.get_or_create.call_args_list, [])

    """
    🔽🔽🔽 Put with UserInvite, passing Syllabus and it found
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=now))
    @patch('breathecode.notify.actions.send_email_message', MagicMock(return_value=None))
    @patch('breathecode.authenticate.models.Token.get_or_create', MagicMock(wraps=Token.get_or_create))
    def test_task__put__with_user_invite__syllabus_found(self):
        token = self.bc.random.string(lower=True, upper=True, number=True, size=40)
        user_invite = {
            'email': 'pokemon@potato.io',
            'status': 'WAITING_LIST',
            'token': token,
            'cohort_id': None,
        }
        model = self.bc.database.create(user_invite=user_invite, cohort=1, syllabus_version=1)
        url = reverse_lazy('authenticate:subscribe')
        data = {
            'email': 'pokemon@potato.io',
            'first_name': 'lord',
            'last_name': 'valdomero',
            'phone': '+123123123',
            'syllabus': 1,
            'token': token,
        }

        access_token = self.bc.random.string(lower=True, upper=True, number=True, size=40)
        with patch('binascii.hexlify', MagicMock(return_value=bytes(access_token, 'utf-8'))):
            response = self.client.put(url, data, format='json')

        del data['token']

        json = response.json()

        expected = put_serializer(model.user_invite, data={
            'id': 1,
            'access_token': access_token,
            **data,
        })

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        del data['syllabus']
        self.assertEqual(self.bc.database.list_of('authenticate.UserInvite'), [
            {
                'academy_id': 1,
                'author_id': None,
                'cohort_id': None,
                'id': 1,
                'role_id': None,
                'sent_at': None,
                'status': 'ACCEPTED',
                'token': hashlib.sha1((str(now) + 'pokemon@potato.io').encode('UTF-8')).hexdigest(),
                'process_message': '',
                'process_status': 'DONE',
                'token': token,
                'syllabus_id': 1,
                **data,
            },
        ])

        self.assertEqual(self.bc.database.list_of('payments.Plan'), [])

        user_db = self.bc.database.list_of('auth.User')
        for item in user_db:
            self.assertTrue(isinstance(item['date_joined'], datetime))
            del item['date_joined']

        self.assertEqual(user_db, [{
            'email': 'pokemon@potato.io',
            'first_name': 'lord',
            'id': 1,
            'is_active': True,
            'is_staff': False,
            'is_superuser': False,
            'last_login': None,
            'last_name': 'valdomero',
            'password': '',
            'username': 'pokemon@potato.io',
        }])

        self.assertEqual(notify_actions.send_email_message.call_args_list, [
            call(
                'pick_password', 'pokemon@potato.io', {
                    'SUBJECT': 'Set your password at 4Geeks',
                    'LINK': f'http://localhost:8000/v1/auth/password/{token}'
                })
        ])

        user = self.bc.database.get('auth.User', 1, dict=False)
        self.assertEqual(Token.get_or_create.call_args_list, [
            call(user=user, token_type='login'),
        ])

    """
    🔽🔽🔽 Put with UserInvite, passing Syllabus and it found, Academy available as saas, User does not exists
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=now))
    @patch('breathecode.notify.actions.send_email_message', MagicMock(return_value=None))
    @patch('breathecode.authenticate.models.Token.get_or_create', MagicMock(wraps=Token.get_or_create))
    def test_task__put__with_user_invite__syllabus_found__academy_available_as_saas__user_does_not_exists(
            self):
        token = self.bc.random.string(lower=True, upper=True, number=True, size=40)
        user_invite = {
            'email': 'pokemon@potato.io',
            'status': 'WAITING_LIST',
            'token': token,
            'cohort_id': None,
        }
        academy = {'available_as_saas': True}
        model = self.bc.database.create(user_invite=user_invite,
                                        cohort=1,
                                        syllabus_version=1,
                                        academy=academy)
        url = reverse_lazy('authenticate:subscribe')
        data = {
            'email': 'pokemon@potato.io',
            'first_name': 'lord',
            'last_name': 'valdomero',
            'phone': '+123123123',
            'syllabus': 1,
            'token': token,
        }
        access_token = self.bc.random.string(lower=True, upper=True, number=True, size=40)
        with patch('binascii.hexlify', MagicMock(return_value=bytes(access_token, 'utf-8'))):
            response = self.client.put(url, data, format='json')

        del data['token']

        json = response.json()
        expected = put_serializer(model.user_invite, data={
            'id': 1,
            'access_token': access_token,
            **data,
        })

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        del data['syllabus']
        self.assertEqual(self.bc.database.list_of('authenticate.UserInvite'),
                         [{
                             'academy_id': 1,
                             'author_id': None,
                             'cohort_id': None,
                             'id': 1,
                             'role_id': None,
                             'sent_at': None,
                             'status': 'ACCEPTED',
                             'token': hashlib.sha1(
                                 (str(now) + 'pokemon@potato.io').encode('UTF-8')).hexdigest(),
                             'process_message': '',
                             'process_status': 'DONE',
                             'token': token,
                             'syllabus_id': 1,
                             **data,
                         }])

        user_db = self.bc.database.list_of('auth.User')
        for item in user_db:
            self.assertTrue(isinstance(item['date_joined'], datetime))
            del item['date_joined']

        self.assertEqual(user_db, [{
            'email': 'pokemon@potato.io',
            'first_name': 'lord',
            'id': 1,
            'is_active': True,
            'is_staff': False,
            'is_superuser': False,
            'last_login': None,
            'last_name': 'valdomero',
            'password': '',
            'username': 'pokemon@potato.io',
        }])

        self.assertEqual(self.bc.database.list_of('payments.Plan'), [])

        self.assertEqual(notify_actions.send_email_message.call_args_list, [
            call(
                'pick_password', 'pokemon@potato.io', {
                    'SUBJECT': 'Set your password at 4Geeks',
                    'LINK': f'http://localhost:8000/v1/auth/password/{token}'
                })
        ])

        user = self.bc.database.get('auth.User', 1, dict=False)
        self.assertEqual(Token.get_or_create.call_args_list, [
            call(user=user, token_type='login'),
        ])

    """
    🔽🔽🔽 Put with UserInvite, passing Syllabus and it found, Academy available as saas, User exists
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=now))
    @patch('breathecode.notify.actions.send_email_message', MagicMock(return_value=None))
    @patch('breathecode.authenticate.models.Token.get_or_create', MagicMock(wraps=Token.get_or_create))
    def test_task__put__with_user_invite__syllabus_found__academy_available_as_saas__user_exists(self):
        token = self.bc.random.string(lower=True, upper=True, number=True, size=40)
        user_invite = {
            'email': 'pokemon@potato.io',
            'status': 'WAITING_LIST',
            'token': token,
            'cohort_id': None,
        }
        academy = {'available_as_saas': True}
        user = {'email': 'pokemon@potato.io'}
        model = self.bc.database.create(user_invite=user_invite,
                                        cohort=1,
                                        syllabus_version=1,
                                        syllabus=1,
                                        academy=academy,
                                        user=user)
        url = reverse_lazy('authenticate:subscribe')
        data = {
            'email': 'pokemon@potato.io',
            'first_name': 'lord',
            'last_name': 'valdomero',
            'phone': '+123123123',
            'syllabus': 1,
            'token': token,
        }
        access_token = self.bc.random.string(lower=True, upper=True, number=True, size=40)
        with patch('binascii.hexlify', MagicMock(return_value=bytes(access_token, 'utf-8'))):
            response = self.client.put(url, data, format='json')

        del data['token']

        json = response.json()
        expected = put_serializer(model.user_invite, data={
            'id': 1,
            'access_token': access_token,
            **data,
        })

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        del data['syllabus']
        self.assertEqual(self.bc.database.list_of('authenticate.UserInvite'),
                         [{
                             'academy_id': 1,
                             'author_id': 1,
                             'cohort_id': None,
                             'id': 1,
                             'role_id': None,
                             'sent_at': None,
                             'status': 'ACCEPTED',
                             'token': hashlib.sha1(
                                 (str(now) + 'pokemon@potato.io').encode('UTF-8')).hexdigest(),
                             'process_message': '',
                             'process_status': 'DONE',
                             'token': token,
                             'syllabus_id': 1,
                             **data,
                         }])

        self.assertEqual(self.bc.database.list_of('payments.Plan'), [])
        self.assertEqual(self.bc.database.list_of('auth.User'), [self.bc.format.to_dict(model.user)])

        self.assertEqual(notify_actions.send_email_message.call_args_list, [])
        self.assertEqual(Token.get_or_create.call_args_list, [
            call(user=model.user, token_type='login'),
        ])

    """
    🔽🔽🔽 Put with UserInvite, passing Cohort and it found, Academy available as saas, User does not exists,
    Plan does not exists
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=now))
    @patch('breathecode.notify.actions.send_email_message', MagicMock(return_value=None))
    @patch('breathecode.authenticate.models.Token.get_or_create', MagicMock(wraps=Token.get_or_create))
    def test_task__put__plan_does_not_exist(self):
        token = self.bc.random.string(lower=True, upper=True, number=True, size=40)
        user_invite = {
            'email': 'pokemon@potato.io',
            'status': 'WAITING_LIST',
            'token': token,
        }
        academy = {'available_as_saas': True}
        self.bc.database.create(user_invite=user_invite, cohort=1, academy=academy)
        url = reverse_lazy('authenticate:subscribe')
        data = {
            'email': 'pokemon@potato.io',
            'first_name': 'lord',
            'last_name': 'valdomero',
            'phone': '+123123123',
            # 'cohort': 1,
            'token': token,
            'plan': 1,
        }
        access_token = self.bc.random.string(lower=True, upper=True, number=True, size=40)
        with patch('binascii.hexlify', MagicMock(return_value=bytes(access_token, 'utf-8'))):
            response = self.client.put(url, data, format='json')

        del data['token']

        json = response.json()
        expected = {'detail': 'plan-not-found', 'status_code': 400}

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # del data['cohort']
        self.assertEqual(self.bc.database.list_of('authenticate.UserInvite'),
                         [{
                             'academy_id': 1,
                             'author_id': None,
                             'cohort_id': 1,
                             'id': 1,
                             'role_id': None,
                             'sent_at': None,
                             'status': 'WAITING_LIST',
                             'email': 'pokemon@potato.io',
                             'first_name': None,
                             'last_name': None,
                             'phone': '',
                             'token': hashlib.sha1(
                                 (str(now) + 'pokemon@potato.io').encode('UTF-8')).hexdigest(),
                             'process_message': '',
                             'process_status': 'PENDING',
                             'token': token,
                             'syllabus_id': None,
                         }])

        self.assertEqual(self.bc.database.list_of('payments.Plan'), [])
        user_db = self.bc.database.list_of('auth.User')
        for item in user_db:
            self.assertTrue(isinstance(item['date_joined'], datetime))
            del item['date_joined']

        self.assertEqual(user_db, [])

        self.assertEqual(notify_actions.send_email_message.call_args_list, [])
        self.assertEqual(Token.get_or_create.call_args_list, [])

    """
    🔽🔽🔽 Put with UserInvite, passing Cohort and it found, Academy available as saas, User does not exists,
    Plan with has_waiting_list = True
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=now))
    @patch('breathecode.notify.actions.send_email_message', MagicMock(return_value=None))
    @patch('breathecode.authenticate.models.Token.get_or_create', MagicMock(wraps=Token.get_or_create))
    def test_task__put__plan_has_waiting_list(self):
        token = self.bc.random.string(lower=True, upper=True, number=True, size=40)
        user_invite = {
            'email': 'pokemon@potato.io',
            'status': 'WAITING_LIST',
            'token': token,
        }
        academy = {'available_as_saas': True}
        plan = {'time_of_life': None, 'time_of_life_unit': None, 'has_waiting_list': True, 'invites': []}
        model = self.bc.database.create(user_invite=user_invite, academy=academy, plan=plan)
        url = reverse_lazy('authenticate:subscribe')
        data = {
            'email': 'pokemon@potato.io',
            'first_name': 'lord',
            'last_name': 'valdomero',
            'phone': '+123123123',
            'token': token,
            'plan': 1,
        }
        access_token = self.bc.random.string(lower=True, upper=True, number=True, size=40)
        with patch('binascii.hexlify', MagicMock(return_value=bytes(access_token, 'utf-8'))):
            response = self.client.put(url, data, format='json')

        del data['token']
        del data['plan']

        json = response.json()
        expected = put_serializer(model.user_invite, plans=[model.plan], data={
            'id': 1,
            **data,
        })

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(self.bc.database.list_of('authenticate.UserInvite'), [{
            'academy_id': 1,
            'author_id': None,
            'cohort_id': None,
            'id': 1,
            'role_id': None,
            'sent_at': None,
            'status': 'WAITING_LIST',
            'process_message': '',
            'process_status': 'PENDING',
            'token': token,
            'syllabus_id': None,
            **data,
        }])

        self.assertEqual(self.bc.database.list_of('auth.User'), [])

        self.assertEqual(self.bc.database.list_of('payments.Plan'), [plan_db_item(model.plan, data={})])
        self.bc.check.queryset_with_pks(model.plan.invites.all(), [1])

        self.assertEqual(notify_actions.send_email_message.call_args_list, [])
        self.assertEqual(Token.get_or_create.call_args_list, [])

    """
    🔽🔽🔽 Put with UserInvite, passing Cohort and it found, Academy available as saas, User does not exists,
    Plan with has_waiting_list = False
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=now))
    @patch('breathecode.notify.actions.send_email_message', MagicMock(return_value=None))
    @patch('breathecode.authenticate.models.Token.get_or_create', MagicMock(wraps=Token.get_or_create))
    def test_task__put__plan_has_not_waiting_list(self):
        token = self.bc.random.string(lower=True, upper=True, number=True, size=40)
        user_invite = {
            'email': 'pokemon@potato.io',
            'status': 'WAITING_LIST',
            'token': token,
            'cohort_id': None,
        }
        academy = {'available_as_saas': True}
        plan = {'time_of_life': None, 'time_of_life_unit': None, 'has_waiting_list': False, 'invites': []}
        model = self.bc.database.create(user_invite=user_invite, cohort=1, academy=academy, plan=plan)
        url = reverse_lazy('authenticate:subscribe')
        data = {
            'email': 'pokemon@potato.io',
            'first_name': 'lord',
            'last_name': 'valdomero',
            'phone': '+123123123',
            'token': token,
            'plan': 1,
        }
        access_token = self.bc.random.string(lower=True, upper=True, number=True, size=40)
        with patch('binascii.hexlify', MagicMock(return_value=bytes(access_token, 'utf-8'))):
            response = self.client.put(url, data, format='json')

        del data['token']
        del data['plan']

        json = response.json()
        expected = put_serializer(model.user_invite,
                                  plans=[model.plan],
                                  data={
                                      'id': 1,
                                      'access_token': access_token,
                                      **data,
                                  })

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(self.bc.database.list_of('authenticate.UserInvite'), [{
            'academy_id': 1,
            'author_id': None,
            'cohort_id': None,
            'id': 1,
            'role_id': None,
            'sent_at': None,
            'status': 'ACCEPTED',
            'process_message': '',
            'process_status': 'DONE',
            'token': token,
            'syllabus_id': None,
            **data,
        }])

        user_db = self.bc.database.list_of('auth.User')
        for item in user_db:
            self.assertTrue(isinstance(item['date_joined'], datetime))
            del item['date_joined']

        self.assertEqual(self.bc.database.list_of('payments.Plan'), [plan_db_item(model.plan, data={})])
        self.bc.check.queryset_with_pks(model.plan.invites.all(), [1])

        self.assertEqual(user_db, [{
            'email': 'pokemon@potato.io',
            'first_name': 'lord',
            'id': 1,
            'is_active': True,
            'is_staff': False,
            'is_superuser': False,
            'last_login': None,
            'last_name': 'valdomero',
            'password': '',
            'username': 'pokemon@potato.io',
        }])

        self.assertEqual(notify_actions.send_email_message.call_args_list, [
            call(
                'pick_password', 'pokemon@potato.io', {
                    'SUBJECT': 'Set your password at 4Geeks',
                    'LINK': f'http://localhost:8000/v1/auth/password/{token}'
                })
        ])

        user = self.bc.database.get('auth.User', 1, dict=False)
        self.assertEqual(Token.get_or_create.call_args_list, [
            call(user=user, token_type='login'),
        ])
