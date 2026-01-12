from pydantic import BaseModel, EmailStr

# Données partagées
class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True

# Ce qu'on reçoit à l'inscription
class UserCreate(UserBase):
    password: str

# Ce qu'on renvoie au front (JAMAIS le mot de passe !)
class UserOut(UserBase):
    id: int
    
    class Config:
        from_attributes = True
