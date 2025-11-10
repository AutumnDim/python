yr1 = 1980; yr2 = 1980;
nfile = 1;
site_name = 'Shennj';
vname_ID = 2;

vname = {'TAVG'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN'};
cname = {'T2', 'R2', 'T2', 'T2', 'RH2', 'D32', 'W2'};

vad_value = [-60 60; 0 1000; -60 60; -60 60; 0 100; 0 18; 0 20]*10;

vname_unit = {'^oC', 'mm', '^oC', '^oC', '%', 'Hour', 'm/s'};

fdbs = 'E:\MeteoGrid\Station\Stations_5k.txt';

fsite = 'E:\MeteoGrid\Station\CNERN_CERN.xls';

ftif = ['D:\STSZHANGLI\SRTM\SRTM_' site_name '_250m.tif'];
proj = geotiffinfo(ftif);
[mcd, R, bbox] = geotiffread(ftif);
x0 = bbox(1,1): R(2,1): bbox(2,1);
y0 = bbox(1,2): R(2,1): bbox(2,2);

dbs_wks = 'D:\STSZHANGLI\ShennjTest2s\temp';
krg_wks = 'D:\STSZHANGLI\ShenKrig';

vname = {'TAVG'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN'};
vad_value = [-60 60; 0 1000; -60 60; -60 60; 0 100; 0 18; 0 20]*10;
v = 1;
csz = 250;
xc = 4515790.96680921; yc = 3335334.34307641;
bbox = [xc - csz*1000 yc-csz*1000; xc+csz*1000 yc+csz*1000];
dgrid = [250 250];

for yr = yr1 : yr2
    days = datenum(yr + 1, 1, 1) - datenum(yr, 1, 1);
    for i = 1 : nfile
        ff = [dbs_wks '\' vname{v} '\' vname{v} '_' num2str(yr * 1000 + i) '.txt'];
        dat = read_fixedDat(ff);
        if yr == yr1 && i == 1
            x0 = dat(:,2); y0 = dat(:,3);
            x1 = x0(x0 >= bbox(1,1) & x0 <= bbox(2,1) & y0 >= bbox(1,2) & y0 <= bbox(2,2));
            y1 = y0(x0 >= bbox(1,1) & x0 <= bbox(2,1) & y0 >= bbox(1,2) & y0 <= bbox(2,2));
            coord = [x1 y1];
            maximum = max(coord);
            minimum = min(coord);
            ix = abs(round((maximum(1)-minimum(1))/dgrid(1)))+1;
            iy = abs(round((maximum(2)-minimum(2))/dgrid(2)))+1;     
        end
        for j = 2 : 2
            val = dat(x0 >= bbox(1,1) & x0 <= bbox(2,1) & y0 >= bbox(1,2) & y0 <= bbox(2,2), j + 4);
            pos = [x1 y1]/1000;
            
            [gamma,h]=semivar_exp(pos,val);
            plot(h,gamma);
            
            V=visim_init(x1,y1);
            V.rseed=1;
            V.Va.a_hmax=200; % maximum correlation length
            V.Va.a_hmin=5; % minumum correlation length
            V.Va.ang1=90-22.5; % Rotation angle of dip(clockwise from north)
            V.Va.it=1; % Gaussian semivariogram
            V.D = val;
            V=visim(V); % run visim;
            
            [x_obs,y_obs]=meshgrid(x1,y1);
            d_obs=V.D(:,:,1);
            n_obs=prod(size(d_obs));
            % CHOOSE SOME DATA FOR SEMIVARIOGRAM ANALYSIS
            n_use=1000;
            i_use=round(rand(1,n_use)*(n_obs-1))+1;
            i_use=unique(i_use);
            x_use=x_obs(i_use);
            y_use=y_obs(i_use);
            d_use=d_obs(i_use);
            
            % PLOT DATA
            % figure(1);
            
            % input = [x1 y1 val];
            % [output,errorvariance] = vebyk(input,[250 250],16,1,0,0.98,10000,0,1);
            % % outdat = matrixdisplay(output,iy,ix); colorbar; hold on;
            % fout = [krg_wks '\' vname{v} '\' vname{v} '_' num2str(yr * 1000 + (i - 1) * 12 + j) '.flt'];
            % fop = fopen(fout, 'w');
            % fwrite(fop, outdat, 'float32');
            % fclose(fop);
            % 
            % outvar = matrixdisplay(errorvariance,iy,ix); colorbar; hold on;
            % contour(outdat,10);
        end
    end
end