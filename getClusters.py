from sklearn.cluster import KMeans
from sklearn import preprocessing
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
import sqlite3
import pandas as pd

def produce_cluster(parameters):
    #Load the dataset as DataFrame
    #Parameters - list of the column labels
    # connect to the SQLite database
    conn = sqlite3.connect("path/to/your/database.db")

    # create a cursor object to execute SQL commands
    cursor = conn.cursor()

    # execute a SQL query to retrieve the data you want
    cursor.execute("SELECT * FROM user_data")

    # retrieve the results of the query into a pandas dataframe
    df = pd.DataFrame(cursor.fetchall())

    # specify the column names for the dataframe
    df.columns = [col[0] for col in cursor.description]

    # close the cursor and connection objects
    cursor.close()
    conn.close()

    df = df[parameters]
    
    int_cols = [col for col in df.columns if df[col].dtype == 'int64']
    float_cols = [col for col in df.columns if df[col].dtype == 'float64']
    str_cols = [col for col in df.columns if df[col].dtype == 'object']

    # apply MinMaxScaler to int and float columns
    scaler = MinMaxScaler()
    if(int_cols.len>0):
        df[int_cols] = scaler.fit_transform(df[int_cols].values)
    if(float_cols.len>0):
        df[float_cols] = scaler.fit_transform(df[float_cols].values)

    # apply LabelEncoder to string columns
    encoder = LabelEncoder()
    if(str_cols.len>0):
        df[str_cols] = df[str_cols].apply(lambda col: encoder.fit_transform(col))
    
    kmeans = KMeans(n_clusters = 2, random_state = 0).fit(df)
    print(kmeans.labels_)