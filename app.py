from flask import Flask, request, render_template,jsonify,json
import sqlite3
import asyncio
import pandas as pd
from sklearn.cluster import KMeans
from sklearn import preprocessing
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import matplotlib
from io import BytesIO
import urllib
import os
import datetime
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

app = Flask(__name__, static_folder='static')

def create_connection():
    conn = sqlite3.connect("user_data.db")
    return conn

def create_table(conn):
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS user_data (id INTEGER PRIMARY KEY)")
    conn.commit()

def add_column(conn, column_name):
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE user_data ADD COLUMN '{}' TEXT".format(column_name))
    except:
        pass
    conn.commit()

def store_data_in_database(data):
    conn = create_connection()
    create_table(conn)
    key = data["key"]
    column_name = data["column_name"]
    column_value = data["value"]
    add_column(conn, column_name)   
    c = conn.cursor()
    try:
        c.execute(f"INSERT INTO user_data ( id, {column_name} ) VALUES ('{key}','{column_value}')" )
    except:            
        c.execute(f"UPDATE user_data set {column_name} = '{column_value}' where id = '{key}'")
    conn.commit()
    conn.close()


def get_column_values():
    conn = create_connection()
    create_table(conn)
    c = conn.cursor()
    data = c.execute('''SELECT * FROM user_data''')
    cols = [column[0] for column in data.description]
    print(cols)
    conn.commit()
    conn.close()
    return cols


def produce_cluster(parameters):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_data")
    df = pd.DataFrame(cursor.fetchall())
    df.columns = [col[0] for col in cursor.description]
    cursor.close()
    conn.close()

    if len(parameters)==1 and parameters[0]!='id':
        parameters.append('id')
    
    
    int_cols = [col for col in df.columns if df[col].dtype == 'int64']
    float_cols = [col for col in df.columns if df[col].dtype == 'float64']
    str_cols = [col for col in df.columns if df[col].dtype == 'object']

    # apply MinMaxScaler to int and float columns
    scaler = MinMaxScaler()
    if(len(int_cols)>0):
        df[int_cols] = scaler.fit_transform(df[int_cols].values)
    if(len(float_cols)>0):
        df[float_cols] = scaler.fit_transform(df[float_cols].values)
    # apply LabelEncoder to string columns
    encoder = LabelEncoder()
    if(len(str_cols)>0):
        df[str_cols] = df[str_cols].apply(lambda col: encoder.fit_transform(col))
    
    kmeans = KMeans(n_clusters = 4, random_state = 0)
    labels = kmeans.fit_predict(df)
    df = df[parameters]
    fig = plt.figure()
    plt.xlabel(parameters[0])
    plt.ylabel(parameters[1])
    plt.scatter( df.iloc[:, 0], df.iloc[:, 1], c=labels, cmap='viridis') 
    plot_file = os.path.join(app.static_folder, "plot.png")
    plt.savefig(plot_file)
    canvas = matplotlib.backends.backend_agg.FigureCanvasAgg(fig)
    image = BytesIO()
    canvas.print_png(image)
    image.seek(0)
    return urllib.parse.quote(image.getvalue())


def identify_duplicate_user():
    ip_address_list = ['ip', 'ip_address', 'ip_add', 'ip']
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_data")
    df = pd.DataFrame(cursor.fetchall())
    cursor.close()
    conn.close()
    common_list=[]

    columns = df.columns
    ip_address_values = []
    
    print(columns)

    for cname in columns:
        if cname in ip_address_list:
            ip_address_values = df[4].tolist()
    ip_address_values = df[4].tolist()
      

    for ip_i in range(0, len(ip_address_values)):
        for ip_j in range(ip_i, len(ip_address_values)):            
            if(ip_address_values[ip_i]==ip_address_values[ip_j]):
                print(ip_i,' ',ip_j)
                common_list.append([ip_i,ip_j])
                if check_subscription_join_and_end_date(ip_i, ip_j)==True:                    
                    common_list.append([ip_i,ip_j])
                
                       
    return common_list


def check_subscription_join_and_end_date(user1, user2):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_data")
    df = pd.DataFrame(cursor.fetchall())
    cursor.close()
    conn.close()
    flag = False
    
    startDate_user1 = df.iloc[user1][5]
    startDate_user2 = df.iloc[user2][5]
    endDate_user1 = df.iloc[user1][6]
    endDate_user2 = df.iloc[user2][6]
    
    if startDate_user1==None or startDate_user2 == None or endDate_user1==None or endDate_user2==None:
        flag=False

    startDate_user1 = get_date_format(startDate_user1)
    startDate_user2 = get_date_format(startDate_user2)
    endDate_user1 = get_date_format(endDate_user1)
    endDate_user2 = get_date_format(endDate_user2)

    
    
    # user1_data = df.iloc[user1]
    # user2_data = df.iloc[user2]

   

    # total_similarity = 0
    # count = 0

    # for data1, data2 in user1_data, user2_data:
    #     if data1!=np.nan and data2!=np.nan:
    #         if type(data1)==str and type(data2)==str:
    #             total_similarity = total_similarity+cosine_similarity_string(data1, data2)
    #             count = count+1
    # similarity = total_similarity/count

    # if(similarity>0.9):
    #     flag = True

    if (startDate_user1 < endDate_user2 or startDate_user2<endDate_user1) and flag!=True:
        flag = False
    elif (startDate_user2 < endDate_user1 or startDate_user1<endDate_user2) and flag!=True:
        flag=False
    else:
        flag = True
    return flag
        
def get_date_format(date):  
    if date ==None:
        date='01-01-2000'  
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

    

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":                       
        data = request.form        
        store_data_in_database(data)                
    return render_template("index.html")

from flask import Flask, request



@app.route("/graphs", methods=["GET", "POST"])
def graphs():    
    cols = get_column_values()
    ip_copy = identify_duplicate_user()    
    print(ip_copy)
    final_ip = []
    for item in ip_copy:
        if item[0]!=item[1]:
            final_ip.append(item)
    
    print('Final',final_ip)
    
    img_data = []

    if request.method == "POST":
        selected_features = request.form.get("selected_features")
        selected_features = json.loads(selected_features)
        print(selected_features)
        img_data = produce_cluster(selected_features)        

    return render_template("graphs.html",cols = cols,plot_data=img_data,ip_data = final_ip)


if __name__ == "__main__":
    app.run()
