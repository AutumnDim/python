function subset_dbase(yr1, yr2, sub_name, sub_sta, vs, wks, owk)
%_________________By:jbwang@igsnrr.ac.cn,On Dec.30, 2016___________________
% clear all
% close all
% clc

v_db_name = {'TMEAN'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN';'PRCP'};
vname = {'TAVG'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN';'PRCP'};
vad_value = [-90 90; 0 300; -90 90; -90 90; 0 100; 0 24; 0 50; 0 300]*10;
headerline = 1;
X = [];
js = 1;
for v = 1 : length(vs)
    sub_filled =  [wks, filesep, vname{v}];
    for yr = yr2:-1:yr1
        [days, dy2, ~] = daily2timestep(yr, 30);
        % READ GHCN-CIMISS
        file_filled = [sub_filled '\' vname{v} '_' num2str(yr) '_Filled.csv'];
        if exist(file_filled, 'file')
            [gid, xd, n1] = readFilledbase(file_filled,days+3, headerline);
            gid = char(gid);
            geo = xd(:, 2:4);
            x0 = [];
            for s = 1 : length(sub_name)
                ks = find(strcmpi(gid, sub_sta(s)) > 0);
                if ~isempty(ks)
                    x0(s, :) = xd(ks, :);
                else
                    x0(s, :) = -9999 * ones(1, days);
                end
            end
        end
        
        
        
    end
    
end
for s = 1 : length(sub_name)
    ftxt = [owk, filesep, sub_name{s}, '.txt'];
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
end

% disp('That''s all, go home!');

