# import libraries
import sys
import pandas as pd
import numpy as np
import sqlite3
import sqlalchemy
from sqlalchemy import create_engine


def load_data(messages_filepath, categories_filepath):
    """
    Function to load and merge 2 datasets from the filepaths

    Parameters:
    messages_filepath: messages csv file path
    categories_filepath: categories csv file path
    
    Returns:
    df: dataframe containing datasets from messages_filepath and categories_filepath merged
    """
     # load datasets
    messages = pd.read_csv(messages_filepath)
    categories = pd.read_csv(categories_filepath)
    # merge datasets on common id of both datasets and assign it to df variable
    df = messages.merge(categories, how ="outer", on ="id")
    return df

def clean_data(df):
    """
    Function to clean dataframe
    
    Parameters-
    df: dataframe

    Returns-
    Cleansed dataframe df
    """
    # create a dataframe of the 36 individual category columns
    categories = df["categories"].str.split(";",expand=True)

    # select the first row of the categories dataframe
    row = categories.head(1)

    # use the row to extract a list of new column names for categories.
    # apply a lambda function that takes everything 
    # up to the second to last character of each string with slicing
    category_colnames = row.applymap(lambda x: x[0:-2]).iloc[0]

    # rename the columns of 'categories'
    categories.columns = category_colnames

    # iterate through the category columns in df to keep only the
    # last character of each string 
    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].str.get(-1)
        # convert column from string to numeric
        categories[column] = categories[column].astype("int")

    # since the related column also has 2s replace them with 1s
    categories["related"] = categories["related"].replace(to_replace=2, value=1)

    # drop the original categories column from `df`
    df=df.drop(columns="categories",axis="columns")

    # concatenate the original dataframe with the new `categories` dataframe
    frames = [df,categories]
    df= pd.concat(frames,axis="columns")

    # drop duplicates   
    df=df.drop_duplicates()

    return df

def save_data(df, database_filepath):
    """
    Store the dataframe df in a sql lite database.
    Index_Label is not used for column name in the table

    Paramaters:
    df: dataframe
    database_filepath: filepath of the database
    """  
    engine = create_engine(f'sqlite:///{database_filepath}')
    df.to_sql('disaster_messages', engine, index=False, if_exists='replace')  

def main():
    """
    Loads the data , cleans it and saves the cleansed data to the SQL Lite database
    """
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()
