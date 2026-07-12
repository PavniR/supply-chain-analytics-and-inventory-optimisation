import os
import psycopg2
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

@st.cache_resource
def get_connection():

    # Local development (.env)
    if os.getenv("DB_HOST"):

        return psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )

    # Streamlit Cloud (Secrets)
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        database=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        port=st.secrets["DB_PORT"]
    )


@st.cache_data(ttl=600)
def run_query(query):

    conn = get_connection()
    return pd.read_sql(query, conn)