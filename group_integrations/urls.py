from django.urls import path
from .views import *

urlpatterns = [
    path('sycn-data/',SyncDataView.as_view()),

    path('group-list/',GroupListView.as_view()),
    path('contact-list/',ContactListView.as_view()),

    path('whatsapp-logout/',WhatsappAccountLogoutView.as_view()),
    path('whatsapp-profile/',WhatsappProfileInfoView.as_view()),
    path('whatsapp-login/',WhatsappLoginView.as_view()),
    path('whatsapp-message/',GroupMessageView.as_view()),
    path('whatsapp-image-message/',GroupImageMessageView.as_view()),

    path('chapter/',ChapterView.as_view()),
    path('chapter-list/',ChapterListView.as_view()),
    path('templates/',TemplateView.as_view()),
    path('templates-list/',TemplateListView.as_view()),

    path('excel-file-column-names/',ExcelFileColumnNamesView.as_view()),
    path('excel-file-data/',ExcelFileExtarctionView.as_view()),
    path('excel-file-sheet-names/',ExcelFileSheetNamesView.as_view()),

    path('excel-file-sheet-chapter/',SheetBasedChapterView.as_view()),
]