#
# 3DE4.script.name:	Load Alembic..
#
# 3DE4.script.version:	v1.0
#
# 3DE4.script.gui:	Main Window::Shotgrid::Load
#
# 3DE4.script.comment:	Add comment here.


#
scene_file = tde4.getProjectPath()
if scene_file is not None and scene_file.startswith('/Shares/T/studio/projects'):
    
    import os
    
    try:
        exec(open('/tmp/3de_alembic_import.py').read())

        os.system('rm -rvf /tmp/3de_alembic_import.py')

    except FileNotFoundError:
        tde4.postQuestionRequester(
                "FWX SGTK Warning..",
                f"Select published \"Alembics\" from\n\
                MainWindow's Shotgrid -> File Loader",
                "Ok"
                )

else:
    
    tde4.postQuestionRequester(
                "FWX SGTK Info..",
                f"SGTK Environment is Not Initialized\n\
                Please set using MainWindow's Shotgrid -> Set Env",
                "Ok"
                )
