# You can run this tests from the parent dir. (you need pytest, coverage, pytest-cov)
# pytest -v
# pytest --cov=linkConfig --cov-report=html tests/

import pytest

from argparse import Namespace
from datetime import datetime, timedelta

from peewee import SqliteDatabase

import store
import auth
import read

MODELS = (
    store.User,
    store.Account,
    store.UserAccount,
    store.Transaction,
)

@pytest.fixture
def db(monkeypatch):
    testdb = SqliteDatabase('test.db')
    monkeypatch.setattr(store, 'db', testdb)
    for model in MODELS:
        monkeypatch.setattr(model._meta, 'database', testdb)
    yield testdb


@pytest.fixture
def db_basic_structure(db):
    db.create_tables(MODELS)
    now = datetime.utcnow()
    time1 = now - timedelta(1)
    u1 = store.User(
        username='testUser',
        password_hash=store.User.hash_password('testPassword'),
        date_created=time1,
        date_modified=time1,
        name='FirstName',
        surname='LastName',
    )
    u1.save()
    u2 = store.User(
        username='testUser2',
        password_hash=store.User.hash_password('testPassword2'),
        date_created=now,
        date_modified=now,
        name='FirstName2',
        surname='LastName2',
    )
    u2.save()
    yield u1, u2
    db.drop_tables(MODELS)

@pytest.fixture
def db_structure(db_basic_structure):
    u1, u2 = db_basic_structure
    now = datetime.utcnow()
    # some user 1 stuff
    a1 = store.Account(
        name = 'Cuenta personal',
        iban = 'ES232100123303030032',
        currency = 'EUR',
        balance = 352,
        date_created = now,
        date_modified = now,
    )
    a1.save()
    ua1 = store.UserAccount(
        user = u1,
        account = a1,
        role = 'Titular',
    )
    ua1.save()
    a2 = store.Account(
        name = 'Cuenta ahorro',
        iban = 'ES232100523522355235',
        currency = 'EUR',
        balance = 1322.2,
        date_created = now,
        date_modified = now,
    )
    a2.save()
    ua2 = store.UserAccount(
        user = u1,
        account = a2,
        role = 'Titular'
    )
    ua2.save()

    # some user2 stuff
    ua3 = store.UserAccount(
        user = u2,
        account = a2,
        role = 'Observador'
    )
    ua3.save()

    a4 = store.Account(
        name = 'Cuenta ahorro',
        iban = 'ES232100003522000000',
        currency = 'USD',
        balance = 132.9,
        date_created = now,
        date_modified = now,
    )
    a4.save()
    ua4 = store.UserAccount(
        user = u2,
        account = a4,
        role = 'Titular'
    )
    ua4.save()

    tu2 = store.Transaction(
        account = a4,
        date_created = now,
        amount = -50,
        note = 'Bar New York',
    )
    tu2.save()

    # user 1 transactions
    t1 = store.Transaction(
        account = a1,
        date_created = now,
        amount = -30,
        note = 'Bar Pepe',
    )
    t1.save()

    t2 = store.Transaction(
        account = a1,
        date_created = now - timedelta(1),
        amount = 100,
        note = 'Transferencia',
    )
    t2.save()

    t11 = store.Transaction(
        account = a2,
        date_created = now,
        amount = -12,
        note = 'McDonalds',
    )
    t11.save()

    t12 = store.Transaction(
        account = a2,
        date_created = now - timedelta(1),
        amount = 280,
        note = 'Nomina',
    )
    t12.save()

    return u1, u2



@pytest.mark.usefixtures("db_basic_structure")
class TestBasicStore:
    def test_rightDatabase(self):
        user = store.User.select().order_by(store.User.date_created)[:1][0]
        assert user.username == 'testUser'


@pytest.mark.usefixtures("db_basic_structure")
class TestAuth:
    def test_session_login_ok(self):
        auth.set_session('testUser', 'testPassword')
        assert auth.global_session.logged

    def test_session_login_bad_pass(self):
        auth.set_session('testUser', 'testPasswordX')
        assert not auth.global_session.logged

    def test_session_login_bad_user(self):
        auth.set_session('testUserX', 'testPassword')
        assert not auth.global_session.logged


@pytest.mark.usefixtures("db_structure")
class TestStore:
    def test_user_accounts(self):
        u1 = store.User.get(store.User.username == 'testUser')
        u2 = store.User.get(store.User.username == 'testUser2')
        user_accounts = u1.accounts()
        assert len(user_accounts) == 2
        a1_users = [ x.user for x in user_accounts[0].useraccount_set ]
        assert a1_users == [u1]
        a2_users = [ x.user for x in user_accounts[1].useraccount_set ]
        assert a2_users == [u1, u2]

    def test_account_statement(self):
        a1 = store.Account.get(store.Account.iban == 'ES232100123303030032')
        statements = a1.statement()
        assert len(statements) == 2
        s1 = statements[0]
        assert s1.amount == -30
        assert s1.balance == a1.balance
        s2 = statements[1]
        assert s2.amount == 100
        assert s2.balance == a1.balance - s1.amount
        assert s1.date_created > s2.date_created
