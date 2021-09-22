import traceback
from datetime import datetime
from time import sleep

from twitter import Twitter, OAuth

from pages import PAGES
from twitter_utils import post_tweet, dm_developer_page_exception, dm_developer_internal_exception, TweetData
from settings import ACCESS_TOKEN, ACCESS_TOKEN_SECRET, API_KEY, API_KEY_SECRET

t = Twitter(
    auth=OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, API_KEY, API_KEY_SECRET)
) if ACCESS_TOKEN else None

TWEETS = {}


def run():
    latest_exception = ()
    counter = 0
    while True:
        for page in PAGES:
            try:
                print(f'Checking {page.name}')
                if page.check_stock():
                    print('In Stock')
                    if page.name in TWEETS:
                        print('Already tweeted')
                        continue
                    tweet = TweetData(page=page, time=datetime.now())
                    if counter > 0:
                        if t:
                            post_tweet(t, tweet)
                        else:
                            print(f"Not really tweeting: {tweet}")
                    TWEETS[page.name] = tweet
                elif page.name in TWEETS:
                    TWEETS.pop(page.name)
            except Exception as ex:
                e = traceback.format_exc()
                print(ex)
                if t:
                    # Workaround to not spam developer with exceptions. Only one per hour if it is the same.
                    if not latest_exception:
                        latest_exception = (datetime.now(), ex)
                    if datetime.now().hour != latest_exception[0].hour and ex != latest_exception[1]:
                        latest_exception = (datetime.now(), ex)
                        try:
                            rsp = dm_developer_page_exception(t, e, page)
                        except Exception:
                            # retry DM to developer if it fails the first time. This time with what caused the dm to fail.
                            twitter_error = f"Twitter dm error {traceback.format_exc()}"
                            try:
                                dm_developer_internal_exception(t, {"rsp": rsp, "error": twitter_error, "exc": traceback.format_exc()})
                            except Exception as final_ex:
                                print(final_ex)

        counter = counter + 1
        sleep(5)


if __name__ == '__main__':
    run()
