#
# 3DE4.script.name:	Export Camera To Alembic...
#
# 3DE4.script.version:	v1.0
#
# 3DE4.script.gui:	Main Window::FWX Tools::Export
#
# 3DE4.script.comment:	Export the current project as Alembic (.abc).
#

import imath
import alembic

import os

from vl_sdv import *


def export_camera_alembic(filename):
    import tde4
    
    try:	archive = alembic.Abc.OArchive(filename)
    except:	tde4.postQuestionRequester("Export Alembic Archive...","Can't open file \"%s\" for writing."%os.path.basename(filename),"Ok")
    else:
        
        # preparations...
        for campg in tde4.getPGroupList(0):
            if tde4.getPGroupType(campg)=="CAMERA": break
        c	= tde4.getCurrentCamera()
        nframes	= tde4.getCameraNoFrames(c)
        
        transop	= alembic.AbcGeom.XformOp(alembic.AbcGeom.XformOperationType.kTranslateOperation,0)
        rotatop	= alembic.AbcGeom.XformOp(alembic.AbcGeom.XformOperationType.kRotateOperation,0)
        scaleop	= alembic.AbcGeom.XformOp(alembic.AbcGeom.XformOperationType.kScaleOperation,0)
        matrixop= alembic.AbcGeom.XformOp(alembic.AbcGeom.XformOperationType.kMatrixOperation,0)

        loc_box	= imath.Box3d()
        loc_box.extendBy(imath.V3d(0,0,0))
        loc_box.extendBy(imath.V3d(1,1,1))
        
        fps	= 1.0/tde4.getCameraFPS(c)
        ts	= alembic.AbcCoreAbstract.TimeSampling(fps,0.0)
        tsidx	= archive.addTimeSampling(ts)
        
        # gather user input...
        oscanw			= float(100)
        oscanh			= float(100)
        export_distortion	= 1
                
        # write scene node...
        p3d	= tde4.getScenePosition3D()
        s	= tde4.getSceneScale3D()
        r3d	= tde4.getSceneRotation3D()
        
        root	= archive.getTop()
        scene	= alembic.AbcGeom.OXform(root,"3DE scene node",tsidx)
        xschema	= scene.getSchema()
        sample	= alembic.AbcGeom.XformSample()
        sample.addOp(transop,imath.V3d(p3d[0],p3d[1],p3d[2]))
        sample.addOp(matrixop,imath.M44d(r3d[0][0],r3d[1][0],r3d[2][0],0.0, r3d[0][1],r3d[1][1],r3d[2][1],0.0, r3d[0][2],r3d[1][2],r3d[2][2],0.0, 0.0,0.0,0.0,1.0 ))
        sample.addOp(scaleop,imath.V3d(s,s,s))
        xschema.set(sample)
        
        # write camera(s)...
        tde4.updateProgressRequester(1,"Writing Cameras...")
        cl	= tde4.getCameraList(0)
        count = 1 
        for cam in cl:
            if cam==c:
                camtype	= tde4.getCameraType(cam)
                if camtype=="SEQUENCE":
                    lens	= tde4.getCameraLens(cam)
                    name	= tde4.getCameraName(cam)
                    n	= tde4.getCameraNoFrames(cam)
                    
                    xf	= alembic.AbcGeom.OXform(scene,name,tsidx)
                    xschema	= xf.getSchema()
                    cschema	= alembic.AbcGeom.OCamera(xf,name+'Shape'+str(count),tsidx).getSchema()
                    uprops	= cschema.getUserProperties()
                    
                    # set 3de custom footage properties...
                    path	= tde4.getCameraPath(cam)
                    alembic.Abc.OStringProperty(uprops,"3DE4.footage.path").setValue(path)
                    prop	= alembic.Abc.OInt32Property(uprops,"3DE4.footage.sequence_attributes")
                    attr	= tde4.getCameraSequenceAttr(cam)
                    prop.setValue(attr[0])
                    prop.setValue(attr[1])
                    prop.setValue(attr[2])
                    
                    # write camera animation and lens...
                    for f in range(1,n+1):
                        # rot/pos...
                        p3d	= tde4.getPGroupPosition3D(campg,cam,f)
                        r3d	= tde4.getPGroupRotation3D(campg,cam,f)
                        sample	= alembic.AbcGeom.XformSample()
                        sample.addOp(matrixop,imath.M44d(r3d[0][0],r3d[1][0],r3d[2][0],0.0, r3d[0][1],r3d[1][1],r3d[2][1],0.0, r3d[0][2],r3d[1][2],r3d[2][2],0.0, p3d[0],p3d[1],p3d[2],1.0 ))
                        xschema.set(sample)

                        # lens attributes...
                        fbw	= tde4.getLensFBackWidth(lens)
                        fbh	= tde4.getLensFBackHeight(lens)
                        paspect	= tde4.getLensPixelAspect(lens)
                        lcox	= tde4.getLensLensCenterX(lens)
                        lcoy	= tde4.getLensLensCenterY(lens)
                        focal	= tde4.getCameraFocalLength(cam,f)
                        focus	= tde4.getCameraFocus(cam,f)
                        sample	= alembic.AbcGeom.CameraSample()
                        sample.setHorizontalAperture(fbw)
                        sample.setVerticalAperture(fbh)
                        sample.setLensSqueezeRatio(paspect)
                        sample.setHorizontalFilmOffset(lcox)
                        sample.setVerticalFilmOffset(lcoy)
                        sample.setFocalLength(focal*10.0)
                        sample.setFocusDistance(focus)
                        sample.setOverScanLeft((oscanw-100.0)/2.0)
                        sample.setOverScanRight((oscanw-100.0)/2.0)
                        sample.setOverScanTop((oscanh-100.0)/2.0)
                        sample.setOverScanBottom((oscanh-100.0)/2.0)
                        cschema.set(sample)
                        
                    # write 3de custom distortion properties...
                    if export_distortion:
                        dmodel	= tde4.getLensLDModel(lens)
                        alembic.Abc.OStringProperty(uprops,"3DE4.lens_distortion_model").setValue(dmodel)
                        ddmode	= tde4.getLensDynamicDistortionMode(lens)
                        alembic.Abc.OStringProperty(uprops,"3DE4.dynamic_distortion_mode").setValue(ddmode)
                        nparas	= tde4.getLDModelNoParameters(dmodel)
                        for p in range(nparas):
                            para	= tde4.getLDModelParameterName(dmodel,p)
                            prop	= alembic.Abc.ODoubleProperty(uprops,"3DE4."+para)
                            for f in range(1,n+1):
                                focal	= tde4.getCameraFocalLength(cam,f)
                                focus	= tde4.getCameraFocus(cam,f)
                                d	= tde4.getLensLDAdjustableParameter(lens,para,focal,focus)
                                prop.setValue(d)
            count = count + 1
    



