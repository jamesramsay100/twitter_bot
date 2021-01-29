import requests, os, json, re
import pandas as pd
from nltk.tokenize import WordPunctTokenizer
from bs4 import BeautifulSoup
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv(override=True)

# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'


def auth():
    return os.environ.get("BEARER_TOKEN")


def create_url(user_id, max_id=None):
    # Replace with user ID below
    # user_id = 2244994945
    if max_id:
        return f"https://api.twitter.com/2/users/{user_id}/tweets?max_results={100}&until_id={max_id}&exclude=retweets,replies"
    else:
        return f"https://api.twitter.com/2/users/{user_id}/tweets?max_results={100}&exclude=retweets,replies"


def get_params():
    # Tweet fields are adjustable.
    # Options include:
    # attachments, author_id, context_annotations,
    # conversation_id, created_at, entities, geo, id,
    # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
    # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
    # source, text, and withheld
    return {"tweet.fields": "created_at"}


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def connect_to_endpoint(url, headers, params):
    response = requests.request("GET", url, headers=headers, params=params)
    # print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def download(user_id):

    user_tweets = pd.DataFrame()

    bearer_token = auth()
    url = create_url(user_id)
    headers = create_headers(bearer_token)
    params = get_params()
    json_response = connect_to_endpoint(url, headers, params)

    try:
        tweets = pd.DataFrame(json_response['data'])
        user_tweets = user_tweets.append(tweets)

        # can only download 100 tweets at a time
        while tweets.shape[0] == 100:

            max_id = tweets['id'].iloc[-1]
            url = create_url(user_id, max_id)
            json_response = connect_to_endpoint(url, headers, params)
            tweets = pd.DataFrame(json_response['data'])
            user_tweets = user_tweets.append(tweets)

    except:
        pass

    print(f"Downloaded {user_tweets.shape[0]} tweets from user: {user_id}")

    return user_tweets


tok = WordPunctTokenizer()

def tweet_cleaner(text):

    pat1 = r'@[A-Za-z0-9]+'
    pat2 = r'https?://[A-Za-z0-9./]+'
    combined_pat = r'|'.join((pat1, pat2))

    soup = BeautifulSoup(text, 'lxml')
    souped = soup.get_text()
    stripped = re.sub(combined_pat, '', souped)
    try:
        clean = stripped.decode("utf-8-sig").replace(u"\ufffd", "?")
    except:
        clean = stripped
    # letters_only = re.sub("[^a-zA-Z]", " ", clean)
    letters_only = re.sub(r'[\W_]+', ' ', clean)
    lower_case = letters_only  # .lower()
    # During the letters_only process two lines above, it has created unnecessay white spaces,
    # I will tokenize and join together to remove unneccessary white spaces
    words = tok.tokenize(lower_case)
    return (" ".join(words)).strip()




if __name__ == "__main__":

    USER_IDS = [
        # nonsense accounts
        16298441,  # dril
        1174980053668524033, # dril_gpt2
        531739833,  # @__MICHAELJ0RDAN 
        # spoof football
        2725825164, # deludedbrendan
        1573649600, # boringmilner
        1065236066, # usasoccerguy
        146950195, # optajoke
        288674541, # wengerknowsbest
        2742171811, # bruceatwedding
        88551365,  # TheBig_Sam
        # football pundits
        394986531,  # PhilippeAuclair
        179707847,  # Jonathan Wilson @jonawils
        92965107,  # Michael Cox @ZonalMarking
        767638855101124609,  # Rory Smith @RorySmithTimes
        37896651,  # Henry Winter @henrywinter
        108957853,  # Sid Lowe @sidlowe
        1347812356152287236,  # Iain Macintosh @iainmacintosh
        3247497561,  # @alanshearer
        44606764,  # @optajoe
        182301693,  # @samuelluckhurst
        2778225595, # fantasyscout1
        252753618,  # @luisnani
        287834630,  # @GNev2
        82916196,  # @SwissRamble
        1347812356152287236,  # @iainmacintosh
        166767883,  # @Joey7Barton
    ]
    
    print('Downloading tweets...')
    all_tweets = pd.DataFrame()
    for user_id in USER_IDS:
        tweets = download(user_id)
        all_tweets = all_tweets.append(tweets)

    print('Cleaning tweets...')
    all_tweets['text_clean'] = ''
    for index, row in all_tweets.iterrows():
        row['text_clean'] = tweet_cleaner(row['text'])

    # ignore really short tweets
    min_length_mask = (all_tweets['text_clean'].str.len() > 10)
    
    # save to csv
    all_tweets.loc[min_length_mask].to_csv(
        'tweets_clean.csv', 
        columns=['text_clean'],
        index=False,
        header=False
    )