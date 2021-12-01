#
# 3DE4.script.name:	File Save..
#
# 3DE4.script.version:	v1.0
#
# 3DE4.script.gui:	Main Window::Shotgrid
#
# 3DE4.script.comment:	Add comment here.
#

from engine_config import TDE4BaseFactory
from importlib import reload
import os
import engine_config
reload(engine_config)

def resolve_sgtk_template(tde_file_path):

    non_shot_config = TDE4BaseFactory(None)

    sgtk_shot_entity = non_shot_config.sgtk_resolve_path_from_context(tde_file_path)
    get_shot = sgtk_shot_entity.entity['name']
    
    shot_config = TDE4BaseFactory(str(get_shot))
    sgtk_filter_shot = shot_config.sgtk_find_shot()
    return shot_config

def tde_save_first_version_scene_file(tde_file_path):

    resolved_shot_config =resolve_sgtk_template(tde_file_path)
    sgtk_resolve_shot = resolved_shot_config.sgtk_resolve_path()

    get_action = tde4.postQuestionRequester(
                "FWX SGTK Info..",
                f"Proceed with Saving File \n \"{sgtk_resolve_shot}\"",
                "Ok", "Cancel"
                )  
    if get_action == 1:    
        
        tde4.saveProject(sgtk_resolve_shot)

        tde4.setProjectPath(
                    sgtk_resolve_shot
        )

def tde_incremental_version_scene_file(tde_file_path):

    versions = []
    for tde_scene_file in tde_file_path:
        
        resolved_shot_config =resolve_sgtk_template(tde_scene_file)
        template_path = resolved_shot_config.get_template_path()
        versions.append(template_path.get_fields(tde_scene_file)['version'])
    
    version = max(versions)
    version = version + 1 

    resolved_shot_config =resolve_sgtk_template(tde_file_path[0])
    sgtk_resolve_shot = resolved_shot_config.sgtk_resolve_path(version)

    get_action = tde4.postQuestionRequester(
                "FWX SGTK Info..",
                f"Proceed with Saving File \n \"{sgtk_resolve_shot}\"",
                "Ok", "Cancel"
                )  
    if get_action == 1:
        tde4.saveProject(sgtk_resolve_shot)
        tde4.setProjectPath(
                   sgtk_resolve_shot
        )


scene_file = tde4.getProjectPath()

if scene_file is None or not scene_file.startswith('/Shares/T/studio/projects'):
    
    tde4.postQuestionRequester(
                "FWX SGTK Info..",
                f"SGTK Environment is Not Initialized\n\
                Please set using MainWindow's Shotgrid -> Set Env",
                "Ok"
                )
else:
    if scene_file.endswith('3de4.3de'):
        
        scene_file_prj_folder_path = scene_file.split('.3de')[0]
        
    else:
        
        scene_file_prj_folder_path = os.path.dirname(scene_file)
        
    tde_scene_files_list = os.listdir(scene_file_prj_folder_path)

    if not tde_scene_files_list:

        tde_save_first_version_scene_file(scene_file_prj_folder_path)
        
    else:

        scene_file_collection = []
        for tde_scene_files in tde_scene_files_list:
            scene_file_path = os.path.join(
                scene_file_prj_folder_path,
                tde_scene_files
                )
            scene_file_collection.append(scene_file_path)
            
    
        tde_incremental_version_scene_file(scene_file_collection)