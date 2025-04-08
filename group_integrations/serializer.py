from rest_framework import serializers
from .models import *

class GroupDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = GroupDetails
        fields = '__all__'

class ContactDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactDetails
        fields = '__all__'


class ChapterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chapter
        fields = '__all__'

class ChaperGroupDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChaperGroupDetails
        fields = '__all__'

class ChaperContactDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChaperContactDetails
        fields = '__all__'


class TemplatesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Templates
        fields = '__all__'

