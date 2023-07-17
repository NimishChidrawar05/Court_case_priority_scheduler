import os
import spacy
import array
import PyPDF2 as pdf
import unicodedata
import string

regexTestTxt = open("modelTrainOutput.csv","w")

nlp = spacy.load(r"./model-best")
# Folder path to retrieve the pdf files
dir_path = r'./static/case_files_to_schedule/'
# List to store files
currPdfFile = []

countTuples = 0

fileIndex = 0

# Iterate the directory
for path in os.listdir(dir_path):
    # Check if current path is a file
    if os.path.isfile(os.path.join(dir_path, path)):
       currPdfFile.append(path)

# print(currPdfFile)

# Absolute dir the script is in
script_dir = os.path.dirname(__file__) 

# Select a current pdf
for pdfs in currPdfFile:    

    try:
            rel_path = dir_path + pdfs
            abs_file_path = os.path.join(script_dir, rel_path)
            file = open(abs_file_path,'rb')
            try:
                pdf_reader = pdf.PdfReader(file)
            except:
                # regexTestTxt.writelines("Error," + pdfs + "\n")
                continue
            
            newTxt = ""


            # Select all text from the current pdf and save it into newTxt
            for pages in range(1, pdf_reader.getNumPages()):
                newTxt += pdf_reader.getPage(pages).extractText()
                
            newTxt = newTxt.replace("\n", " ")
            newTxt = newTxt.replace(u'\xa0', u' ')
            newTxt = newTxt.replace(u'\xad', u' ')
            newTxt = newTxt.replace('”', u' ')
            newTxt = newTxt.replace('“', u' ')
            newTxt = newTxt.replace('—', u' ')
            newTxt = newTxt.replace('…', u' ')
            newTxt = newTxt.replace('‘', u' ')
            newTxt = newTxt.replace('’', u' ')
            newTxt = newTxt.replace('–', u' ')            

            index = 0

            for ch in newTxt:
                if (ch == ' ') & (newTxt[index - 1] == ' '):
                    newTxt = newTxt[:index] + '' + newTxt[index + 1:]
                    continue
                index += 1

            sentences = newTxt.split('.')
            processedActNames = []

            for sentence in sentences:
                sentence = sentence.strip(' ')
                sentence = sentence.lstrip('-%,[]()0123456789[]()')
                sentence = sentence.translate(str.maketrans('', '', string.punctuation))
                sentence = sentence.strip(' ')

                doc = nlp(sentence)
                # # displacy.serve(doc, style="ent") # display in web browser 'localhost:5000'

                actNames = doc.ents
                


                for actName in actNames:

                    extractedActName = unicodedata.normalize("NFKD", str(actName))

                    processedActNames.append(extractedActName)

                
            print(processedActNames, "\n")
            regexTestTxt.writelines( str('#'.join(processedActNames))+','+pdfs+'\n')
            
    except Exception as e:
        # regexTestTxt.writelines("Error," + pdfs + "\n")
        print(e)
        continue

    fileIndex+=1
