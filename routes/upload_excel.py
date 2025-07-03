import io
from fastapi import  File, APIRouter, UploadFile
import pandas as pd
from fastapi.responses import JSONResponse
import requests
import dotenv
import os
from utils.access_token import get_access_token
from fastapi.responses import  FileResponse
dotenv.load_dotenv()
router = APIRouter()


@router.post('/upload-excel')
async def upload_excel(file: UploadFile = File(...)):
    if file.filename.endswith('.xlsx'):
        try:
           contents = await file.read()
           excel_data = io.BytesIO(contents)
           df = pd.read_excel(excel_data)
           data = df.to_dict(orient='records')
           # check if the headers are correct
           required_headers = {'ticket_id','case_status','comments'}
           headers = data[0].keys()
           excel_headers = set(headers)
           if required_headers != excel_headers:
               return JSONResponse(content={"message":"Excel headers mismatch found"},status_code=200)
           else:
               session = requests.Session()
               access_token = get_access_token()
               tickets_updated_list = []
               if access_token is None:
                   return JSONResponse(content={"Internal server error"},status_code=500)
               for ticket in data:
                   record_id = '' #initially record_id is empty
                   ticket_update_dict = dict()  # holds the fields which needs to be updated after validation
                   comment_dict = dict()  # holds the fields which needed to be updated via
                   for keys,value in ticket.items():

                       if keys == 'ticket_id' and value != '': #if ticket_id is not empty
                         #find the ticket record and obtain the record_id
                         print(value)
                         header = {
                             "Authorization": f"Zoho-oauthtoken {access_token}",
                             "orgId": os.getenv("ORG_ID")
                         }
                         response = session.get(f"https://desk.zoho.com/api/v1/tickets/search?limit=1&ticketNumber={value}",headers=header)

                         if response.status_code != 200:
                            print("continue unable to find record_id of that particular ticket")
                            break
                         data = response.json()
                         record_id = (data.get('data')[0]).get('id')
                       if keys == 'case_status' and value != '':
                               ticket_update_dict.update({'cf' : {"cf_case_status" :value}})
                       if keys=='comments' and value != '':
                               comment_dict.update({
                              "content": value,
                              "commenterId": "666329000003193001",
                               "isPublic": True })
                   print(ticket_update_dict)
                   print(comment_dict)
                   #update the tickets with the excel data
                   if ticket_update_dict.__len__() !=0 and record_id != '':
                       headers = {
                           "Authorization": f"Zoho-oauthtoken {access_token}",
                           "orgId": os.getenv("ORG_ID")
                       }
                       response = session.put(f"https://desk.zoho.com/api/v1/tickets/{record_id}",headers=headers,json=ticket_update_dict)
                       print(response.text)
                       if response.status_code == 200:
                           tickets_updated_list.append(ticket.get('ticket_id'))

                   if comment_dict.__len__() !=0 and record_id != '':
                       headers = {
                           "Authorization": f"Zoho-oauthtoken {access_token}",
                           "orgId": os.getenv("ORG_ID")
                       }
                       response = session.post(f"https://desk.zoho.com/api/v1/tickets/{record_id}/comments",headers=headers,json=comment_dict)
                       print(response.text)
                       if response.status_code == 200 and ticket.get('ticket_id') not in tickets_updated_list:
                           tickets_updated_list.append(ticket.get('ticket_id'))
               return JSONResponse(content={"message":f"Total {len(tickets_updated_list)} is updated Id's ->{tickets_updated_list}"},status_code=200)
        except Exception as e:
            print(e)
            return JSONResponse(content="Internal server error",status_code=500)
    else:
        return{"message":"unsupported file type"}

@router.get('/get-sample-file')
def get_sample_file():
    return FileResponse(
        path="ticket_sample.xlsx",
        filename="sample_file.xlsx",  # optional, browser will download with this name
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.get('/health-check')
def hello():
    return JSONResponse(content="Server is up and running",status_code=200)




