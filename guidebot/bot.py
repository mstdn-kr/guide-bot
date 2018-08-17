import logging
import os

from pprint import pprint

import attrdict
import mastodon
from lxml import html

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Account


class StreamHandler(mastodon.StreamListener):

    def __init__(self, api: mastodon.Mastodon, db_session):
        super().__init__()
        self.api = api
        self.db_session = db_session
        self.logger = logging.getLogger()
        self.me = api.account_verify_credentials()

        print(self.me.acct)

    def on_notification(self, notification):
        notification = attrdict.AttrDict(notification)

        if notification.type != 'mention':
            return

        status = notification.status
        context = attrdict.AttrDict(self.api.status_context(status.id))
        ancestors = context.ancestors
        descendants = context.descendants

        pprint([f'{status.account.acct}: {self.plain_text(status.content)}'
                for status in ancestors])
        pprint(f'{status.account.acct}: {self.plain_text(status.content)}')
        pprint([f'{status.account.acct}: {self.plain_text(status.content)}'
                for status in descendants])

    def get_helpers(self):
        return [
            account.acct
            for account in self.db_session.query(Account)
        ]

    def add_helper(self, acct: str):
        if '@' not in acct:
            instance = self.api.instance()['uri']
            acct = f'{acct}@{instance}'
        account = Account()
        account.acct = acct
        self.db_session.add(account)
        try:
            self.db_session.commit()
        except Exception as e:
            self.db_session.rollback()
            print(e)
        finally:
            self.db_session.close()

    def remove_helper(self, acct: str):
        if '@' not in acct:
            instance = self.api.instance()['uri']
            acct = f'{acct}@{instance}'

        account = self.db_session.query(Account).get(acct)

        if account:
            self.db_session.remove(account)
        try:
            self.db_session.commit()
        except Exception as e:
            print(e)
            self.db_session.rollback()
        finally:
            self.db_session.close()

    @staticmethod
    def plain_text(text: str):
        doc = html.fromstring(text)
        for link in doc.xpath('//a'):
            link.drop_tree()

        return doc.text_content().strip()


def main():
    engine = create_engine(os.environ.get('DATABASE_URL'))
    Session = sessionmaker(engine)

    session = Session()

    api = mastodon.Mastodon(
        api_base_url='https://qdon.space',
        client_id=os.environ.get('MASTODON_CLIENT_KEY'),
        client_secret=os.environ.get('MASTODON_CLIENT_SECRET'),
        access_token=os.environ.get('MASTODON_ACCESS_TOKEN'))

    handler = StreamHandler(api, session)

    api.stream_user(handler)
