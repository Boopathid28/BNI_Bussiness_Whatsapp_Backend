from rest_framework.response import Response
from rest_framework import status,viewsets
from rest_framework.views import APIView
from django.utils import timezone
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
import requests
from django.conf import settings
import json
import pandas as pd
import math
from .models import *
from .serializer import *
from django.db import transaction
from django.core.paginator import Paginator
import uuid
import time

def check_watsapp_status():

    # url = "https://gate.whapi.cloud/health"

    # headers = {
    #         "accept": "application/json",
    #         "authorization": "Bearer "+str(settings.WHAPI_TOKEN)
    #     }

    # response = requests.get(url, headers=headers)

    # response_data = json.loads(response.content)

    # status_data = response_data.get('user',None)

    # if status_data == None:

    #     contact_queryset = ContactDetails.objects.all()

    #     for contact in  contact_queryset:

    #         contact.delete()

    #     group_queryset = GroupDetails.objects.all()

    #     for group in group_queryset:

    #         group.delete()

    #     return False
    # else:

    #     return True

    return True


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class SyncDataView(APIView):

    @transaction.atomic
    def get(self,request):

        status_data = check_watsapp_status()

        if status_data == False:

            return Response(
                {
                    "message":"Please Login to whatsapp",
                    "status":status.HTTP_204_NO_CONTENT
                },status=status.HTTP_200_OK
            )

        page_url = "https://gate.whapi.cloud/groups?count=10&offset=1"

        headers = {
            "accept": "application/json",
            "authorization": "Bearer "+str(settings.WHAPI_TOKEN)
        }
        
        page_response = requests.get(page_url, headers=headers)
        
        
        page_response_data = json.loads(page_response.content)

        total = page_response_data.get('total')


        i = total/500

        if i > 1 :
            pages = math.ceil(i)

        else:

            pages = 1



        for a in range(0,(pages+1)):

            url = "https://gate.whapi.cloud/groups?count=500&offset="+str(a+1)
        
        
            response = requests.get(url, headers=headers)

            if response.status_code == 200:

                res_data = json.loads(response.content)

                all_groups = res_data.get('groups',[])

                for groups in all_groups:

                    group_id = groups.get('id',None)
                    group_name = groups.get('name',None)

                    if group_id != None and group_name != None:

                        try:

                            group_queryset = GroupDetails.objects.get(group_id=group_id)

                            group_data = {}
                            group_data['group_id'] = group_id

                            group_data['group_name'] = group_name
                            group_data['is_updated'] = True

                            old_serializer = GroupDetailsSerializer(group_queryset,data=group_data,partial=True)

                            if old_serializer.is_valid():
                                old_serializer.save()

                            else:
                                
                                transaction.set_rollback(True)
                                return Response(
                                    {
                                        "data":old_serializer.errors,
                                        "message":"Group data is not updated",
                                        "stauts":status.HTTP_400_BAD_REQUEST
                                    }
                                )
                            
                        except GroupDetails.DoesNotExist:

                            group_data = {}
                            group_data['group_id'] = group_id
                            group_data['is_updated'] = True

                            if group_name != None:

                                group_data['group_name'] = group_name

                            new_serializer = GroupDetailsSerializer(data=group_data)

                            if new_serializer.is_valid():

                                new_serializer.save()

                            else:
                                transaction.set_rollback(True)

                                return Response(
                                    {
                                        "data":old_serializer.errors,
                                        "message":"Group data is not updated",
                                        "stauts":status.HTTP_400_BAD_REQUEST
                                    }
                                )
                            
                        except Exception as err:
                            transaction.set_rollback(True)
                            return Response(
                                {
                                    "data":str(err),
                                    "message":"Something Went Wrong",
                                    "status":status.HTTP_204_NO_CONTENT
                                },status=status.HTTP_200_OK
                            )

            elif response.status_code == 500:
                transaction.set_rollback(True)
                return Response(
                    {
                        "message":"Server Error",
                        "status":status.HTTP_204_NO_CONTENT,
                    },status=status.HTTP_200_OK
                )
            elif response.status_code == 400:
                transaction.set_rollback(True)
                return Response(
                    {
                        "message":"Invalid Request",
                        "status":status.HTTP_204_NO_CONTENT,
                    },status=status.HTTP_200_OK
                )
            
        group_update_queryset = GroupDetails.objects.filter(is_updated=False)


        for group_details in group_update_queryset:

            chapter_queryset = ChaperGroupDetails.objects.filter(group_details=group_details.pk)

            for chapter_group in chapter_queryset:

                chapter_group.delete()

            group_details.delete()


        group_reset_queryset = GroupDetails.objects.all()

        for group_reset in group_reset_queryset:

            group_reset.is_updated = False
            group_reset.save()
        

        contact_url = "https://gate.whapi.cloud/contacts?count=10&offset=1"

        headers = {
            "accept": "application/json",
            "authorization": "Bearer "+str(settings.WHAPI_TOKEN)
        }

        contact_response = requests.get(contact_url, headers=headers)

        contact_response_data =  json.loads(contact_response.content)

        total_contact = contact_response_data.get('total')


        j = total_contact/500


        if j > 1 :

            contact_pages = math.ceil(j)

        else:

            contact_pages = 1
                                
        for b  in range(0,(contact_pages+1)):

            contact_response_url = "https://gate.whapi.cloud/contacts?count=500&offset="+str(b+1)

            contact_headers = {
                "accept": "application/json",
                "authorization": "Bearer "+str(settings.WHAPI_TOKEN)
            }

            contact_response_data = requests.get(contact_response_url, headers=contact_headers)

            if contact_response_data.status_code == 200:

                contact_res_data = json.loads(contact_response_data.content)

                all_contacts = contact_res_data.get('contacts',[])


                for contacts in all_contacts:
                    contact_id = contacts.get('id',None)
                    contact_name = contacts.get('pushname',None)

                    if contact_id != None and contact_name != None:

                        try:

                            contact_queryset = ContactDetails.objects.get(contact_id=contact_id)

                            contact_data = {}

                            contact_data['contact_id'] = contact_id
                            contact_data['is_updated'] = True

                            if contact_name != None:

                                contact_data['contact_name'] = contact_name

                            old_contact_serializer = ContactDetailsSerializer(contact_queryset,data=contact_data,partial=True)

                            if old_contact_serializer.is_valid():

                                old_contact_serializer.save()

                            else:
                                transaction.set_rollback(True)
                                return Response(
                                    {
                                        "data":old_contact_serializer.errors,
                                        "message":"Contacts data is not updated",
                                        "stauts":status.HTTP_400_BAD_REQUEST
                                    }
                                )
                            
                        
                        except ContactDetails.DoesNotExist:

                            contact_data = {}

                            contact_data['contact_id'] = contact_id
                            contact_data['is_updated'] = True

                            if contact_name != None:

                                contact_data['contact_name'] = contact_name

                            new_contact_serializer = ContactDetailsSerializer(data=contact_data)

                            if new_contact_serializer.is_valid():

                                new_contact_serializer.save()

                            else:
                                transaction.set_rollback(True)
                                return Response(
                                    {
                                        "data":new_contact_serializer.errors,
                                        "message":"Contacts data is not updated",
                                        "stauts":status.HTTP_400_BAD_REQUEST
                                    }
                                )

                        except Exception as err:

                            return Response(
                                {
                                    "data":str(err),
                                    "status":status.HTTP_204_NO_CONTENT
                                },status=status.HTTP_200_OK
                            )
            elif contact_response_data.status_code == 400:
                transaction.set_rollback(True)
                return Response(
                    {
                        "message":"Wrong Request Parameters",
                        "status":status.HTTP_204_NO_CONTENT
                    },status=status.HTTP_200_OK
                )
            elif contact_response_data.status_code == 404:
                transaction.set_rollback(True)
                return Response(
                    {
                        "message":"Specified Contact Not found",
                        "status":status.HTTP_204_NO_CONTENT
                    },status=status.HTTP_200_OK
                )
            elif contact_response_data.status_code == 500:
                transaction.set_rollback(True)
                return Response(
                    {
                        "message":"server error",
                        "status":status.HTTP_204_NO_CONTENT
                    },status=status.HTTP_200_OK
                )
        
        contact_update_queryset = ContactDetails.objects.filter(is_updated=False)

        for contac_details in contact_update_queryset:

            chapter_queryset = ChaperContactDetails.objects.filter(contact_details=contac_details.pk)

            for chapter_contact in chapter_queryset:

                chapter_contact.delete()

            contac_details.delete()

        contact_reset_queryset = ContactDetails.objects.all()

        for contact_reset in contact_reset_queryset:

            contact_reset.is_updated = False
            contact_reset.save()

        return Response(
            {
                "message":"Data Sync Sucessfull",
                "status":status.HTTP_200_OK
            },status=status.HTTP_200_OK
        )
    
        
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class WhatsappAccountLogoutView(APIView):
    
    def get(self,request):
        
        try:
            
            url = "https://gate.whapi.cloud/users/logout"

            headers = {
                "accept": "application/json",
                "authorization": "Bearer "+str(settings.WHAPI_TOKEN)
            }

            response = requests.post(url, headers=headers)
            
            res_msg = json.loads(response.content)
            
            
            if response.status_code == 200:
                
                return Response(
                    {
                        "message":"User Loggedout Sucessfully",
                        "status":status.HTTP_200_OK
                    },status=status.HTTP_200_OK
                )
                
            elif response.status_code == 409:
                
                return Response(
                    {
                        "message":"Channel already loggedout",
                        "status":status.HTTP_200_OK
                    },status=status.HTTP_200_OK
                )
                
            else:
                
                return Response(
                    {
                        "message":"Something went wrong",
                        "status":status.HTTP_204_NO_CONTENT
                    },status=status.HTTP_200_OK
                )
            
        except Exception  as err:
            
            return Response(
                {
                    "data":str(err),
                    "message":"Something went wrong",
                    "status":status.HTTP_204_NO_CONTENT
                },status=status.HTTP_200_OK
            )
            
            
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class WhatsappProfileInfoView(APIView):
    
    def get(self,request):
        
        try:
            
            url = "https://gate.whapi.cloud/users/profile"

            headers = {"authorization": "Bearer "+str(settings.WHAPI_TOKEN)}

            response = requests.get(url, headers=headers)
            
            res_content = json.loads(response.content)

            
            
            if response.status_code == 200:
            
                return Response(
                    {
                        "data":res_content,
                        "message":"Data retrieved sucessfully",
                        "status":status.HTTP_200_OK
                    },status=status.HTTP_200_OK
                )
                
            else:
                
                return Response(
                    {
                        "message":"Please Login",
                        "status":status.HTTP_200_OK
                    },status=status.HTTP_200_OK
                )
            
            
        except Exception as err:
            
            return Response(
                {
                    "data":str(err),
                    "message":"Something Went Wrong",
                    "status":status.HTTP_204_NO_CONTENT 
                },status=status.HTTP_200_OK
            )
            
            
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class WhatsappLoginView(APIView):
    
    def get(self,request):
        
        phone_number = request.GET.get('phone_number',None)
        
        url = "https://gate.whapi.cloud/users/login/"+str(phone_number)

        headers = {
            "accept": "application/json",
            "authorization": "Bearer "+str(settings.WHAPI_TOKEN)
        }

        response = requests.get(url, headers=headers)
        
        res_msg = json.loads(response.content)
        
        
        if response.status_code == 200:
            
            return Response(
                {
                    "data":res_msg,
                    "message":"OTP sent sucessfully",
                    "status":status.HTTP_200_OK
                }
            )
            
        elif response.status_code == 400:
            
            return Response(
                {
                    "message":"Please enter a valid phone number",
                    "status":status.HTTP_204_NO_CONTENT
                },status=status.HTTP_200_OK
            )
        elif response.status_code == 406:
            
            return Response(
                {
                    "message":"Not acceptable for mobile type channel",
                    "status":status.HTTP_204_NO_CONTENT
                },status=status.HTTP_200_OK
            )
        
        elif response.status_code == 409:
            
            return Response(
                {
                    "message":"Channel Already AUthenticated",
                    "status":status.HTTP_204_NO_CONTENT
                },status=status.HTTP_200_OK
            )


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class GroupMessageView(APIView):

    def post(self,request):

        # status_data = check_watsapp_status()

        # if status_data == False:

        #     return Response(
        #         {
        #             "message":"Please Login to whatsapp",
        #             "status":status.HTTP_204_NO_CONTENT
        #         },status=status.HTTP_200_OK
        #     )

        request_data = request.POST
        
        message = request_data.get('message')
        selected_columns = request_data.get('column_names', '')
        selected_fav_group = request_data.get('fav_group', "")

        add_link = request.POST.get('add_link', 'false')
        link_column_index = request.POST.get('link_column_index', None)

        selected_columns = selected_columns.split(',')
        selected_fav_group = selected_fav_group.split(',')

        group_with_message = []

        if request_data.get('has_excel', "false") == "true":

            excel_index = request_data.get('excel_index', None)
            excel_file = request.FILES.get('excel_file', None)
            selected_sheet = request_data.get('selected_sheet', None)

            sheet_data = pd.read_excel(excel_file, sheet_name=int(selected_sheet))

            columns = list(sheet_data.columns)

            indexOfSelectedColumns = []

            for col in selected_columns:
                index = columns.index(col)
                indexOfSelectedColumns.append(index)

            group_list_from_sheet = []

            for data in list(sheet_data.values):
                group_list_from_sheet.append(data[int(excel_index)].lower())



            unique_group_list_from_sheet = list(set(group_list_from_sheet))

            added_groups = []

            for fav_group in selected_fav_group:
                for sheet_group in unique_group_list_from_sheet:
                    try:
                        fav_group_queryset = list(ChaperGroupDetails.objects.filter(chapter_details=fav_group, group_details__group_name__icontains=sheet_group))

                        for i in fav_group_queryset:
                            dict_data = {
                                "message": message,
                                "group_id": i.group_details.group_id,
                                "group_name": i.group_details.group_name,
                                "chapter": i.chapter_details.chapter_name
                            }

                            names_list = []
                            link = ""
                            for row in list(sheet_data.values):
                                
                                if str(row[int(excel_index)]).lower() in i.group_details.group_name.lower().split(" "):
                                    
                                    if add_link == "true":
                                        link = str(row[int(link_column_index)])

                                    columns_value = []
                                    for item in indexOfSelectedColumns:
                                        columns_value.append(str(row[int(item)]))
                                    names_list.append("    ".join(columns_value))

                            if len(names_list) > 0:
                                sheet_message = "\n".join(names_list)

                                if add_link == 'true':
                                    dict_data["message"] = '\n\n'.join([message, sheet_message, link])
                                else:
                                    dict_data["message"] = '\n\n'.join([message, sheet_message])
                                
                                if i.group_details.group_id not in added_groups:
                                    group_with_message.append(dict_data)
                                    added_groups.append(i.group_details.group_id)

                    except Exception as err:
                        pass

        else:

            for fav_group in selected_fav_group:

                try:
                    fav_group_queryset = list(ChaperGroupDetails.objects.filter(chapter_details=fav_group))
                    for fav in fav_group_queryset:
                        dict_data = {
                            "message": message,
                            "group_id": fav.group_details.group_id,
                            "group_name": fav.group_details.group_name,
                            "chapter": fav.chapter_details.chapter_name
                        }
                        group_with_message.append(dict_data)
                except Exception as err:
                    pass

        response_list = []

        sented_groups = []

        for msg in group_with_message:

            page_url = "https://gate.whapi.cloud/messages/text"

            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": "Bearer "+str(settings.WHAPI_TOKEN)
            }

            body = {
                "typing_time": 0,
                "to": msg['group_id'],
                "body": msg['message']
            }

            # if msg['group_id'] not in sented_groups:
            
            response = requests.request("POST", page_url, headers=headers, data=json.dumps(body))
            # print(">>>>>>>",response.status_code)
            sented_groups.append(msg['group_id'])
            if response.status_code == 200:
                page_response_data = json.loads(response.content)
                # print("response_data",page_response_data)
                res_dict = {
                    "group_name": msg['group_name'],
                    "chapter_name": msg['chapter'],
                    "message": page_response_data["sent"]
                }

                response_list.append(res_dict)
            else:
                page_response_data = json.loads(response.content)
                # print("error",page_response_data)
                res_dict = {
                    "group_name": msg['group_name'],
                    "chapter_name": msg['chapter'],
                    "message": False
                }

                response_list.append(res_dict)

            time.sleep(1)
            
        
        return Response(
            {   
                "data": group_with_message,
                "message":"message sent sucessfully",
                "status":status.HTTP_200_OK
            },status=status.HTTP_200_OK
        )

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class GroupImageMessageView(APIView):

    def post(self,request):

        # status_data = check_watsapp_status()

        # if status_data == False:

        #     return Response(
        #         {
        #             "message":"Please Login to whatsapp",
        #             "status":status.HTTP_204_NO_CONTENT
        #         },status=status.HTTP_200_OK
        #     )
        
        data = request.data.get('message_list')
        
        response_list = []

        for msg in data:

            page_url = "https://gate.whapi.cloud/messages/image"

            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": "Bearer "+str(settings.WHAPI_TOKEN)
            }

            body = {
                "view_once": False,
                "to": msg['to'],
                "caption": msg['message'],
                "media": msg['image']
            }
            
            response = requests.request("POST", page_url, headers=headers, data=json.dumps(body))
            
            if response.status_code == 200:
                page_response_data = json.loads(response.content)

                res_dict = {
                    "group_name": msg['group_name'],
                    "chapter_name": msg['chapter'],
                    "message": page_response_data["sent"]
                }

                response_list.append(res_dict)
            else:
                res_dict = {
                    "group_name": msg['group_name'],
                    "chapter_name": msg['chapter'],
                    "message": False
                }

                response_list.append(res_dict)

            time.sleep(1)
            
        
        return Response(
            {   
                "data": response_list,
                "message":"message sent sucessfully",
                "status":status.HTTP_200_OK
            },status=status.HTTP_200_OK
        )

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class GroupListView(APIView):

    def post(self,request):

        # status_data = check_watsapp_status()

        # if status_data == False:

        #     return Response(
        #         {
        #             "message":"Please Login to whatsapp",
        #             "status":status.HTTP_204_NO_CONTENT
        #         },status=status.HTTP_200_OK
        #     )

        search = request.data.get('search',None)
        page = request.data.get('page',1)
        items_per_page = request.data.get('items_per_page',10)



        queryset = GroupDetails.objects.filter(group_name__icontains=search).order_by('-id')

        paginated_data = Paginator(queryset, items_per_page)
        serializer = GroupDetailsSerializer(paginated_data.get_page(page), many=True)
        total_items = len(queryset)

        response_data = serializer.data

        for i in range(len(response_data)):

            response_data[i]['s_no'] = i+1

        return Response(
            {
                "data":{
                    "list":response_data,
                    "total_pages": paginated_data.num_pages,
                    "current_page": page,
                    "total_items": total_items,
                    "current_items": len(serializer.data)
                },
                "message":"Group Table List",
                "status":status.HTTP_200_OK
            },status=status.HTTP_200_OK
        )
    
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class ContactListView(APIView):

    def post(self,request):

        # status_data = check_watsapp_status()

        # if status_data == False:

        #     return Response(
        #         {
        #             "message":"Please Login to whatsapp",
        #             "status":status.HTTP_204_NO_CONTENT
        #         },status=status.HTTP_200_OK
        #     )

        search = request.data.get('search',None)
        page = request.data.get('page',1)
        items_per_page = request.data.get('items_per_page',10)


        queryset = ContactDetails.objects.filter(contact_name__icontains=search).order_by('-id')

        paginated_data = Paginator(queryset, items_per_page)
        serializer =ContactDetailsSerializer(paginated_data.get_page(page), many=True)
        total_items = len(queryset)

        response_data = serializer.data

        for i in range(len(response_data)):

            response_data[i]['s_no'] = i+1

        return Response(
            {
                "data":{
                    "list":response_data,
                    "total_pages": paginated_data.num_pages,
                    "current_page": page,
                    "total_items": total_items,
                    "current_items": len(serializer.data)
                },
                "message":"Contact Table List",
                "status":status.HTTP_200_OK
            },status=status.HTTP_200_OK
        )
    


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class ChapterView(APIView):

    @transaction.atomic
    def post(self,request):

        status_data = check_watsapp_status()

        if status_data == False:

            return Response(
                {
                    "message":"Please Login to whatsapp",
                    "status":status.HTTP_204_NO_CONTENT
                },status=status.HTTP_200_OK
            )
        
        request_data = request.data 

        serializer = ChapterSerializer(data=request_data)

        if serializer.is_valid():

            serializer.save()

            group_details = request_data.get('group_details',[])

            for group in group_details:

                group_data = {}

                group_data['chapter_details'] = serializer.data['id']
                group_data['group_details'] = group

                group_serializer = ChaperGroupDetailsSerializer(data=group_data)

                if group_serializer.is_valid():

                    group_serializer.save()

                else:
                    transaction.set_rollback(True)
                    return Response(
                        {
                            "data":group_serializer.errors,
                            "message":"Chapter not Created",
                            "status":status.HTTP_400_BAD_REQUEST
                        },status=status.HTTP_200_OK
                    )
                

            contact_details = request_data.get('contact_details',[])

            for contact in contact_details:

                contact_data = {}

                contact_data['chapter_details'] = serializer.data['id']
                contact_data['contact_details'] = contact
                
                contact_serializer = ChaperContactDetailsSerializer(data=contact_data)

                if contact_serializer.is_valid():

                    contact_serializer.save()

                else:

                    transaction.set_rollback(True)
                    return Response(
                        {
                            "data":contact_serializer.errors,
                            "message":"Chapter not Created",
                            "status":status.HTTP_400_BAD_REQUEST
                        },status=status.HTTP_200_OK
                    )
                
            return Response(
                {
                    "data":serializer.data,
                    "message":"Chapter Created Sucessfully",
                    "status":status.HTTP_200_OK
                },status=status.HTTP_200_OK
            )


        else:

            return Response(
                {
                    "data":serializer.errors,
                    "message":"Chapter is not created",
                    "status":status.HTTP_400_BAD_REQUEST
                },status=status.HTTP_200_OK
            )
    
    @transaction.atomic
    def put(self,request):

        try:

            pk = request.data.get('id',None)

            if pk == None:

                return Response(
                    {
                        "message":"Please Enter the ID",
                        "status":status.HTTP_204_NO_CONTENT
                    },status=status.HTTP_200_OK
                )
            
            queryset = Chapter.objects.get(id=pk)

            request_data = request.data
            

            remove_group = request_data.get('remove_group',[])

            for group in remove_group:

                try:

                    remove_queryset = ChaperGroupDetails.objects.get(id=group)

                    remove_queryset.delete()

                except:

                    transaction.set_rollback(True)

                    return Response(
                        {
                            "message":"Group Does not Exsist",
                            "status":status.HTTP_404_NOT_FOUND
                        },status=status.HTTP_200_OK
                    )

            add_group = request_data.get('add_group',[])

            for new_groups in add_group:

                group_data = {}


                group_data['chapter_details'] = queryset.pk

                group_data['group_details'] = new_groups

                group_serializer = ChaperGroupDetailsSerializer(data=group_data)

                if group_serializer.is_valid():

                    group_serializer.save()

                else:
                    transaction.set_rollback(True)
                    return Response(
                        {
                            "data":group_serializer.errors,
                            "message":"Group Not Update",
                            "status":status.HTTP_400_BAD_REQUEST
                        },status=status.HTTP_200_OK
                    )
                
            remove_contacts = request_data.get('remove_contacts',[])

            for contacts in remove_contacts:

                try:

                    contact_queryset = ChaperContactDetails.objects.get(id=contacts)

                    contact_queryset.delete()

                except:

                    transaction.set_rollback(True)

                    return Response(
                        {
                            "message":"Contact Does not Exsist",
                            "status":status.HTTP_404_NOT_FOUND
                        },status=status.HTTP_200_OK
                    )

            add_contact = request_data.get('add_contact',[])

            for new_contact in add_contact:

                contact_data = {}

                contact_data['chapter_details'] = queryset.pk
                contact_data['contact_details'] = new_contact

                contact_serializer = ChaperContactDetailsSerializer(data=contact_data)

                if contact_serializer.is_valid():

                    contact_serializer.save()

                else:
                    transaction.set_rollback(True)
                    return Response(
                        {
                            "data":contact_serializer.errors,
                            "message":"Chapter Not Updated",
                            "status":status.HTTP_400_BAD_REQUEST
                        },status=status.HTTP_200_OK
                    )


        except Exception as err:

            return Response(
                {
                    "data":str(err),
                    "message":"Something Went Wrong",
                    "status":status.HTTP_204_NO_CONTENT
                },status=status.HTTP_200_OK
            )
        
    def get(self,request):

        try:

            status_data = check_watsapp_status()

            if status_data == False:

                return Response(
                    {
                        "message":"Please Login to whatsapp",
                        "status":status.HTTP_204_NO_CONTENT
                    },status=status.HTTP_200_OK
                )

            pk = request.GET.get('id',None)

            if pk == None:

                return Response(
                    {
                        "message":"Please Enter the ID",
                        "status":status.HTTP_204_NO_CONTENT
                    },status=status.HTTP_200_OK
                )
            
            queryset = Chapter.objects.get(id=pk)

            serializer = ChapterSerializer(queryset)

            res_data = serializer.data

            group_queryset = ChaperGroupDetails.objects.filter(chapter_details=queryset.pk).order_by('-id').values('id','chapter_details','group_details','group_details__group_name')

            
            res_data['group_details'] = group_queryset


            contact_queryset = ChaperContactDetails.objects.filter(chapter_details=queryset.pk).order_by('-id').values('id','chapter_details','contact_details','contact_details__contact_name')


            res_data['contact_details']  = contact_queryset


            return Response(
                {
                    "data":res_data,
                    "message":"Chapter Details Retrived Sucessfully",
                    "status":status.HTTP_200_OK
                },status=status.HTTP_200_OK
            )
        
        except Chapter.DoesNotExist:

            return Response(
                {
                    "message":"Chapter Doesnot Exsist",
                    "status":status.HTTP_404_NOT_FOUND
                },status=status.HTTP_200_OK
            )

        except Exception as err:

            return Response(
                {
                    "data":str(err),
                    "message":"Something Went Wrong",
                    "status":status.HTTP_400_BAD_REQUEST
                },status=status.HTTP_200_OK
            )
        
    def delete(self,request):

        try:

            status_data = check_watsapp_status()

            if status_data == False:

                return Response(
                    {
                        "message":"Please Login to whatsapp",
                        "status":status.HTTP_204_NO_CONTENT
                    },status=status.HTTP_200_OK
                )

            pk = request.GET.get('id',None)

            if pk == None:

                return Response(
                    {
                        "message":"Please Enter the ID",
                        "status":status.HTTP_204_NO_CONTENT
                    },status=status.HTTP_200_OK
                )
            
            queryset = Chapter.objects.get(id=pk)

            queryset.delete()


            return Response(
                {
                    "message":"Chapter Deleted Sucessfully",
                    "status":status.HTTP_200_OK
                },status=status.HTTP_200_OK
            )
        
        except Chapter.DoesNotExist:

            return Response(
                {
                    "message":"Chapter Doesnot Exsist",
                    "status":status.HTTP_404_NOT_FOUND
                },status=status.HTTP_200_OK
            )

        except Exception as err:

            return Response(
                {
                    "data":str(err),
                    "message":"Something Went Wrong",
                    "status":status.HTTP_400_BAD_REQUEST
                },status=status.HTTP_200_OK
            )
        
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class ChapterListView(APIView):

    def get(self,request):

        status_data = check_watsapp_status()

        if status_data == False:

            return Response(
                {
                    "message":"Please Login to whatsapp",
                    "status":status.HTTP_204_NO_CONTENT
                },status=status.HTTP_200_OK
            )
        
        search = request.GET.get('search',"")
        page = request.GET.get('page',1)
        items_per_page = request.GET.get('items_per_page',10)
        

        queryset = Chapter.objects.filter(chapter_name__icontains=search).order_by('-id')
        paginated_data = Paginator(queryset, items_per_page)
        serializer =ChapterSerializer(paginated_data.get_page(page), many=True)
        total_items = len(queryset)


        response_data = []

        for chapter in  serializer.data:

            res_data = chapter

            chapter_queryset = Chapter.objects.get(id=chapter['id'])

            res_data['id'] = chapter_queryset.pk
            res_data['chapter_name'] = chapter_queryset.chapter_name

            group_count = ChaperGroupDetails.objects.filter(chapter_details=chapter_queryset.pk).count()
            contact_count = ChaperContactDetails.objects.filter(chapter_details=chapter_queryset.pk).count()

            res_data['group_count'] = group_count
            res_data['contact_count'] = contact_count

            response_data.append(res_data)


        return Response(
            {
                "data":{
                    "list":response_data,
                    "total_pages": paginated_data.num_pages,
                    "current_page": page,
                    "total_items": total_items,
                    "current_items": len(serializer.data)
                },
                "message":"Chapter Table List",
                "status":status.HTTP_200_OK
            },status=status.HTTP_200_OK
        )
    
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class TemplateView(APIView):

    def post(self,request):

        # status_data = check_watsapp_status()

        # if status_data == False:

        #     return Response(
        #         {
        #             "message":"Please Login to whatsapp",
        #             "status":status.HTTP_204_NO_CONTENT
        #         },status=status.HTTP_200_OK
        #     )
        
        request_data = request.data 

        serializer = TemplatesSerializer(data=request_data)

        if serializer.is_valid():

            serializer.save()

            return Response(
                {
                    "data":serializer.data,
                    "message":"Template Created Sucessfully",
                    "status":status.HTTP_200_OK
                },status=status.HTTP_200_OK
            )

        else:

            return Response(
                {
                    "data":serializer.errors,
                    "message":"Template Not Created",
                    "status":status.HTTP_400_BAD_REQUEST
                },status=status.HTTP_200_OK
            )
        
    def get(self,request):

        try:

            status_data = check_watsapp_status()

            if status_data == False:

                return Response(
                    {
                        "message":"Please Login to whatsapp",
                        "status":status.HTTP_204_NO_CONTENT
                    },status=status.HTTP_200_OK
                )

            pk = request.GET.get('id',None)

            if pk == None:

                return Response(
                    {
                        "message":"Please Enter the ID",
                        "status":status.HTTP_204_NO_CONTENT
                    },status=status.HTTP_200_OK
                )
            
            queryset = Templates.objects.get(id=pk)

            serializer = TemplatesSerializer(queryset)

            return Response(
                {
                    "data":serializer.data,
                    "message":"Template Retrieved Sucessfully",
                    "status":status.HTTP_200_OK
                },status=status.HTTP_200_OK
            )
        
        except Templates.DoesNotExist:

            return Response(
                {
                    "message":"Template Does not Exsist",
                    "status":status.HTTP_404_NOT_FOUND
                },status=status.HTTP_200_OK
            )

        except Exception as err:

            return Response(
                {
                    "data":str(err),
                    "message":"something went wrong",
                    "status":status.HTTP_204_NO_CONTENT
                },status=status.HTTP_200_OK
            )
        
    def put(self,request):

        try:

            status_data = check_watsapp_status()

            if status_data == False:

                return Response(
                    {
                        "message":"Please Login to whatsapp",
                        "status":status.HTTP_204_NO_CONTENT
                    },status=status.HTTP_200_OK
                )

            pk = request.data.get('id',None)

            if pk == None:

                return Response(
                    {
                        "message":"Please Enter the ID",
                        "status":status.HTTP_204_NO_CONTENT
                    },status=status.HTTP_200_OK
                )
            
            request_data = request.data
            
            queryset = Templates.objects.get(id=pk)

            serializer = TemplatesSerializer(queryset,data=request_data,partial=True)

            if serializer.is_valid():

                serializer.save()

                return Response(
                    {
                        "data":serializer.data,
                        "message":"Template Uppdated Sucessfully",
                        "status":status.HTTP_200_OK
                    },status=status.HTTP_200_OK
                )
            
            else:

                return Response(
                    {
                        "data":serializer.errors,
                        "message":"Template Not Updated",
                        "status":status.HTTP_400_BAD_REQUEST
                    },status=status.HTTP_200_OK
                )
        
        except Templates.DoesNotExist:

            return Response(
                {
                    "message":"Template Does not Exsist",
                    "status":status.HTTP_404_NOT_FOUND
                },status=status.HTTP_200_OK
            )

        except Exception as err:

            return Response(
                {
                    "data":str(err),
                    "message":"something went wrong",
                    "status":status.HTTP_204_NO_CONTENT
                },status=status.HTTP_200_OK
            )
        
    def delete(self,request):

        try:

            status_data = check_watsapp_status()

            if status_data == False:

                return Response(
                    {
                        "message":"Please Login to whatsapp",
                        "status":status.HTTP_204_NO_CONTENT
                    },status=status.HTTP_200_OK
                )

            pk = request.GET.get('id',None)

            if pk == None:

                return Response(
                    {
                        "message":"Please Enter the ID",
                        "status":status.HTTP_204_NO_CONTENT
                    },status=status.HTTP_200_OK
                )
            
            queryset = Templates.objects.get(id=pk)

            queryset.delete()

            return Response(
                {
                    "message":"Template Deleted Sucessfully",
                    "status":status.HTTP_200_OK
                },status=status.HTTP_200_OK
            )
        
        except Templates.DoesNotExist:

            return Response(
                {
                    "message":"Template Does not Exsist",
                    "status":status.HTTP_404_NOT_FOUND
                },status=status.HTTP_200_OK
            )

        except Exception as err:

            return Response(
                {
                    "data":str(err),
                    "message":"something went wrong",
                    "status":status.HTTP_204_NO_CONTENT
                },status=status.HTTP_200_OK
            )
        

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class TemplateListView(APIView):

    def get(self, request):

        queryset = Templates.objects.all().order_by('-id')

        serializer = TemplatesSerializer(queryset, many=True)

        return Response(
            {
                "data":{
                    "list":serializer.data,
                },
                "message":"Template List",
                "status":status.HTTP_200_OK
            },status=status.HTTP_200_OK
        )

    def post(self,request):

        status_data = check_watsapp_status()

        if status_data == False:

            return Response(
                {
                    "message":"Please Login to whatsapp",
                    "status":status.HTTP_204_NO_CONTENT
                },status=status.HTTP_200_OK
            )
        
        search = request.data.get('search',"")
        page = request.data.get('page',1)
        items_per_page = request.data.get('items_per_page',10)

        queryset = Templates.objects.filter(template_name__icontains=search).order_by('-id')

        paginated_data = Paginator(queryset, items_per_page)
        serializer =TemplatesSerializer(paginated_data.get_page(page), many=True)
        total_items = len(queryset)

        return Response(
            {
                "data":{
                    "list":serializer.data,
                    "total_pages": paginated_data.num_pages,
                    "current_page": page,
                    "total_items": total_items,
                    "current_items": len(serializer.data)
                },
                "message":"Template Table List",
                "status":status.HTTP_200_OK
            },status=status.HTTP_200_OK
        )
        
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class ExcelFileColumnNamesView(APIView):

    def post(self, request):

        file_data = request.FILES.get('excel_file', None)
        selected_sheet = request.POST.get('selected_sheet', None)

        if file_data is None:
            return Response({
                "message": "File is required",
                "status": status.HTTP_204_NO_CONTENT
            }, status = status.HTTP_200_OK)
        else:
            
            file = pd.read_excel(file_data, sheet_name=int(selected_sheet)).columns

            return Response({
                "data": {
                    "column_list": file,
                },
                "message": "Column names retrieved",
                "status": status.HTTP_200_OK
            }, status = status.HTTP_200_OK)

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class ExcelFileSheetNamesView(APIView):

    def post(self, request):

        file_data = request.FILES.get('excel_file', None)

        if file_data is None:
            return Response({
                "message": "File is required",
                "status": status.HTTP_204_NO_CONTENT
            }, status = status.HTTP_200_OK)
        else:
            
            sheet_names = pd.ExcelFile(file_data).sheet_names

            return Response({
                "data": {
                    "sheet_name_list" :list(sheet_names)
                },
                "message": "Column names retrieved",
                "status": status.HTTP_200_OK
            }, status = status.HTTP_200_OK)

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class ExcelFileExtarctionView(APIView):

    def post(self, request):

        file_data = request.FILES.get('excel_file', None)
        selected_fav_group = request.POST.get('fav_group', "")
        selected_columns = request.POST.get('column_names', '')
        message = request.POST.get('message', '')
        sort = request.POST.get('sort', 'false')
        sort_column = request.POST.get('sort_column', '')
        leave_row = request.POST.get('leave_row', 'false')
        leave_row_value = request.POST.get('leave_row_value', '')
        leave_row_column_name = request.POST.get('leave_row_column_name', '')
        excel_index = request.POST.get('excel_index', None)
        selected_sheet = request.POST.get('selected_sheet', None)
        add_link = request.POST.get('add_link', 'false')
        link_column_index = request.POST.get('link_column_index', None)
        

        if file_data is None:
            return Response({
                "message": "File is required",
                "status": status.HTTP_204_NO_CONTENT
            }, status = status.HTTP_200_OK)
        else:

            selected_fav_group = selected_fav_group.split(',')
            selected_columns = selected_columns.split(',')
            
            excel_file = pd.read_excel(file_data, sheet_name=int(selected_sheet))

            if sort == "true":
                file = excel_file.sort_values(by=sort_column, ascending=False)
            else:
                file = excel_file

            columns = list(file.columns)

            if leave_row == "true":
                leave_row_column_index = columns.index(leave_row_column_name)

            indexOfSelectedColumns = []

            for col in selected_columns:
                index = columns.index(col)
                indexOfSelectedColumns.append(index)

            chapter_details_list = []

            for fav_group in selected_fav_group:

                try:
                    chapter_queryset = list(ChaperGroupDetails.objects.filter(chapter_details=fav_group))
                    
                    for chapter_group in chapter_queryset:
                        sheet_data = []

                        link = ""

                        for row in list(file.values):
                            if str(row[int(excel_index)]).lower() in chapter_group.group_details.group_name.lower().split(" "):
                                
                                if add_link == "true":
                                    link = str(row[int(link_column_index)])
                                
                                
                                if leave_row == "true":
                                    if str(row[leave_row_column_index]) not in leave_row_value.split(','):
                                        columns_value = {}
                                        for item in indexOfSelectedColumns:
                                            columns_value["_".join(columns[item].split(' '))] = row[item]
                                        sheet_data.append(columns_value)
                                else:
                                    columns_value = {}
                                    for item in indexOfSelectedColumns:
                                        columns_value["_".join(columns[item].split(' '))] = row[item]
                                    sheet_data.append(columns_value)
                            
                        dict_data = {
                            "unique_id": uuid.uuid4(),
                            "chapter_pk": chapter_group.pk,
                            "chapter_name": chapter_group.chapter_details.chapter_name,
                            "group_name": chapter_group.group_details.group_name,
                            "group_id": chapter_group.group_details.group_id,
                            "sheet_data": sheet_data
                        }

                        if add_link == 'true':
                            dict_data['message'] = message + " \n " + link
                        else:
                            dict_data['message'] = message

                        if len(sheet_data) > 0:
                            chapter_details_list.append(dict_data)
                except Exception as err:
                    pass

            


            return Response({
                "data": {
                    "column_list": selected_columns,
                    "data_list": chapter_details_list
                },
                "message": "Column names retrieved",
                "status": status.HTTP_200_OK
            }, status = status.HTTP_200_OK)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class SheetBasedChapterView(APIView):

    def post(self,request):

        file_data = request.FILES.get('excel_file', None)
        fav_group = request.POST.get('fav_group', None)
        message = request.POST.get('message', None)
        
        # selected_fav_group = []
        # if len(fav_group) > 1:
        selected_fav_group = fav_group.split(',')
        # else:
        #     selected_fav_group.append(fav_group)

        if file_data is None:
            return Response({
                "message": "File is required",
                "status": status.HTTP_204_NO_CONTENT
            }, status = status.HTTP_200_OK)
        else:
            
            sheet_names = pd.ExcelFile(file_data).sheet_names

        response_data = []
        
        for fav in selected_fav_group:
            try:
                fav_group_queryset = list(ChaperGroupDetails.objects.filter(chapter_details=fav))
                
                for i in fav_group_queryset:

                    for index,sheets in enumerate(sheet_names):
                        if str(sheets).lower() in i.group_details.group_name.lower():

                            res_data = {
                                "message": message,
                                "group_id": i.group_details.group_id,
                                "group_name": i.group_details.group_name,
                            }

                            res_data['chapter_name'] = sheets
                            res_data["unique_id"] = uuid.uuid4()

                            excel_data = pd.read_excel(file_data, sheet_name=int(index))

                            column_data = excel_data.columns

                            index_data = {}

                            for index_value,columns in enumerate(column_data):

                                if str(columns).lower() == 'name':

                                    index_data['name_index']  = index_value

                                elif str(columns).lower() == 'status':

                                    index_data['status_index'] = index_value

                            sheed_data = []

                            for data in excel_data.values:

                                if str(data[index_data['status_index']]).lower() != "yes":

                                    member_data ={}

                                    member_data['name'] = str(data[index_data['name_index']])
                                    member_data['message'] = str(data[index_data['status_index']])

                                    sheed_data.append(member_data)

                            res_data['sheet_data'] = sheed_data

                            response_data.append(res_data)

            except Exception as err:
                pass

        # response_data = []

        # for index,sheets in enumerate(sheet_names):

        #     res_data = {}

        #     res_data['chapter_name'] = sheets
        #     res_data["unique_id"] = uuid.uuid4()

        #     excel_data = pd.read_excel(file_data, sheet_name=int(index))

        #     column_data = excel_data.columns

        #     index_data = {}

        #     for index_value,columns in enumerate(column_data):

        #         if str(columns).lower() == 'name':

        #            index_data['name_index']  = index_value

        #         elif str(columns).lower() == 'status':

        #            index_data['status_index'] = index_value

        #     sheed_data = []

        #     for data in excel_data.values:

        #         if str(data[index_data['status_index']]).lower() != "yes":

        #             member_data ={}

        #             member_data['name'] = str(data[index_data['name_index']])
        #             member_data['message'] = str(data[index_data['status_index']])

        #             sheed_data.append(member_data)

        #     res_data['sheet_data'] = sheed_data

        #     response_data.append(res_data)

        return Response(
            {
                "data":response_data,
                "message":"Data Retrived Sucessfully",
                "status":status.HTTP_200_OK
            },status=status.HTTP_200_OK
        )
    















 



        




        

                    

    




        





        
        
