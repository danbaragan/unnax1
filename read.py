#!/usr/bin/env python3

import argparse

from store import db, User
from auth import global_session, set_session, authenticated, authorized
from fixtures import auto_fix



@authenticated
@authorized
def read_and_print(username):
    u = User.select().where(User.username == username).get()
    accounts = u.accounts()
    print(f"Accounts( {len(accounts)} )")
    for a in accounts:
        print(f"\tAccount Data:")
        print(f"\t\tName: {a.name}")
        print(f"\t\tNumber: {a.iban}")
        print(f"\t\tCurrency: {a.currency}")
        print(f"\t\tBalance: {a.balance}")

        print(f"\tTotal Customers: {a.useraccount_set.count()}")
        for u in a.useraccount_set:
            print(f"\t\tCustomer Data:")
            print(f"\t\t\tName: {u.user.name} {u.user.surname} ({u.user.username})")
            print(f"\t\t\tParticipation: {u.role}")
            print(f"\t\t\tDoc: {u.user.username}")
            print(f"\t\t\tAddress: {u.user.address}")
            print(f"\t\t\tEmail: {u.user.email}")
            print(f"\t\t\tPhone: {u.user.phone}")

        statements = a.statement()
        print(f"\tStatements ({len(statements)})")
        print(f"\t\tDate                       | Amt | Balance| Concept ")
        for s in statements:
            print(f"\t\t{s.date_created} | {s.amount} | {s.balance} | {s.note}")

def main(username):
    read_and_print(username)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Login to username and interogate his bank accounts")
    parser.add_argument("-u", "--username", help="Username whos bank information you want to see")
    parser.add_argument("-p", "--password", help="The password of the above user")
    args = parser.parse_args()
    db.connect()

    auto_fix()

    set_session(args.username, args.password)

    main(args.username)
    db.close()

