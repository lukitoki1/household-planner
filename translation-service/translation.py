import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="gtranslate-key.json"

def get_translation(lang: str, text: str):
    import six
    from google.cloud import translate_v2 as translate
    translate_client = translate.Client()
    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=lang)

    print(u"Text: {}".format(result["input"]))
    print(u"Translation: {}".format(result["translatedText"]))
    print(u"Detected source language: {}".format(result["detectedSourceLanguage"]))
    dict={}
    dict['lang']=lang
    dict['text']=result['translatedText']
    return dict


