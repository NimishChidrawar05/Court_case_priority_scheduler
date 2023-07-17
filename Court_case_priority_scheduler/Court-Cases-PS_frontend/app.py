import re
from flask import Flask, render_template, request, redirect, url_for
from CaseinputForm import CaseInputForm
import csv , pickle
import numpy as np
import pandas as pd
from datetime import datetime
import sqlite3
import os
from werkzeug.utils import secure_filename
import subprocess

app = Flask(__name__)

app.config["SECRET_KEY"]= "yugd87ayudgduyguyguyqw"
app.config['UPLOAD_FOLDER']= "./static/case_files_to_schedule"

@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')
@app.route('/clerkLogin', methods=["GET","POST"])
def clerkLogin():
    if request.method == 'POST':
    # do stuff when the form is submitted

    # redirect to end the POST handling
    # the redirect can be to the same route or somewhere else
        return redirect(url_for('clerkPostLogin'))

    # show the form, it wasn't submitted
    return render_template('clerk-login.html')
def convert_filing_date_to_days(date_string):
    date_obj = datetime.strptime(date_string, '%Y-%m-%d')
    year, month, day = date_obj.year, date_obj.month, date_obj.day
    total_days = year * 365 + month * 30 + day
    return -total_days

def min_max_scaling(df):
    # copy the dataframe
    df_norm = df.copy()
    df_min_max = pd.read_csv("casestoSchedule.csv")

    # apply min-max scaling
    for column in df_norm.columns:
        if df_norm[column].min() < df_min_max[column].min():
            min = df_norm[column].min()
        else:
            min = df_min_max[column].min()

        df_norm[column] = (df_norm[column] - min) / (df_min_max[column].max() - min)            
    return df_norm

def remove_pet_resp_outliers(value):
    if value > 8:
        return 8
    return value

@app.route('/clerkPostLogin', methods=["GET","POST"])
def clerkPostLogin():
    form = CaseInputForm()
    def change_date_format(dt):
        return re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})', '\\3-\\2-\\1', dt)
    if form.validate_on_submit():
        caseFile = form.caseFile.data
        caseFile.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename(caseFile.filename)))
        datestr = str(form.data['filingDate'])
        dateInDays = convert_filing_date_to_days(datestr)
        petitioners = form.data['petitioners']
        petitioners = remove_pet_resp_outliers(petitioners)
        respondents = form.data['respondents']
        respondents = remove_pet_resp_outliers(respondents)
        df_old = pd.read_csv('casestoSchedule.csv')
        # takes these form values and store them in the db till 30-40 cases are reached 
        with open("casestoSchedule.csv", "a", newline="") as file:
            writer = csv.writer(file)
                # writer.writerow(header)
            list = [dateInDays, petitioners, respondents]
            writer.writerow(list)

        ################
        
        model = pickle.load((open('classificationModel.pkl','rb')))        
        df = pd.read_csv("casestoSchedule.csv")
        df= min_max_scaling(df)
        features = ['filingDate', 'petitioners', 'respondents']
        X = np.array(df[features])
        prediction = model.predict(X)
        os.remove('casestoSchedule.csv')
        df = df_old
        df=df[['filingDate','petitioners','respondents']]
        df.to_csv('casestoSchedule.csv', index= False)
        cases = []
        for i in range(1,31):
            case_dict = {
                'id': i ,
                'priorityNumber' : prediction[i+99]
            }
            cases.append(case_dict)

        # preparing statutes for each uploaded case in the csv of case-case statutes
        subprocess.run(['python', 'test.py'])

        # preparing mapped case categories for each case from their statutes
        subprocess.run(['python', 'actsBucketMapper.py', 'modelTrainOutput.csv', 'mappedBuckets.csv'])

        # using case categories to query for the best available judge 
        subprocess.run(['python', 'queryForBestAvailJudge.py', 'mappedBuckets.csv', 'JudgeBucketCount', 'judgeAssigned.csv'])

        def schedule_cases(cases):
            cases_biforcated_as_per_class = [[],[],[],[],[]]
            scheduled_cases = []
            for el in cases:
                cases_biforcated_as_per_class[int(el["priorityNumber"])-1].append(el)

            total_length = len(cases_biforcated_as_per_class[0]) + len(cases_biforcated_as_per_class[1]) + \
            len(cases_biforcated_as_per_class[2]) + len(cases_biforcated_as_per_class[3]) + len(cases_biforcated_as_per_class[4])
            while total_length != 0:
                for i in range(4, -1, -1):
                    if len(cases_biforcated_as_per_class[i]) != 0:
                        scheduled_cases.append(cases_biforcated_as_per_class[i].pop())
                total_length = len(cases_biforcated_as_per_class[0]) + len(cases_biforcated_as_per_class[1]) + \
                len(cases_biforcated_as_per_class[2]) + len(cases_biforcated_as_per_class[3]) + len(cases_biforcated_as_per_class[4])        
            return scheduled_cases
            
        def batch_cases(batch_size):
            batched_cases = []
            scheduled_cases = schedule_cases(cases)

            while len(scheduled_cases) > 0:
                batch = scheduled_cases[:batch_size]
                batch.sort(key=lambda x: x["priorityNumber"], reverse=True)
                batched_cases.append(batch)
                scheduled_cases = scheduled_cases[batch_size:]

            return batched_cases
        
        batched_cases = batch_cases(5)

        def increment_priority_of_remaining_cases(left_cases):
            if len(left_cases) == 5:
                return
            return [{**el, "priorityNumber": str(int(el["priorityNumber"]) + 1)} for el in left_cases]
        con = sqlite3.connect('cases.db')
        cursor = con.cursor()
        cursor.executescript('''
        DELETE from Cases;
        DELETE from Batch;
        INSERT INTO Cases(date, petitioners,respondents) values ("01-01-2010","1","7"),("01-01-2011","2","4"),("01-01-2012","3","3"),("01-01-2013","4","2"),("01-01-2014","5","1"),("01-01-2015","6","7"),("01-01-2016","7","6"),("01-01-2017","2","5"),("01-01-2017","3","4"),("01-01-2018","4","2"),("01-01-2019","5","1"),("01-01-2017","6","7"),("01-01-2020","7","6"),("01-01-2021","1","5"),("01-01-2022","3","4"),("01-01-2023","4","3"),("01-01-1990","5","1"),("01-01-1991","6","7"),("01-01-1992","7","6"),("01-01-2017","1","5"),("01-01-1993","2","4"),("01-01-1994","4","3"),("01-01-1995","5","2"),("01-01-1996","6","7"),("01-01-1997","7","6"),("01-01-1998","1","5"),("01-01-1999","2","4"),("01-01-2000","3","3"),("01-01-2001","4","2");
        ''')
        if request.method =='POST':
            pdf = request.form.get('caseFile')
            date = request.form.get('filingDate')
            date = change_date_format(date)
            petitioners = request.form.get('petitioners')
            respondents = request.form.get('respondents')
            with sqlite3.connect('cases.db') as con:
                cur = con.cursor()
                cur.execute('INSERT INTO cases (date,petitioners, respondents) values (?,?,?)',(date,petitioners,respondents))
                con.commit()
        for i in range (0,7):
            if len(batched_cases) > i:
                for j in range(0,6):
                    if len(batched_cases[i]) > j:
                        n= (i*5)+(j+1)
                        m = int(batched_cases[i][j]['id'])
                        p= (int(batched_cases[i][j]['priorityNumber']))
                        cur = con.cursor()
                        cur2 = con.cursor()
                        cur.execute('INSERT INTO Batch (id,caseid) values (?,?);', (n,m))
                        cur2.execute('UPDATE Cases SET priority = ? WHERE id = ?',(p,m))
                        con.commit()
        return redirect(url_for('clerkScheduleList'))

    return render_template('clerk-post-login.html', form=form)

@app.route('/clerkScheduleList', methods=["GET","POST"])
def clerkScheduleList():
    # date = request.args.get('filingDate', None)
    con = sqlite3.connect('cases.db')
    cur = con.cursor()
    cur2 = con.cursor()
    cur.execute('select * from Cases')
    cur2.execute('select * from Batch')
    row=[0]*30
    caserow=[0]*30
    for i in range(0,30):
        row[i]= cur.fetchone()
    for i in range(0,30):
        caserow[i]= cur2.fetchone()
    return render_template('clerk-schedule-list.html', row=row, caserow=caserow)
@app.route('/userLogin', methods=["GET","POST"])
def userLogin():
    if request.method == 'POST':
    # do stuff when the form is submitted

    # redirect to end the POST handling
    # the redirect can be to the same route or somewhere else
        return redirect(url_for('userPostLogin'))

    # show the form, it wasn't submitted
    return render_template('user-login.html')
@app.route('/userPostLogin', methods=["GET","POST"])
def userPostLogin():
    if request.method =='POST':
        return redirect(url_for('userPostLoginStatus'))
    return render_template('user-post-login.html')
@app.route('/userPostLoginStatus', methods=["GET","POST"])
def userPostLoginStatus():
    return render_template('user-post-login-status.html')
@app.route('/judgeLogin', methods=["GET","POST"])
def judgeLogin():
    if request.method == 'POST':
    # do stuff when the form is submitted

    # redirect to end the POST handling
    # the redirect can be to the same route or somewhere else
        return redirect(url_for('judgePostLogin'))

    # show the form, it wasn't submitted
    return render_template('judge-login.html')
@app.route('/judgePostLogin', methods=["GET","POST"])
def judgePostLogin():
    return render_template('judge-post-login.html')
app.run("localhost", "9999", debug=True)
