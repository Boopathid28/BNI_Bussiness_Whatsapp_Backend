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

class LoginView(APIView):
    
    def post(self,request):
        
        data = request.data
        
        user_name = data.get('username') 
        password = data.get('password')
        
        try:
            
            queryset = User.objects.get(username=user_name)

        except Exception as err:

            return Response(
                {
                    "message":"User Does not exsist",
                    "status":status.HTTP_404_NOT_FOUND
                },status=status.HTTP_200_OK
            )
            
        user = authenticate(username=queryset.username,password=password)

        if user is not None:
            
            try:
                
                token_queryset = Token.objects.get(user=queryset.pk)
                
                
            except Token.DoesNotExist:
            
                token_queryset = Token.objects.create(user=queryset)
                
            res_data = {}
            
            res_data['token'] = token_queryset.key
            res_data['id'] = queryset.pk
            res_data['username'] = queryset.username
        
            
            return Response(
                {
                    "data":res_data,
                    "message":"User Loggedin Sucessfully",
                    "status":status.HTTP_200_OK   
                },status=status.HTTP_200_OK
            )
            
        else:
            
            return Response(
                {
                    "message":"Invalid Username or Password",
                    "status":status.HTTP_401_UNAUTHORIZED
                },status=status.HTTP_200_OK
            )
            
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])          
class LogoutView(APIView):
    
    def get(self,request):
        
        try:
            
            token_queryset = Token.objects.get(user=request.user.pk)
            
            token_queryset.delete()
            
            return Response(
                {
                    "message":"User Loggedout Sucessfully",
                    "status":status.HTTP_200_OK
                },status=status.HTTP_200_OK
            )
            
            
        except Exception as err:
            
            return Response(
                {
                    "message":"User Does Exsist",
                    "status":status.HTTP_404_NOT_FOUND
                },status=status.HTTP_200_OK
            )
    
    
            
            