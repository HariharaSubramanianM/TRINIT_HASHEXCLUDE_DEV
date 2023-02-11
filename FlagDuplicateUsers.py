import pandas as pd
import datetime
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

df = pd.read_csv('users.csv')

ip_address_list = ['ip', 'ip_address', 'ip_add', 'ip']

def identify_duplicate_user():
    columns = df.columns
    ip_address_values = []
    for cname in columns:
        if cname in ip_address_list:
            ip_address_values = df[cname]
    
    for ip_i in range(0, ip_address_values.len()):
        for ip_j in range(ip_i, ip_address_values.len()):
            if(ip_address_values[ip_i]==ip_address_values[ip_j]):
                check_subscription_join_and_end_date(ip_i, ip_j)




def create_flag(i, j):
    print("User using same mobile device")


def check_subscription_join_and_end_date(user1, user2):

    flag = False

    startDate_user1 = df.iloc[user1]['startDate']
    startDate_user2 = df.iloc[user2]['startDate']
    endDate_user1 = df.iloc[user1]['endDate']
    endDate_user2 = df.iloc[user2]['endDate']

    startDate_user1 = get_date_format(startDate_user1)
    startDate_user2 = get_date_format(startDate_user2)
    endDate_user1 = get_date_format(endDate_user1)
    endDate_user2 = get_date_format(endDate_user2)
    
    user1_data = df.iloc[user1]
    user2_data = df.iloc[user2]

    total_similarity = 0
    count = 0

    for data1, data2 in user1_data, user2_data:
        if data1!=np.nan and data2!=np.nan:
            if type(data1)==str and type(data2)==str:
                total_similarity = total_similarity+cosine_similarity_string(data1, data2)
                count = count+1
    similarity = total_similarity/count

    if(similarity>0.9):
        flag = True

    if (startDate_user1 < endDate_user2 or startDate_user2<endDate_user1) and flag!=True:
        flag = False
    else:
        flag = True

    #Send information from here
    #flag is True then the user is duplicate


def get_date_format(date):
    #from database DD-MM-YYYY
    #to datetime package YYYY-MM-DD
    date = date.split('-')
    day = int(date[0])
    month = int(date[1])
    year = int(date[2])

    date = datetime.datetime(year, month, day)
    return date


def cosine_similarity_string(text1, text2):
        vectorizer = CountVectorizer().fit_transform([text1, text2])
        similarity = np.dot(vectorizer[0], vectorizer[1].T) / (np.linalg.norm(vectorizer[0]) * np.linalg.norm(vectorizer[1]))
        return similarity


# def do_clustering(parameters):
    