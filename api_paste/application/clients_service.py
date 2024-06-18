from fastapi import HTTPException, status
from sqlalchemy import delete
from sqlmodel import Session, delete, select

from persistence.db_utils import get_engine
from presentation.viewmodels.models import Clients, ClientsUpdate

class ClientsService:


    def __init__(self):

        self.session = Session(get_engine())


    def get_all_clients(self, ordering = None):
    
        if not ordering:

            clients = self.session.query(Clients)

        else:            

            clients = self.session.query(Clients).order_by(*ordering)

        self.session.close()
        
        return clients
    

    def get_client_by_id(self, id: int):

        query = select(Clients).where(Clients.id == id)
        client = self.session.exec(query).first()

        if not client:

            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'Cliente não encontrado!')

        self.session.close()

        return client


    def create_client(self, client: Clients):

        self.session.add(client)
        self.session.commit()
        self.session.refresh(client)
        self.session.close()

        return client
    

    def update_client(self, id: int, client: ClientsUpdate):

        current_client = self.get_client_by_id(id)

        if client.name:
            
            current_client.name = client.name


        if client.email:
            
            current_client.email = client.email


        if client.cpf:
            
            current_client.cpf = client.cpf


        self.session.add(current_client)
        self.session.commit()
        self.session.refresh(current_client)
        self.session.close()


        return current_client
    
    
    def delete_client(self, id: int):

        client = self.get_client_by_id(id)  
        query = delete(Clients).where(Clients.id == id)
        self.session.exec(query)
        self.session.commit()
        self.session.close()

        return client
        