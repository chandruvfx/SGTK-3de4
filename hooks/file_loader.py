#
# 3DE4.script.name:	File Loader..
#
# 3DE4.script.version:	v1.0
#
# 3DE4.script.gui:	Main Window::Shotgrid
#
# 3DE4.script.comment:	Add comment here.
#
from engine_config import TDE4BaseFactory
from importlib import import_module, reload
import os
import sys
import engine_config
import re
reload(engine_config)

current_file_path = os.path.dirname(
            os.path.abspath(__file__)
            )
abc_alembic_import_py_file = os.path.join( 
                                          current_file_path,
                                          'import', 
                                          'sgtk_import_abc.py' 
                                        )
abc_destination_path = '/tmp/3de_alembic_import.py'


scene_file = tde4.getProjectPath()

if scene_file is not None and scene_file.startswith('/Shares/T/studio/projects'):
    
    if '3de4' not in os.path.dirname(scene_file):
        scene_file_prj_folder_path =os.path.join(
                os.path.dirname(scene_file), '3de4')
    else:
        scene_file_prj_folder_path = os.path.dirname(scene_file)


    def set_camera_image_path(publish_path,
                              publish_name,
                              extention, cam):

        img_list = []
        fram_num_seq = []
        start_frame = end_frame = 0
        
        dirname = os.path.dirname(publish_path)
        get_only_partial_dir_path = dirname.split('%')[0]
        #extract 6 from %06d 
        get_frame_seq_count_num = re.search('\d+', publish_path.split('%')[-1]).group(0)

        get_only_name_path = publish_name.split('%')[0]
        
        for exr_files in os.listdir(dirname):

            if exr_files.endswith(extention):
                img_list.append(
                                os.path.join(
                                dirname, 
                                exr_files.split(get_only_partial_dir_path)[0])
                                )
        for exr_files in img_list:
            extract_frame_no_withext = exr_files.split(get_only_name_path)[-1]
            fram_num_seq.append(extract_frame_no_withext.split(extention))

        start_frame = min(fram_num_seq)[0]
        end_frame = max(fram_num_seq)[0]

        action = tde4.postQuestionRequester(
                "FWX SGTK Info..",
                f"Proceed with setting new image plane\n\
                \"{publish_name}\" ",
                "Ok", "Cancel"
                )
        if action == 1:
            tde4.setCameraSequenceAttr(cam, int(start_frame), int(end_frame), 1)
            hash_palceholder = '#' * int(get_frame_seq_count_num)
            img_path =  publish_path.split('%')[0] + \
                        hash_palceholder + \
                        extention
            tde4.setCameraPath(cam, img_path)
        
        
    def file_handler(destination_path, publish_path):

        with open(destination_path, 'r+') as read_file:
            readed_file = read_file.read()
            path_assignment = readed_file.replace('{path}', publish_path)

        with open(destination_path, 'w') as write_file:
            write_file.write(path_assignment)


    def import_obj(publish_name, publish_path):

        action = tde4.postQuestionRequester(
                "FWX SGTK Info..",
                f"Proceed with Importing Obj\n\
                \"{publish_name}\" ",
                "Ok", "Cancel"
                )
        if action == 1:
            get_current_grp = tde4.getPGroupList(0)[0]
            get_model =  tde4.create3DModel(get_current_grp)
            tde4.set3DModelName(get_current_grp,
                                get_model,
                                publish_name)
            tde4.importOBJ3DModel(
                        get_current_grp,
                        get_model,
                        publish_path    
            )

        
    def resolve_sgtk_template(tde_file_path):

        non_shot_config = TDE4BaseFactory(None)

        sgtk_shot_entity = non_shot_config.sgtk_resolve_path_from_context(tde_file_path)
        get_shot = sgtk_shot_entity.entity['name']
        
        shot_config = TDE4BaseFactory(str(get_shot))
        shot_config.sgtk_find_shot()
        return shot_config.sgtk_find_published_files()

        
    def file_loader(requester,widget,action):
        if widget == 'sg_ele_list':
            cam = tde4.getCurrentCamera()
            try:
                index = tde4.getListWidgetSelectedItems(requester, "sg_ele_list")[0]

                if not index==0: 

                    selected_element_file = tde4.getListWidgetItemLabel(requester, "sg_ele_list",index)
                    resolved_publish_dict = resolve_sgtk_template(scene_file)
                    
                    
                    for publish_name, publish_path in resolved_publish_dict.items():
                        
                        if selected_element_file == publish_name:
                            if publish_path.endswith('.abc'):

                                action = tde4.postQuestionRequester(
                                        "FWX SGTK Info..",
                                        f"Set import for \"{publish_name}\" ?? ",
                                        "Ok", "Cancel"
                                        )
                                if action == 1:
                                    os.system('cp -rf %s %s' %( abc_alembic_import_py_file, abc_destination_path ))
                                    file_handler(abc_destination_path, publish_path)
                                

                            elif publish_path.endswith('.obj'):
                                
                                import_obj(publish_name, publish_path)
                                pass

                            elif publish_path.endswith('.exr'):
                                
                                set_camera_image_path( publish_path, 
                                                       publish_name,
                                                       '.exr', cam )

                            elif publish_path.endswith('.jpg'):
                                
                                set_camera_image_path( publish_path, 
                                                       publish_name,
                                                       '.jpg', cam )

                            elif publish_path.endswith('.jpeg'):
                                
                                set_camera_image_path( publish_path, 
                                                       publish_name,
                                                       '.jpeg', cam )

 
            except: pass 
        return


    def _FileLoaderUpdate(requester):

        tde4.removeAllListWidgetItems(requester,"sg_ele_list")
        resolved_publish_dict = resolve_sgtk_template(scene_file)
        abc_index = tde4.insertListWidgetItem(requester, "sg_ele_list",'Alembic',0,"LIST_ITEM_NODE")
        
        for publish_name, _ in resolved_publish_dict.items():
            if publish_name.endswith('.abc'):
                tde4.insertListWidgetItem( requester, "sg_ele_list",
                                        publish_name, abc_index,
                                        "LIST_ITEM_ATOM",abc_index )
                
        obj_index = tde4.insertListWidgetItem(requester, "sg_ele_list",'Objs',1,"LIST_ITEM_NODE") 
        for publish_name, _ in resolved_publish_dict.items():
            if publish_name.endswith('.obj'):
                tde4.insertListWidgetItem( requester, 
                                        "sg_ele_list", publish_name, 
                                        obj_index, "LIST_ITEM_ATOM", obj_index ) 

        exr_index = tde4.insertListWidgetItem(requester, "sg_ele_list",'Exrs',2,"LIST_ITEM_NODE")
        for publish_name, _ in resolved_publish_dict.items():
            if publish_name.endswith('.exr'):
                tde4.insertListWidgetItem( requester, "sg_ele_list",
                                        publish_name, exr_index,
                                        "LIST_ITEM_ATOM", exr_index ) 

        jpg_index = tde4.insertListWidgetItem(requester, "sg_ele_list",'Jpegs',2,"LIST_ITEM_NODE")
        for publish_name, _ in resolved_publish_dict.items():
            if publish_name.endswith('.jpg') or \
                        publish_name.endswith('.jpeg') or \
                        publish_name.endswith('.JPG') or \
                        publish_name.endswith('.JPEG'):
                tde4.insertListWidgetItem( requester, "sg_ele_list",
                                        publish_name, jpg_index,
                                        "LIST_ITEM_ATOM", jpg_index )
        return


    #
    # DO NOT ADD ANY CUSTOM CODE BEYOND THIS POINT!
    #

    try:
        requester	= _FileLoader_requester
    except (ValueError,NameError,TypeError):
        requester = tde4.createCustomRequester()
        tde4.addLabelWidget(requester,"flile_loader_lbl","FWX Sgtk File Loader","ALIGN_LABEL_LEFT")
        tde4.setWidgetOffsets(requester,"flile_loader_lbl",289,0,6,0)
        tde4.setWidgetAttachModes(requester,"flile_loader_lbl","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE")
        tde4.setWidgetSize(requester,"flile_loader_lbl",200,20)
        tde4.setWidgetCallbackFunction(requester,"flile_loader_lbl","file_loader")
        tde4.addListWidget(requester,"sg_ele_list","SG_element_list",0)
        tde4.setWidgetOffsets(requester,"sg_ele_list",0,0,97,0)
        tde4.setWidgetAttachModes(requester,"sg_ele_list","ATTACH_WINDOW","ATTACH_WINDOW","ATTACH_WINDOW","ATTACH_WINDOW")
        tde4.setWidgetSize(requester,"sg_ele_list",500,500)
        tde4.setWidgetCallbackFunction(requester,"sg_ele_list","file_loader")
        tde4.addLabelWidget(requester,"note_lbl","Note: Steps To import Alembic Files","ALIGN_LABEL_LEFT")
        tde4.setWidgetOffsets(requester,"note_lbl",11,0,30,0)
        tde4.setWidgetAttachModes(requester,"note_lbl","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE")
        tde4.setWidgetSize(requester,"note_lbl",600,20)
        tde4.setWidgetCallbackFunction(requester,"note_lbl","file_loader")
        tde4.addLabelWidget(requester,"note_lbl1","1. Select \"Alembic File\" you want to import. ","ALIGN_LABEL_LEFT")
        tde4.setWidgetOffsets(requester,"note_lbl1",14,0,50,0)
        tde4.setWidgetAttachModes(requester,"note_lbl1","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE")
        tde4.setWidgetSize(requester,"note_lbl1",600,20)
        tde4.setWidgetCallbackFunction(requester,"note_lbl1","file_loader")
        tde4.setWidgetFGColor(requester,"note_lbl1",1.000000,0.870000,0.000000)
        tde4.addLabelWidget(requester,"note_lbl2","2. Select Shotgrid -> Load -> Load Alembic from Main Window","ALIGN_LABEL_LEFT")
        tde4.setWidgetOffsets(requester,"note_lbl2",16,0,72,0)
        tde4.setWidgetAttachModes(requester,"note_lbl2","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE")
        tde4.setWidgetSize(requester,"note_lbl2",600,20)
        tde4.setWidgetFGColor(requester,"note_lbl2",1.000000,0.870000,0.000000)
        tde4.setWidgetLinks(requester,"flile_loader_lbl","","","","")
        tde4.setWidgetLinks(requester,"sg_ele_list","","","","")
        tde4.setWidgetLinks(requester,"note_lbl","","","","")
        tde4.setWidgetLinks(requester,"note_lbl1","","","","")
        tde4.setWidgetLinks(requester,"note_lbl2","","","","")
        _FileLoader_requester = requester

    #
    # DO NOT ADD ANY CUSTOM CODE UP TO THIS POINT!
    #

    if tde4.isCustomRequesterPosted(_FileLoader_requester)=="REQUESTER_UNPOSTED":
        if tde4.getCurrentScriptCallHint()=="CALL_GUI_CONFIG_MENU":
            tde4.postCustomRequesterAndContinue(_FileLoader_requester,"File Loader..",0,0,"_FileLoaderUpdate")
        else:
            tde4.postCustomRequesterAndContinue(_FileLoader_requester,"File Loader.. v1.0",800,600,"_FileLoaderUpdate")
    else:	tde4.postQuestionRequester("_FileLoader","Window/Pane is already posted, close manually first!","Ok")

else:

    tde4.postQuestionRequester(
                "FWX SGTK Info..",
                f"SGTK Environment is Not Initialized\n\
                Please set using MainWindow's Shotgrid -> Set Env",
                "Ok"
                )
