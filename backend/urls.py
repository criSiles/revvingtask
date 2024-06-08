from django.urls import path
from .views import rawdata, calculateRevenues, reset_database, get_database

urlpatterns = [
    path('rawdata/', rawdata, name='rawdata'),
    path('calculateValues/', calculateRevenues, name='calculateValues'),
    path('reset/', reset_database, name='reset'),
    path('get/', get_database, name='get')
]
