import io
from fastapi import  File, APIRouter, UploadFile,Form
import pandas as pd
from fastapi.responses import JSONResponse
import requests
import dotenv
import os
from utils.date_validator import india_to_utc,get_date
from utils.comments import comments_name_tage

from requests import Request

from utils.access_token import get_access_token
from fastapi.responses import  FileResponse
dotenv.load_dotenv()
router = APIRouter()


@router.post('/upload-excel')
async def upload_excel(file: UploadFile = File(...),username: str = Form(...)):
    if file.filename.endswith('.xlsx'):
           user_id_dict = {"Sutapa Roy":"666329000003193001","Subhasini T S":"666329000000724001","Namrata Srivastava":"666329000003200001"}
           user = user_id_dict.get(username)
           contents = await file.read()
           excel_data = io.BytesIO(contents)
           df = pd.read_excel(excel_data,dtype={'due_date': str,'lender_login_date':str,"loan_start_date":str}).fillna('')
           data = df.to_dict(orient='records')
           print("This is the data->", data)
           if len(data) == 0:
               return JSONResponse(status_code=404, content={"message": "No Ticket found To Update please provide some ticket"})
           # check if the headers are correct
           required_headers = {'ticket_id','lender','due_date','case_status','stage','lender_login_date','type_of_case_login','lender_rejection_reason','lender_rejection_explanation','customer_rejection_reason','customer_rejection_explanation',
           'ticket_login','type_of_loan','approved_amount','sanction_amount','roi','pf_percentage','pf_amount','loan_start_date','comments','owner','department'}
           headers = data[0].keys()
           print(headers)

           excel_headers = set(headers)
           missing = required_headers - headers
           extra = headers - required_headers

           if missing or extra:
               detail = {}
               if missing:
                   detail['missing_headers'] = list(missing)
               if extra:
                   detail['unexpected_headers'] = list(extra)

               return JSONResponse(
                   content={
                       "message": "Excel headers mismatch found",
                       "details": detail
                   },
                   status_code=200
               )

           #     return JSONResponse(content={"message":"No ticket found for update provide some ticket"},status_code=200)
           else:
               access_token = get_access_token()
               common_headers = {
                   "Authorization": f"Zoho-oauthtoken {access_token}",
                   "orgId": os.getenv("ORG_ID")
               }

               session = requests.Session()
               session.headers.update(common_headers)  # Set headers once for session

               # Field mapping dictionary to avoid repetitive if-else
               field_mapping = {
                   'lender': 'cf_lender',
                   'case_status': 'cf_case_status',
                   'due_date': 'dueDate',
                   'stage': 'cf_stage',
                   'lender_login_date': 'cf_lender_login_date',#date
                   'type_of_case_login': 'cf_type_of_case_login',
                   'lender_rejection_reason': 'cf_lender_rejection_reason',
                   'lender_rejection_explanation': 'cf_lender_rejection_explanation',
                   'customer_rejection_reason': 'cf_customer_rejection_reason',
                   'customer_rejection_explanation': 'cf_customer_rejection_explanation',
                   'ticket_login':'cf_picklist_1_1',
                   'type_of_loan':'cf_type_of_loan',
                   'approved_amount':'cf_approved_amount',#money
                   'sanction_amount':'cf_sanction_amount',#money
                   'roi':'cf_roi',#percentage type
                   'pf_percentage':'cf_pf_percentage',
                   'pf_amount':'cf_processing_fee',
                   'loan_start_date':'cf_loan_start_date',#date
                   'owner': 'assigneeId',
                   'department': 'departmentId'
               }
               #holds all the owner id's to update ticket owner
               owner_id_dict = {
                   'Amare  Gowda':'666329000003245383',
                   'Ayush Dingane':'666329000003245307',
                   'Digamber Pandey':'666329000003244001',
                   'Gattu Pallavi':'666329000003245421',
                   'Honnappa Dinni':'666329000003245345',
                   'Namrata Srivastava':'666329000003200001',
                   'Sandip Kumar Jena':'666329000003202001',
                   'Sonu  Sathyan':'666329000000804001',
                   'Subhasini T S':'"666329000000724001',
                   'Sutapa Roy B':'666329000003193001',
                   'Kavya KB':'666329000003245117'
               }
               department_id_dict = {#holds all the departments
                   'SOURCING':'666329000000006907',
                   'INVOICE':'666329000000867029',
                   'LENDING':'666329000002161065',
                   'INSURENCE':'666329000003634305'
                    }
               tickets_updated_list = []
               error_dict = dict()# this dict holds all the
               if access_token is None:
                   return JSONResponse(content={"Internal server error"},status_code=500)
               for ticket in data:
                   record_id = '' #initially record_id is empty
                   ticket_update_dict = {"cf":{}}  # holds the fields which needs to be updated after validation
                   comment_dict = dict()  # holds the fields which needed to be updated via
                   dept=dict()#holds the dept id which needs to update
                   ticket_id = ticket.get('ticket_id', '')
                   if ticket_id == '':
                       continue
                   print(ticket_id)
                   # Single API call to get record_id
                   try:
                       response = session.get(
                           f"https://desk.zoho.com/api/v1/tickets/search?limit=1&ticketNumber={ticket_id}")
                       if response.status_code == 200:
                           data_response = response.json()
                           if data_response.get('data') and len(data_response.get('data')) > 0:
                               record_id = data_response.get('data')[0].get('id')
                           else:
                               print(f"No ticket found for ticket_id: {ticket_id}")
                               continue
                       else:
                           print(f"Failed to fetch ticket {ticket_id}: {response.status_code}")
                           error_dict.update({ticket_id:{"ticket_id error unable to find ticket"}})
                           continue
                   except Exception as e:
                       print(f"Error fetching ticket {ticket_id}: {e}")
                       continue

                   # Process fields using mapping dictionary instead of multiple if-else
                   for field_name, cf_field_name in field_mapping.items():
                       value = ticket.get(field_name, '')
                       if value!='':
                               if field_name == 'lender_login_date' or field_name == 'loan_start_date':
                                   ticket_update_dict["cf"].update({cf_field_name:get_date(value)})
                               elif field_name == 'owner':
                                   ticket_update_dict.update({cf_field_name:owner_id_dict.get(value)})
                               elif field_name == 'department':
                                    dept.update({cf_field_name:department_id_dict.get(value)})
                               elif field_name == 'due_date':
                                   #convert the date and time to iso format
                                   ticket_update_dict.update({cf_field_name:india_to_utc(str(value))})
                               else:
                                   ticket_update_dict["cf"].update({cf_field_name: value})

                   # Handle comments separately
                   comments = ticket.get('comments', '')
                   if comments:
                       comment = comments_name_tage(comments)
                       comment_dict = {
                           "content": comment,
                           "commenterId": user,
                           "isPublic": True
                       }
                   #handles the dept movement
                   dept_success = False
                   department = department_id_dict.get('departmentId','')
                   if department:
                       try:
                           response = session.put(f"https://desk.zoho.com/api/v1/tickets/{ticket_id}/move",json=dept)
                           if response.status_code == 200:
                             print("Ticket moved successfully")
                             dept_success = True
                           else:
                             print(f"Failed to move ticket {ticket_id}: {response.status_code}")
                       except Exception as e:
                           print(f"Error moving the ticket {ticket_id}: {e}")

                   print(ticket_update_dict)
                   print(comment_dict)
                   print(dept)

                   # Batch API calls - combine update and comment operations
                   update_success = False
                   comment_success = False

                   # Update ticket if there are fields to update
                   if ticket_update_dict["cf"] and record_id:
                       try:
                           response = session.put(f"https://desk.zoho.com/api/v1/tickets/{record_id}",
                                                  json=ticket_update_dict)
                           print(response.status_code)
                           if response.status_code == 200:
                               update_success = True
                               print(f"Successfully updated ticket {ticket_id}")
                           else:
                               print(f"Failed to update ticket {ticket_id}: {response.status_code}")
                               error_dict.update({ticket_id: {"error": f"unable to update ticket error {response.text}"}})
                       except Exception as e:
                           print(f"Error updating ticket {ticket_id}: {e}")
                   # Add comment if there is one
                   if comment_dict and record_id:
                       try:
                           response = session.post(f"https://desk.zoho.com/api/v1/tickets/{record_id}/comments",
                                                   json=comment_dict)
                           if response.status_code == 200:
                               comment_success = True
                               print(f"Successfully added comment to ticket {ticket_id}")
                           else:
                               print(f"Failed to add comment to ticket {ticket_id}: {response.status_code}")
                               error_dict.get(ticket_id).update({f"unable to add comment to ticket {ticket_id}"})
                       except Exception as e:
                           print(f"Error adding comment to ticket {ticket_id}: {e}")

                   # Add to updated list if either operation succeeded
                   if (update_success or comment_success or dept_success) and ticket_id not in tickets_updated_list:
                        tickets_updated_list.append(ticket_id)

    return JSONResponse(content={"message":f"Total {len(tickets_updated_list)} is updated Id's ->{tickets_updated_list}","error":error_dict},status_code=200)

@router.get('/get-sample-file')
def get_sample_file():
    return FileResponse(
        path="sample_tickets.xlsx",
        filename="sample_file.xlsx",  # optional, browser will download with this name
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.get('/health-check')
def hello():
    return JSONResponse(content="Server is up and running",status_code=200)




