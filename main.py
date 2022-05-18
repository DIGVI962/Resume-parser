from pdfminer.high_level import extract_text
import docx2txt
import spacy
from spacy.matcher import Matcher
import re
import pandas as pd
import pprint
import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('stopwords')

!python -m spacy download en_core_web_sm

nlp = spacy.load('en_core_web_sm')

matcher = Matcher(nlp.vocab)

RESERVED_WORDS = [
    'school',
    'college',
    'university',
    'academy',
    'faculty',
    'institute',
    'faculdades',
    'Schola',
    'schule',
    'lise',
    'lyceum',
    'lycee',
    'polytechnic',
    'kolej',
    'ünivers',
    'okul',
    'BE','B.E.', 'B.E', 'BS', 'B.S', 
    'ME', 'M.E', 'M.E.', 'MS', 'M.S', 
    'BTECH', 'B.TECH', 'M.TECH', 'MTECH', 
    'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII',
    'bachelors', 'masters'
]

resumedata = {}
'''
class ResumeParser():
    def __init__(self,filepath):
        self.filepath = filepath
'''

def extract_text_from_docx(docx_path):
    txt = docx2txt.process(docx_path)
    if txt:
        return txt.replace('\t', ' ')
    return None

def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

def extract_names(resume_txt):
    names = []
    nlp_text = nlp(resume_txt)
    nlp_text = [sent.text.strip() for sent in nlp_text.sents]
    resume_text = nlp(nlp_text[0])
    noun_chunks = resume_text.noun_chunks
    tokens = [token.text for token in resume_text if not token.is_stop]
    if tokens[0]==':' or tokens[0].lower()=='name':
        tokens[0]=tokens[1]
        tokens[1]=tokens[2]
    return tokens[0],tokens[1]
    


def extract_mobile_number(resume_txt):
    phone = re.findall(re.compile(r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'), resume_txt)

    if phone:
        number = ''.join(phone[0])
        if len(number) > 10:
            return '+' + number
        else:
            return number
    else:
        return None

def extract_email(resume_txt):
    email = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", resume_txt)
    if email:
        try:
            return email[0].split()[0].strip(';')
        except IndexError:
            return None

def extract_skills(resume_text):
    nlp_text = nlp(resume_text)
    noun_chunks = nlp_text.noun_chunks

    tokens = [token.text for token in nlp_text if not token.is_stop]

    data = pd.read_csv("skills.csv") 

    skills = list(data.columns.values)

    skillset = []

    for token in tokens:
        if token.lower() in skills:
            skillset.append(token)

    for token in noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)

    return [skil.capitalize() for skil in set([skil.lower() for skil in skillset])]

def extract_education(resume_txt):
    organizations = []

    for sent in nltk.sent_tokenize(resume_txt):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
            if hasattr(chunk, 'label') and chunk.label() == 'ORGANIZATION':
                organizations.append(' '.join(c[0] for c in chunk.leaves()))

    education = set()
    temp=0
    for org in organizations:
        for word in RESERVED_WORDS:
            if org.lower().find(word) >= 0:
                education.add(org)
                temp=1
    if temp==0:
        return 'Nil'
    elif temp==1:
        return education
    

def main(resume_txt):
    resumedata['First_Name'], resumedata['Last_Name'] = extract_names(resume_txt)
    resumedata['Number'] = extract_mobile_number(resume_txt)
    resumedata['Email_Id'] = extract_email(resume_txt)
    resumedata['Skills'] = extract_skills(resume_txt)
    resumedata['Education'] = extract_education(resume_txt)
    pprint.pprint(resumedata)    
    
if __name__ == '__main__':
    file_path = 'C://Users//IAmTheWizard//Downloads//archive//Resumes//Kumar Raj.docx'
    if file_path[-1]=='x':
        resume_txt = extract_text_from_docx(file_path)
    elif file_path[-1]=='f':
        resume_txt = extract_text_from_pdf(file_path)
    main(resume_txt)    
