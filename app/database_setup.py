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
                "username": "carolinamagni@jus.mendoza.gov.ar",
                "email": "carolinamagni@jus.mendoza.gov.ar",
                "eliminado": False,
                "suspendido": False
            },
            {
                "nombre": "portal",
                "apellido": "portal",
                "username": "portal",
                "email": "portal@jus.mendoza.gov.ar",
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
        existing_domain = session.query(Dominio).filter_by(id=dominio_id).first()
        if existing_domain:
            print("Domain 'General' already exists")
            return existing_domain 
        domain = Dominio(
            id=dominio_id,
            #id_dominio_ext=uuid.uuid4(),
            #id_dominio_ext tiene que ser el mismo que id_dominio de organismo
            id_dominio_ext=dominio_id, #must match harcoded id dominio from usher.py untill we have a proper domain setup
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
        id_organismo="cb08f738-7590-4331-871e-26f0f09ff4ca" #must match harcoded id organismo from sync.py x_organismo
        #existing_organismo = session.query(Organismo).filter_by(descripcion="Organismo General").first()
        existing_organismo_by_id = session.query(Organismo).filter_by(id=id_organismo).first()
        #if existing_organismo or existing_organismo_by_id:
        #    print("Organismo 'Organismo General' already exists")
        if existing_organismo_by_id:
            print("Organismo with the specified ID already exists")
            return existing_organismo_by_id

        organismo = Organismo(
            id="cb08f738-7590-4331-871e-26f0f09ff4ca", #harcoded organismo must match id from sync.py x_organismo
            id_organismo_ext=uuid.uuid4(),
            circunscripcion_judicial="General",
            descripcion="Organismo General",
            descripcion_corta="ORG",
            habilitado=True,
            fecha_actualizacion=datetime.now(),
            id_dominio_ext="06737c52-5132-41bb-bf82-98af37a9ed80" #harcoded fuero juz paz lavalle
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
            id_dominio_ext=domain.id_dominio_ext,
            id_organismo_ext=organismo.id_organismo_ext,
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
                'id': '',
                'url': '/alertas',
                'descripcion': 'Consultar Alerta',
                'caso_uso': [{"codigo": "consultar-alerta"}],
                'metodo': 'GET'
            },
            {
                'id': '',
                'url': '/expedientes',
                'descripcion': 'Consultar Expediente',
                'caso_uso': [{"codigo": "consultar-expediente"}],
                'metodo': 'GET'
            },
             {
                'id': '',
                'url': '/grupo',
                'descripcion': 'GET grupo',
                'caso_uso': [{"codigo": "consultar-grupo"}],
                'metodo': 'GET'
            },
             {
                'id': '',
                'url': '/label_grupo',
                'descripcion': 'GET label_grupo',
                'caso_uso': [{"codigo": "consultar-label"}],
                'metodo': 'GET'
            },
        {
                'id': '',
                'url': '/nota',
                'descripcion': 'Consultar Nota',
                'caso_uso': [{"codigo": "consultar-nota"}],
                'metodo': 'GET'
            },
{
                'id': '',
                'url': '/tarea_detalle',
                'descripcion': 'GET tarea_detalle',
                'caso_uso': [{"codigo": "consultar-tarea"}],
                'metodo': 'GET'
            },
             {
                'id': '',
                'url': '/tarea',
                'descripcion': 'Get tarea',
                'caso_uso': [{"codigo": "consultar-tarea"}],
                'metodo': 'GET'
            },
            {
                'id': '',
                'url': '/tipo_tarea',
                'descripcion': 'Get tipo_tarea',
                'caso_uso': [{"codigo": "consultar-tipo-tarea"}],
                'metodo': 'GET'
            },
            {
                'id': '',
                'url': '/usuario',
                'descripcion': 'GET usuario',
                'caso_uso': [{"codigo": "consultar-usuario"}],
                'metodo': 'GET'
            },
            {
                'id': '',
                'url': '/usuarios_grupo',
                'descripcion': 'GET usuarios_grupo',
                'caso_uso': [{"codigo": "consultar-usuarios_grupo"}],
                'metodo': 'GET'
            },
             {
                'id': '',
                'url': '/grupo',
                'descripcion': 'POST grupo',
                'caso_uso': [{"codigo": "crear-grupo"}],
                'metodo': 'POST'
            },
            {
                'id': '',
                'url': '/label',
                'descripcion': 'POST label',
                'caso_uso': [{"codigo": "crear-label"}],
                'metodo': 'POST'
            },
             {
                'id': '',
                'url': '/nota',
                'descripcion': 'POST nota',
                'caso_uso': [{"codigo": "crear-nota"}],
                'metodo': 'POST'
            },
            {
                'id': '',
                'url': '/tarea',
                'descripcion': 'Crear tarea',
                'caso_uso': [{"codigo": "crear-tarea"}],
                'metodo': 'POST'
            },
             {
                'id': '',
                'url': '/tipo_tarea',
                'descripcion': 'POST tipo_tarea',
                'caso_uso': [{"codigo": "crear-tipo-tarea"}],
                'metodo': 'POST'
            },
            {
                'id': '',
                'url': '/usuario',
                'descripcion': 'POST usuario',
                'caso_uso': [{"codigo": "crear-usuario"}],
                'metodo': 'POST'
            },
            {
                'id': '',
                'url': '/grupo',
                'descripcion': 'DELETE grupo',
                'caso_uso': [{"codigo": "eliminar-grupo"}],
                'metodo': 'DELETE'
            },
             {
                'id': '',
                'url': '/label',
                'descripcion': 'Delete label',
                'caso_uso': [{"codigo": "eliminar-label"}],
                'metodo': 'DELETE'
            },
              {
                'id': '',
                'url': '/nota',
                'descripcion': 'DELETE nota',
                'caso_uso': [{"codigo": "eliminar-nota"}],
                'metodo': 'DELETE'
            },
            {
                'id': '',
                'url': '/tarea',
                'descripcion': 'Delete tarea',
                'caso_uso': [{"codigo": "eliminar-tarea"}],
                'metodo': 'DELETE'
            },
 {
                'id': '',
                'url': '/tipo_tarea',
                'descripcion': 'Delete tipo_tarea',
                'caso_uso': [{"codigo": "eliminar-tipo-tarea"}],
                'metodo': 'DELETE'
            },
            {
                'id': '',
                'url': '/usuario',
                'descripcion': 'DELETE usuario',
                'caso_uso': [{"codigo": "eliminar-usuario"}],
                'metodo': 'DELETE'
            },
            {
                'id': '',
                'url': '/grupo',
                'descripcion': 'Modificar grupo',
                'caso_uso': [{"codigo": "modificar-grupo"}],
                'metodo': 'PATCH'
            },
{
                'id': '',
                'url': '/tarea',
                'descripcion': 'Modificar tarea',
                'caso_uso': [{"codigo": "modificar-tarea"}],
                'metodo': 'PATCH'
            },
            {
                'id': '',
                'url': '/tipo_tarea',
                'descripcion': 'Patch tipo_tarea',
                'caso_uso': [{"codigo": "modificar-tipo-tarea"}],
                'metodo': 'PATCH'
            },
{
                'id': '',
                'url': '/usuario',
                'descripcion': 'Patch usuario',
                'caso_uso': [{"codigo": "modificar-usuario"}],
                'metodo': 'PATCH'
            },
            {
                'id': '',
                'url': '/tarea_notas',
                'descripcion': 'GET tarea_notas',
                'caso_uso': [{"codigo": "consultar-tarea-notas"}],
                'metodo': 'GET'
            },
              
            {
                'id': '',
                'url': '/groups_with_base',
                'descripcion': 'GET groups_with_base',
                'caso_uso': [{"codigo": "consultar-grupos-grupo-base"}],
                'metodo': 'GET'
            },
               {
                'id': '',
                'url': '/subtipo_tarea',
                'descripcion': 'Eliminar subtipo de tarea',
                'caso_uso': [{"codigo": "eliminar-subtipo-tarea"}],
                'metodo': 'DELETE'
            },
             {
                'id': '',
                'url': '/tarea_grupo',
                'descripcion': 'GET tarea_grupo',
                'caso_uso': [{"codigo": "consultar-tarea-grupo"}],
                'metodo': 'GET'
            },
            {
                'id': '',
                'url': '/actuacion',
                'descripcion': 'Get actuacion',
                'caso_uso': [{"codigo": "consultar-actuacion"}],
                'metodo': 'GET'
            },
              {
                'id': '545869a8-deed-45ae-95db-bb6be5ed9e3a',
                'url': '/usuario_rol',
                'descripcion': 'GET usuario_rol',
                'caso_uso': [{"codigo": "consultar-usuario-rol"}],
                'metodo': 'GET'
            },
            {
                'id': '',
                'url': '/endpoint',
                'descripcion': 'POST ep',
                'caso_uso': [{"codigo": "crear-endpoint"}],
                'metodo': 'POST'
            },
             {
                'id': '',
                'url': '/dominio',
                'descripcion': 'GET dominio',
                'caso_uso': [{"codigo": "consultar-dominio"}],
                'metodo': 'GET'
            },
             {
                'id': '',
                'url': '/ep',
                'descripcion': 'GET ep',
                'caso_uso': [{"codigo": "consultar-endpoint"}],
                'metodo': 'GET'
            },
             {
                'id': '',
                'url': '/lote_tarea_v2',
                'descripcion': 'PATCH lote_tareas_v2',
                'caso_uso': [{"codigo": "modificar-tarea-lote-v2"}],
                'metodo': 'PATCH'
            },
             {
                'id': '',
                'url': '/subtipo_tarea',
                'descripcion': 'POST subtipo_tarea',
                'caso_uso': [{"codigo": "crear-subtipo-tarea"}],
                'metodo': 'POST'
            },
              {
                'id': '',
                'url': '/grupo_usuario',
                'descripcion': 'GET grupo_usuario',
                'caso_uso': [{"codigo": "consultar-grupo-usuario"}],
                'metodo': 'GET'
            },
            {
                'id': '',
                'url': '/label_tarea',
                'descripcion': 'GET label_tarea',
                'caso_uso': [{"codigo": "consultar-labela"}],
                'metodo': 'GET'
            },
            {
                'id': '',
                'url': '/grupos_grupobase',
                'descripcion': 'GET grupo base',
                'caso_uso': [{"codigo": "consultar-grupo"}],
                'metodo': 'GET'
            }
            
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
                id_dominio_ext=domain.id_dominio_ext
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
                id_dominio_ext=domain.id_dominio_ext,
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