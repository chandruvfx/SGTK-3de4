#
# 3DE4.script.name:	Open Latest..
#
# 3DE4.script.version:	v1.0
#
# 3DE4.script.gui:	Main Window::Shotgrid
#
# 3DE4.script.comment:	Add comment here.
#
import re
import os

scene_file = tde4.getProjectPath()
versions = []
max_version = 0
file_full_path_dict = {}

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

    if tde_scene_files_list:

        versions = [ int(re.search('\d+', re.search('v\d{3}',version).group(0)).group(0))
                            for version in tde_scene_files_list ]
        # Obtain New verion ot the file
        max_version = max(versions)

        for scene_files, version in zip(tde_scene_files_list, versions):
            full_path = os.path.join(
                scene_file_prj_folder_path, 
                scene_files
            )
            file_full_path_dict[version] = full_path

        # Get tehe maximum version 3de scene file
        latest_scene_file = file_full_path_dict[max_version]

        get_action = tde4.postQuestionRequester(
                            "FWX SGTK Info..",
                            f"Open Recent File\n{latest_scene_file}",
                            "Ok", "Cancel"
                            )
        if get_action == 1:
            tde4.loadProject(latest_scene_file) 
            tde4.setProjectPath(
                        latest_scene_file
                )

            tde4.postQuestionRequester(
                                    "FWX SGTK Info..",
                                    f"SGTK Environment Initialzed.\nProject Environment Setted to \"{latest_scene_file}\""
                                    ,"Ok"
                                    )

    else:

        tde4.postQuestionRequester(
                            "FWX SGTK Info..",
                            f"No Scene File exist!!!",
                            "Ok", "Cancel"
                            )

    