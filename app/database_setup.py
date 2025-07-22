import uuid
from datetime import datetime
from models.alch_model import Base, EP, Usuario, Grupo, Dominio, Organismo
from config.config import Config
from db.alchemy_db import db

class DatabaseSetup:
    def __init__(self):
        pass

    def create_initial_user(self, session):
        print("Creating initial admin user...")
        admin_user = Usuario(
            id=uuid.uuid4(),
            nombre="Admin",
            apellido="System",
            username="admin",
            email="admin@system.com",
            habilitado=True,
            fecha_actualizacion=datetime.now()
        )
        session.add(admin_user)
        session.commit()
        print(f"Created admin user with ID: {admin_user.id}")
        return admin_user

    def create_initial_domain(self, session):
        print("Creating initial domain...")
        existing_domain = session.query(Dominio).filter_by(descripcion="General").first()
        if existing_domain:
            print("Domain 'General' already exists")
            return existing_domain
        domain = Dominio(
            id=uuid.uuid4(),
            id_dominio_ext=uuid.uuid4(),
            descripcion="General",
            descripcion_corta="GEN",
            prefijo="GEN",
            fecha_actualizacion=datetime.now(),
            habilitado=True
        )
        session.add(domain)
        session.commit()
        print(f"Created domain with ID: {domain.id}")
        return domain

    def create_initial_organismo(self, session):
        print("Creating initial organismo...")
        existing_organismo = session.query(Organismo).filter_by(descripcion="Organismo General").first()
        if existing_organismo:
            print("Organismo 'Organismo General' already exists")
            return existing_organismo
        organismo = Organismo(
            id=uuid.uuid4(),
            id_organismo_ext=uuid.uuid4(),
            circunscripcion_judicial="General",
            descripcion="Organismo General",
            descripcion_corta="ORG",
            habilitado=True,
            fecha_actualizacion=datetime.now()
        )
        session.add(organismo)
        session.commit()
        print(f"Created organismo with ID: {organismo.id}")
        return organismo

    def create_initial_group(self, session, admin_user, domain, organismo):
        print("Creating initial group...")
        existing_group = session.query(Grupo).filter_by(nombre="Grupo General").first()
        if existing_group:
            print("Group 'Grupo General' already exists")
            return existing_group
        group = Grupo(
            id=uuid.uuid4(),
            id_dominio=domain.id,
            id_organismo=organismo.id,
            nombre="Grupo General",
            descripcion="Grupo general del sistema",
            id_user_actualizacion=admin_user.id,
            fecha_actualizacion=datetime.now(),
            fecha_creacion=datetime.now(),
            base=True
        )
        session.add(group)
        session.commit()
        print(f"Created group with ID: {group.id}")
        return group

    def populate_endpoints(self, session, admin_user):
        print("Populating endpoints...")
        endpoints_data = [
            {
                'id': '015bd2ca-b148-4efc-8399-02576b5e9340',
                'url': '/tarea_detalle',
                'descripcion': 'GET tarea_detalle',
                'caso_uso': '[{"codigo": "consultar-tarea"}]',
                'metodo': 'GET'
            },
            {
                'id': '137d7d23-41fe-4598-813a-41eafcd10e4c',
                'url': '/tarea_notas',
                'descripcion': 'GET tarea_notas',
                'caso_uso': '[{"codigo": "consultar-tarea"}]',
                'metodo': 'GET'
            },
            {
                'id': '1517d8e0-ab5a-4f22-9dc1-122adca5581b',
                'url': '/ep',
                'descripcion': 'GET EP',
                'caso_uso': '[{"codigo": "consultar-tarea"}, {"codigo": "consultar-grupo"}]',
                'metodo': 'GET'
            },
            {
                'id': '25e7c829-b4b9-416f-8286-05939e392451',
                'url': '/label',
                'descripcion': 'Delete label',
                'caso_uso': '[{"codigo": "eliminar-label"}]',
                'metodo': 'DELETE'
            },
            {
                'id': '25f027f3-af2b-4909-8701-27783713f746',
                'url': '/grupo',
                'descripcion': 'POST grupo',
                'caso_uso': '[{"codigo": "crear-grupo"}]',
                'metodo': 'POST'
            },
            {
                'id': '2e8dc99d-9605-4ae5-aacd-2e22ae5c704e',
                'url': '/label_grupo',
                'descripcion': 'GET label_grupo',
                'caso_uso': '[{"codigo": "consultar-label"}]',
                'metodo': 'GET'
            },
            {
                'id': '32957337-799f-4d01-b4e3-0d40fcfe952b',
                'url': '/tipo_tarea',
                'descripcion': 'Get tipo_tarea',
                'caso_uso': '[{"codigo": "consultar-tarea"}]',
                'metodo': 'GET'
            },
            {
                'id': '34773fe7-063e-4edf-98ba-1c5168471277',
                'url': '/groups_with_base',
                'descripcion': 'GET groups_with_base',
                'caso_uso': '[{"codigo": "consultar-usuario"}]',
                'metodo': 'GET'
            },
            {
                'id': '3a2c8947-3209-4100-a94a-10e1c433d005',
                'url': '/tipo_tarea',
                'descripcion': 'Patch tipo_tarea',
                'caso_uso': '[{"codigo": "modificar-tipo-tarea"}]',
                'metodo': 'PATCH'
            },
            {
                'id': '44797749-84f7-47f4-8fb7-ef8335bff613',
                'url': '/subtipo_tarea',
                'descripcion': 'Eliminar subtipo de tarea',
                'caso_uso': '[{"codigo": "eliminar-subtipo-tarea"}]',
                'metodo': 'DELETE'
            },
            {
                'id': '4cefc783-63e4-415b-8683-22f1bb447148',
                'url': '/grupo',
                'descripcion': 'GET grupo',
                'caso_uso': '[{"codigo": "consultar-grupo"}]',
                'metodo': 'GET'
            },
            {
                'id': '4ded8f1e-0ad5-4014-bdd7-0c115b913657',
                'url': '/tarea_grupo',
                'descripcion': 'GET tarea_grupo',
                'caso_uso': '[{"codigo": "consultar-tarea"}]',
                'metodo': 'GET'
            },
            {
                'id': '4fbe819d-ddbc-4503-970c-2c9e96ac07b9',
                'url': '/grupo',
                'descripcion': 'DELETE grupo',
                'caso_uso': '[{"codigo": "eliminar-grupo"}]',
                'metodo': 'DELETE'
            },
            {
                'id': '540d9d45-549c-4ada-ab4f-855b3c73150b',
                'url': '/actuacion',
                'descripcion': 'Get actuacion',
                'caso_uso': '[{"codigo": "consultar-actuacion"}]',
                'metodo': 'GET'
            },
            {
                'id': '545869a8-deed-45ae-95db-bb6be5ed9e3a',
                'url': '/usuario_rol',
                'descripcion': 'GET usuario_rol',
                'caso_uso': '[{"codigo": "consultar-usuario"}]',
                'metodo': 'GET'
            },
            {
                'id': '5c984baf-75b8-425c-8271-c9de803582f8',
                'url': '/usuario',
                'descripcion': 'DELETE usuario',
                'caso_uso': '[{"codigo": "eliminar-usuario"}]',
                'metodo': 'DELETE'
            },
            {
                'id': '5cb16bd7-c475-4897-8161-c5d9c4c931b0',
                'url': '/lote_tareas',
                'descripcion': 'Modificar tarea',
                'caso_uso': '[{"codigo": "modificar-tarea"}]',
                'metodo': 'PATCH'
            },
            {
                'id': '6083167a-eda2-42fd-b87a-288153102b62',
                'url': '/tarea',
                'descripcion': 'Delete tarea',
                'caso_uso': '[{"codigo": "eliminar-tarea"}]',
                'metodo': 'DELETE'
            },
            {
                'id': '683048cf-d29c-4719-8a51-430d56a5f364',
                'url': '/nota',
                'descripcion': 'DELETE nota',
                'caso_uso': '[{"codigo": "eliminar-nota"}]',
                'metodo': 'DELETE'
            },
            {
                'id': '6b78d70f-2870-4466-aece-c94b1aa5f3a5',
                'url': '/usuarios_grupo',
                'descripcion': 'GET usuarios_grupo',
                'caso_uso': '[{"codigo": "consultar-grupo"}]',
                'metodo': 'GET'
            },
        ]
        for ep in endpoints_data:
            exists = session.query(EP).filter_by(url=ep['url'], metodo=ep['metodo']).first()
            if not exists:
                endpoint = EP(
                    id=ep['id'],
                    url=ep['url'],
                    descripcion=ep['descripcion'],
                    caso_uso=ep['caso_uso'],
                    metodo=ep['metodo'],
                    id_user_actualizacion=admin_user.id,
                    fecha_actualizacion=datetime.now()
                )
                session.add(endpoint)
                print(f"Added endpoint: {ep['url']} [{ep['metodo']}]" )
            else:
                print(f"Endpoint already exists: {ep['url']} [{ep['metodo']}]" )
        session.commit()

    def run(self):
        print("Running full database setup...")
        session = db.session
        admin_user = self.create_initial_user(session)
        domain = self.create_initial_domain(session)
        organismo = self.create_initial_organismo(session)
        group = self.create_initial_group(session, admin_user, domain, organismo)
        self.populate_endpoints(session, admin_user)
        print("Database setup complete.") 