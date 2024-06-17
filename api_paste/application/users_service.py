from sqlmodel import Session, select
from fastapi import HTTPException, status, Depends
from jose import jwt

from persistence.db_utils import get_engine
from presentation.viewmodels.models import Users, UsersCreate, UsersRole, LoginData, Token
from security.hash_provider import hash, verify
from security.token_provider import create_access_token, SECRET_KEY, ALGORITHM


class UsersService:


    def __init__(self):

        self.session = Session(get_engine())


    def get_user_by_id(self, id: int):

        query = select(Users).where(Users.id == id)
        user = self.session.exec(query).first()

        if not user:

            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'Usuário não encontrado!')

        return user
    

    def get_user_by_login(self, login: str):

        query = select(Users).where(Users.login == login)
        user = self.session.exec(query).first()

        if not user:

            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = 'Credenciais incorretas!')

        return user
    

    def generate_token(self, login_data: LoginData):

        user = self.get_user_by_login(login_data.login)

        validation = verify(login_data.password, user.password)

        if not validation:

            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = 'Credenciais incorretas!')
        
        user = {'login': user.login, 'status': user.status, 'role': user.role}

        token = create_access_token(user)

        self.session.close()

        return {'access_token': token, 'token_type': 'Bearer'}
    

    def get_current_user(self, token = Depends(Token)):

        try:

            payload = jwt.decode(token.access_token, SECRET_KEY, algorithms = [ALGORITHM])
            login: str = payload.get("login")

            if token.token_type != 'Bearer':

                raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = 'Token inválido ou expirado!')
            
            user = self.get_user_by_login(login)

        except jwt.JWTError:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = 'Token inválido ou expirado!')
        
        self.session.close()
        
        return user


    def create_user(self, user: UsersCreate):

        hashed_password = hash(user.password)

        role = ''

        if user.role == 'manager':

            role = UsersRole.manager

        else:

            role = UsersRole.functionary

        user_db = Users(name = user.name, login = user.login, password = hashed_password, status = user.status, role = role)
        self.session.add(user_db)
        self.session.commit()
        self.session.refresh(user_db)
        self.session.close()
        return user_db