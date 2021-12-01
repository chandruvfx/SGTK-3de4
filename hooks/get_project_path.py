#
# 3DE4.script.name:	Env Info ..
#
# 3DE4.script.version:	v1.0
#
# 3DE4.script.gui:	Main Window::Shotgrid
#
# 3DE4.script.comment:	Add comment here.
#

scene_file = tde4.getProjectPath()

tde4.postQuestionRequester(
                "FWX SGTK Info..",
                f"Shot Environment Setted to\n\
                {scene_file}",
                "Ok"
                )