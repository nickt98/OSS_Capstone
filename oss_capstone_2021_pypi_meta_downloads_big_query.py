#import libraries
import os
import pandas as pd
import json
from google.cloud import bigquery
from google.oauth2 import service_account


key_path = 'msdscapstone-db80de77b383.json'

credentials = service_account.Credentials.from_service_account_file(
    key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

client = bigquery.Client(credentials=credentials, project=credentials.project_id,)

#this query gets all rows in metatable and splits dependency array into seperate columns and left joins back with the table to explode as rows. 
# thsi is supposed to join those with no dependencies as well
meta_all =  """
    SELECT p.name, p.version, p.author, p.author_email, p.license, p.home_page, dependency
    FROM `the-psf.pypi.distribution_metadata` as p
    LEFT JOIN UNNEST(p.requires_dist) as dependency
    WHERE version NOT LIKE '%%dev%%' 
    """
query_job = client.query(meta_all)  # Make an API request.
results = query_job.result()  # Waits for job to complete.

meta_all_df = results.to_dataframe()

meta_all_df.to_csv('/project/class/sds_sdad/oss_capstone2021-2022/pypi_meta_all_no_dev.csv')


#This query gives number of rows in the distribution meta data table which have licenses and have the home_page in github with dependencies exploded
meta_github = """
    SELECT p.name, p.version, p.author, p.author_email, p.license, p.home_page, dependency
    --, ARRAY_TO_STRING(p.requires_dist,',') as dependency
    FROM `the-psf.pypi.distribution_metadata` as p
    LEFT JOIN UNNEST(p.requires_dist) as dependency
    WHERE (lower(license) <> 'none' or lower(license) <> 'no license' or license is NOT NULL) and
    version NOT LIKE '%%dev%%' and home_page LIKE '%%github%%' 
    -- LIMIT 10
"""
query_job = client.query(meta_github)  # Make an API request.
results = query_job.result()  # Waits for job to complete.

dataframe_meta_with_license_dependecies = results.to_dataframe()

dataframe_meta_with_license_dependecies.to_csv('/project/class/sds_sdad/oss_capstone2021-2022/pypi_meta_licence_github_no_dev.csv')


#thsi query get downloads data from pypi big query downloads table for 01012020 t0 12-31-2020
query_downloads = """
    SELECT  country_code, file.project as name, file.version as version, Count(file.project) as num_downloads --, DATE(timestamp) as timestamp
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE
    DATE(timestamp)
    BETWEEN DATE_TRUNC(DATE_SUB(DATE('2020-12-31'), INTERVAL 365 DAY), DAY)
    AND DATE('2020-12-31') --CURRENT_DATE()
    GROUP BY country_code, file.project, file.version --,timestamp
    ORDER BY Count(file.project) 
    -- LIMIT 5 --use for checking sample data before running whole query
"""
query_job_dl = client.query(query_downloads)  # Make an API request.
results_downloads = query_job_dl.result()  # Waits for job to complete.

dataframe_downloads = results_downloads.to_dataframe()

dataframe_downloads.to_csv('/project/class/sds_sdad/oss_capstone2021-2022/pypi_downloads_365DAY_01012020.csv')