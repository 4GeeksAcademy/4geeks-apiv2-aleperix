from datetime import timedelta
import random
from unittest.mock import MagicMock, call, patch
from rest_framework.authtoken.models import Token

from django.urls import reverse_lazy
from rest_framework import status

from breathecode.payments import signals

from django.utils import timezone
from ..mixins import PaymentsTestCase

UTC_NOW = timezone.now()


def format_user_setting(data={}):
    return {
        'id': 1,
        'user_id': 1,
        'main_currency_id': None,
        'lang': 'en',
        **data,
    }


def format_invoice_item(data={}):
    return {
        'academy_id': None,
        'amount': 0.0,
        'currency_id': 1,
        'bag_id': None,
        'id': 1,
        'paid_at': UTC_NOW,
        'status': 'FULFILLED',
        'stripe_id': None,
        'user_id': 1,
        **data,
    }


def get_serializer(self, currency, user, data={}):
    return {
        'amount': 0,
        'currency': {
            'code': currency.code,
            'name': currency.name,
        },
        'paid_at': self.bc.datetime.to_iso_string(UTC_NOW),
        'status': 'FULFILLED',
        'user': {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        },
        **data,
    }


def generate_amounts_by_time():
    return {
        'amount_per_month': random.random() * 100 + 1,
        'amount_per_quarter': random.random() * 100 + 1,
        'amount_per_half': random.random() * 100 + 1,
        'amount_per_year': random.random() * 100 + 1,
    }


def generate_three_amounts_by_time():
    l = random.shuffle([
        0,
        random.random() * 100 + 1,
        random.random() * 100 + 1,
        random.random() * 100 + 1,
    ])
    return {
        'amount_per_month': l[0],
        'amount_per_quarter': l[1],
        'amount_per_half': l[2],
        'amount_per_year': l[3],
    }


def which_amount_is_zero(data={}):
    for key in data:
        if key == 'amount_per_quarter':
            return 'MONTH', 1


CHOSEN_PERIOD = {
    'MONTH': 'amount_per_month',
    'QUARTER': 'amount_per_quarter',
    'HALF': 'amount_per_half',
    'YEAR': 'amount_per_year',
}


def get_amount_per_period(period, data):
    return data[CHOSEN_PERIOD[period]]


def invoice_mock():

    class FakeInvoice():
        id = 1
        amount = 100

    return FakeInvoice()


class SignalTestSuite(PaymentsTestCase):
    """
    🔽🔽🔽 GET without auth
    """

    def test__without_auth(self):
        url = reverse_lazy('payments:pay')
        response = self.client.post(url)

        json = response.json()
        expected = {'detail': 'Authentication credentials were not provided.', 'status_code': 401}

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.assertEqual(self.bc.database.list_of('payments.Bag'), [])
        self.assertEqual(self.bc.database.list_of('authenticate.UserSetting'), [])

    """
    🔽🔽🔽 Get with zero Bag, without passing token
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__without_bag__without_passing_token(self):
        model = self.bc.database.create(user=1)
        self.bc.request.authenticate(model.user)

        url = reverse_lazy('payments:pay')
        response = self.client.post(url)
        self.bc.request.authenticate(model.user)

        json = response.json()
        expected = {'detail': 'missing-token', 'status_code': 404}

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(self.bc.database.list_of('payments.Bag'), [])
        self.assertEqual(self.bc.database.list_of('payments.Invoice'), [])
        self.assertEqual(self.bc.database.list_of('authenticate.UserSetting'), [
            format_user_setting({'lang': 'en'}),
        ])

    """
    🔽🔽🔽 Get with zero Bag, passing token
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__without_bag__passing_token(self):
        model = self.bc.database.create(user=1)
        self.bc.request.authenticate(model.user)

        url = reverse_lazy('payments:pay')
        data = {'token': 'xdxdxdxdxdxdxdxdxdxd'}
        response = self.client.post(url, data, format='json')
        self.bc.request.authenticate(model.user)

        json = response.json()
        expected = {'detail': 'not-found-or-without-checking', 'status_code': 404}

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(self.bc.database.list_of('payments.Bag'), [])
        self.assertEqual(self.bc.database.list_of('payments.Invoice'), [])
        self.assertEqual(self.bc.database.list_of('authenticate.UserSetting'), [
            format_user_setting({'lang': 'en'}),
        ])

    """
    🔽🔽🔽 Get with zero Bag, passing token, without Plan and ServiceItem
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__without_bag__passing_token__empty_bag(self):
        bag = {
            'token': 'xdxdxdxdxdxdxdxdxdxd',
            'expires_at': UTC_NOW,
            'status': 'CHECKING',
            'type': 'BAG',
        }
        model = self.bc.database.create(user=1, bag=bag, currency=1, academy=1)
        self.bc.request.authenticate(model.user)

        url = reverse_lazy('payments:pay')
        data = {'token': 'xdxdxdxdxdxdxdxdxdxd'}
        response = self.client.post(url, data, format='json')
        self.bc.request.authenticate(model.user)

        json = response.json()
        expected = {'detail': 'bag-is-empty', 'status_code': 400}

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(self.bc.database.list_of('payments.Bag'), [self.bc.format.to_dict(model.bag)])
        self.assertEqual(self.bc.database.list_of('payments.Invoice'), [])
        self.assertEqual(self.bc.database.list_of('authenticate.UserSetting'), [
            format_user_setting({'lang': 'en'}),
        ])

        self.bc.check.queryset_with_pks(model.bag.plans.all(), [])
        self.bc.check.queryset_with_pks(model.bag.service_items.all(), [])

    """
    🔽🔽🔽 Get with zero Bag, passing token, with Plan and ServiceItem
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__without_bag__passing_token__with_bag_filled(self):
        bag = {
            'token': 'xdxdxdxdxdxdxdxdxdxd',
            'expires_at': UTC_NOW,
            'status': 'CHECKING',
            'type': 'BAG',
        }
        model = self.bc.database.create(user=1, bag=bag, academy=1, currency=1, plan=1, service_item=1)
        self.bc.request.authenticate(model.user)

        url = reverse_lazy('payments:pay')
        data = {'token': 'xdxdxdxdxdxdxdxdxdxd'}
        response = self.client.post(url, data, format='json')
        self.bc.request.authenticate(model.user)

        json = response.json()
        expected = {'detail': 'missing-chosen-period', 'status_code': 400}

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(self.bc.database.list_of('payments.Bag'), [self.bc.format.to_dict(model.bag)])
        self.assertEqual(self.bc.database.list_of('payments.Invoice'), [])
        self.assertEqual(self.bc.database.list_of('authenticate.UserSetting'), [
            format_user_setting({'lang': 'en'}),
        ])

        self.bc.check.queryset_with_pks(model.bag.plans.all(), [1])
        self.bc.check.queryset_with_pks(model.bag.service_items.all(), [1])

    """
    🔽🔽🔽 Get with zero Bag, passing token, with Plan and ServiceItem, passing chosen_period
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__without_bag__passing_token__passing_chosen_period__bad_value(self):
        bag = {
            'token': 'xdxdxdxdxdxdxdxdxdxd',
            'expires_at': UTC_NOW,
            'status': 'CHECKING',
            'type': 'BAG',
        }
        model = self.bc.database.create(user=1, bag=bag, academy=1, currency=1, plan=1, service_item=1)
        self.bc.request.authenticate(model.user)

        url = reverse_lazy('payments:pay')
        # data = {'token': 'xdxdxdxdxdxdxdxdxdxd', 'chosen_period': 'MONTH'}
        data = {'token': 'xdxdxdxdxdxdxdxdxdxd', 'chosen_period': self.bc.fake.slug()}
        response = self.client.post(url, data, format='json')
        self.bc.request.authenticate(model.user)

        json = response.json()
        expected = {'detail': 'invalid-chosen-period', 'status_code': 400}

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(self.bc.database.list_of('payments.Bag'), [self.bc.format.to_dict(model.bag)])
        self.assertEqual(self.bc.database.list_of('payments.Invoice'), [])
        self.assertEqual(self.bc.database.list_of('authenticate.UserSetting'), [
            format_user_setting({'lang': 'en'}),
        ])

        self.bc.check.queryset_with_pks(model.bag.plans.all(), [1])
        self.bc.check.queryset_with_pks(model.bag.service_items.all(), [1])

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    @patch('breathecode.payments.tasks.build_subscription.delay', MagicMock())
    def test__without_bag__passing_token__passing_chosen_period__good_value(self):
        bag = {
            'token': 'xdxdxdxdxdxdxdxdxdxd',
            'expires_at': UTC_NOW,
            'status': 'CHECKING',
            'type': 'BAG',
        }
        chosen_period = random.choice(['MONTH', 'QUARTER', 'HALF', 'YEAR'])
        model = self.bc.database.create(user=1, bag=bag, academy=1, currency=1, plan=1, service_item=1)
        self.bc.request.authenticate(model.user)

        url = reverse_lazy('payments:pay')
        data = {
            'token': 'xdxdxdxdxdxdxdxdxdxd',
            'chosen_period': chosen_period,
        }
        response = self.client.post(url, data, format='json')
        self.bc.request.authenticate(model.user)

        json = response.json()
        expected = get_serializer(self, model.currency, model.user, data={})

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(self.bc.database.list_of('payments.Bag'),
                         [{
                             **self.bc.format.to_dict(model.bag),
                             'token': None,
                             'status': 'PAID',
                             'expires_at': None,
                             'chosen_period': chosen_period,
                         }])
        self.assertEqual(self.bc.database.list_of('payments.Invoice'), [format_invoice_item()])
        self.assertEqual(self.bc.database.list_of('authenticate.UserSetting'), [
            format_user_setting({'lang': 'en'}),
        ])

        self.bc.check.queryset_with_pks(model.bag.plans.all(), [1])
        self.bc.check.queryset_with_pks(model.bag.service_items.all(), [1])

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    @patch('breathecode.payments.tasks.build_subscription.delay', MagicMock())
    @patch('stripe.Charge.create', MagicMock(return_value={'id': 1}))
    @patch('stripe.Customer.create', MagicMock(return_value={'id': 1}))
    def test__without_bag__passing_token__passing_chosen_period__good_value__amount_set(self):
        bag = {
            'token': 'xdxdxdxdxdxdxdxdxdxd',
            'expires_at': UTC_NOW,
            'status': 'CHECKING',
            'type': 'BAG',
            **generate_amounts_by_time()
        }
        chosen_period = random.choice(['MONTH', 'QUARTER', 'HALF', 'YEAR'])
        amount = get_amount_per_period(chosen_period, bag)
        model = self.bc.database.create(user=1, bag=bag, academy=1, currency=1, plan=1, service_item=1)
        self.bc.request.authenticate(model.user)

        url = reverse_lazy('payments:pay')
        data = {
            'token': 'xdxdxdxdxdxdxdxdxdxd',
            'chosen_period': chosen_period,
        }
        response = self.client.post(url, data, format='json')
        self.bc.request.authenticate(model.user)

        json = response.json()
        expected = get_serializer(self, model.currency, model.user, data={'amount': amount})

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(self.bc.database.list_of('payments.Bag'),
                         [{
                             **self.bc.format.to_dict(model.bag),
                             'token': None,
                             'status': 'PAID',
                             'expires_at': None,
                             'chosen_period': chosen_period,
                         }])
        self.assertEqual(self.bc.database.list_of('payments.Invoice'), [
            format_invoice_item({
                'amount': amount,
                'stripe_id': '1',
            }),
        ])
        self.assertEqual(self.bc.database.list_of('authenticate.UserSetting'), [
            format_user_setting({'lang': 'en'}),
        ])

        self.bc.check.queryset_with_pks(model.bag.plans.all(), [1])
        self.bc.check.queryset_with_pks(model.bag.service_items.all(), [1])

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    @patch('breathecode.payments.tasks.build_subscription.delay', MagicMock())
    @patch('stripe.Charge.create', MagicMock(return_value={'id': 1}))
    @patch('stripe.Customer.create', MagicMock(return_value={'id': 1}))
    def test__without_bag__passing_token__passing_chosen_period__good_value__amount_set__(self):
        cases = [
            (
                'MONTH',  # chosen period
                { # values
                    'amount_per_month': random.random() * 99 + 1,
                    'amount_per_quarter': 0,
                    'amount_per_half': 0,
                    'amount_per_year': 0,
                },
                'amount_per_month',  # field pick up to calculate the amount
                1,  # multiplier of the amount
            ),
            (
                'QUARTER',
                {
                    'amount_per_month': random.random() * 99 + 1,
                    'amount_per_quarter': 0,
                    'amount_per_half': 0,
                    'amount_per_year': 0,
                },
                'amount_per_month',
                3,
            ),
            (
                'HALF',
                {
                    'amount_per_month': 0,
                    'amount_per_quarter': random.random() * 99 + 1,
                    'amount_per_half': 0,
                    'amount_per_year': 0,
                },
                'amount_per_quarter',
                2,
            ),
            (
                'HALF',
                {
                    'amount_per_month': random.random() * 99 + 1,
                    'amount_per_quarter': 0,
                    'amount_per_half': 0,
                    'amount_per_year': 0,
                },
                'amount_per_month',
                6,
            ),
            (
                'YEAR',
                {
                    'amount_per_month': 0,
                    'amount_per_quarter': 0,
                    'amount_per_half': random.random() * 99 + 1,
                    'amount_per_year': 0,
                },
                'amount_per_half',
                2,
            ),
            (
                'YEAR',
                {
                    'amount_per_month': 0,
                    'amount_per_quarter': random.random() * 99 + 1,
                    'amount_per_half': 0,
                    'amount_per_year': 0,
                },
                'amount_per_quarter',
                4,
            ),
            (
                'YEAR',
                {
                    'amount_per_month': random.random() * 99 + 1,
                    'amount_per_quarter': 0,
                    'amount_per_half': 0,
                    'amount_per_year': 0,
                },
                'amount_per_month',
                12,
            ),
        ]
        cases = [(0, 0, random.random() * 99 + 1, 0)]
        bag = {
            'token': 'xdxdxdxdxdxdxdxdxdxd',
            'expires_at': UTC_NOW,
            'status': 'CHECKING',
            'type': 'BAG',
            **generate_amounts_by_time()
        }
        chosen_period = random.choice(['MONTH', 'QUARTER', 'HALF', 'YEAR'])
        amount = get_amount_per_period(chosen_period, bag)
        model = self.bc.database.create(user=1, bag=bag, academy=1, currency=1, plan=1, service_item=1)
        self.bc.request.authenticate(model.user)

        url = reverse_lazy('payments:pay')
        data = {
            'token': 'xdxdxdxdxdxdxdxdxdxd',
            'chosen_period': chosen_period,
        }
        response = self.client.post(url, data, format='json')
        self.bc.request.authenticate(model.user)

        json = response.json()
        expected = get_serializer(self, model.currency, model.user, data={'amount': amount})

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(self.bc.database.list_of('payments.Bag'),
                         [{
                             **self.bc.format.to_dict(model.bag),
                             'token': None,
                             'status': 'PAID',
                             'expires_at': None,
                             'chosen_period': chosen_period,
                         }])
        self.assertEqual(self.bc.database.list_of('payments.Invoice'), [
            format_invoice_item({
                'amount': amount,
                'stripe_id': '1',
            }),
        ])
        self.assertEqual(self.bc.database.list_of('authenticate.UserSetting'), [
            format_user_setting({'lang': 'en'}),
        ])

        self.bc.check.queryset_with_pks(model.bag.plans.all(), [1])
        self.bc.check.queryset_with_pks(model.bag.service_items.all(), [1])
