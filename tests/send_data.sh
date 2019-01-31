#!/usr/bin/env bash

curl -X POST -d 'sessionJSON={"testId":"test","participant":{"name":["email","age","gender"],"response":["asd","30","female"]},"trials":[{"id":"lss1","type":"likert_single_stimulus","responses":[{"stimulus":"C1","stimulusRating":"not at all","time":1771},{"stimulus":"C2","stimulusRating":"not a lot","time":803},{"stimulus":"C3","stimulusRating":"not a lot","time":712}]}],"config":"configs/default.yaml"}' http://localhost:5000/service/write.php
