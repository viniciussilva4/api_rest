from fastapi import HTTPException, status

def verify_status(current_user):

    if current_user.status != True:

        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = 'Requisição não autorizada!')

def verify_role(current_user):

    if current_user.role != 'manager':

        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = 'Requisição não autorizada!')

