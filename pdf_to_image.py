import fitz  # PyMuPDF
from PIL import Image
from datetime import datetime
from dateutil import parser
# import pytesseract
# import cv2
import re
import os
import spacy
import nltk
import csv
from csv import writer
from nltk.corpus import stopwords
from country_named_entity_recognition import find_countries
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
# Initialize stemming, lemmatization, and stopwords
ps = PorterStemmer()
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

path = os. getcwd()
image_output_folder = 'Extracted-Images'
states_path = os. getcwd() + '\\states.txt' 


# nlp = spacy.load("en_core_web_sm")
nlp = spacy.load('en_core_web_lg')

keywords = ["TECHNICAL EXPERIENCE", "WORK EXPERIENCE", "WORK"]
characters_to_remove = r"./?@#%^*()_-+=!|\\,.\~`:"

headerList = ['resume_name','locations','grades','present_dates','months_in_the_company','university_names','skills_and_experience']

with open("Output.csv", 'w') as file:
    dw = csv.DictWriter(file, delimiter=',',
                        fieldnames=headerList)
    dw.writeheader()


def write_to_csv(data):
    with open(data, 'a') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(row)
    return data
                
def extract_universities(text):
    # Process the text with spaCy
    doc = nlp(text)

    # Extract entities labeled as "ORG" using spaCy's named entities
    universities = [ent.text for ent in doc.ents if ent.label_ == "ORG"]

    return universities

def extract_degree(text_list):
    degree_pattern = re.compile(r'Bachelor.*?|Master.*?|B.Tech*?|M.Tech*?|Ph\.?D.*?', re.IGNORECASE)

    for text in text_list:
        match = degree_pattern.search(text)
        if match:
            return match.group().strip()

    return None

def extract_dates(text):
    try:
        date_pattern = re.compile(r'Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec ?\d{4} ?- ?Present', re.IGNORECASE)
        matches = date_pattern.findall(text)
        result = [elem for elem in matches if re.search(r'(?i)present', elem)][0]
    except:
        date_pattern=re.compile(r'\d{4}-Present', re.IGNORECASE)
        result = date_pattern.findall(text)[0]        
    return result

def remove_characters(text):
    return re.sub(f"[{re.escape(characters_to_remove)}]", "", text)

def calculate_months(date_str):
    present_date = datetime.now()
    if 'Present' in date_str:
        start_date = parser.parse(date_str.split('-')[0])
        years_difference = (present_date.year - start_date.year) * 12 
        return years_difference
    else:
        return None

def convert_pdf_to_images(pdf_path, image_folder,img):
    pdf_document = fitz.open(pdf_path)
    num_pages = pdf_document.page_count

    for page_num in range(num_pages):
        page = pdf_document.load_page(page_num)
        image = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))  # Adjust the scaling as needed
        image.save(f"{image_folder}/page_{img}.png")

        pdf_document.close()

for (dirpath, dirnames, filenames) in os.walk(path):
    if dirpath.endswith('Resumes-Dataset'):
        for file in filenames:
            img_name = str(file.split(".")[0])
            p_path = path + '\\Resumes-Dataset\\' + file
            i_folder = path+'\\Resumes-Dataset\\'+image_output_folder
            # convert_pdf_to_images(p_path,i_folder,img_name)
    '''After converting pdf to image this image data will 
                        be given to ocr for text axtraction on colab'''
    
    if dirpath.endswith('Generated_OCR_Text'):
        for file in filenames:
            file_name = file
            row = []
            with open(dirpath+ '\\' +file, 'r') as file:
                file_content = file.read()
                # print("File content                :\n", file_content)
                doc = nlp(file_content)
                locations = [ent.text for ent in doc.ents if ent.label_ == "GPE" or ent.label_ == "LOC"]
                with open(states_path, 'r') as file:
                    words_in_file = file.read().split()
                present_words = [word for word in locations if word in words_in_file]
                all_locations = ",".join(present_words)
                grade_regex = r'(?:\d{1,2}\.\d{1,2})'
                grades = re.findall(grade_regex, file_content)[0]
                present_dates = extract_dates(file_content) 
                extracted_universities = extract_universities(file_content)
                education_keywords = ['university', 'college']
                university_names =  [word for word in extracted_universities if any(keyword in word.lower() for keyword in education_keywords)][0]
                pattern = re.compile(r'\b(?:' + '|'.join(map(re.escape, keywords)) + r')\b', re.IGNORECASE)
                sections = re.split(pattern, file_content)
                extracted_text = {keyword.strip(): section.strip() for keyword, section in zip(keywords, sections[1:])}
                for keyword, text in extracted_text.items():
                    # Tokenize the text
                    text = remove_characters(text)
                    text = re.sub(r'\d+', '', text)
                    words = word_tokenize(text)
                    # Remove stopwords, apply stemming, and lemmatization
                    cleaned_words = [lemmatizer.lemmatize(ps.stem(word)) for word in words if word.lower() not in stop_words]
                    skills_and_experience = ",".join(cleaned_words)
                months_in_the_company = calculate_months(present_dates)
                print(months_in_the_company)
                row.extend([file_name,all_locations,grades,present_dates,months_in_the_company,university_names,skills_and_experience])
                write_to_csv("Output.csv")
            





