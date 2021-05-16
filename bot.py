import spacy
from spacy.language import Language
from spacy_langdetect import LanguageDetector
import boto3
import praw
import sys
import time

#language codes list
langCodes = {
    'zh' : 'Chinese',
    'en' : 'English',
    'fr' : 'French',
    'de' : 'German',
    'it' : 'Italian',
    'ja' : 'Japanese',
    'ko' : 'Korean',
    'pt' : 'Portuguese',
    'ru' : 'Russian',
    'es' : 'Spanish',
}

#spacy language detect init
def get_lang_detector(nlp, name):
    return LanguageDetector()

nlp = spacy.load("en_core_web_sm")
Language.factory("language_detector", func=get_lang_detector)
nlp.add_pipe('language_detector', last=True)

#boto3 translator init
translator=boto3.client('translate',
                        aws_access_key_id='AKIAJCCGCJMWIVKQRVTA',
                        aws_secret_access_key='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',
                        region_name="ap-south-1")

#reddit praw init
reddit=praw.Reddit("bot2")
subs=['gaming','memes','funny','dankmemes','askreddit','aww','science','worldnews','news','gifs','food','mildyinteresting']
sub='+'.join(subs)
subreddit=reddit.subreddit(sub)

#subs to not monitor
exemptSubs = []
i=0

for comment in subreddit.stream.comments():
    text=comment.body.lower()
    if len(text)<50 or str(comment.subreddit).lower in exemptSubs:
        continue
    doc = nlp(text)
    sourceLang = doc._.language['language']
    if doc._.language['score']*100<90 or sourceLang not in langCodes.keys():
        continue
    if sourceLang !='en':
        res = translator.translate_text(
            Text=text,
            SourceLanguageCode=sourceLang,
            TargetLanguageCode='en'
        )
        translated=res["TranslatedText"]
        replyMsg = f"_Translated comment from **{langCodes[sourceLang]}** to **English**_ : \n\n"
        replyMsg+=translated
        try:
            comment.reply(replyMsg)
        #rate limit handling incomplete
        except Exception as e:
            time.sleep(1000)
            # print(f"Error {type(e)} : {e}")
            # sys.exit()
        i+=1
        print(f"Comments Translated : {i}")
