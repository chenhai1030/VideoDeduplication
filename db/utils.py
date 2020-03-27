
from glob import glob
import numpy as np
import os
import pandas as pd
import json
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine,Table, Column, String, MetaData,Integer,Binary,Boolean,Float,ARRAY
from sqlalchemy.orm import sessionmaker

from .schema import Signature,Scenes,VideoMetadata

def create_engine_session(conn_string):
    """Creates DB engine from connection string
    
    Arguments:
        conn_string {string} -- Connection string with format postgres://postgres:[USER]:[PASSWORD]@[HOST]:[PORT]/[DBNAME]

        eg. postgres://postgres:admin@localhost:5432/test
    """

    db_engine = create_engine(conn_string)
    Session = sessionmaker(bind=db_engine)
    session = Session()

    return db_engine,session


# Initial table creation / deletion
def create_tables(engine):
    
    Signature.metadata.create_all(engine)
    Scenes.metadata.create_all(engine)
    VideoMetadata.metadata.create_all(engine)
    
def delete_tables(engine):
    Signature.metadata.drop_all(engine)
    Scenes.metadata.drop_all(engine)
    VideoMetadata.metadata.drop_all(engine)
    
# Bulk loading the original output into target tables


def load_scenes(session,scenes_df_path):
    """Loads scene information into the scenes DB table
    
    Arguments:
        session {DB Session} -- created by a previous instantiation of the db session
        scenes_df_path {string} -- Path to the scenes detection output (csv file)
    """

    df = pd.read_csv(scenes_df_path)

    session.add_all([Scenes(original_filename=x['fp'],
                            video_duration = x['video_duration'],
                            avg_duration = x['avg_duration'],
                            scene_duration = json.loads(x['scene_duration'])
                            
    ) for i,x in df.iterrows()])
    

def load_signatures(session,signatures_fp,signatures_index):
    """Load signatures into DB
    
    Arguments:
        session {DB Session} -- created by a previous instantiation
        signatures_fp {string} -- path to generated signatures
        signatures_index {string} -- path to the index of generated signatures
    """

    signatures = np.load(signatures_fp)
    filenames = np.load(signatures_index)

    print(signatures.shape)
    print(filenames.shape)
    
    session.add_all([Signature(original_filename=x[0],
                               signature=x[1]) for x in zip(list(filenames),list(signatures)) ])
    

def load_metadata(session,metadata_df_path):
    """Loads video metadata into DB (video metadata table)
    
    Arguments:
        session {DB Session} -- created by a previous instantiation
        scenes_df_path {string} -- Path to the video metadataoutput (csv file)
    """


    df  = pd.read_csv(metadata_df_path)
    
    session.add_all([VideoMetadata(
                                   original_filename=x['fn'],
                                   video_length = x['video_length'],
                                   avg_act = x['avg_act'],
                                   video_avg_std = x['video_avg_std'],
                                   video_max_dif = x['video_max_dif'],
                                   gray_avg= x['gray_avg'],
                                   gray_std = x['gray_std'],
                                   gray_max = x['gray_max'],
                                   video_dark_flag = x['video_dark_flag'],
                                   video_duration_flag = x['video_duration_flag'],
                                   flagged = x['flagged']
                                   
                                   ) for i,x in df.iterrows()])
    

# DB Queries

def get_all(session,instance):

    query = session.query(instance)
    return query.all()
