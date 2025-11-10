% Read nc dataset provided by BGC (http://www.bgc-jena.mpg.de/geodb/)
% Written by Junbang Wang (IGSNRR, CAS)
% On Jan 24, 2015
%
% This example shows how to use the MATLAB netCDF functions to explore the contents of a netCDF file. The section uses the example netCDF file included with MATLAB, example.nc, as an illustration. For an example of reading data from a netCDF file, see Reading Data from a netCDF File
% Open the netCDF file using the netcdf.open function. This function returns an identifier that you use thereafter to refer to the file. The example opens the file for read-only access, but you can specify other access modes. For more information about modes, see netCDF.open.
% ncid = netcdf.open('example.nc','NC_NOWRITE');
% Explore the contents of the file using the netcdf.inq function. This function returns the number of dimensions, variables, and global attributes in the file, and returns the identifier of the unlimited dimension in the file. (An unlimited dimension can grow.)
% [ndims,nvars,natts,unlimdimID]= netcdf.inq(ncid)
% Get more information about the dimensions, variables, and global attributes in the file by using netCDF inquiry functions. For example, to get information about the global attribute, first get the name of the attribute, using the netcdf.inqAttName function. After you get the name, 'creation_date' in this case, you can use the netcdf.inqAtt function to get information about the data type and length of the attribute.
% To get the name of an attribute, you must specify the ID of the variable the attribute is associated with and the attribute number. To access a global attribute, which isn't associated with a particular variable, use the constant 'NC_GLOBAL' as the variable ID. The attribute number is a zero-based index that identifies the attribute. For example, the first attribute has the index value 0, and so on.
% global_att_name = netcdf.inqAttName(ncid,netcdf.getConstant('NC_GLOBAL'),0)
% [xtype attlen] = netcdf.inqAtt(ncid,netcdf.getConstant('NC_GLOBAL'),global_att_name)
% Get the value of the attribute, using the netcdf.getAtt function.
% global_att_value = netcdf.getAtt(ncid,netcdf.getConstant('NC_GLOBAL'),global_att_name)
% Get information about the dimensions defined in the file through a series of calls to netcdf.inqDim. This function returns the name and length of the dimension. The netcdf.inqDim function requires the dimension ID, which is a zero-based index that identifies the dimensions. For example, the first dimension has the index value 0, and so on.
% [dimname, dimlen] = netcdf.inqDim(ncid,0)
% Get information about the variables in the file through a series of calls to netcdf.inqVar. This function returns the name, data type, dimension ID, and the number of attributes associated with the variable. The netcdf.inqVar function requires the variable ID, which is a zero-based index that identifies the variables. For example, the first variable has the index value 0, and so on.
% [varname, vartype, dimids, natts] = netcdf.inqVar(ncid,0)
% The data type information returned in vartype is the numeric value of the netCDF data type constants, such as, NC_INT and NC_BYTE. See the official netCDF documentation for information about these constants.
% Reading Data from a netCDF File
% After you understand the contents of a netCDF file, by using the inquiry functions, you can retrieve the data from the variables and attributes in the file. To read the data associated with the variable avagadros_number in the example file, use the netcdf.getVar function. The following example uses the netCDF file identifier returned in the previous section, Exploring the Contents of a netCDF File. The variable ID is a zero-based index that identifies the variables. For example, the first variable has the index value 0, and so on. (To learn how to write data to a netCDF file, see Storing Data in a netCDF File.)
% A_number = netcdf.getVar(ncid,0)
% The netCDF functions automatically choose the MATLAB class that best matches the netCDF data type, but you can also specify the class of the return data by using an optional argument to netcdf.getVar. The following table shows the default mapping. For more information about netCDF data types, see the NetCDF C Interface Guide for version 3.6.2.

clear all;close all;clc
mymap=[white(1); jet(150)];
wks = 'G:\Workspace\Global8km\ncep\ncep2_nc\';
owk = 'D:\Global8km\datm7\ncep2_windfactor';

fmsk = 'D:\Global8km\Parameters\Continent_5km.tif';
msk = (imread(fmsk))';
imagesc(msk',[0 5]);

yr1 = 1981; yr2 = 1981;
xmn = [];
xday = []; j = 1;
for d = 1 : 365
    for i = 1 : 4
        xday(j,:) = [j, d, i];
        j = j + 1;
    end
end
xday1 = []; j = 1;
for d = 1 : 366
    for i = 1 : 4
        xday1(j,:) = [j, d, i];
        j = j + 1;
    end
end

for yr = yr1 : yr2
    tic;
    days = datenum(yr + 1, 1, 1) - datenum(yr, 1, 1);
    if days == 365
        xd = xday;
    else
        xd = xday1;
    end
    
    % vwnd.10m.gauss.2020
    fland = [wks, '\vwnd.10m.gauss.', num2str(yr),  '.nc'];
    disp(fland);
    % (1) Open the netCDF file using the netcdf.open function.
    ncid = netcdf.open(fland, 'nowrite');
    % (2) Explore the contents of the file using the netcdf.inq function.
    % [ndims,nvars,natts,unlimdimID] = netcdf.inq(ncid);
    %
    % for i = 0 : nvars-1
    %     [dimname, dimlen(i+1)] = netcdf.inqVar(ncid,i);
    %     disp([num2str(i), ' ', dimname ' ' num2str(dimlen(i+1))]);
    % end
    tm = netcdf.getVar(ncid,3);
    lon = netcdf.getVar(ncid,2);
    lat = netcdf.getVar(ncid,1);
    vwnd = netcdf.getVar(ncid,4);
    % x0 = dat(:,:, 1);
    % imagesc(lon, lat, x0')
    % set(gca, 'Ydir', 'normal')
    netcdf.close(ncid);
    
    % vwnd.10m.gauss.2020
    fland = [wks, '\uwnd.10m.gauss.', num2str(yr),  '.nc'];
    disp(fland);
    % (1) Open the netCDF file using the netcdf.open function.
    ncid = netcdf.open(fland, 'nowrite');
    % (2) Explore the contents of the file using the netcdf.inq function.
    % [ndims,nvars,natts,unlimdimID] = netcdf.inq(ncid);
    %
    % for i = 0 : nvars-1
    %     [dimname, dimlen(i+1)] = netcdf.inqVar(ncid,i);
    %     disp([num2str(i), ' ', dimname ' ' num2str(dimlen(i+1))]);
    % end
    tm = netcdf.getVar(ncid,3);
    lon = netcdf.getVar(ncid,2);
    lat = netcdf.getVar(ncid,1);
    uwnd = netcdf.getVar(ncid,4);
    netcdf.close(ncid);
    
    [n, m, tn] = size(uwnd);
    xu = reshape(uwnd, n*m, tn);
    xv = reshape(vwnd, n*m, tn);
    % x0 = uwnd(:,:, 1);
    lon = lon + 360;
    % imagesc(x0'); colorbar; lon, lat, 
    % set(gca, 'Ydir', 'normal')
    dat = (xu.^2 + xv.^2).^0.5;
    
    % mn_xu = mean(xu);
    % mn_xv = mean(xv);
    % mn_uv = mean(dat);
    %
    % plot(tm, mn_xu, 'b-', tm, mn_xv, 'r-', tm, mn_uv, 'g-');
    
    
    jx = xd(:, 2);
    jd = fix((jx - 1) / 8) + 1;
    Wf = zeros(n*m, 46) - 9999;
    for dy = 1 : 46
        x0 = dat(:, jd == dy);
        x0(x0 < 0 | x0 > 999) = -9999;
        [n0,m0] = size(x0);
        
        ws = x0 .* (x0 - 5.0).^2;
        
        ws(x0 < 5.0) = 0;
        wf = mean(ws, 2, 'omitnan'); % [mean(wf), mean(x1), mean(wf(Us >= 5.0))];
        
        
        
        bnd = quantile(wf(wf>0), [0.05, 0.95]);
        x2 = reshape(wf, n, m);
        x3 = x2';
        x4 = x3(m:-1:1,:);
        % figure(1); imagesc(x4, bnd);
        % pause(0.01);
        
        x3f = [owk, '\ncep2_' num2str(yr * 1000 + dy) '.flt'];
        x3p = fopen(x3f, 'wb');
        fwrite(x3p, x0, 'float32');
        fclose(x3p);
    end
    
    disp([yr, toc]);
end
