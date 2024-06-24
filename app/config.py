
import os
#add default string values if variable is not exported
os.environ.setdefault('postgres_user', 'NOT_SET')
os.environ.setdefault('postgres_password', 'NOT_SET')
class Config:
    POSGRESS_USER = os.environ.get('postgres_user') 
    POSGRESS_PASSWORD = os.environ.get('postgres_password')
   