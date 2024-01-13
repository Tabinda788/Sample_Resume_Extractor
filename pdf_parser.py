import os 
import PyPDF2

path = os. getcwd()
output_folder = 'Extracted-Data'

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ''
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text

for (dirpath, dirnames, filenames) in os.walk(path):
    
    if dirpath.endswith('Resumes-Dataset'):
        for file in filenames:
            # print(dirpath + '\\' + file)
            resume_text = extract_text_from_pdf(dirpath + '\\' + file)
            # print(resume_text)
            txt_filename = os.path.splitext(file)[0] + '.txt'
            txt_filepath = os.path.join(dirpath + '\\' + output_folder, txt_filename)
            with open(txt_filepath, 'w', encoding='utf-8') as txt_file:
                    txt_file.write(resume_text)

            print(f"Text extracted from '{file}' and saved to '{txt_filename}'")
            
