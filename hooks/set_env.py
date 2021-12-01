#
# 3DE4.script.name:	Set Env
#
# 3DE4.script.version:	v1.0
#
# 3DE4.script.gui:	Main Window::Shotgrid
#
# 3DE4.script.comment:	Add comment here.
#

from engine_config import TDE4BaseFactory
from importlib import reload
import sgtk
import os
import engine_config
reload(engine_config)


def make_folders(path):
    
    try:
        os.makedirs(path)
    except:
        pass

def create_3de_new_project(sgtk_shot_folder):

        tde4.newProject()
        tde4.setProjectPath(sgtk_shot_folder)
            
        tde4.postQuestionRequester(
                "FWX SGTK Info..",
                f"SGTK Environment Initialzed.\nProject Environment Setted to \"{sgtk_shot_folder}\""
                ,"Ok"
                )
        
    
def init_env(requester,widget,action):
    #print ("New callback from widget ",widget," received, action: ",action)
    #print ("Put your code here...")
    if widget == 'set_env':
        shot = tde4.getWidgetValue(requester, 'shot_name')
        
        if shot is not None:
            
            shot_config = TDE4BaseFactory(str(shot))
            prj_name = shot_config.get_project_name()
            sgtk_filter_shot = shot_config.sgtk_find_shot()
            
            
            if not sgtk_filter_shot:
                
                tde4.postQuestionRequester(
                        "FWX SGTK Warning..",
                        f"Specified Shot '{str(shot)}' not exist in project '{prj_name}'"
                        ,"Ok"
                        )
            
            else:

                # Check the user given shot name exist in project or not
                proceed = False
                tk = sgtk.sgtk_from_path(shot_config.get_project_path())
                prj_filters = [[ 'sg_status', 'is', 'Active']]
                prj_name_field = [ 'tank_name']
                prj_find = tk.shotgun.find('Project', prj_filters, prj_name_field)
                current_project = {}
                for projects in prj_find:
                    if projects['tank_name'] == shot_config.get_project_name():
                        current_project = projects
                get_all_shots = tk.shotgun.find('Shot', [[ 'project', 'is', current_project ]] , ['code'])
                for get_shots in get_all_shots:
                    if shot == get_shots['code']:
                        proceed = True
                        

                if proceed:
                    
                    get_resolved_tde_prj_path = shot_config.sgtk_resolve_path()
                    get_sgtk_shot_folder = os.path.dirname(get_resolved_tde_prj_path)  
                    make_folders(get_sgtk_shot_folder)

                    current_scene_folder = ''
                    if tde4.getProjectPath() is not None:
                        current_scene_folder = os.path.join(
                                os.path.dirname(tde4.getProjectPath()),
                                '3de4')
                                    
                    if tde4.getProjectPath() is None:
                        
                        create_3de_new_project(get_sgtk_shot_folder)
                        #Close the current window
                        tde4.unpostCustomRequester(requester)
                        
                    elif get_sgtk_shot_folder == current_scene_folder:
                        tde4.postQuestionRequester(
                            "FWX SGTK Info..",
                            f"SGTK Environment Already Initialzed for Project \"{prj_name}\ Shot \"{str(shot)}\""
                            ,"Ok"
                            )
                        pass

                    elif get_sgtk_shot_folder != current_scene_folder:
                        
                        create_3de_new_project(get_sgtk_shot_folder)
                        #Close the current window
                        tde4.unpostCustomRequester(requester)
                        pass
                    
                else:

                     tde4.postQuestionRequester(
                            "FWX SGTK Info..",
                            f"Specified Shot '{str(shot)}' not exist in project '{prj_name}'"
                            ,"Ok"
                            )
                
        else:
            tde4.postQuestionRequester(
                        "FWX SGTK Warning..",
                        "Shot Name is Not Entered"
                        ,"Ok"
                        )
     
    return


def _SetEnvUpdate(requester):
    #print ("New update callback received, put your code here...")
    return


#
# DO NOT ADD ANY CUSTOM CODE BEYOND THIS POINT!
#

try:
    requester	= _SetEnv_requester
except (ValueError,NameError,TypeError):
    requester = tde4.createCustomRequester()
    tde4.addTextFieldWidget(requester,"shot_name","Enter Shot Name","")
    tde4.setWidgetOffsets(requester,"shot_name",299,0,52,0)
    tde4.setWidgetAttachModes(requester,"shot_name","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE")
    tde4.setWidgetSize(requester,"shot_name",200,20)
    tde4.setWidgetCallbackFunction(requester,"shot_name","init_env")
    tde4.addLabelWidget(requester,"init_env_lbl","FWX SGTK - Intiatialize environment","ALIGN_LABEL_LEFT")
    tde4.setWidgetOffsets(requester,"init_env_lbl",290,0,12,0)
    tde4.setWidgetAttachModes(requester,"init_env_lbl","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE")
    tde4.setWidgetSize(requester,"init_env_lbl",200,20)
    tde4.setWidgetCallbackFunction(requester,"init_env_lbl","init_env")
    tde4.addButtonWidget(requester,"set_env","Set Env")
    tde4.setWidgetOffsets(requester,"set_env",336,0,93,0)
    tde4.setWidgetAttachModes(requester,"set_env","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE")
    tde4.setWidgetSize(requester,"set_env",100,40)
    tde4.setWidgetCallbackFunction(requester,"set_env","init_env")
    tde4.setWidgetLinks(requester,"shot_name","","","","")
    tde4.setWidgetLinks(requester,"init_env_lbl","","","","")
    tde4.setWidgetLinks(requester,"set_env","","","","")
    _SetEnv_requester = requester

#
# DO NOT ADD ANY CUSTOM CODE UP TO THIS POINT!
#

if tde4.isCustomRequesterPosted(_SetEnv_requester)=="REQUESTER_UNPOSTED":
    if tde4.getCurrentScriptCallHint()=="CALL_GUI_CONFIG_MENU":
        tde4.postCustomRequesterAndContinue(_SetEnv_requester,"Set Env",0,0,"_SetEnvUpdate")
    else:
        tde4.postCustomRequesterAndContinue(_SetEnv_requester,"Set Env v1.0",800,200,"_SetEnvUpdate")
else:	tde4.postQuestionRequester("_SetEnv","Window/Pane is already posted, close manually first!","Ok")


