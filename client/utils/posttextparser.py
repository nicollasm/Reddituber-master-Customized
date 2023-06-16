import re

from utils import settings
from utils.console import print_step, takeinput
from utils.voice import sanitize_text

# alphabets= r"([A-Za-z])"
# prefixes = r"(Mr|St|Mrs|Ms|Dr)[.]"
# suffixes = r"(Inc|Ltd|Jr|Sr|Co)"
# starters = r"(Mr|Mrs|Ms|Dr|Prof|Capt|Cpt|Lt|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
# acronyms =r"([A-Z][.][A-Z][.](?:[A-Z][.])?)"
# websites = r"[.](com|net|org|io|gov|edu|me)"
# digits = r"([0-9])"

# def replace_with_prd(main_str:str, word:str) -> str:
#     if word in main_str:
#         main_str = main_str.replace(word,word.replace(".","<prd>"))
#     return main_str

# def break_with(text:str ,keyword:str)-> list[str]:
#     """   """
#     text = text.replace(keyword,keyword+"<stop>")  
#     return text.split("<stop>")


# def posttextparser(text:str) -> list[str]:
#     text = " " + text + "  "
#     text = text.replace("\n"," ")
#     text = re.sub(prefixes,"\\1<prd>",text)
#     text = re.sub(websites,"<prd>\\1",text)
#     text = re.sub(digits + "[.]" + digits,"\\1<prd>\\2",text)

#     text = replace_with_prd(text, "..." )
#     text = replace_with_prd(text, "Ph.D" )
#     text = replace_with_prd(text, "A.I")
#     # if "..." in text: text = text.replace("...","<prd><prd><prd>")
#     # if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
#     # if "A.I" in text: text = text.replace("A.I","A<prd>I")

#     text = re.sub(r"\s" + alphabets + "[.] "," \\1<prd> ",text)
#     text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
#     text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
#     text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
#     text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
#     text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
#     text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)

#     if "”" in text: text = text.replace(".”","”.")
#     if "\"" in text: text = text.replace(".\"","\".")
#     if "!" in text: text = text.replace("!\"","\"!")
#     if "?" in text: text = text.replace("?\"","\"?")

#     text = text.replace(".",".<stop>")
#     text = text.replace("?","?<stop>")
#     # text = text.replace("!","!<stop>")
#     # text = text.replace(",", ",<stop>")
#     # text = text.replace("and","<stop>and")
#     text = text.replace("<prd>",".")
#     sentences = text.split("<stop>")
#     sentences = sentences[:-1]
#     sentences = [s.strip() for s in sentences]
#     return sentences

# working good
def posttextparser(text) -> list[str]:
    if settings.config["pereference"]["manual_text_correct"]:
        text = takeinput(text)

    import spacy
    text = re.sub("\n", " ", text)
    try:
        nlp = spacy.load('en_core_web_sm')
    except OSError:
        print_step("The spacy model can't load. You need to install it with \npython -m spacy download en_core_web_sm")
        exit()
    doc = nlp(text)
    newtext: list[str] = []
    # to check for space str
    for line in doc.sents:
        if sanitize_text(line.text):
            newtext.append(line.text)
        print(line)

    return newtext


def parseComment(text:str) -> str:



    if text.startswith(">"):
        t :list = text.split("\n")
        return "\n".join(t[1:])
    
    return "\n".join(text.split("\n")) 