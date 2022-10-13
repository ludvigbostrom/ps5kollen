from dataclasses import dataclass
from datetime import datetime

from twitter import Twitter

from pages import Page
from settings import DEV_TWITTER


@dataclass
class TweetData:
    page: Page


def dm_developer_internal_exception(t: Twitter, errors: dict):
    if not DEV_TWITTER:
        raise Exception("No dev username")
    return t.direct_messages.events.new(
        _json={
            "event": {
                "type": "message_create",
                "message_create": {
                    "target": {
                        "recipient_id": t.users.show(screen_name=DEV_TWITTER)["id"]},
                    "message_data": {
                        "text": f'Errors from ps5kollen: {errors}'}}}})


def dm_developer_page_exception(t: Twitter, stacktrace: str, page: Page = None):
    if not DEV_TWITTER:
        raise Exception("No dev username")
    return t.direct_messages.events.new(
        _json={
            "event": {
                "type": "message_create",
                "message_create": {
                    "target": {
                        "recipient_id": t.users.show(screen_name=DEV_TWITTER)["id"]},
                    "message_data": {
                        "text": f'Error for page {page.name if page else "Tomter"}: {stacktrace}'}}}})


def post_tweet(t: Twitter, tweet_data: TweetData):
    url = tweet_data.page.visit_url or tweet_data.page.url
    t.statuses.update(status=f"{tweet_data.page.msg} {url}")
