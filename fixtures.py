from datetime import datetime, timedelta
from peewee import OperationalError

from store import (
    db,
    User,
    Account,
    UserAccount,
    Transaction,
)


def auto_fix():
    try:
        User.select().count()
    except OperationalError as e:
        if "no such table:" in str(e):
            db.create_tables([
                User,
                Account,
                UserAccount,
                Transaction,
            ])
            # insert some data
            now = datetime.utcnow()
            u1 = User(
                username='Y3216434F',
                password_hash=User.hash_password('pperez2018'),
                date_created=now,
                date_modified=now,
                name='Pepito',
                surname='Perez',
            )
            u1.save()
            
            u2 = User(
                username='second',
                password_hash=User.hash_password('secondPass'),
                date_created=now,
                date_modified=now,
                name='P',
                surname='P',
            )
            u2.save()

            a1 = Account(
                name = 'Cuenta personal',
                iban = 'ES232100123303030032',
                currency = 'EUR',
                balance = 352,
                date_created = now,
                date_modified = now,
            )
            a1.save()
            ua1 = UserAccount(
                user = u1,
                account = a1,
                role = 'Titular',
            )
            ua1.save()
            a2 = Account(
                name = 'Cuenta ahorro',
                iban = 'ES232100523522355235',
                currency = 'EUR',
                balance = 1322.2,
                date_created = now,
                date_modified = now,
            )
            a2.save()
            ua2 = UserAccount(
                user = u1,
                account = a2,
                role = 'Titular'
            )
            ua2.save()

            ua3 = UserAccount(
                user = u2,
                account = a2,
                role = 'Observador'
            )
            ua3.save()

            t1 = Transaction(
                account = a1,
                date_created = now,
                amount = -30,
                note = 'Bar Pepe',
            )
            t1.save()

            t2 = Transaction(
                account = a1,
                date_created = now - timedelta(1),
                amount = 100,
                note = 'Transferencia',
            )
            t2.save()

            t3 = Transaction(
                account = a1,
                date_created = now - timedelta(2),
                amount = -20,
                note = 'Compra online',
            )
            t3.save()

            t11 = Transaction(
                account = a2,
                date_created = now,
                amount = -12,
                note = 'McDonalds',
            )
            t11.save()

            t12 = Transaction(
                account = a2,
                date_created = now - timedelta(1),
                amount = 280,
                note = 'Nomina',
            )
            t12.save()

            t13 = Transaction(
                account = a2,
                date_created = now - timedelta(2),
                amount = 280,
                note = 'Nomina',
            )
            t13.save()

            db.close()
            db.connect()
