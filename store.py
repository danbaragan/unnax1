from peewee import (
    SqliteDatabase,
    Model,
    CharField,
    DecimalField,
    DateTimeField,
    ForeignKeyField,
)

from hasher import *

db = SqliteDatabase('bank.db')



class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    username = CharField()
    password_hash = CharField()
    date_created = DateTimeField()
    date_modified = DateTimeField()
    name = CharField()
    middlename = CharField(null=True)
    surname = CharField()
    address = CharField(null=True)
    email = CharField(null=True)
    phone = CharField(null=True)


    @staticmethod
    def hash_password(password):
        return hasher.hash(password)

    def accounts(self):
        # get this user accounts. also get addtional users for those accounts
        # peewee is kind enough to let us use subqueries so we'll send a single query to engine
        # peewee will also nest the objects according to model,
        # thus the duplicate infomation from our single big query will be nest duplicated
        # so instead of:
        # a1 u1
        # a2 u1
        # a2 u2
        # we will get
        # a1 [u1]
        # a2 [u1, u2]
        # a2 [u1, u2]

        TargetAccount = Account.alias()
        target_accounts = (TargetAccount
            .select(TargetAccount.id)
            .join(UserAccount)
            .join(User)
            .where(User.username == self.username)
            .alias('target_accounts')
        )
        accounts = (Account
            .select(Account, User)
            .where(Account.id << target_accounts)
            .join(UserAccount)
            .join(User)
            .order_by(Account.id)
        )

        pruned_accounts = []
        for account in accounts:
            last_id = pruned_accounts[-1].id if len(pruned_accounts) else None
            if last_id != account.id:
                pruned_accounts.append(account)

        return pruned_accounts


class Account(BaseModel):
    name = CharField()
    iban = CharField()
    currency = CharField()
    balance = DecimalField(10, 2)
    date_created = DateTimeField()
    date_modified = DateTimeField()

    # allow time bounds here
    def statement(self):
        # get transactions, compute balance
        # we can also use an SQL agregate function here
        # but it does not make sense unless we select all the required info
        # in a single big query along with account and users
        # this will confuse each class responsability and make everything messy and
        # it sure looks like premature optimization
        statements = self.transactions.order_by(Transaction.date_created.desc())
        balance = self.balance
        for s in statements:
            s.balance = balance
            balance -= s.amount

        return statements


class UserAccount(BaseModel):
    user = ForeignKeyField(User)
    account = ForeignKeyField(Account)
    role = CharField()


class Transaction(BaseModel):
    account = ForeignKeyField(Account, backref='transactions')
    date_created = DateTimeField()
    amount = DecimalField(10, 2)
    note = CharField()

