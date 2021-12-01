#
# 3DE4.script.name:	Publish
#
# 3DE4.script.version:	v1.0
#
# 3DE4.script.gui:	Main Window::Shotgrid
#
# 3DE4.script.comment:	Add comment here.
#
from engine_config import TDE4BaseFactory
from export import (
            export_nuke_Lens_Distortion_Node as export_nuke_lde,
            export_mesh as export_mesh_abc,
            export_camera as export_cam_abc
            )

from importlib import reload
import shutil
import sgtk
import os
import re
import engine_config
reload(engine_config)

scene_file = tde4.getProjectPath()
if scene_file is None or \
                not scene_file.startswith('/Shares/T/studio/projects'):

    tde4.postQuestionRequester(
            "FWX SGTK Info..",
            f"SGTK Environment is Not Initialized\n\
            Please set using MainWindow's Shotgrid -> Set Env",
            "Ok"
            )
elif '3de4.3de' in scene_file:
   
    tde4.postQuestionRequester(
            "FWX SGTK Info..",
            f"Publisher Accept only valid Files",
            "Ok"
            )
else:
    __HOME_DIR__ = os.path.expanduser('~')
    scene_cam = tde4.getCurrentCamera()
    get_first_frame = tde4.getCameraFrameOffset(scene_cam)

    scene_file_prj_folder_path = os.path.dirname(scene_file)
    non_shot_config = TDE4BaseFactory(None)
    sgtk_shot_entity = non_shot_config.sgtk_resolve_path_from_context(scene_file_prj_folder_path)
    get_shot = sgtk_shot_entity.entity['name']

    shot_config = TDE4BaseFactory(str(get_shot))
    sg_shot_info = shot_config.sgtk_find_shot()
    get_pub_dict = shot_config.sgtk_find_published_files()



    def make_folders(path):

        ''' Make Folders'''
        
        try:
            os.makedirs(path)
        except:
            pass

        
    def create_ld_node(splited_file_name, naming_convention, 
                    user_name, version_str) -> str:

        ''' Create Ld Node and pass to the master function '''

        nuke_lde_script = f'{splited_file_name}{naming_convention}{user_name}_{version_str}.nk'
        lde_distortion_node_path =  os.path.join( __HOME_DIR__, 
                                                nuke_lde_script )
        tde4.postProgressRequesterAndContinue("Export LD node ...","%s..." %nuke_lde_script,1,"Ok")
        export_nuke_lde.export_LDE_node(lde_distortion_node_path, 
                                        get_first_frame )
        tde4.updateProgressRequester(3,"Writing LD Node ...")
        return lde_distortion_node_path



    def create_alembic_file(widget_label, 
                                splited_file_name, 
                                naming_convention, 
                                user_name, version_str) -> str:

        ''' Create Alembic camera and mesh node
        Pass the path to the master function'''

        alemic_name = f'{splited_file_name}{naming_convention}{user_name}_{version_str}.abc'
        alembic_tmp_path = os.path.join( __HOME_DIR__, 
                                        alemic_name )
        tde4.postProgressRequesterAndContinue("Export Alembic ...","%s..." %alemic_name,1,"Ok")
        
        if widget_label ==  'Geo Alembic':
            
            export_mesh_abc.exportAlembic(alembic_tmp_path)
        if widget_label ==  'Camera Alembic':
            
            export_cam_abc.export_camera_alembic(alembic_tmp_path)
            
        tde4.updateProgressRequester(3,"Writing alembic ...")
        return alembic_tmp_path



    def save_new_ver_file() -> str:

        ''' Function parse the dir path of the file 
        Collect all files into a list and identify the 
        latest version. once found, the new version sended
        back to SGTK template resolver to parse the path for new version.
        New path been generated with new version and returned
        '''
        
        prj_folder_path = os.path.dirname(scene_file)
        tde_scene_files_list = os.listdir(scene_file_prj_folder_path)
        scene_file_collection = []
        for tde_scene_files in tde_scene_files_list:
            scene_file_path = os.path.join(
                prj_folder_path,
                tde_scene_files
                )
            scene_file_collection.append(scene_file_path)
            
        versions = []
        for tde_scene_file in scene_file_collection:
            
            template_path = shot_config.get_template_path()
            versions.append(template_path.get_fields(tde_scene_file)['version'])
        
        version = max(versions)
        version = version + 1 

        sgtk_resolve_shot = shot_config.sgtk_resolve_path(version)

        return sgtk_resolve_shot,version



    def submit_scene_publish() -> None:

        ''' Master Functin to publish current 3de file '''

        # Resolve current 3de pub path
        current_tde_pub_scene_path = shot_config.sgtk_resolve_3de_file_publish_path()
        versions =[]
        version = 0
        
        tde_file_name = os.path.basename(current_tde_pub_scene_path)
        
        extract_version = re.search('v\d{3}', tde_file_name).group(0)
        partial_3de_file_name = tde_file_name.split(extract_version)[0]

        # Check Whether the already publishes exists
        if get_pub_dict != {}:
            # If yes get through iterations. check the Publishing naming 
            # file already exist also .3de extention. if no then v001
            for published_3de_files,_ in get_pub_dict.items():
                if partial_3de_file_name in published_3de_files and \
                            published_3de_files.endswith('.3de'):

                    # Extract 'v001
                    pub_version_str= re.search('v\d{3}', published_3de_files).group(0)
                    # Extract 001 from v. and make it integer
                    pub_version_no = int(re.search('\d{3}', pub_version_str).group(0))
                    versions.append(pub_version_no)

            max_ver = max(versions) if versions else 0
            version = max_ver + 1

            # Resolve the publish path with the new version
            version_up_current_tde_pub_scene_path = shot_config.sgtk_resolve_3de_file_publish_path(version)

            # Get dir path and file name seperately
            tde_pub_path = os.path.dirname(version_up_current_tde_pub_scene_path)
            tde_file_name = os.path.basename(version_up_current_tde_pub_scene_path)

            make_folders(tde_pub_path)
            
            # Create Instace of sgtk for future use
            tk = sgtk.sgtk_from_path(shot_config.get_project_path())
            tk.synchronize_filesystem_structure()
            
            ctx = tk.context_from_path(version_up_current_tde_pub_scene_path)
            
            f = [[ 'entity', 'is', {'type': 'Shot', 'id': sg_shot_info[0]['id']} ]]

            # Get tthe tracking task id to use in publish register
            track_task = dict
            task_schema = tk.shotgun.find('Task', f, ['content'])
            
            for task in task_schema:
                
                if task['content'] == 'Tracking':
                    
                    track_task = task
                    
            if track_task == '':
                tde4.postQuestionRequester(
                        "FWX SGTK Warning..",
                        f"Tracking Task Not exist in SG!!",
                        "Ok"
                        )
                    
            else:
                tde4.postProgressRequesterAndContinue("Publishing Process ...","%s" %tde_file_name,1,"Ok")
                sgtk.util.register_publish(tk=tk,
                                        context=ctx,
                                        path=version_up_current_tde_pub_scene_path,
                                        task=track_task,
                                        name= tde_file_name,
                                        version_number = version,
                                        published_file_type = '3de File'
                                        )

                shutil.copyfile(scene_file, version_up_current_tde_pub_scene_path)
                tde4.updateProgressRequester(3,"SGTK 3de Publishing ...")

                # ONce published the file is  is saved to new version
                new_scene_file, new_version = save_new_ver_file()
                tde4.saveProject(new_scene_file)
                
                #Save the file and initialize Env
                tde4.setProjectPath(new_scene_file)
                
                tde4.postQuestionRequester(
                            "FWX SGTK Info..",
                        f"Current Scene File Saved as {new_version}\n\
                        SGTK Environment Initialzed.\nProject Environment Setted to \"{new_scene_file}\""
                            ,"Ok"
                            )

        

    def submit_publish( widget_label, 
                    set_naming, 
                    node_name) -> None:

        '''Master Function

        Function Generate SG publish path and made entry into 
        the respective shot. And transfer the data to the SG
        Based folder structure'''
        
        node_pub_path =''
        mode = 0
        ud_node_path =''
        
        if widget_label == 'UD Node':

            node_pub_path = shot_config.sgtk_resolve_publish_path_nk()
            mode = 1

        if widget_label == 'Geo Alembic':
            
            node_pub_path = shot_config.sgtk_resolve_publish_path_alembic()
            mode = 2 

        if widget_label == 'Camera Alembic':
            
            node_pub_path = shot_config.sgtk_resolve_publish_path_alembic()
            mode = 3
        

        #insert Naming Convention and Usen Naming
        # Get File name 
        get_file_name_from_path = os.path.basename(node_pub_path)

        # get dir path of the template resolved path
        get_dir_file_path = os.path.dirname(node_pub_path)

        # Extract strng 'v001' from the template path
        version_str= re.search('v\d{3}', get_file_name_from_path).group(0)

        # path_splitted_with_version
        splited_file_name = get_file_name_from_path.split(version_str)[0]

        naming_convention = set_naming
        user_entered_name = f"_{node_name}"

        # GEt only pub_dev7_MMtrack_Mala_ to check whether
        # this naming file already published or not
        first_part_file_name = splited_file_name + naming_convention + user_entered_name + '_'
        
        versions =[] 
        version = 0
        
        #Get Ld Node
        # Create Ud node and generate and get the path
        if mode == 1:
            ud_node_path = create_ld_node( 
                                        splited_file_name, 
                                        naming_convention, 
                                        user_entered_name, 
                                        version_str )
        if mode == 2:

            ud_node_path = create_alembic_file( 
                                        widget_label,
                                        splited_file_name, 
                                        naming_convention, 
                                        user_entered_name, 
                                        version_str )
        if mode == 3:

            ud_node_path = create_alembic_file( 
                                        widget_label,
                                        splited_file_name, 
                                        naming_convention, 
                                        user_entered_name, 
                                        version_str )

        # Determine Extention
        ext = '.abc' if mode == 2 else '.abc' if mode == 3 else '.nk'
        publish_type = 'Alembic Cache' if mode == 2 or mode == 3 else 'Nuke Script'
        
        # Create Instace of sgtk for future use
        tk = sgtk.sgtk_from_path(shot_config.get_project_path())
        tk.synchronize_filesystem_structure()
        
        # Check Whether the already publishes exists
        if get_pub_dict != {}:
            # If yes get through iterations. check the Publishing naming 
            # file already exist. if no then v001
            for published_nk_scripts,_ in get_pub_dict.items():
                if first_part_file_name in published_nk_scripts:

                    # Extract 'v001
                    pub_version_str= re.search('v\d{3}', published_nk_scripts).group(0)
                    # Extract 001 from v. and make it integer
                    pub_version_no = int(re.search('\d{3}', pub_version_str).group(0))
                    versions.append(pub_version_no)

            max_ver = max(versions) if versions else 0
            version = max_ver + 1
            
            #Resolve publish path with new version no
            if mode == 1:
                node_pub_path = shot_config.sgtk_resolve_publish_path_nk(version)
                
            elif mode == 2 or mode == 3:
                node_pub_path = shot_config.sgtk_resolve_publish_path_alembic(version)
                
                
            # Get dir Name
            get_file_name_from_path = os.path.basename(node_pub_path)

            # get dir path of the template resolved path
            get_dir_file_path = os.path.dirname(node_pub_path)
            
            final_base_name = first_part_file_name + 'v%03d' %version
            f = [[ 'entity', 'is', {'type': 'Shot', 'id': sg_shot_info[0]['id']} ]]

            track_task = dict
            task_schema = tk.shotgun.find('Task', f, ['content'])
            for task in task_schema:
                if task['content'] == 'Tracking':
                    track_task = task
            

            make_folders( os.path.join( 
                                    get_dir_file_path, 
                                    final_base_name ) )
            
            # Final Publish first version publish path
            first_version_pub_path = get_dir_file_path + \
                                    '/' + final_base_name + \
                                    '/' + final_base_name + ext
            ctx = tk.context_from_path(first_version_pub_path)
            
            tde4.postProgressRequesterAndContinue("Publishing Process ...","%s..." %final_base_name,1,"Ok")
            sgtk.util.register_publish(tk=tk,
                                    context=ctx,
                                    path=first_version_pub_path,
                                    task=track_task,
                                    name= final_base_name + ext,
                                    version_number = version,
                                    published_file_type = publish_type
                                    )
            shutil.copyfile(ud_node_path, first_version_pub_path)
            tde4.updateProgressRequester(3,"SGTK Publishing ...")
            os.system(f'rm -rvf {ud_node_path}')
            
        else:

            tde4.postQuestionRequester(
                            "FWX SGTK Warning..",
                            f"No publishes were Made for this Shot in Shotgrid",
                            "Ok"
                            )

        
    def publish(requester,widget,action):

        # Set Node options visibility
        widgets = {'ud_node_opt' : 'uc_name',  
                'cam_node_opt': 'cam_name', 
                'geo_node_opt': 'geo_name'}
        
        set_naming = ''
        custom_name_dict = {}
        get_user_text = []
        ud_node_name = ''
        abc_node_name = ''

        # DEtermine when the text fields get activated. if respective
        # Options enabled then the parellel text field enaled 
        for option_widget, text_field_widgets in widgets.items():
            
            if int(tde4.getWidgetValue(requester, option_widget )) == 1:
                
                tde4.setWidgetSensitiveFlag(requester, text_field_widgets, 1)
                
                # Save Widget label and user entered text in the dictionary
                custom_name_dict[tde4.getWidgetLabel(requester, option_widget)] \
                                = tde4.getWidgetValue(requester, text_field_widgets)
                
            else:
                tde4.setWidgetSensitiveFlag(requester, text_field_widgets, 0)
                
        # add the all user enter custom names in to list
        for _, user_txt in custom_name_dict.items():
            get_user_text.append(user_txt)

        # COunt how many times same name appear and append in list
        # If duplicate found then will raise error
        get_duplicate_tx  = [ x for x in get_user_text 
                            if get_user_text.count(x) > 1]

        # Get index value of the naming convention widget
        get_naming_selection_index = tde4.getWidgetValue(requester, "naming_convention")

        # If Ud node is switched onthen determine naming convention
        # Same to alembic options 
        if int(tde4.getWidgetValue(requester, "ud_node_opt" )) == 1:
            if int(get_naming_selection_index) == 2:
                ud_node_name = 'MMtrack'
            elif int(get_naming_selection_index) == 3:
                ud_node_name = 'RAtrack'
        
        if int(tde4.getWidgetValue(requester, "cam_node_opt" )) == 1 or \
                    int(tde4.getWidgetValue(requester, "geo_node_opt" )) == 1:
            if int(get_naming_selection_index) == 2:
                abc_node_name = 'MMtrackalembic'
            elif int(get_naming_selection_index) == 3:
                abc_node_name = 'RAtrackalembic'

                
        if widget == 'launch_publish':

            # Check Naming convention option is selected or Not
            if int(get_naming_selection_index) == 1:

                tde4.postQuestionRequester(
                        "FWX SGTK Warning..",
                        f"Select Naming Convention",
                        "Ok"
                        )
                
            else:
                # If any duplicates are there then Notify
                if get_duplicate_tx:

                    tde4.postQuestionRequester(
                            "FWX SGTK Warning..",
                            f"Identical names are specified or no named specified",
                            "Ok"
                            )
                else:
                    # Check camera has img loaded. Otherwise alembic
                    # exxport through error
                    cam = tde4.getCurrentCamera()
                    if tde4.getCameraPath(cam) != '':
                        
                        for widget_lbl, user_text in custom_name_dict.items():
                            if user_text is not None: 
                                if widget_lbl == 'UD Node':
                                    submit_publish(
                                                widget_lbl,
                                                ud_node_name, 
                                                user_text
                                                )
                                    
                                for _ in [ 'Camera Alembic', 'Geo Alembic']:
                                    if widget_lbl == _:
                                        submit_publish(  
                                                widget_lbl,
                                                abc_node_name, 
                                                user_text
                                        )
                        # Check all the options are off then trigger gui
                        # else always publish 3de files with the other nodes
                        
                        if int(tde4.getWidgetValue(requester, "cam_node_opt" )) == 0 and \
                            int(tde4.getWidgetValue(requester, "geo_node_opt" )) ==  0 and \
                            int(tde4.getWidgetValue(requester, "ud_node_opt" )) == 0:
                            
                            
                            action = tde4.postQuestionRequester(
                                    "FWX SGTK Info..",
                                    f"Publish only Current Scene File ???.",
                                    "Ok", "Cancel"
                                    )      
                            if action == 1:     
                                submit_scene_publish()
                        else:
                            if user_text is not None:
                                submit_scene_publish()
    
                        tde4.unpostCustomRequester(requester)
                      
                    else: 
                        tde4.postQuestionRequester(
                                    "FWX SGTK Warning..",
                                    f"Setup the File to prcoceed \n\
                                    Load camera img sequence and meshes, etc....",
                                    "Ok", "Cancel"
                                    ) 

                                            
        return


    def _PublishUpdate(requester):
        #print ("New update callback received, put your code here...")
        
        return


    #
    # DO NOT ADD ANY CUSTOM CODE BEYOND THIS POINT!
    #

    try:
        requester	= _Publish_requester
    except (ValueError,NameError,TypeError):
        requester = tde4.createCustomRequester()
        tde4.addLabelWidget(requester,"publish_lbl","FWX SGTK Publisher","ALIGN_LABEL_LEFT")
        tde4.setWidgetOffsets(requester,"publish_lbl",161,120,15,0)
        tde4.setWidgetAttachModes(requester,"publish_lbl","ATTACH_WINDOW","ATTACH_WINDOW","ATTACH_WINDOW","ATTACH_NONE")
        tde4.setWidgetSize(requester,"publish_lbl",200,20)
        tde4.setWidgetCallbackFunction(requester,"publish_lbl","publish")
        tde4.setWidgetFGColor(requester,"publish_lbl",1.000000,0.750000,0.300000)
        tde4.addToggleWidget(requester,"ud_node_opt","UD Node",0)
        tde4.setWidgetOffsets(requester,"ud_node_opt",127,0,52,0)
        tde4.setWidgetAttachModes(requester,"ud_node_opt","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE")
        tde4.setWidgetSize(requester,"ud_node_opt",20,20)
        tde4.setWidgetCallbackFunction(requester,"ud_node_opt","publish")
        tde4.addTextFieldWidget(requester,"uc_name","Name","")
        tde4.setWidgetOffsets(requester,"uc_name",206,341,49,0)
        tde4.setWidgetAttachModes(requester,"uc_name","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE")
        tde4.setWidgetSize(requester,"uc_name",250,20)
        tde4.setWidgetCallbackFunction(requester,"uc_name","publish")
        tde4.setWidgetSensitiveFlag(requester,"uc_name",0)
        tde4.addToggleWidget(requester,"cam_node_opt","Camera Alembic",0)
        tde4.setWidgetOffsets(requester,"cam_node_opt",127,0,106,0)
        tde4.setWidgetAttachModes(requester,"cam_node_opt","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE")
        tde4.setWidgetSize(requester,"cam_node_opt",20,20)
        tde4.setWidgetCallbackFunction(requester,"cam_node_opt","publish")
        tde4.addSeparatorWidget(requester,"sep1")
        tde4.setWidgetOffsets(requester,"sep1",19,0,78,0)
        tde4.setWidgetAttachModes(requester,"sep1","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE")
        tde4.setWidgetSize(requester,"sep1",480,20)
        tde4.setWidgetCallbackFunction(requester,"sep1","publish")
        tde4.addTextFieldWidget(requester,"cam_name","Name","")
        tde4.setWidgetOffsets(requester,"cam_name",207,0,111,0)
        tde4.setWidgetAttachModes(requester,"cam_name","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE")
        tde4.setWidgetSize(requester,"cam_name",250,20)
        tde4.setWidgetCallbackFunction(requester,"cam_name","publish")
        tde4.setWidgetSensitiveFlag(requester,"cam_name",0)
        tde4.addSeparatorWidget(requester,"sep2")
        tde4.setWidgetOffsets(requester,"sep2",17,0,135,0)
        tde4.setWidgetAttachModes(requester,"sep2","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE")
        tde4.setWidgetSize(requester,"sep2",480,20)
        tde4.setWidgetCallbackFunction(requester,"sep2","publish")
        tde4.addToggleWidget(requester,"geo_node_opt","Geo Alembic",0)
        tde4.setWidgetOffsets(requester,"geo_node_opt",125,0,164,0)
        tde4.setWidgetAttachModes(requester,"geo_node_opt","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE")
        tde4.setWidgetSize(requester,"geo_node_opt",20,20)
        tde4.setWidgetCallbackFunction(requester,"geo_node_opt","publish")
        tde4.addTextFieldWidget(requester,"geo_name","Name","")
        tde4.setWidgetOffsets(requester,"geo_name",209,0,165,0)
        tde4.setWidgetAttachModes(requester,"geo_name","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE")
        tde4.setWidgetSize(requester,"geo_name",250,20)
        tde4.setWidgetCallbackFunction(requester,"geo_name","publish")
        tde4.setWidgetSensitiveFlag(requester,"geo_name",0)
        tde4.addSeparatorWidget(requester,"sep3")
        tde4.setWidgetOffsets(requester,"sep3",11,0,194,0)
        tde4.setWidgetAttachModes(requester,"sep3","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE")
        tde4.setWidgetSize(requester,"sep3",480,20)
        tde4.setWidgetCallbackFunction(requester,"sep3","publish")
        tde4.addButtonWidget(requester,"launch_publish","Publish")
        tde4.setWidgetOffsets(requester,"launch_publish",224,0,272,0)
        tde4.setWidgetAttachModes(requester,"launch_publish","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE")
        tde4.setWidgetSize(requester,"launch_publish",100,40)
        tde4.setWidgetCallbackFunction(requester,"launch_publish","publish")
        tde4.addOptionMenuWidget(requester,"naming_convention","Select Publish naming convention","Click Here ..","MMtrack","RAtrack")
        tde4.setWidgetOffsets(requester,"naming_convention",277,0,221,0)
        tde4.setWidgetAttachModes(requester,"naming_convention","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE")
        tde4.setWidgetSize(requester,"naming_convention",150,20)
        tde4.setWidgetCallbackFunction(requester,"naming_convention","publish")
        tde4.setWidgetLinks(requester,"publish_lbl","","","","")
        tde4.setWidgetLinks(requester,"ud_node_opt","","","","")
        tde4.setWidgetLinks(requester,"uc_name","","","","")
        tde4.setWidgetLinks(requester,"cam_node_opt","","","","")
        tde4.setWidgetLinks(requester,"sep1","","","","")
        tde4.setWidgetLinks(requester,"cam_name","","","","")
        tde4.setWidgetLinks(requester,"sep2","","","","")
        tde4.setWidgetLinks(requester,"geo_node_opt","","","","")
        tde4.setWidgetLinks(requester,"geo_name","","","","")
        tde4.setWidgetLinks(requester,"sep3","","","","")
        tde4.setWidgetLinks(requester,"launch_publish","","","","")
        tde4.setWidgetLinks(requester,"naming_convention","","","","")
        _Publish_requester = requester

    #
    # DO NOT ADD ANY CUSTOM CODE UP TO THIS POINT!
    #

    if tde4.isCustomRequesterPosted(_Publish_requester)=="REQUESTER_UNPOSTED":
        if tde4.getCurrentScriptCallHint()=="CALL_GUI_CONFIG_MENU":
            tde4.postCustomRequesterAndContinue(_Publish_requester,"Publish",0,0,"_PublishUpdate")
        else:
            tde4.postCustomRequesterAndContinue(_Publish_requester,"Publish v1.0",500,350,"_PublishUpdate")
    else:	tde4.postQuestionRequester("_Publish","Window/Pane is already posted, close manually first!","Ok")


