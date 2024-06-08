from django.urls import path
from .views import rawdata, totalValues, reset_database, get_database

urlpatterns = [
    path('rawdata/', rawdata, name='rawdata'),
    path('totalValues/', totalValues, name='totalValues'),
    path('reset/', reset_database, name='reset'),
    path('get/', get_database, name='get')
]
