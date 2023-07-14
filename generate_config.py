import json
from report import CONFIG_FILE_NAME

config_dict = {
    "report_language": "English",
    "country": "Poland",
    "continent": "Europe",
    "start_hour": "8:00",
    "end_hour": "17:00",
    "work_days" : [1,2,3,4,5],    
    "holiday":"Holiday",
    "vacation":"Vacation"
}

json_data = json.dumps(config_dict)

# Save JSON data to a file
with open(CONFIG_FILE_NAME, "w", encoding="utf-8") as file:
    file.write(json_data)
