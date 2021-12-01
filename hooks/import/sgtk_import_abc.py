#
# 3DE4.script.name:	Import Alembic test..
#
# 3DE4.script.version:	v1.4
#
# 3DE4.script.gui:	Main Window::test::import
#
# 3DE4.script.comment:	Open an Alembic file and interactively import selected elements (cameras, 3D models, point groups, points, etc.).
#

import imath
import alembic
import sys
import tde4
import os
from vl_sdv import *

def abcImportButtonCB(req,widget,action):
    global _abc_import_obj_list
    
    pg	= tde4.getCurrentPGroup()
    c0	= tde4.getCurrentCamera()
    pgl	= tde4.getPGroupList(0)
    for campg in pgl:
        if tde4.getPGroupType(campg)=="CAMERA": break
    
    if widget=="refresh":
        tde4.setWidgetValue(req,"abc_file", '{path}')
        
        filename		= tde4.getWidgetValue(req,"abc_file")
        tde4.postProgressRequesterAndContinue("Import Alembic...","Importing Alembic File...",2,"Ok")
        
        tde4.updateProgressRequester(1,"Importing Alembic File...")
        _abcImportUpdateList(req,filename)
        tde4.updateProgressRequester(2,"Importing Alembic File...")
        tde4.unpostProgressRequester()
        return
    
    if widget=="expand_all":
        n	= tde4.getListWidgetNoItems(req,"list")
        for i in range(n): tde4.setListWidgetItemCollapsedFlag(req,"list",i,0)
        return
    
    if widget=="select_all":
        n	= tde4.getListWidgetNoItems(req,"list")
        for i in range(n): tde4.setListWidgetItemSelectionFlag(req,"list",i,1)
        return
    
    if widget=="import_objects" or (widget=="list" and action==1):
        kWrapEx		= alembic.Abc.WrapExistingFlag.kWrapExisting
        replace_points	= tde4.getWidgetValue(req,"replace_points")
        apply_xforms	= tde4.getWidgetValue(req,"apply_xforms")
        new_camera	= tde4.getWidgetValue(req,"add_new_camera")
        new_pgroup	= tde4.getWidgetValue(req,"add_new_pgroup")
        import_uvs	= tde4.getWidgetValue(req,"import_uvs")
        import_mocap	= tde4.getWidgetValue(req,"import_as_mocap")
        l	 	= tde4.getListWidgetSelectedItems(req,"list")
        for i in l:
            item	= _abc_import_obj_list[i]
            
            #
            # import a point...
            if item[1]=="Locator":
                pg0	= tde4.findPGroupByName(_abcImportFindParentPGroupName(req,i))
                if pg0==None: pg0 = pg
                p	= tde4.findPointByName(pg0,item[0].getName())
                if p==None: p = tde4.createPoint(pg0)
                elif replace_points==0: p = None
                if p!=None:
                    tde4.setPointName(pg0,p,item[0].getName())
                    xschema	= alembic.AbcGeom.IXform(item[0],kWrapEx).getSchema()
                    n	= xschema.getNumSamples()
                    
                    # mocap...
                    if n>1 and tde4.getPGroupType(pg0)=="MOCAP":
                        n0	= tde4.getCameraNoFrames(c0)
                        if n>n0: n = n0
                        for f in range(n):
                            x = xschema.getValue(f).getMatrix()
                            if apply_xforms==1: x = _abcImportAccumulateXFormRek(item[0].getParent(),x)
                            tde4.setPointMoCapSurveyPosition3D(pg0,p,c0,f+1,[x[3][0],x[3][1],x[3][2]])
                    else:
                        if apply_xforms==1: x = _abcImportAccumulateXFormRek(item[0],imath.M44d())
                        else: x = xschema.getValue().getMatrix()
                        tde4.setPointSurveyPosition3D(pg0,p,[x[3][0],x[3][1],x[3][2]])
                    tde4.setPointSurveyMode(pg0,p,"SURVEY_EXACT")
                    
                    # import optional 2d tracking data...
                    kid	= item[0].children[0]
                    propx	= _abcImportFindPropRek(kid.getProperties(),"3DE4.2d_tracking.x")
                    if propx!=None:
                        propy	= _abcImportFindPropRek(kid.getProperties(),"3DE4.2d_tracking.y")
                        curve	= []
                        n	= propx.getNumSamples()
                        n0	= tde4.getCameraNoFrames(c0)
                        if n>n0: n = n0
                        for f in range(n):
                            curve.append([propx.getValue(f),propy.getValue(f)])
                        tde4.setPointPosition2DBlock(pg0,p,c0,1,curve)
            
            
            #
            # import a camera...
            if item[1]=="Camera":
                if new_camera==1:
                    if item[2]>1: c = tde4.createCamera("SEQUENCE")
                    else: c = tde4.createCamera("REF_FRAME")
                    lens	= tde4.createLens()
                    tde4.setCameraLens(c,lens)
                else:	c	= c0
                if c0==None:
                    tde4.setCurrentCamera(c)
                    c0	= c
                cam	= alembic.AbcGeom.ICamera(item[0],kWrapEx).getSchema()
                n	= cam.getNumSamples()
                lens	= tde4.getCameraLens(c)
                s	= cam.getValue(0)
                tde4.setCameraName(c,item[0].getName())
                tde4.setCameraFocusMode(c,"FOCUS_USE_FROM_LENS")
                tde4.setCameraFocalLengthMode(c,"FOCAL_USE_FROM_LENS")
                fbw	= s.getHorizontalAperture()
                fbh	= s.getVerticalAperture()
                paspect	= s.getLensSqueezeRatio()
                tde4.setLensFBackWidth(lens,fbw)
                tde4.setLensFBackHeight(lens,fbh)
                tde4.setLensPixelAspect(lens,paspect)
                tde4.setLensLensCenterX(lens,s.getHorizontalFilmOffset())
                tde4.setLensLensCenterY(lens,s.getVerticalFilmOffset())
                tde4.setLensFocalLength(lens,s.getFocalLength()/10.0)
                tde4.setLensFocus(lens,s.getFocusDistance())
                tde4.setCameraPath(c,"/home/user/proxy.####.jpg")
                tde4.setCameraSequenceAttr(c,1,n,1)
                tde4.setCameraImageWidth(c,2048)
                tde4.setCameraImageHeight(c,int(2048.0/(fbw*paspect/fbh)))
                
                tde4.setCameraFocusMode(c,"FOCUS_DYNAMIC")
                tde4.setCameraFocalLengthMode(c,"FOCAL_DYNAMIC")
                zooming		= 0
                focuspull	= 0
                for f in range(0,n):
                    s	= cam.getValue(f)
                    focal	= s.getFocalLength()/10.0
                    focus	= s.getFocusDistance()
                    if f>0 and focal0!=focal: zooming = 1
                    if f>0 and focus0!=focus: focuspull = 1
                    tde4.setCameraFocalLength(c,f+1,focal)
                    tde4.setCameraFocus(c,f+1,focus)
                    focus0	= focus
                    focal0	= focal
                if zooming==0: tde4.setCameraFocalLengthMode(c,"FOCAL_USE_FROM_LENS")
                if focuspull==0: tde4.setCameraFocusMode(c,"FOCUS_USE_FROM_LENS")
                    
                xf	= alembic.AbcGeom.IXform(item[0].getParent(),kWrapEx).getSchema()
                n	= xf.getNumSamples()
                for f in range(0,n):
                    s	= xf.getValue(f)
                    m	= s.getMatrix()
                    tde4.setPGroupPosition3D(campg,c,f+1,[ m[3][0],m[3][1],m[3][2] ])
                    tde4.setPGroupRotation3D(campg,c,f+1,[ [m[0][0],m[1][0],m[2][0]], [m[0][1],m[1][1],m[2][1]], [m[0][2],m[1][2],m[2][2]] ])
                tde4.copyPGroupEditCurvesToFilteredCurves(campg,c)
                
                # import footage data...
                prop	= _abcImportFindPropRek(item[0].getProperties(),"3DE4.footage.path")
                if prop!=None:
                    tde4.setCameraPath(c,prop.getValue())
                    prop	= _abcImportFindPropRek(item[0].getProperties(),"3DE4.footage.sequence_attributes")	
                    start	= prop.getValue(0)
                    end	= prop.getValue(1)
                    step	= prop.getValue(2)
                    tde4.setCameraSequenceAttr(c,start,end,step)
                
                # import distortion data...
                prop	= _abcImportFindPropRek(item[0].getProperties(),"3DE4.lens_distortion_model")
                if prop!=None:
                    ldmodel	= prop.getValue()
                    tde4.setLensLDModel(lens,ldmodel)
                    prop	= _abcImportFindPropRek(item[0].getProperties(),"3DE4.dynamic_distortion_mode")
                    if prop!=None: tde4.setLensDynamicDistortionMode(lens,prop.getValue())
                    n	= tde4.getLDModelNoParameters(ldmodel)
                    for p in range(n):
                        pname	= tde4.getLDModelParameterName(ldmodel,p)
                        prop	= _abcImportFindPropRek(item[0].getProperties(),"3DE4."+pname)
                        if prop!=None:
                            n0	= prop.getNumSamples()
                            for f in range(1,n0+1):
                                try:	focal	= tde4.getCameraFocalLength(c,f)
                                except:	break
                                else:	
                                    focus	= tde4.getCameraFocus(c,f)
                                    v	= prop.getValue(f-1)
                                    tde4.setLensLDAdjustableParameter(lens,pname,focal,focus,v)
                
            
            #
            # import a 3D model...
            if item[1]=="PolyMesh":
                pg0	= tde4.findPGroupByName(_abcImportFindParentPGroupName(req,i))
                if pg0==None: pg0 = pg
                mesh	= alembic.AbcGeom.IPolyMesh(item[0],kWrapEx).getSchema()
                n	= mesh.getNumSamples()
                if n>1 and import_mocap==1:
                    # mocap import...
                    tde4.setPGroupType(pg0,"MOCAP")
                    n0	= tde4.getCameraNoFrames(c0)
                    if n>n0: n = n0
                    sample	= mesh.getValue()
                    fcounts	= sample.getFaceCounts()
                    findex	= sample.getFaceIndices()
                    vertex	= sample.getPositions()
                    nv	= len(vertex)
                    m	= tde4.create3DModel(pg0,len(vertex))
                    tde4.set3DModelPointLinksFlag(pg0,m,1)
                    tde4.set3DModelName(pg0,m,item[0].getName())

                    if len(vertex)>20000: tde4.postProgressRequesterAndContinue("Import Alembic...","Importing 3D Model/PolyMesh \"%s\"..."%item[0].getName(),3,"Ok")
                    if len(vertex)>20000: tde4.updateProgressRequester(1,"Importing 3D Model/PolyMesh \"%s\"..."%item[0].getName())

                    for i in range(0,nv):
                        p	= tde4.createPoint(pg0)
                        tde4.setPointSurveyMode(pg0,p,"SURVEY_EXACT")
                        tde4.add3DModelVertex(pg0,m,[0,0,0])
                        tde4.set3DModelPointLink(pg0,m,i,p)
                        for f in range(0,n):
                            sample	= mesh.getValue(f)
                            vertex	= sample.getPositions()
                            v	= vertex[i]
                            tde4.setPointMoCapSurveyPosition3D(pg0,p,c0,f+1,[v[0],v[1],v[2]])

                else:
                    # regular (static) import...
                    sample	= mesh.getValue()
                    fcounts	= sample.getFaceCounts()
                    findex	= sample.getFaceIndices()
                    vertex	= sample.getPositions()
                    m	= tde4.create3DModel(pg0,len(vertex))
                    if import_uvs==1:
                        if mesh.getUVsParam().getNumSamples()==0: import_uvs = 0
                        else:
                            import_uvs	= 1
                            uvsample	= mesh.getUVsParam().getIndexedValue()

                    tde4.set3DModelName(pg0,m,item[0].getName())

                    if len(vertex)>20000: tde4.postProgressRequesterAndContinue("Import Alembic...","Importing 3D Model/PolyMesh \"%s\"..."%item[0].getName(),3,"Ok")
                    if len(vertex)>20000: tde4.updateProgressRequester(1,"Importing 3D Model/PolyMesh \"%s\"..."%item[0].getName())

                    for v in vertex: tde4.add3DModelVertex(pg0,m,[v[0],v[1],v[2]])

                if len(vertex)>2000: tde4.updateProgressRequester(2,"Importing 3D Model/PolyMesh \"%s\"..."%item[0].getName())
                
                j	= 0
                face	= 0
                for i in range(0,len(fcounts)):
                    n	= fcounts[i]
                    l	= []
                    uv	= []
                    for i0 in range(0,n):
                        l.append(findex[j])
                        if import_uvs==1: uv.append(uvsample.getVals()[j])
                        j	= j+1
                    l.reverse()
                    uv.reverse()
                    if n>2:
                        tde4.add3DModelFace(pg0,m,l)
                        if import_uvs==1:
                            for i0 in range(0,n): tde4.set3DModelFaceUVCoord(pg0,m,face,i0,uv[i0][0],uv[i0][1])
                        face	= face+1
                    l.append(l[0])
                    tde4.add3DModelLine(pg0,m,l)

                if len(vertex)>20000: tde4.updateProgressRequester(2,"Importing 3D Model/PolyMesh \"%s\"..."%item[0].getName())

                # apply parent transformations...
                if apply_xforms==1:
                    x	= _abcImportAccumulateXFormRek(item[0].getParent(),imath.M44d())
                    tde4.set3DModelPosition3D(pg0,m,[ x[3][0],x[3][1],x[3][2] ])
                    tde4.set3DModelRotationScale3D(pg0,m,[ [x[0][0],x[1][0],x[2][0]], [x[0][1],x[1][1],x[2][1]], [x[0][2],x[1][2],x[2][2]] ])

                if len(vertex)>20000: tde4.unpostProgressRequester()
            
            
            #
            # import an object point group...
            if item[1]=="Group":
                if new_pgroup==1: pg0 = tde4.createPGroup("OBJECT")
                else: pg0 = pg
                pgtype	= tde4.getPGroupType(pg0)
                tde4.setPGroupName(pg0,item[0].getName())
                xf	= alembic.AbcGeom.IXform(item[0],kWrapEx).getSchema()
                n0	= tde4.getCameraNoFrames(c0)
                n	= xf.getNumSamples()
                if n>n0: n = n0
                for f in range(0,n):
                    # x	= _abcImportAccumulateXFormRek(item[0],imath.M44d())
                    s	= xf.getValue(f)
                    m	= s.getMatrix()
                    r3d	= mat3d([m[0][0],m[1][0],m[2][0]], [m[0][1],m[1][1],m[2][1]], [m[0][2],m[1][2],m[2][2]])
                    scale	= math.pow(r3d.det(),1.0/3.0)
                    r3d	= (r3d/scale).list()
                    p3d	= [m[3][0],m[3][1],m[3][2]]
                    if pgtype=="OBJECT": r3d,p3d = tde4.convertObjectPGroupTransformationWorldTo3DE(c0,f+1,r3d,p3d,scale,1)
                    tde4.setPGroupPosition3D(pg0,c0,f+1,p3d)
                    tde4.setPGroupRotation3D(pg0,c0,f+1,r3d)
                    tde4.setPGroupScale3D(pg0,scale)
                tde4.copyPGroupEditCurvesToFilteredCurves(pg0,c0)
                
        tde4.updateGUI()
        return

    return


def _ImportAlembicUpdate(req):
    # print "New update callback received, put your code here..."
    return


def _abcImportAccumulateXFormRek(obj,xf):
    if alembic.AbcGeom.IXform.matches(obj.getMetaData()):
        kWrapEx	= alembic.Abc.WrapExistingFlag.kWrapExisting
        xform	= alembic.AbcGeom.IXform(obj, kWrapEx)
        xschema	= xform.getSchema()
        n	= xschema.getNumSamples()
        if n<=1:
            xsample	= xschema.getValue()
            xf	= xf*xsample.getMatrix()
            return _abcImportAccumulateXFormRek(obj.getParent(),xf)
    return xf


def _abcImportFindParentPGroupName(req,index):
    global _abc_import_obj_list
    
    parent	= tde4.getListWidgetItemParentIndex(req,"list",index)
    while parent!=-1:
        item	= _abc_import_obj_list[parent]
        if item[1]=="Group" and item[2]>1: return item[0].getName()
        parent	= tde4.getListWidgetItemParentIndex(req,"list",parent)
    return ""


def _abcImportUpdateList(req,filename):
    global _abc_import_archive,_abc_import_obj_list
    
    try:
        f			= alembic.Abc.IArchive(filename)
    except:
        tde4.postQuestionRequester("Import Alembic...","File \"%s\" doesn't seem to be a valid .abc file."%os.path.basename(filename),"Ok")
        tde4.removeAllListWidgetItems(req,"list")
        tde4.setWidgetSensitiveFlag(req,"list",0)
        _abc_import_obj_list	= []
        _abc_import_archive	= None
    else:
        tde4.removeAllListWidgetItems(req,"list")
        o0			= f.getTop()
        _abc_import_obj_list	= []
        _abcImportAddObjItemRek(req,o0,-1)
        tde4.setListWidgetItemCollapsedFlag(req,"list",0,0)
        tde4.setWidgetSensitiveFlag(req,"list",1)
    return


def _abcImportFindPropRek(prop,name):
    if prop.getName()==name: return prop
    try: 	n = prop.getNumProperties() 
    except:	n = 0
    for i in range(0,n):
        p	= _abcImportFindPropRek(prop.getProperty(i),name)
        if p!=None: return p
    return None

def _abcImportAddObjItemRek(req,obj,parent):
    global _abc_import_obj_list
    
    kWrapEx		= alembic.Abc.WrapExistingFlag.kWrapExisting
    selectable	= 0
    nkids		= len(obj.children)
    md		= obj.getMetaData()
    custom		= ""
    
    if alembic.AbcGeom.ICamera.matches(md):
        type0		= "Camera"
        frames		= alembic.AbcGeom.ICamera(obj,kWrapEx).getSchema().getNumSamples()
        selectable	= 1
        
        # check vor "3de custom" footage...
        if _abcImportFindPropRek(obj.getProperties(),"3DE4.footage.path")!=None: custom = custom+"footage"
        if _abcImportFindPropRek(obj.getProperties(),"3DE4.lens_distortion_model")!=None: custom = custom+", distortion"
        if custom!="": custom = "["+custom+"]"
        
    elif alembic.AbcGeom.ICurves.matches(md):
        type0		= "Curves"
        frames		= alembic.AbcGeom.ICurves(obj,kWrapEx).getSchema().getNumSamples()
    elif alembic.AbcGeom.IFaceSet.matches(md):
        type0		= "FaceSet"
        frames		= alembic.AbcGeom.IFaceSet(obj,kWrapEx).getSchema().getNumSamples()
    elif alembic.AbcGeom.ILight.matches(md):
        type0		= "Light"
        frames		= alembic.AbcGeom.ILight(obj,kWrapEx).getSchema().getNumSamples()
    elif alembic.AbcGeom.INuPatch.matches(md):
        type0		= "NuPatch"
        frames		= alembic.AbcGeom.INuPatch(obj,kWrapEx).getSchema().getNumSamples()
    elif alembic.AbcGeom.IPoints.matches(md):
        type0		= "Points"
        frames		= alembic.AbcGeom.IPoints(obj,kWrapEx).getSchema().getNumSamples()
    elif alembic.AbcGeom.IPolyMesh.matches(md):
        type0		= "PolyMesh"
        frames		= alembic.AbcGeom.IPolyMesh(obj,kWrapEx).getSchema().getNumSamples()
        selectable	= 1
    elif alembic.AbcGeom.ISubD.matches(md):
        type0		= "SubD"
        frames		= alembic.AbcGeom.ISubD(obj,kWrapEx).getSchema().getNumSamples()
    elif alembic.AbcGeom.IXform.matches(md):
        type0		= "Group"
        frames		= alembic.AbcGeom.IXform(obj,kWrapEx).getSchema().getNumSamples()
        if frames>1: selectable = 1
        
        if len(obj.children)>=1:
            kid	= obj.children[0]
            mdkid	= kid.getMetaData()
            
            # is there eventually a camera beneath that thing?
            if alembic.AbcGeom.ICamera.matches(mdkid):
                selectable = 0

            # is this one of those hacked "locators"?
            if alembic.AbcGeom.IXform.matches(mdkid):
                p	= _abcImportFindPropRek(kid.getProperties(),"locator")
                if p!=None:
                    type0		= "Locator"
                    frames		= alembic.AbcGeom.IXform(obj,kWrapEx).getSchema().getNumSamples()
                    selectable	= 1
                    nkids		= 0
                    if _abcImportFindPropRek(kid.getProperties(),"3DE4.2d_tracking.x")!=None: custom = "[tracking]"

    else:
        type0		= "Root"
        frames		= 0
    label = "%s: \"%s\""%(type0,obj.getName())
    if nkids>0: label = label+", kids: %d"%nkids
    if frames>1: label = label+", frames: %d"%frames
    if custom!="": label = label+"   "+custom
    if nkids>0: index = tde4.insertListWidgetItem(req,"list",label,0,"LIST_ITEM_NODE",parent)
    else: index = tde4.insertListWidgetItem(req,"list",label,0,"LIST_ITEM_ATOM",parent)
    tde4.setListWidgetItemSelectableFlag(req,"list",index,selectable)
    if not selectable: tde4.setListWidgetItemColor(req,"list",index,0.75,0.75,0.75)
    else: tde4.setListWidgetItemColor(req,"list",index,1.0,0.9,0.0)
    _abc_import_obj_list.append([obj,type0,frames])
    if nkids>0:
        for kid in obj.children: _abcImportAddObjItemRek(req,kid,index)
    return






#
# DO NOT ADD ANY CUSTOM CODE BEYOND THIS POINT!
#

try:
    requester	= _ImportAlembic_requester_sgtk
except (ValueError,NameError,TypeError):
    requester = tde4.createCustomRequester()
    tde4.addTextFieldWidget(requester,"abc_file"," "," ")
    tde4.setWidgetOffsets(requester,"abc_file",120,100,5,0)
    tde4.setWidgetAttachModes(requester,"abc_file","ATTACH_WINDOW","ATTACH_WINDOW","ATTACH_WINDOW","ATTACH_NONE")
    tde4.setWidgetSize(requester,"abc_file",200,20)
    tde4.setWidgetCallbackFunction(requester,"abc_file","abcImportButtonCB")
    tde4.addButtonWidget(requester,"refresh","Refresh ...")
    tde4.setWidgetOffsets(requester,"refresh",600,500,5,775)
    tde4.setWidgetAttachModes(requester,"refresh","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW")
    tde4.setWidgetSize(requester,"refresh",80,20)
    tde4.setWidgetCallbackFunction(requester,"refresh","abcImportButtonCB")
    tde4.addButtonWidget(requester,"import_objects","Import")
    tde4.setWidgetOffsets(requester,"import_objects",618,5,553,5)
    tde4.setWidgetAttachModes(requester,"import_objects","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW")
    tde4.setWidgetSize(requester,"import_objects",80,20)
    tde4.setWidgetCallbackFunction(requester,"import_objects","abcImportButtonCB")
    tde4.addButtonWidget(requester,"expand_all","Expand All")
    tde4.setWidgetOffsets(requester,"expand_all",10,0,574,5)
    tde4.setWidgetAttachModes(requester,"expand_all","ATTACH_WINDOW","ATTACH_NONE","ATTACH_NONE","ATTACH_WINDOW")
    tde4.setWidgetSize(requester,"expand_all",80,20)
    tde4.setWidgetCallbackFunction(requester,"expand_all","abcImportButtonCB")
    tde4.addButtonWidget(requester,"select_all","Select All")
    tde4.setWidgetOffsets(requester,"select_all",5,0,574,5)
    tde4.setWidgetAttachModes(requester,"select_all","ATTACH_WIDGET","ATTACH_NONE","ATTACH_NONE","ATTACH_WINDOW")
    tde4.setWidgetSize(requester,"select_all",80,20)
    tde4.setWidgetCallbackFunction(requester,"select_all","abcImportButtonCB")
    tde4.addListWidget(requester,"list","",1)
    tde4.setWidgetOffsets(requester,"list",10,5,5,5)
    tde4.setWidgetAttachModes(requester,"list","ATTACH_WINDOW","ATTACH_WINDOW","ATTACH_WIDGET","ATTACH_WIDGET")
    tde4.setWidgetSize(requester,"list",150,150)
    tde4.setWidgetCallbackFunction(requester,"list","abcImportButtonCB")
    tde4.setWidgetSensitiveFlag(requester,"list",0)
    tde4.addMenuBarWidget(requester,"mbar")
    tde4.setWidgetOffsets(requester,"mbar",5,5,5,0)
    tde4.setWidgetAttachModes(requester,"mbar","ATTACH_WIDGET","ATTACH_WINDOW","ATTACH_WINDOW","ATTACH_NONE")
    tde4.setWidgetSize(requester,"mbar",100,20)
    tde4.addMenuWidget(requester,"options","Options","mbar",0)
    tde4.setWidgetOffsets(requester,"options",0,0,0,0)
    tde4.setWidgetAttachModes(requester,"options","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE")
    tde4.setWidgetSize(requester,"options",80,20)
    tde4.addMenuToggleWidget(requester,"replace_points","Replace Already Existing Points","options",1)
    tde4.setWidgetOffsets(requester,"replace_points",0,0,0,0)
    tde4.setWidgetAttachModes(requester,"replace_points","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE")
    tde4.setWidgetSize(requester,"replace_points",80,20)
    tde4.addMenuToggleWidget(requester,"apply_xforms","Apply Parent Transformations","options",1)
    tde4.setWidgetOffsets(requester,"apply_xforms",0,0,0,0)
    tde4.setWidgetAttachModes(requester,"apply_xforms","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE")
    tde4.setWidgetSize(requester,"apply_xforms",80,20)
    tde4.addMenuToggleWidget(requester,"add_new_camera","Add New Camera & Lens Automatically","options",0)
    tde4.setWidgetOffsets(requester,"add_new_camera",0,0,0,0)
    tde4.setWidgetAttachModes(requester,"add_new_camera","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE")
    tde4.setWidgetSize(requester,"add_new_camera",80,20)
    tde4.addMenuToggleWidget(requester,"add_new_pgroup","Add New Object PGroup Automatically","options",1)
    tde4.setWidgetOffsets(requester,"add_new_pgroup",0,0,0,0)
    tde4.setWidgetAttachModes(requester,"add_new_pgroup","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE")
    tde4.setWidgetSize(requester,"add_new_pgroup",80,20)
    tde4.addMenuToggleWidget(requester,"import_uvs","Import UV Coordinates","options",0)
    tde4.setWidgetOffsets(requester,"import_uvs",0,0,0,0)
    tde4.setWidgetAttachModes(requester,"import_uvs","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE")
    tde4.setWidgetSize(requester,"import_uvs",80,20)
    tde4.addMenuToggleWidget(requester,"import_as_mocap","Import Anim. PolyMeshes as Mocap PGroups","options",1)
    tde4.setWidgetOffsets(requester,"import_as_mocap",0,0,0,0)
    tde4.setWidgetAttachModes(requester,"import_as_mocap","ATTACH_WINDOW","ATTACH_NONE","ATTACH_WINDOW","ATTACH_NONE")
    tde4.setWidgetSize(requester,"import_as_mocap",80,20)
    tde4.setWidgetLinks(requester,"abc_file","","","","")
    tde4.setWidgetLinks(requester,"refresh","","","","")
    tde4.setWidgetLinks(requester,"import_objects","","","","")
    tde4.setWidgetLinks(requester,"expand_all","","","","")
    tde4.setWidgetLinks(requester,"select_all","expand_all","","","")
    tde4.setWidgetLinks(requester,"list","","","abc_file","import_objects")
    tde4.setWidgetLinks(requester,"mbar","abc_file","","","")
    _ImportAlembic_requester_sgtk = requester

#
# DO NOT ADD ANY CUSTOM CODE UP TO THIS POINT!
#

    _abc_import_archive	= None
    _abc_import_obj_list	= []


if tde4.isCustomRequesterPosted(_ImportAlembic_requester_sgtk)=="REQUESTER_UNPOSTED":
    if tde4.getCurrentScriptCallHint()=="CALL_GUI_CONFIG_MENU":
        tde4.postCustomRequesterAndContinue(_ImportAlembic_requester_sgtk,"Import Alembic...",0,0,"_ImportAlembicUpdate")
    else:
        tde4.postCustomRequesterAndContinue(_ImportAlembic_requester_sgtk,"Import Alembic... v1.3",600,800,"_ImportAlembicUpdate")
else:	tde4.postQuestionRequester("_ImportAlembic","Window/Pane is already posted, close manually first!","Ok")

