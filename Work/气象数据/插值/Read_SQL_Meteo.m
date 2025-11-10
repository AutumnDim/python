close all; clear all; clc;

vname = {'PRES'; 'WIN';'TAVG'; 'TMAX'; 'TMIN'; 'RHU'; 'PRCP';  'SSD'};

conn = database('MeteoSQL', 'DESKTOP-7VCAVPF\wangjb', 'Wang2018');

yr1 = 2018; yr2 = 2018;

for yr = yr2 : -1 : yr1
    
    days = datenum(yr + 1, 1, 1) - datenum(yr, 1, 1);
    
    cursorA = exec(conn, ['SELECT * FROM dbo.all' num2str(yr)]);
    
    cursorA = fetch(cursorA);
    
    id = unique(cursorA.Data(:,1));
    
    sid = cursorA.Data(:,1);
    
    xdt = cell2mat(cursorA.Data(:,2:end));
    
    jday = datenum(xdt(:,1), xdt(:,2), xdt(:,3)) - datenum(xdt(:,1), 1, 1) + 1;
    
    tic
    ns = length(id);
    nd = days + 4;
    
    for v = 1 : length(vname)
        X = [];
        for i = 1 : length(id)
            
            js = strcmp(sid, id(i));
            
            disp([num2str(v) ' ' id{i} ' ' num2str(sum(js))]);
            
            x0 = xdt(js,:);
            
            jd = jday(js,:);
            
            gid = [x0(1,1), x0(1,4:6), ones(1,days) * 99999];
            x1 = (x0(:,v + 6))';
            
            for j = 1 :length(jd)
                jk = find(jd == j);
                % disp(jk')
                if isempty(jk)
                    gid(1,jd(j) + 4) = 999999;
                else
                    if length(jk) > 1
                        x2 = min(x1(jk));
                    else
                        x2 = x1(j);
                    end
                    gid(1, jd(j) + 4) = x2;
                end
            end
            X(i, :) = gid;
        end
        fcsv = ['E:\MeteoGrid\TEMP\' vname{v} '_' num2str(yr) '.csv'];
        fop = fopen(fcsv, 'w');
        fprintf(fop, 'SID\tYEAR\tLAT\tLON\tELV');
        for j = 1 : days
            fprintf(fop, '\tD%03d', j);
        end
        for i = 1 : length(id)
            fprintf(fop, '\n%s\t%d\t%f\t%f\t%f', id{i}, X(i,1:4));
            for j = 1 : days
                fprintf(fop, '\t%f', X(i, j + 4));
            end
        end
        fclose(fop);
    end
    toc
end
close(conn);