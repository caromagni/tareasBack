import uuid
from datetime import datetime
from models.alch_model import Base, EP, Usuario, Grupo, Dominio, Organismo, RolExt, UsuarioGrupo, UsuarioRol
from config.config import Config
from db.alchemy_db import db

class DatabaseSetup:
    def __init__(self):
        pass

    def create_initial_user(self, session):
        print("Creating initial users...")
        
        # Array of hardcoded users that will match JWT tokens
        initial_users = [
            {
                "nombre": "Martin",
                "apellido": "Diaz",
                "username": "cristiandiaz@jus.mendoza.gov.ar",
                "email": "cristiandiaz@jus.mendoza.gov.ar",
                "eliminado": False,
                "suspendido": False
            },
            {
                "nombre": "Silvia",
                "apellido": "Imperiale",
                "username": "simperiale@jus.mendoza.gov.ar",
                "email": "simperiale@jus.mendoza.gov.ar",
                "eliminado": False,
                "suspendido": False
            },
            {
                "nombre": "Mauro",
                "apellido": "Bonadeo",
                "username": "mbonadeo@jus.mendoza.gov.ar",
                "email": "mbonadeo@jus.mendoza.gov.ar",
                "eliminado": False,
                "suspendido": False
            },
            {
                "nombre": "Carolina",
                "apellido": "Magni",
                "username": "cmagni@jus.mendoza.gov.ar",
                "email": "cmagni@jus.mendoza.gov.ar",
                "eliminado": False,
                "suspendido": False
            }
        ]
        
        created_users = []
        
        for user_data in initial_users:
            existing_user = session.query(Usuario).filter_by(email=user_data["email"]).first()
            if existing_user:
                print(f"User '{user_data['email']}' already exists")
                created_users.append(existing_user)
                continue
                
            user = Usuario(
                id=uuid.uuid4(),
                nombre=user_data["nombre"],
                apellido=user_data["apellido"],
                username=user_data["username"],
                email=user_data["email"],
                eliminado=user_data["eliminado"],
                suspendido=user_data["suspendido"],
                fecha_actualizacion=datetime.now()
            )
            session.add(user)
            created_users.append(user)
            print(f"Created user '{user_data['email']}' with ID: {user.id}")
        
        session.commit()
        return created_users

    def create_initial_domain(self, session, admin_user):
        dominio_id="06737c52-5132-41bb-bf82-98af37a9ed80" #must match harcoded id dominio from usher.py untill we have a proper domain setup
        print("Creating initial domain...")
        existing_domain = session.query(Dominio).filter_by(descripcion="General").first()
        if existing_domain:
            print("Domain 'General' already exists")
            return existing_domain 
        domain = Dominio(
            id=dominio_id,
            id_dominio_ext=uuid.uuid4(),
            descripcion="General",
            descripcion_corta="GEN",
            prefijo="GEN",
            fecha_actualizacion=datetime.now(),
            id_user_actualizacion=admin_user.id,
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
            id="cb08f738-7590-4331-871e-26f0f09ff4ca", #harcoded organismo must match id from sync.py x_organismo
            id_organismo_ext=uuid.uuid4(),
            circunscripcion_judicial="General",
            descripcion="Organismo General",
            descripcion_corta="ORG",
            habilitado=True,
            fecha_actualizacion=datetime.now(),
            id_fuero="06737c52-5132-41bb-bf82-98af37a9ed80" #harcoded fuero juz paz lavalle
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
                'caso_uso': [{"codigo": "consultar-tarea"}],
                'metodo': 'GET'
            },
            {
                'id': '137d7d23-41fe-4598-813a-41eafcd10e4c',
                'url': '/tarea_notas',
                'descripcion': 'GET tarea_notas',
                'caso_uso': [{"codigo": "consultar-tarea"}],
                'metodo': 'GET'
            },
            {
                'id': '1517d8e0-ab5a-4f22-9dc1-122adca5581b',
                'url': '/ep',
                'descripcion': 'GET EP',
                'caso_uso': [{"codigo": "consultar-tarea"}, {"codigo": "consultar-grupo"}],
                'metodo': 'GET'
            },
            {
                'id': '25e7c829-b4b9-416f-8286-05939e392451',
                'url': '/label',
                'descripcion': 'Delete label',
                'caso_uso': [{"codigo": "eliminar-label"}],
                'metodo': 'DELETE'
            },
            {
                'id': '25f027f3-af2b-4909-8701-27783713f746',
                'url': '/grupo',
                'descripcion': 'POST grupo',
                'caso_uso': [{"codigo": "crear-grupo"}],
                'metodo': 'POST'
            },
            {
                'id': '2e8dc99d-9605-4ae5-aacd-2e22ae5c704e',
                'url': '/label_grupo',
                'descripcion': 'GET label_grupo',
                'caso_uso': [{"codigo": "consultar-label"}],
                'metodo': 'GET'
            },
            {
                'id': '32957337-799f-4d01-b4e3-0d40fcfe952b',
                'url': '/tipo_tarea',
                'descripcion': 'Get tipo_tarea',
                'caso_uso': [{"codigo": "consultar-tarea"}],
                'metodo': 'GET'
            },
            
            {
                'id': 'd1b1b706-506b-44c6-bc07-8c458accc6fc',
                'url': '/tarea',
                'descripcion': 'Get tarea',
                'caso_uso': [{"codigo": "consultar-tarea"}],
                'metodo': 'GET'
            },
            {
                'id': '34773fe7-063e-4edf-98ba-1c5168471277',
                'url': '/groups_with_base',
                'descripcion': 'GET groups_with_base',
                'caso_uso': [{"codigo": "consultar-usuario"}],
                'metodo': 'GET'
            },
            {
                'id': '3a2c8947-3209-4100-a94a-10e1c433d005',
                'url': '/tipo_tarea',
                'descripcion': 'Patch tipo_tarea',
                'caso_uso': [{"codigo": "modificar-tipo-tarea"}],
                'metodo': 'PATCH'
            },
            {
                'id': '44797749-84f7-47f4-8fb7-ef8335bff613',
                'url': '/subtipo_tarea',
                'descripcion': 'Eliminar subtipo de tarea',
                'caso_uso': [{"codigo": "eliminar-subtipo-tarea"}],
                'metodo': 'DELETE'
            },
            {
                'id': '4cefc783-63e4-415b-8683-22f1bb447148',
                'url': '/grupo',
                'descripcion': 'GET grupo',
                'caso_uso': [{"codigo": "consultar-grupo"}],
                'metodo': 'GET'
            },
            {
                'id': '4ded8f1e-0ad5-4014-bdd7-0c115b913657',
                'url': '/tarea_grupo',
                'descripcion': 'GET tarea_grupo',
                'caso_uso': [{"codigo": "consultar-tarea"}],
                'metodo': 'GET'
            },
            {
                'id': '4fbe819d-ddbc-4503-970c-2c9e96ac07b9',
                'url': '/grupo',
                'descripcion': 'DELETE grupo',
                'caso_uso': [{"codigo": "eliminar-grupo"}],
                'metodo': 'DELETE'
            },
            {
                'id': '540d9d45-549c-4ada-ab4f-855b3c73150b',
                'url': '/actuacion',
                'descripcion': 'Get actuacion',
                'caso_uso': [{"codigo": "consultar-actuacion"}],
                'metodo': 'GET'
            },
            {
                'id': '545869a8-deed-45ae-95db-bb6be5ed9e3a',
                'url': '/usuario_rol',
                'descripcion': 'GET usuario_rol',
                'caso_uso': [{"codigo": "consultar-usuario"}],
                'metodo': 'GET'
            },
            
            {
                'id': 'c60fd41c-3962-418d-b898-ef8595bd44f5',
                'url': '/usuario',
                'descripcion': 'DELETE usuario',
                'caso_uso': [{"codigo": "eliminar-usuario"}],
                'metodo': 'DELETE'
            }, {
                'id': '5c984baf-75b8-425c-8271-c9de803582f8',
                'url': '/usuario',
                'descripcion': 'GET usuario',
                'caso_uso': [{"codigo": "consultar-usuario"}],
                'metodo': 'GET'
            },
            {
                'id': '5cb16bd7-c475-4897-8161-c5d9c4c931b0',
                'url': '/lote_tareas',
                'descripcion': 'Modificar tarea',
                'caso_uso': [{"codigo": "modificar-tarea"}],
                'metodo': 'PATCH'
            },
            {
                'id': '6083167a-eda2-42fd-b87a-288153102b62',
                'url': '/tarea',
                'descripcion': 'Delete tarea',
                'caso_uso': [{"codigo": "eliminar-tarea"}],
                'metodo': 'DELETE'
            },
            {
                'id': '683048cf-d29c-4719-8a51-430d56a5f364',
                'url': '/nota',
                'descripcion': 'DELETE nota',
                'caso_uso': [{"codigo": "eliminar-nota"}],
                'metodo': 'DELETE'
            },
            {
                'id': '6b78d70f-2870-4466-aece-c94b1aa5f3a5',
                'url': '/usuarios_grupo',
                'descripcion': 'GET usuarios_grupo',
                'caso_uso': [{"codigo": "consultar-grupo"}],
                'metodo': 'GET'
            },
            {
                'id': '1d158a1a-dcc1-425c-803b-c53733a31cc6',
                'url': '/alertas',
                'descripcion': 'GET alertas',
                'caso_uso': [{"codigo": "consultar-usuario"}],
                'metodo': 'GET'
            },
            {
                'id': '',
                'url': '/endpoint',
                'descripcion': 'POST ep',
                'caso_uso': [{"codigo": "crear-tarea"}],
                'metodo': 'POST'
            },
            {
                'id': '',
                'url': '/dominio',
                'descripcion': 'GET dominio',
                'caso_uso': [{"codigo": "crear-tarea"}],
                'metodo': 'GET'
            },
            {
                'id': '',
                'url': '/ep',
                'descripcion': 'GET ep',
                'caso_uso': [{"codigo": "consultar-tarea"}],
                'metodo': 'GET'
            },
            {
                'id': '',
                'url': '/lote_tarea_v2',
                'descripcion': 'PATCH lote_tareas_v2',
                'caso_uso': [{"codigo": "modificar-tarea"}],
                'metodo': 'PATCH'
            },
        ]
        for ep in endpoints_data:
            exists = session.query(EP).filter_by(url=ep['url'], metodo=ep['metodo']).first()
            if not exists:
                if ep['id'] == '':
                    ep['id'] = uuid.uuid4()
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

    def create_initial_usuario_grupo(self, session, admin_user, group):
        print("Creating initial usuario_grupo relationship...")
        existing_usuario_grupo = session.query(UsuarioGrupo).filter_by(
            id_usuario=admin_user.id,
            id_grupo=group.id
        ).first()
        if existing_usuario_grupo:
            print("Usuario_grupo relationship already exists")
            return existing_usuario_grupo
        
        usuario_grupo = UsuarioGrupo(
            id=uuid.uuid4(),
            id_usuario=admin_user.id,
            id_grupo=group.id,
            fecha_actualizacion=datetime.now(),
            id_user_actualizacion=admin_user.id,
            eliminado=False
        )
        session.add(usuario_grupo)
        session.commit()
        print(f"Created usuario_grupo relationship with ID: {usuario_grupo.id}")
        return usuario_grupo

    def create_initial_usuario_rol(self, session, users, domain):
        print("Creating initial usuario_rol relationships...")
        created_usuario_roles = []
        
        for user in users:
            print(f"Creating usuario_rol for {user.email}...")
            
            # Get the usuario_grupo relationship for this user
            usuario_grupo = session.query(UsuarioGrupo).filter_by(
                id_usuario=user.id
            ).first()
            
            if not usuario_grupo:
                print(f"No usuario_grupo found for user {user.email}, skipping...")
                continue
                
            # Get the rol_ext for this user
            rol_ext = session.query(RolExt).filter_by(
                email=user.email,
                rol="superadmin"
            ).first()
            
            if not rol_ext:
                print(f"No rol_ext found for user {user.email}, skipping...")
                continue
                
            # Check if usuario_rol already exists
            existing_usuario_rol = session.query(UsuarioRol).filter_by(
                id_usuario_grupo=usuario_grupo.id,
                id_rol_ext=rol_ext.id,
                id_dominio=domain.id
            ).first()
            
            if existing_usuario_rol:
                print(f"Usuario_rol relationship already exists for {user.email}")
                created_usuario_roles.append(existing_usuario_rol)
                continue
                
            # Create the usuario_rol relationship
            usuario_rol = UsuarioRol(
                id=uuid.uuid4(),
                id_usuario_grupo=usuario_grupo.id,
                id_rol_ext=rol_ext.id,
                id_dominio=domain.id,
                base_desnz=True,
                fecha_actualizacion=datetime.now(),
                id_user_actualizacion=user.id,
                eliminado=False
            )
            session.add(usuario_rol)
            created_usuario_roles.append(usuario_rol)
            print(f"Created usuario_rol with ID: {usuario_rol.id} for {user.email}")
        
        session.commit()
        return created_usuario_roles

    def create_superadmin_role(self, session, users):
        print("Creating superadmin roles for all users...")
        created_roles = []
        
        for user in users:
            print(f"Creating superadmin role for {user.email}...")
            existing_role = session.query(RolExt).filter_by(
                email=user.email,
                rol="superadmin"
            ).first()
            if existing_role:
                print(f"Superadmin role for {user.email} already exists")
                created_roles.append(existing_role)
                continue
            
            superadmin_role = RolExt(
                id=uuid.uuid4(),
                email=user.email,
                rol="superadmin",
                id_rol_ext=uuid.uuid4(),
                id_organismo=None,  # Can be None for superadmin
                descripcion_ext="Administrador",
                fecha_actualizacion=datetime.now()
            )
            session.add(superadmin_role)
            created_roles.append(superadmin_role)
            print(f"Created superadmin role with ID: {superadmin_role.id} for {user.email}")
        
        session.commit()
        return created_roles

    def run(self):
        print("Running full database setup...")
        session = db.session
        users = self.create_initial_user(session)
        
        # Use the first user as admin user for backward compatibility
        if users:
            admin_user = users[0]
            print(f"Using '{admin_user.email}' as admin user")
        else:
            print("No users created, cannot proceed")
            return
            
        domain = self.create_initial_domain(session, admin_user)
        organismo = self.create_initial_organismo(session)
        group = self.create_initial_group(session, admin_user, domain, organismo)
        
        # Create usuario_grupo relationships for all users
        for user in users:
            self.create_initial_usuario_grupo(session, user, group)
            
        self.populate_endpoints(session, admin_user)
        self.create_superadmin_role(session, users)
        self.create_initial_usuario_rol(session, users, domain)
        print("Database setup complete.") 