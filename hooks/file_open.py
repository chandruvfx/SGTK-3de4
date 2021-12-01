#
# 3DE4.script.name:	File Open..
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
import time
reload(engine_config)


scene_file = tde4.getProjectPath()
if scene_file is not None and scene_file.startswith('/Shares/T/studio/projects'):
    
    if '3de4' not in os.path.dirname(scene_file):
        scene_file_prj_folder_path =os.path.join(
                os.path.dirname(scene_file), '3de4')
    else:
        scene_file_prj_folder_path = os.path.dirname(scene_file)
        

    def resolve_sgtk_template(tde_file_path) -> str:

        ''' Initiate the SGTK 3de base class'''

        non_shot_config = TDE4BaseFactory(None)

        sgtk_shot_entity = non_shot_config.sgtk_resolve_path_from_context(tde_file_path)
        get_shot = sgtk_shot_entity.entity['name']
        
        shot_config = TDE4BaseFactory(str(get_shot))
        sgtk_filter_shot = shot_config.sgtk_find_shot()
        return shot_config
    

    def save_new_ver_file() -> str:

        ''' Function parse the dir path of the file.
         
        Collect all files into a list and identify the 
        latest version. once found, the new version sended
        back to SGTK template resolver to parse the path for new version.
        New path been generated with new version and returned
        '''

        # If env is intialised freshly then the scene file name is 3de4.3de
        # the dir path parse only upto publish/work. so 3de4 added manually 
        # to list all the 3de files inside.
        if scene_file.endswith('3de4.3de'):
        
            prj_folder_path = scene_file.split('.3de')[0]
        
        else:
        
            prj_folder_path = os.path.dirname(scene_file)
            
        tde_scene_files_list = os.listdir(prj_folder_path)
        scene_file_collection = []
        for tde_scene_files in tde_scene_files_list:
            scene_file_path = os.path.join(
                prj_folder_path,
                tde_scene_files
                )
            scene_file_collection.append(scene_file_path)
            
        versions = []
        for tde_scene_file in scene_file_collection:
            
            resolved_shot_config =resolve_sgtk_template(tde_scene_file)
            template_path = resolved_shot_config.get_template_path()
            versions.append(template_path.get_fields(tde_scene_file)['version'])
        
        version = max(versions)
        version = version + 1 

        resolved_shot_config =resolve_sgtk_template(scene_file_collection[0])
        sgtk_resolve_shot = resolved_shot_config.sgtk_resolve_path(version)

        return sgtk_resolve_shot,version

    
    def open_scene_file(requester,widget,action):
        #print ("New callback from widget ",widget," received, action: ",action)
        #print ("Put your code here...")
        if widget == 'file_load':
            try: 
                index = tde4.getListWidgetSelectedItems(requester, "file_load")[0] 
                
                if not index==0: 

                    selected_scene_file = tde4.getListWidgetItemLabel(requester, "file_load",index)
                    selected_scene_file_path = os.path.join(
                        scene_file_prj_folder_path,
                        selected_scene_file
                    )

                    # Opening need to version up to a new available version
                    new_scene_file, version = save_new_ver_file()
                    
                    get_action = tde4.postQuestionRequester(
                        "FWX SGTK Info..",
                        f"Open File \n \"{selected_scene_file} to new version \"{version}\"",
                        "Ok", "Cancel"
                        )
                    if get_action == 1:

                        #Set Env Project
                        # Load the selected file 
                        tde4.loadProject(selected_scene_file_path) 

                        # Save the current file to the newly resolved incremented file Name
                        tde4.saveProject(new_scene_file)

                        #Save the file and initialize Env
                        tde4.setProjectPath(new_scene_file)
                        
                        tde4.postQuestionRequester(
                                    "FWX SGTK Info..",
                                    f"SGTK Environment Initialzed.\nProject Environment Setted to \"{new_scene_file}\""
                                    ,"Ok"
                                    )
            except:
                pass
        return


    def _FileOpenUpdate(requester):
        #print ("New update callback received, put your code here...")
        tde4.removeAllListWidgetItems(requester,"file_load")
        index = tde4.insertListWidgetItem(requester, "file_load",'3DE Scene Files',0,"LIST_ITEM_NODE")
        
        tde_scene_list = os.listdir(scene_file_prj_folder_path)
        for i in sorted(tde_scene_list, reverse=True):
            tde4.insertListWidgetItem(requester, "file_load",i,index,"LIST_ITEM_ATOM",index)
        for i in range(1,len(tde_scene_list)+1):
            tde4.setListWidgetItemColor(requester,"file_load",i,1,0.9,0)
        return


    #
    # DO NOT ADD ANY CUSTOM CODE BEYOND THIS POINT!
    #

    try:
        requester	= _FileOpen_requester
    except (ValueError,NameError,TypeError):
        requester = tde4.createCustomRequester()
        tde4.addLabelWidget(requester,"file_open_lbl","SGTK File Open","ALIGN_LABEL_LEFT")
        tde4.setWidgetOffsets(requester,"file_open_lbl",24,0,42,0)
        tde4.setWidgetAttachModes(requester,"file_open_lbl","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE")
        tde4.setWidgetSize(requester,"file_open_lbl",200,20)
        tde4.setWidgetCallbackFunction(requester,"file_open_lbl","open_scene_file")
        tde4.addListWidget(requester,"file_load","file_load",0)
        tde4.setWidgetOffsets(requester,"file_load",16,0,74,0)
        tde4.setWidgetAttachModes(requester,"file_load","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE")
        tde4.setWidgetSize(requester,"file_load",550,500)
        tde4.setWidgetCallbackFunction(requester,"file_load","open_scene_file")
        tde4.setWidgetLinks(requester,"file_open_lbl","","","","")
        tde4.setWidgetLinks(requester,"file_load","","","","")
        _FileOpen_requester = requester

    #
    # DO NOT ADD ANY CUSTOM CODE UP TO THIS POINT!
    #

    if tde4.isCustomRequesterPosted(_FileOpen_requester)=="REQUESTER_UNPOSTED":
        if tde4.getCurrentScriptCallHint()=="CALL_GUI_CONFIG_MENU":
            tde4.postCustomRequesterAndContinue(_FileOpen_requester,"File Open",0,0,"_FileOpenUpdate")
        else:
            tde4.postCustomRequesterAndContinue(_FileOpen_requester,"File Open v1.0",620,600,"_FileOpenUpdate")
    else:	tde4.postQuestionRequester("_FileOpen","Window/Pane is already posted, close manually first!","Ok")

else:
    
    tde4.postQuestionRequester(
                "FWX SGTK Info..",
                f"SGTK Environment is Not Initialized\n\
                Please set using MainWindow's Shotgrid -> Set Env",
                "Ok"
                )
