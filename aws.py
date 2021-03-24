import boto3

s3 = boto3.client('s3')

s3.upload_file('ski_resort_data_full.csv', 'aicore-akirby', 'ski-scraper/ski_resort_data_v0.1')

# list_buckets returns a json file so there is a bit of digging in that's needed.
#print(s3.list_buckets()["Buckets"][0]['Name'])