import imath
import alembic


import os

from vl_sdv import *


def exportAlembic(filename):
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
	

		export_3dmodels		= 1
		export_tracking		= 1
				
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
	
		# write point groups...
		tde4.updateProgressRequester(2,"Writing Point Groups...")
		pgl	= tde4.getPGroupList(0)
		for pg in pgl:
			name	= tde4.getPGroupName(pg)
			pgtype	= tde4.getPGroupType(pg)
			xf0	= alembic.AbcGeom.OXform(scene,name,tsidx)
			xschema	= xf0.getSchema()
			if pgtype=="CAMERA":
				sample	= alembic.AbcGeom.XformSample()
				xschema.set(sample)
			else:
				for f in range(1,nframes+1):
					# rot/pos...
					p3d	= tde4.getPGroupPosition3D(pg,c,f)
					r3d	= tde4.getPGroupRotation3D(pg,c,f)
					sample	= alembic.AbcGeom.XformSample()
					sample.addOp(matrixop,imath.M44d(r3d[0][0],r3d[1][0],r3d[2][0],0.0, r3d[0][1],r3d[1][1],r3d[2][1],0.0, r3d[0][2],r3d[1][2],r3d[2][2],0.0, p3d[0],p3d[1],p3d[2],1.0 ))
					xschema.set(sample)

			# write points...
			pl	= tde4.getPointList(pg,0)
			for p in pl:
				if tde4.isPointCalculated3D(pg,p):
					name	= tde4.getPointName(pg,p)

					xf	= alembic.AbcGeom.OXform(xf0,name,tsidx)
					xschema	= xf.getSchema()
					if pgtype=="OBJECT" or pgtype=="CAMERA":
						p3d	= tde4.getPointCalcPosition3D(pg,p)
						sample	= alembic.AbcGeom.XformSample()
						sample.addOp(transop,imath.V3d(p3d[0],p3d[1],p3d[2]))
						xschema.set(sample)
					if pgtype=="MOCAP":
						# mocap...
						for f in range(1,nframes+1):
							p3d	= tde4.getPointMoCapCalcPosition3D(pg,p,c,f)
							sample	= alembic.AbcGeom.XformSample()
							sample.addOp(transop,imath.V3d(p3d[0],p3d[1],p3d[2]))
							xschema.set(sample)

					loc0	= alembic.AbcGeom.OXform(xf,name,tsidx)
					lprop	= loc0.getProperties()
					alembic.Abc.OBox3dProperty(lprop,"locator").setValue(loc_box)
					
					# export 3de custom "2d tracking" properties...
					if export_tracking:
						uprops	= loc0.getSchema().getUserProperties()
						track	= tde4.getPointPosition2DBlock(pg,p,c,1,nframes)
						propx	= alembic.Abc.ODoubleProperty(uprops,"3DE4.2d_tracking.x")
						propy	= alembic.Abc.ODoubleProperty(uprops,"3DE4.2d_tracking.y")
						for f in range(nframes):
							propx.setValue(track[f][0])
							propy.setValue(track[f][1])

			# write 3D models...	
			count =1 
			if export_3dmodels==1:
				ml	= tde4.get3DModelList(pg,0)
				for m in ml:
					if tde4.get3DModelVisibleFlag(pg,m)==1:
						name	= tde4.get3DModelName(pg,m)

						# collect all vertices...
						n	= tde4.get3DModelNoVertices(pg,m)
						vertices= alembic.Abc.V3fTPTraits.arrayType(n)
						for i in range(n):
							v		= tde4.get3DModelVertex(pg,m,i,c,1)
							vertices[i]	= imath.V3f(v[0],v[1],v[2])

						# collect a stupid array of all concatenated vertex indices of all faces (in reverse order)...
						n	= tde4.get3DModelNoFaces(pg,m)
						n0	= 0
						i0	= 0
						for i in range(n): n0 = n0+len(tde4.get3DModelFaceVertexIndices(pg,m,i))
						faces	= alembic.Abc.Int32TPTraits.arrayType(n0)
						uvs	= alembic.Abc.V2fTPTraits.arrayType(n0)
						for i in range(n):
							face	= tde4.get3DModelFaceVertexIndices(pg,m,i)
							for j in range(len(face)):
								faces[i0] = face[len(face)-j-1]
								v	= tde4.get3DModelFaceUVCoord(pg,m,i,len(face)-j-1)
								uvs[i0]	= imath.V2f(v[0],v[1])
								i0	= i0+1

						# collect the number of vertices for each face and put them into another stupid array...
						fcounts	= alembic.Abc.Int32TPTraits.arrayType(n)
						for i in range(n): fcounts[i] = len(tde4.get3DModelFaceVertexIndices(pg,m,i))
						
						#written by me
						f = nframes
						# create the actual polymesh...
						p3d	= tde4.get3DModelPosition3D(pg,m,c,f)
						r3d	= tde4.get3DModelRotationScale3D(pg,m)
						xf	= alembic.AbcGeom.OXform(xf0,name,tsidx)
						xschema	= xf.getSchema()
						sample	= alembic.AbcGeom.XformSample()
						sample.addOp(matrixop,imath.M44d(r3d[0][0],r3d[1][0],r3d[2][0],0.0, r3d[0][1],r3d[1][1],r3d[2][1],0.0, r3d[0][2],r3d[1][2],r3d[2][2],0.0, p3d[0],p3d[1],p3d[2],1.0 ))
						xschema.set(sample)
						mschema	= alembic.AbcGeom.OPolyMesh(xf,name+'Shape'+str(count),tsidx).getSchema()
						uvs2	= alembic.AbcGeom.OV2fGeomParamSample(uvs,alembic.AbcGeom.GeometryScope.kFacevaryingScope)
						sample	= alembic.AbcGeom.OPolyMeshSchemaSample(vertices,faces,fcounts,uvs2)
						mschema.set(sample)
		
		#tde4.updateProgressRequester(3,"Writing Mesh...")
		#tde4.unpostProgressRequester()
		#tde4.postQuestionRequester("Export Mesh Alembic Archive...","File \"%s\" has been successfully exported."%os.path.basename(filename),"Ok")
	

	



