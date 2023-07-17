import csv
import os

with open('mappedBuckets.csv', mode='r', encoding="UTF-8") as mappedCasesCSV:

    caseCategoryData = csv.reader(mappedCasesCSV , delimiter=',')

    for category in caseCategoryData:
        # print(category[0])

        categoryNumber = 18
        
        if(category[0] == "Land Acquisition & Requisition & Rent Act & Eviction Act Matters"):
            categoryNumber = 1
        elif(category[0] == "Direct Taxes Matter & Indirect Taxes Matters"):
            categoryNumber = 2
        elif(category[0] == "Labour & Service Matters & Matters Relating To Judiciary"):
            categoryNumber = 3
        elif(category[0] == "Academic Matters & Admission/Transfer To Engineering And Medical Colleges"):
            categoryNumber = 4
        elif(category[0] == "Letter Petition & Pil Matters"):
            categoryNumber = 5
        elif(category[0] == "Election Matters"):
            categoryNumber = 6
        elif(category[0] == "Company Law, Mrtp, Trai, Sebi, Idrai & Rbi & Mercantile Laws, Commercial Transactions Including Banking & Consumer Protection"):
            categoryNumber = 7
        elif(category[0] == "Arbitration & Compensation Matters"):
            categoryNumber = 8
        elif(category[0] == "Criminal Matters & State Excise-Trading In Liquor-Privileges, Licences-distilleries Breweries"):
            categoryNumber = 9
        elif(category[0] == "Appeal Against Orders Of Statutory Bodies"):
            categoryNumber = 10
        elif(category[0] == "Contempt Of Court Matters"):
            categoryNumber = 11
        elif(category[0] == "Ordinary Civil & Family Law & Personal Law Matters"):
            categoryNumber = 12
        elif(category[0] == "Religious & Charitable Endowments"):
            categoryNumber = 13
        elif(category[0] == "Appointments Etc., Of Constitutional Functionaries & Statutory Appointments And Appointment Of Other Law Officers"):
            categoryNumber = 14
        elif(category[0] == "Simple Money & Mortgage Matters Etc"):
            categoryNumber = 15
        elif(category[0] == "Land Laws And Agricultural Tenancies"):
            categoryNumber = 16
        elif(category[0] == "MATTERS RELATING TO LEASES, GOVT. CONTRACTS & CONTRACTS BY LOCAL BODIES & RTI"):
            categoryNumber = 17
        elif(category[0] == "Miscellaneous Bucket"):
            categoryNumber = 18

        # print(categoryNumber)

        with open('JudgeBucketCount.csv', mode='r', encoding="utf-8") as judgeExpCSV:
            judgeExpData = csv.reader(judgeExpCSV , delimiter=',')
            maxExpJudge = ""
            currMaxExpValue = 0
            counterToAlterAvail = 0

            for eachJudgeExp in judgeExpData:
                if(int(eachJudgeExp[categoryNumber]) > currMaxExpValue):
                    currMaxExpValue = int(eachJudgeExp[categoryNumber])
                    maxExpJudge = eachJudgeExp[0]
                    counterToAlterAvail += 1

            # judgeExpAvailWriter = csv.writer(judgeExpCSV, delimiter=',')

            # judgeExpAvailWriter.writerow([judgeExpData[counterToAlterAvail],'Unavailable'])

        # print(maxExpJudge)
                    
        with open('judgeAssigned.csv', mode='a+', encoding="UTF-8", newline='') as judgeAssignedCSV:
            csvWriter = csv.writer(judgeAssignedCSV)
            csvWriter.writerow([category[0], maxExpJudge])

os.remove('mappedBuckets.csv')
