
from netCDF4 import Dataset
import numpy as np

class NetCDFOutput:

    def __init__( self, filename=None ):

        self.rootgrp = None
        if filename == None:
            return

        self.rootgrp = Dataset(filename, "w", format="NETCDF4")
        self.rootgrp.createDimension("X")
        self.rootgrp.createDimension("Y")
        self.rootgrp.createDimension("count")
        self.metagrp = self.rootgrp.createGroup("meta")

        self.scale = self.rootgrp.createVariable("scale", "f8")
        self.scale.long_name = "scale"
        self.scale.units = "meter"

        self.count = self.rootgrp.createVariable("count", "u4", ("count") )
        self.count.units = "steps"
        self.count.long_name = "count"
        self.count.field = "time, scalar, series"

        self.time = self.rootgrp.createVariable("time", "f4", ("count") )
        self.time.units = "seconds"
        self.time.long_name = "time"
        self.time.field = "time, scalar, series"

        self.workdir = self.rootgrp.createVariable("workdir", "u8", ("count") )
        self.workdir.units = "workdir"
        self.workdir.long_name = "WASS-like workdir number (ie. frame index)"
        self.workdir.field = "time, scalar, series"

        self.xgrid = self.rootgrp.createVariable( "X_grid", "f8", ("X","Y",) )
        self.xgrid.units = "millimeter"
        self.xgrid.long_name = "X axis grid"
        self.xgrid.field = "X_grid, scalar, series"

        self.ygrid = self.rootgrp.createVariable( "Y_grid", "f8", ("X","Y",) )
        self.ygrid.units = "millimeter"
        self.ygrid.long_name = "Y axis grid"
        self.ygrid.field = "Y_grid, scalar, series"

        self.kx = self.rootgrp.createVariable( "Kx", "f8", ("X","Y",) )
        self.kx.units = "wavenumbers"
        self.kx.long_name = "Horizontal wavenumbers"
        self.kx.field = "Kx, scalar, series"

        self.ky = self.rootgrp.createVariable( "Ky", "f8", ("X","Y",) )
        self.ky.units = "wavenumbers"
        self.ky.long_name = "Vertical wavenumbers"
        self.ky.field = "Ky, scalar, series"

        self.Z = self.rootgrp.createVariable( "Z", "f4", ("count", "X","Y",) )
        self.Z.units = "millimeter"
        self.Z.long_name = "Z data on time over the XY grid"
        self.Z.field = "Z, scalar, series"

        self.maskZ = self.rootgrp.createVariable( "maskZ", "f4", ("X","Y",) )
        self.maskZ.units = "millimeter"
        self.maskZ.long_name = "Z mask over the XY grid"
        self.maskZ.field = "Z, scalar, series"

        self.vlen_t = self.rootgrp.createVLType(np.uint8, "vlenu8")
        self.cam0images = self.rootgrp.createVariable( "cam0images", self.vlen_t, ("count") )
        self.cam0images.long_name = "Camera0 undistorted images in JPEG format"


    def set_grids( self, XX, YY ):
        if self.rootgrp == None:
            return

        self.xgrid[:] = XX
        self.ygrid[:] = YY

    
    def set_kxky( self, kx, ky ):
        if self.rootgrp == None:
            return

        self.kx[:] = kx
        self.ky[:] = ky


    def set_mask( self, maskZ ):
        if self.rootgrp == None:
            return

        self.maskZ[:] = maskZ


    def set_instrinsics( self, K0, K1, kc0, kc1, P0plane ):
        if self.rootgrp == None:
            return

        self.metagrp.createDimension( "V3", 3 )
        self.metagrp.createDimension( "V4", 4 )
        self.metagrp.createDimension( "DistV", 5 )
        K0v = self.metagrp.createVariable("intr0", "f8", ("V3","V3") )
        K0v[:] = K0
        K1v = self.metagrp.createVariable("intr1", "f8", ("V3","V3") )
        K1v[:] = K1
        _P0plane = self.metagrp.createVariable("P0plane", "f8", ("V4","V4") )
        _P0plane[:] = P0plane
        kc0v = self.metagrp.createVariable("dist0", "f8", ("DistV") )
        kc0v[:] = kc0
        kc1v = self.metagrp.createVariable("dist1", "f8", ("DistV") )
        kc1v[:] = kc1

    # def push_Z( self, Zdata, time ):
    #     if self.rootgrp != None:
    #         idx = self.count.shape[0]
    #         self.Z[idx,:,:] = np.expand_dims( Zdata, axis=0 )
    #         self.count[idx] = idx
    #         self.time[idx] = time
    #         if idx%10 == 0:
    #             self.rootgrp.sync() # Flush data to disk

    def push_Z( self, Zdata, time, workdir, image=None ):
        if self.rootgrp != None:
            idx = self.count.shape[0]
            self.Z[idx,:,:] = np.expand_dims( Zdata, axis=0 )
            self.count[idx] = idx
            self.time[idx] = time
            self.workdir[idx] = workdir

            if not image is None:
                self.cam0images[idx] = image

            if idx%10 == 0:
                self.rootgrp.sync() # Flush data to disk


    # def add_global_attribute( self, name, value ):
    #     if self.rootgrp != None:
    #         self.rootgrp.setncattr( name, value )

    def add_meta_attribute( self, name, value ):
        if self.rootgrp != None:
            self.metagrp.setncattr( name, value )

    def close( self ):
        if self.rootgrp != None:
            self.rootgrp.close()