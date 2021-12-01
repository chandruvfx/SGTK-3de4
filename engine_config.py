import logging
import sgtk
import sys
import os 

___SGTK_PROJECT_PATH__ = '/mnt/studio/mmprjs'

authenticator = sgtk.authentication.ShotgunAuthenticator()
user = authenticator.get_user()
sgtk_connection = user.create_sg_connection()
sgtk.set_authenticated_user(user)

logging.basicConfig(format='%(asctime)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S', stream=sys.stdout)
tde_sgtk_logger = logging.getLogger()
tde_sgtk_logger.setLevel(logging.DEBUG)
#tde_sgtk_logger.info(f'Artist {user} Authentication Established')

class TDE4BaseFactory:

    
    def __init__(self, shot_name) -> None:
        
        self.project_name = sgtk.get_sgtk_module_path().split('/install')[0].split('/')[-1]
        self.shot_name = shot_name
        self.step = 'TRK'
        self.task_name = 'Tracking'

        
    def get_project_name(self) -> str:

            return self.project_name

    def get_project_path(self) -> str:

            return os.path.join(
                ___SGTK_PROJECT_PATH__, 
                self.project_name
                )

    def is_project_folder_exists(self) -> bool:

        return True if os.path.exists( 
                    os.path.join(___SGTK_PROJECT_PATH__, 
                    self.project_name)
                    ) \
                    else False

    @property
    def shotname(self) -> str:

        return self.shot_name

    @shotname.setter
    def shotname(self, name) -> None:

        self.shot_name = name

    def sgtk_find_shot(self) -> list:

        if self.is_project_folder_exists():
            self.tank_project = sgtk.sgtk_from_path(self.get_project_path())

            filters = [[ 'code', 'is', '%s' %self.shot_name ]]
            fields = [ 'code', 'sg_sequence', 'project']
            
            return self.tank_project.shotgun.find('Shot', filters ,fields)


    def sgtk_find_published_files(self) -> dict:
        
        if self.is_project_folder_exists():

            shot_schema = self.sgtk_find_shot()
            filters = [[ 'entity', 'is', {'type': 'Shot', 'id': shot_schema[0]['id']} ]]
            fields = ['path']
            publish_files = {}
            for publishes in self.tank_project.shotgun.find('PublishedFile', filters ,fields):
                publish_files[publishes['path']['name']] = publishes['path']['local_path_linux']
            return publish_files


    def get_template_path(self) -> object:

        return self.tank_project.templates['3de4_shot_work']

    def field(self, version) -> str:

        fields = {  'Shot': self.shot_name,
                'Sequence': self.sgtk_find_shot()[0]['sg_sequence']['name'],
                'Step': self.step,
                'task_name': self.task_name,
                'version': version}
        return fields

    def sgtk_resolve_path(self, version=1):

        context = self.get_template_path()
        fields = self.field(version)
        return context.apply_fields(fields)


    def sgtk_resolve_path_from_context(self, path) -> str:
        
        prj_path = sgtk.sgtk_from_path(self.get_project_path())
        prj_path.synchronize_filesystem_structure()
        return prj_path.context_from_path(path)

    def sgtk_resolve_3de_file_publish_path(self, version=1) -> str:

        tde_temp_context = self.tank_project.templates['3de_shot_work']
        fields = self.field(version)
        return tde_temp_context.apply_fields(fields)


    def sgtk_resolve_publish_path_nk(self, version=1) -> str:

        nk_temp_context = self.tank_project.templates['nuke_shot_pub']
        fields = self.field(version)
        return nk_temp_context.apply_fields(fields)

    def sgtk_resolve_publish_path_alembic(self, version=1) -> str:

        abc_temp_context = self.tank_project.templates['shot_alembic_cache']
        fields = self.field(version)
        return abc_temp_context.apply_fields(fields)

    def sgtk_resolve_publish_path_jpg(self, version=1) -> str:

        jpg_temp_context = self.tank_project.templates['nuke_shot_render_pub_mono_jpg']
        fields = self.field(version)
        return jpg_temp_context.apply_fields(fields)

        
    

       

    

    

        
        
         
