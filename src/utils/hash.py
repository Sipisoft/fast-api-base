from passlib.context import CryptContext
import secrets
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
class Hash:
    def encrypt(password:str):
        return pwd_ctx.hash(password)
        
    def verify(plain_password:str, hash: str):
        return pwd_ctx.verify(plain_password, hash)
  
    def generate_token():
        return  secrets.token_urlsafe(32) 
    

    def generate_api_key():
        return secrets.token_urlsafe(24)
    
    
