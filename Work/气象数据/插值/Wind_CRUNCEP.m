% Read nc dataset provided by BGC (http://www.bgc-jena.mpg.de/geodb/)
% Written by Junbang Wang (IGSNRR, CAS) On Jan 24, 2015
%
% This example shows how to use the MATLAB netCDF functions to explore the
% contents of a netCDF file. The section uses the example netCDF file
% included with MATLAB, example.nc, as an illustration. For an example of
% reading data from a netCDF file, see Reading Data from a netCDF File Open
% the netCDF file using the netcdf.open function. This function returns an
% identifier that you use thereafter to refer to the file. The example
% opens the file for read-only access, but you can specify other access
% modes. For more information about modes, see netCDF.open. ncid =
% netcdf.open('example.nc','NC_NOWRITE'); Explore the contents of the file
% using the netcdf.inq function. This function returns the number of
% dimensions, variables, and global attributes in the file, and returns the
% identifier of the unlimited dimension in the file. (An unlimited
% dimension can grow.) [ndims,nvars,natts,unlimdimID]= netcdf.inq(ncid) Get
% more information about the dimensions, variables, and global attributes
% in the file by using netCDF inquiry functions. For example, to get
% information about the global attribute, first get the name of the
% attribute, using the netcdf.inqAttName function. After you get the name,
% 'creation_date' in this case, you can use the netcdf.inqAtt function to
% get information about the data type and length of the attribute. To get
% the name of an attribute, you must specify the ID of the variable the
% attribute is associated with and the attribute number. To access a global
% attribute, which isn't associated with a particular variable, use the
% constant 'NC_GLOBAL' as the variable ID. The attribute number is a
% zero-based index that identifies the attribute. For example, the first
% attribute has the index value 0, and so on. global_att_name =
% netcdf.inqAttName(ncid,netcdf.getConstant('NC_GLOBAL'),0) [xtype attlen]
% = netcdf.inqAtt(ncid,netcdf.getConstant('NC_GLOBAL'),global_att_name) Get
% the value of the attribute, using the netcdf.getAtt function.
% global_att_value =
% netcdf.getAtt(ncid,netcdf.getConstant('NC_GLOBAL'),global_att_name) Get
% information about the dimensions defined in the file through a series of
% calls to netcdf.inqDim. This function returns the name and length of the
% dimension. The netcdf.inqDim function requires the dimension ID, which is
% a zero-based index that identifies the dimensions. For example, the first
% dimension has the index value 0, and so on. [dimname, dimlen] =
% netcdf.inqDim(ncid,0) Get information about the variables in the file
% through a series of calls to netcdf.inqVar. This function returns the
% name, data type, dimension ID, and the number of attributes associated
% with the variable. The netcdf.inqVar function requires the variable ID,
% which is a zero-based index that identifies the variables. For example,
% the first variable has the index value 0, and so on. [varname, vartype,
% dimids, natts] = netcdf.inqVar(ncid,0) The data type information returned
% in vartype is the numeric value of the netCDF data type constants, such
% as, NC_INT and NC_BYTE. See the official netCDF documentation for
% information about these constants. Reading Data from a netCDF File After
% you understand the contents of a netCDF file, by using the inquiry
% functions, you can retrieve the data from the variables and attributes in
% the file. To read the data associated with the variable avagadros_number
% in the example file, use the netcdf.getVar function. The following
% example uses the netCDF file identifier returned in the previous section,
% Exploring the Contents of a netCDF File. The variable ID is a zero-based
% index that identifies the variables. For example, the first variable has
% the index value 0, and so on. (To learn how to write data to a netCDF
% file, see Storing Data in a netCDF File.) A_number =
% netcdf.getVar(ncid,0) The netCDF functions automatically choose the
% MATLAB class that best matches the netCDF data type, but you can also
% specify the class of the return data by using an optional argument to
% netcdf.getVar. The following table shows the default mapping. For more
% information about netCDF data types, see the NetCDF C Interface Guide for
% version 3.6.2.

clear all;close all;clc
mymap=[white(1); jet(150)];
wks = '\\BA-37AEDE\Workspace\MeteoGrid\CRU_NCEP';

fmsk = '\\BA-37AEDE\Temporary\CRU_NCEP\Climate4R\Climate_4R_China.tif';
msk = (imread(fmsk))';
imagesc(msk',[0 5]);

clat = [25.75, 35.25];
clon = [80.25, 100.25];
cy = clat(1) : 0.5 : clat(2);
cx = clon(1) : 0.5 : clon(2);
[X,Y] = meshgrid(cx,cy);
[n,m] = size(X);
DX = [reshape(X, 1, n*m); reshape(Y, 1, n * m)];


cl = fix((cy + 89.75) / 0.5) + 1;
cp = fix((cx -  0.25) / 0.5) + 1;

ccy = clat(1) : 0.1 : clat(2);
ccx = clon(1) : 0.1 : clon(2);
[CX,CY] = meshgrid(ccx,ccy);
[cn, cm] = size(CX);
GX = [reshape(CX, 1, cn * cm); reshape(CY, 1, cn * cm)];

yr1 = 1980; yr2 = 2013;
vr = {'rain','swdown','tair'};
for v = 3 : 3
    xmn = [];
    for yr = yr1 : yr2
        file = [wks '\' vr{v} '\cruncepv5_' vr{v} '_' num2str(yr) '.nc'];
        disp(file);
        
        % (1) Open the netCDF file using the netcdf.open function.
        ncid = netcdf.open(file, 'nowrite');
        
        % (2) Explore the contents of the file using the netcdf.inq
        % function.
        [ndims,nvars,natts,unlimdimID] = netcdf.inq(ncid);
        %
        %         for i = 0 : natts-1
        %             % (3) Get more information about the dimensions,
        %             variables, and global attributes in the file by using
        %             netCDF inquiry functions. global_att_name =
        %             netcdf.inqAttName(ncid,netcdf.getConstant('NC_GLOBAL'),i);
        %
        %             % (4) Get the value of the attribute, using the
        %             netcdf.getAtt function. global_att_value =
        %             netcdf.getAtt(ncid,netcdf.getConstant('NC_GLOBAL'),global_att_name);
        %
        %             % (5) Get information about the dimensions defined in
        %             the file through a series of calls to netcdf.inqDim.
        %             [xtype attlen] =
        %             netcdf.inqAtt(ncid,netcdf.getConstant('NC_GLOBAL'),global_att_name);
        %
        %             disp([global_att_name ': ' global_att_value]);
        %         end
        %
        %         % (6) Get information about the variables in the file
        %         through a series of calls to netcdf.inqVar.
        for i = 0 : nvars-1
            [dimname, dimlen(i+1)] = netcdf.inqVar(ncid,i);
            disp([num2str(i), ' ', dimname ' ' num2str(dimlen(i+1))]);
        end
        
        % (7)  Retrieve the data from the variables and attributes use the
        % netcdf.getVar function
        ntm = netcdf.getVar(ncid,0);
        lon = netcdf.getVar(ncid,1);
        lat = netcdf.getVar(ncid,2);
        dat = netcdf.getVar(ncid,9);
        netcdf.close(ncid);
        
        % imagesc(lat'); colorbar
        ilat = lat(1,:);
        ilon = lon(:, 1);
        
        for t = 1 : length(ntm)
            xt = dat(:,:,t);
            dy0 = 20 : 10: 50;
            dx0 = 70: 10: 150;
            for dx = 1 : length(dx0)
                for dy = 1 : length(dy0)
                    clat = [dy0(dy), dy0(dy) + 15];
                    clon = [dx0(dx), dx0(dx) + 15];
                    
                    cy = clat(1) : 0.5 : clat(2);
                    cx = clon(1) : 0.5 : clon(2);
                    [X,Y] = meshgrid(cx,cy);
                    [n,m] = size(X);
                    DX = [reshape(X, 1, n*m); reshape(Y, 1, n * m)];
                    
                    
                    cl = fix((cy + 89.75) / 0.5) + 1;
                    cp = fix((cx -  0.25) / 0.5) + 1;
                    
                    ccy = clat(1) : 0.1 : clat(2);
                    ccx = clon(1) : 0.1 : clon(2);
                    [CX,CY] = meshgrid(ccx,ccy);
                    [cn, cm] = size(CX);
                    GX = [reshape(CX, 1, cn * cm); reshape(CY, 1, cn * cm)];
                    
                    x0 = (xt(cp, cl))';
                    DY = reshape(x0, 1, n * m);
                    st = tpaps(DX, DY);
                    
                    xd = fnval(st,GX);
                    
%                     x1 = interp2(X, Y, x0, CX, CY,'nearest');
%                     x2 = interp2(X, Y, x0, CX, CY,'cubic');
%                     x3 = interp2(X, Y, x0, CX, CY,'spline');
                    x4 = reshape(xd, cn, cm);
                    
                    bnd = quantile(x0(:), [0.05, 0.95]);
                    figure;
%                     subplot(2, 2, 1); imagesc(cx, cy, x1, bnd); colorbar; set(gca, 'Ydir', 'normal'); title('Nearest');set(gca, 'FontSize', 12);
%                     subplot(2, 2, 2); imagesc(cx, cy, x2, bnd); colorbar; set(gca, 'Ydir', 'normal'); title('Cubic');set(gca, 'FontSize', 12);
%                     subplot(2, 2, 3); imagesc(cx, cy, x3, bnd); colorbar; set(gca, 'Ydir', 'normal'); title('Spine');set(gca, 'FontSize', 12);
%                     subplot(2, 2, 4); 
                    imagesc(cx, cy, x4, bnd); colorbar; set(gca, 'Ydir', 'normal'); title('TPAPS'); set(gca, 'FontSize', 12);
                    
                    print(['Wind_data_interpolate_', num2str(dx), '_', num2str(dy), '.png'], '-dpng', '-r300');
                end
            end
            if t == 1
                xt = x0;
            else
                xt = xt + x0;
            end
        end
        if v == 3
            xt = xt / 1460;
        end
        if v == 3
            xt(xt < 0) = -9999;
        else
            xt(xt < -9999) = -9999;
        end
        
        slat = (max(lat)-min(lat)+0.5)/length(lat);
        slon = (max(lon)-min(lon)+0.5)/length(lon);
        cellsize = slon;
        yul = max(lat);
        xur = max(lon);
        yll = -90;  % min(lat);
        xll = -180; % min(lon);
        NODATA_value = -9999;
        
        
        byteorder = 'LSBFIRST';
        npixels = dimlen(3);nlines = dimlen(2);
        
        nfilename = length(file);
        x3f = [file(1:nfilename-3) '.flt'];
        x3p = fopen(x3f, 'wb');
        fwrite(x3p, xt, 'float32');
        fclose(x3p);
        writegrdhdr(x3f, npixels, nlines, xll, yll, cellsize, NODATA_value, byteorder);
        
        for j = 1 : 5
            if j < 5
                xmn(yr-yr1+1,j) = mean(xt(xt > -9000 & msk == j));
            else
                xmn(yr-yr1+1,j) = mean(xt(xt > -900 & msk < 100 & msk > 0));
            end
        end
    end
    fxls = 'cruncepv5_1980-2013.xls';
    xlswrite(fxls, {'YEAR','QT','TROPICAL','TEMPERATE','CONTINENTAL','NATIONAL'}, vr{v}, 'A1');
    xlswrite(fxls, [(yr1:yr2)' xmn], vr{v}, 'A2');
end
bnd = quantile(xt(xt>-9000), [0.05 0.95]);
figure(1)
imagesc(xt',bnd);
colormap(mymap);
colorbar('horiz');
axis equal
axis off
title(yr2);