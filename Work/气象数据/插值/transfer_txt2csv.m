function transfer_txt2csv(v, yr, st_cn, sid_gh, geo_gh)
%_________________By:jbwang@igsnrr.ac.cn,On Feb. 11, 2022___________________
% clear all
% close all
% clc

v_db_name = {'TMEAN'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN';'PRCP'};
vname = {'TAVG'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN';'PRCP'};
vad_value = [-90 90; 0 300; -90 90; -90 90; 0 100; 0 24; 0 50; 0 300]*10;

% time_step = 8;
% v = 1;

sub_dbase =['F:\MeteoGrid\CMGHfilled\', v_db_name{v}];
sub_filled =  ['F:\MeteoGrid\MeteoFilled\', vname{v}];

days = datenum(yr + 1, 1, 1) - datenum(yr, 1, 1);
% READ GHCN-CIMISS
% file_filled = [sub_filled '\' vname{v} '_' num2str(yr) '_Filled.csv'];
file_raw    = [sub_dbase  '\' v_db_name{v} '_' num2str(yr) '.txt'];
if exist(file_raw, 'file')
    % disp(ff);
    [id_db, xd_db, n1] = readDbase(file_raw,days+0);
    gid = char(id_db);
    
    lat = []; lon = []; elv = []; n_missing = 0;
    for i = 1 : n1
        id = str2double(gid(i, 5:end) );
        js = find(id == st_cn(:, 1));
        if ~isempty(js)
            lat(i,1) = st_cn(js, 2); lon(i,1) = st_cn(js, 3); elv(i,1) = st_cn(js,4);
        else
            ks = find(id == sid_gh);
            if length(ks) > 1
                % disp(sid_gh(ks));
                js = ks(1);
            else
                js = ks;
            end
            
            if ~isempty(js)
                lat(i,1) = geo_gh(js, 2); lon(i,1) = geo_gh(js, 3); elv(i,1) = geo_gh(js,3);
            else
                lat(i,1) = -9999; lon(i,1) = -9999; elv(i,1) = -9999;
                n_missing = n_missing + 1;
            end
        end
    end
    
    x0 =  (xd_db < vad_value(v,1) | xd_db > vad_value(v,2));
    n2_missing = sum(x0(:));
    
    [n,m] = size(xd_db);
    %     if n > 100 && n2_missing > 0
    %         xd_db(xd_db < vad_value(v,1) | xd_db > vad_value(v,2)) = 32766;
    %         geo = [lon, lat, elv];
    %         % Fill missing data if the missing data less than 20%
    %         [filled_data, qc, sta,nf] = fillmissing(xd_db, gid,geo);
    %     end
    filled_data = xd_db;
    ftxt = [sub_filled '\' vname{v} '_' num2str(yr) '_Filled.csv'];
    headerline = {'Year'; 'LATI'; 'LONG'; 'Elva'};
    for i = 1 : m
        headerline{i+4,1} = ['D' num2str(i, '%03d')];
    end
    
    fop = fopen(ftxt, 'w');
    for i = 1 : days + 4
        fprintf(fop, '%s,', headerline{i}');
    end
    
    for i = 1 : n
        fprintf(fop, '\n%s, %d,%f,%f,%f', char(gid(i,:)), yr, lat(i),lon(i),elv(i));
        for j = 1 : m
            fprintf(fop, ',%.3f', filled_data(i,j));
        end
    end
    fclose(fop);
    disp([v, yr, n_missing, n2_missing]);
end




% disp('That''s all, go home!');

