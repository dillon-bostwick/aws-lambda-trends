zip -r deploy.zip . -x history_viz/\*

aws lambda update-function-code --zip-file fileb://./deploy.zip --function-name scrape_serps_and_update

echo 'REDPLOY COMPLETE. TEST HERE: https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions/scrape_serps_and_update?tab=code'