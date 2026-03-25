
from src.models.role import Role
from src.db.database import Base, engine
from src.models.admin import Admin, AdminType


from src.db.database import SessionLocal
from src.utils.hash import Hash
from src.utils.password import generate_strong_password

db = SessionLocal()

region = db.query(Region).filter(Region.name== "Greater Accra").first()
if region is None:
    region = Region(name= "Greater Accra", active=True )
    db.add(region)
    db.commit()
    db.refresh(region)


role = db.query(Role).filter(Role.name== "Super Admin").first()
if role is None:
    role = Role(name= "Super Admin", description="Super Admins" )
    db.add(role)
    db.commit()
    db.refresh(role)


current_admin = db.query(Admin).filter(Admin.username== "admin").first()
if current_admin is None:
    temp_password = generate_strong_password()
    current_admin = Admin(username= "admin", name= "Admin", password= Hash.encrypt(temp_password), email= "admin@admin.com", type= AdminType.external, role_id= role.id)
    db.add(current_admin)
    db.commit()
    db.refresh
    print("PASSSWORD>>>>>", temp_password)

db.close()