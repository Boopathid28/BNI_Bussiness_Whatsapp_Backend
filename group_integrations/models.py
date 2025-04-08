from django.db import models

# Create your models here.

class GroupDetails(models.Model):

    group_id = models.CharField(max_length=150,verbose_name="Group ID",unique=True)
    group_name = models.CharField(max_length=150,verbose_name="Group Name")
    is_updated = models.BooleanField(verbose_name="Updated Staus",default=False)

    class Meta:
        db_table = 'group_details'
        verbose_name = 'group_details'
        verbose_name_plural = 'group_details'

    def __str__(self):
        return self.group_id

class ContactDetails(models.Model):

    contact_id = models.CharField(max_length=150,verbose_name="Contact ID",unique=True)
    contact_name = models.CharField(max_length=150,verbose_name="Contact Name")
    is_updated = models.BooleanField(verbose_name="Updated Staus",default=False)

    class Meta:
        db_table = 'contact_details'
        verbose_name = 'contact_details'
        verbose_name_plural = 'contact_details'

    def __str__(self):
        return self.contact_id
    

class Chapter(models.Model):

    chapter_name = models.CharField(max_length=150,verbose_name="Chapter Name",unique=True)

    class Meta:
        db_table = 'chapter'
        verbose_name = 'chapter'
        verbose_name_plural = 'chapter'

    def __str__(self):
        return self.chapter_name
    
class ChaperGroupDetails(models.Model):

    chapter_details = models.ForeignKey(Chapter,verbose_name="Chapter Details",on_delete=models.CASCADE)
    group_details = models.ForeignKey(GroupDetails,verbose_name="Group Details",on_delete=models.CASCADE)

    class Meta:
        db_table = 'chapter_group'
        verbose_name = 'chapter_group'
        verbose_name_plural = 'chapter_group'

    def __str__(self):
        return self.chapter_details.chapter_name
    

class ChaperContactDetails(models.Model):

    chapter_details = models.ForeignKey(Chapter,verbose_name="Chapter Details",on_delete=models.CASCADE)
    contact_details = models.ForeignKey(ContactDetails,verbose_name="Contact Details",on_delete=models.CASCADE)

    class Meta:
        db_table = 'chapter_contact'
        verbose_name = 'chapter_contact'
        verbose_name_plural = 'chapter_contact'

    def __str__(self):
        return self.chapter_details.chapter_name

class Templates(models.Model):

    template_name = models.CharField(max_length=150,verbose_name="Template Name",unique=True)
    content = models.TextField(verbose_name="Contect",null=True,blank=True)
    content_html = models.TextField(verbose_name="Contect HTML",null=True,blank=True)
    has_excel = models.BooleanField(verbose_name="Has Excel", default=False)
    has_multi_sheet = models.BooleanField(verbose_name="Has Multi Sheet", default=False)
    excel_image = models.BooleanField(verbose_name="Excel Image", default=False)
    is_sortable = models.BooleanField(verbose_name="Shortable", default=False)
    leave_row = models.BooleanField(verbose_name="Leave Row", default=False)
    has_link = models.BooleanField(verbose_name="Has Link", default=False)

    class Meta:
        db_table = 'templates'
        verbose_name = 'templates'
        verbose_name_plural = 'templates'

    def __str__(self):
        return self.template_name



