from django.contrib import admin

from .models import GroupDetails, ContactDetails, Chapter, ChaperGroupDetails, ChaperContactDetails, Templates


@admin.register(GroupDetails)
class GroupDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'group_id', 'group_name', 'is_updated')
    list_filter = ('is_updated',)


@admin.register(ContactDetails)
class ContactDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'contact_id', 'contact_name', 'is_updated')
    list_filter = ('is_updated',)


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('id', 'chapter_name')


@admin.register(ChaperGroupDetails)
class ChaperGroupDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'chapter_details', 'group_details')
    list_filter = ('chapter_details', 'group_details')


@admin.register(ChaperContactDetails)
class ChaperContactDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'chapter_details', 'contact_details')
    list_filter = ('chapter_details', 'contact_details')


@admin.register(Templates)
class TemplatesAdmin(admin.ModelAdmin):
    list_display = ('id', 'template_name', 'content')