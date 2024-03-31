# Librerias
# ==============================================================================
import json
import boto3
import openpyxl
import pandas as pd
import pyarrow as pa
import pyarrow.parquet
from io import BytesIO
from datetime import datetime, timezone
import io
import sys
import os 

# Variables globales
# ==============================================================================
s3_client = boto3.client('s3')
fecha_actual = datetime.now()

# Funciones
# ==============================================================================
  
def read_s3(file_key):
    # Create an S3 client
    s3 = boto3.client('s3')
    # Get the object from S3
    response = s3.get_object(Bucket=source_bucket, Key=file_key)
    # Read the content of the object
    content = response['Body'].read()
    # Return BytesIO object containing the content
    return BytesIO(content)

def write_parquet_to_s3(df, destination_key):
    table = pa.Table.from_pandas(df)
    parquet_buffer = BytesIO()
    pa.parquet.write_table(table, parquet_buffer)
    s3 = boto3.client('s3')
    s3.put_object(Body=parquet_buffer.getvalue(), Bucket=destination_bucket, Key=destination_key)

# Rutas, listas y demás cosas necesarias
# ==============================================================================

# Ruta del Archivo
file = r"users/user1/pruebaappweb_st.csv"
source_bucket = 'sensorsdatav1'
destination_bucket = 'sensorsdatav1'

def lambda_handler(event, context):
    
    # Read the CSV data from S3
    csv_data = read_s3(file)
    
    # Create a Pandas DataFrame from the CSV data
    df = pd.read_csv(csv_data)
    
    # Print the DataFrame
    print(df)
    print(df.dtypes)
    # Get the current date and time
    current_datetime = datetime.now()
    
    # Format the date and time string to include in the file name
    date_string = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    
    # Specify the destination key for the Parquet file in the destination S3 bucket
    destination_key = f'st1_raw/users/user1/user1_{date_string}.parquet'
    # Write the DataFrame to a Parquet file and upload it to S3
    write_parquet_to_s3(df, destination_key)
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }