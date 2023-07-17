# Note do not run this script on more than 4000 rows for safety as on 5000 rows,
# it is inducing an error due to python internal operation handling issues.

import csv
import numpy as np
import os

# Global buckets array for holding counts of non tie-ing cases in terms of frequency of acts of respective buckets.
# Arr size is 18 (17 buckets and one err bucket). Error means when there is no match for an case wrt global buckets array.
bucketsGlobal = [0]*18

bucketNamesArray = ['Land Acquisition & Requisition & Rent Act & Eviction Act Matters', 'Direct Taxes Matter & Indirect Taxes Matters', 'Labour & Service Matters & Matters Relating To Judiciary', 'Academic Matters & Admission/Transfer To Engineering And Medical Colleges', 'Letter Petition & Pil Matters', 'Election Matters', 'Company Law, Mrtp, Trai, Sebi, Idrai & Rbi & Mercantile Laws, Commercial Transactions Including Banking & Consumer Protection', 'Arbitration & Compensation Matters', 'Criminal Matters & State Excise-Trading In Liquor-Privileges, Licences-distilleries Breweries', 'Appeal Against Orders Of Statutory Bodies', 
'Contempt Of Court Matters', 'Ordinary Civil & Family Law & Personal Law Matters', ' Religious & Charitable Endowments', 'Appointments Etc., Of Constitutional Functionaries & Statutory Appointments And Appointment Of Other Law Officers', 'Simple Money & Mortgage Matters Etc', 'Land Laws And Agricultural Tenancies', 'MATTERS RELATING TO LEASES, GOVT. CONTRACTS & CONTRACTS BY LOCAL BODIES & RTI', 'Miscellaneous Bucket']

# File to read acts from and write correspondind buckets into in new column
filename = './modelTrainOutput.csv'

bucketfilename = './buckets.csv'

class actClass:
            def __init__(self, actName, actCountInCurrCase):
                self.actName = actName
                self.actCountInCurrCase = actCountInCurrCase

# Opening the CSV file
with open(filename , mode ='r', encoding= 'UTF-8') as file:

    # Reading the CSV files
    csvFile = csv.reader(file,delimiter=',')

    # Accessing the contents of the acts CSV file
    for lines in csvFile:
        # print(lines[0])

        if not lines[0]:

            with open('./mappedBuckets.csv', mode = 'a+', encoding= 'UTF-8', newline='') as writeFile:

                # Creating a csv writer object 
                csvWriter = csv.writer(writeFile)

                
                csvWriter.writerow(["null"])

            continue

        nonIterableActs = []

        actsObjsListForBucketSearch = [] 
        bucketsLocal = [0]*18

        currCaseActs = lines[0].split('#')

        for act in currCaseActs:
            # print(act)

            if(act not in nonIterableActs):
                currAct = act
                currActCount = 0
                
                for Act in currCaseActs:
                    if(Act == currAct):
                        currActCount +=1
                
                actsObjsListForBucketSearch.append(actClass(currAct, currActCount))
                nonIterableActs.append(currAct)

        # print(actsObjsListForBucketSearch)

        for obj in actsObjsListForBucketSearch:
            # print(obj.actName, obj.actCountInCurrCase)
            # print(obj)
            # print("------------------------------------------------------")

            # if(obj.actCountInCurrCase == 10 ):
            #     print("-------------------------")

            with open(bucketfilename, mode = 'r', encoding = 'UTF-8') as bucketFile:
                bucketsCSV = csv.reader(bucketFile , delimiter=',')

                # Accessing the contents of the buckets CSV file
                for lines in bucketsCSV:
                    # print(lines)
                    itemCount = 0
                    for currBucketRowAct in lines:
                        # print(currBucketRowAct)
                        # if(obj.actCountInCurrCase == 10 ):
                        #     print(obj.actName)
                        if(obj.actName == currBucketRowAct):
                            bucketsLocal[itemCount] += obj.actCountInCurrCase
                            # print(obj.actName, currBucketRowAct)
                            # itemCount += 1
                            # print("------------>>", bucketsLocal[itemCount])
                        else:
                            itemCount += 1

                        # print(itemCount)
                        # Error bucket handling
                        # The 2178 fig. is total elements searched in bucket csv ie. 121*18 (need not be hardcoded as here)
                        # if(itemCount==2178 and obj.actName != currBucketRowAct):
                        #     bucketsLocal[17] += obj.actCountInCurrCase

            bucketFile.close()

        print(bucketsLocal)
        # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        nparr = np.array(bucketsLocal)
        isAllZero = np.all((nparr == 0))

        # print(isAllZero)

        if(isAllZero):
            with open('./mappedBuckets.csv', mode = 'a+', encoding= 'UTF-8', newline='') as writeFile:

                # Creating a csv writer object 
                csvWriter = csv.writer(writeFile)

                # written tied for testing
                csvWriter.writerow(["not found"])
                continue

        maxBucketCountIndex = 0
        matchFoundFlag = 0

        # Find max count holding bucket index
        for currBucketCountIndex in range(0, 18):
            if( bucketsLocal[currBucketCountIndex] >= bucketsLocal[maxBucketCountIndex] ):
                maxBucketCountIndex = currBucketCountIndex
                matchFoundFlag = 1

        bucketCountMatchFlag = 0

        # Compare all local buckets to find a tie in Count in any of the buckets with max bucket count found above (here error bucket will not be included)
        for currArrVar in range(0, 18):
            if( bucketsLocal[currArrVar] == bucketsLocal[maxBucketCountIndex] and maxBucketCountIndex != currArrVar ):
                bucketCountMatchFlag=1

               
        # print(maxBucketCountIndex)
        # print(bucketCountMatchFlag)
        # print(matchFoundFlag)

        if(bucketCountMatchFlag == 0 and matchFoundFlag == 1):
            # Max count bucket will be incremented in the global buckets
            bucketsGlobal[maxBucketCountIndex] += 1
            
            bucketToWrite = bucketNamesArray[maxBucketCountIndex]

            # print(bucketToWrite)

            with open('./mappedBuckets.csv', mode = 'a+', encoding= 'UTF-8', newline='') as writeFile:

                # Creating a csv writer object 
                csvWriter = csv.writer(writeFile)

                
                csvWriter.writerow([bucketToWrite])

            #         # Writing the fields 
            #         csvWriter.writerow()

            # print(bucketToWrite)

        else:
            with open('./mappedBuckets.csv', mode = 'a+', encoding= 'UTF-8', newline='') as writeFile:

                # Creating a csv writer object 
                csvWriter = csv.writer(writeFile)

                # written tied for testing
                csvWriter.writerow(["tied"]) 
            
# print(bucketsGlobal)

os.remove('modelTrainOutput.csv')