clear all
close all
clc
vname1 = {'PRCP'; 'TMIN'; 'TMAX'; 'TEM'; 'RHU'; 'SSD';  'WIN'; 'WVP'};
vname2 = {'PRE'; 'TMN'; 'TMX'; 'TEM'; 'RHU'; 'SSD';  'WIN'; 'WVP'};
v = 1;
tic

% STATIONS
ff = 'I:\Database\meteo\CMGH\CMGH\GHCN_CHINA_DEM_ACEA-ed.txt';
[no st x0 y0 elv dem flg] = textread(ff, '%d%s%f%f%f%f%d');
n = length(x0);
sid = cell2mat(st);

tp = strmatch('CH0',sid(:,1:3),'exact');
tx=setdiff(no,tp);
gid = sid(tx,:);
gn = length(tx);

flp = fopen('MergeghcnChina.log','w');
k = 1;
for v = 4:4
    var1 = cell2mat(vname2(v));
    var2 = cell2mat(vname1(v));
    
    sub  = ['I:\Database\meteo\CMGH2013\' var2];
    if ~exist(sub,'dir')
        system(['mkdir ' sub]);
    end
    
    if var(1) == 'R'
        scale = 1;
    else
        scale = 1;
    end
    
    yr1 = 1980;yr2 = 2013;
    
    for y = yr1:yr2
        days = datenum(y+1,1,1)-datenum(y,1,1);
        % READ GHCN
        ff = ['I:\Database\meteo\GHCN\VAR\' var2 '\' var2 '_' num2str(y) '.txt'];
        disp(ff);
        [id xd n1] = readghcn(ff,days);
        sd = char(id);
        j = 1;
        nsd = []; xsd = [];
        for i = 1 : gn
            td = strmatch(gid(i,:), sd);
            if ~isempty(td)
                nsd(j,:) = gid(i,:);
                if v == 4
                    xsd(j,:) = xd(td,:);
                else
                    xsd(j,:) = xd(td,3:days+2);
                end
                j = j + 1;
            end
        end
        n2 = j - 1;
        
        ff = ['I:\Database\meteo\CMGH\Daily2013\' var1 '\' var1 '_' num2str(y) '.csv'];
        disp(ff);
        xx = load(ff);
        [n3 m] = size(xx);
        ncd = xx(:,1);
        xcd = xx(:,2:m);
        
        for i = 1 : n3
            j = n2 + i;
            nsd(j,:) = ['CH0000' num2str(ncd(i))];
            xsd(j,:) = xcd(i,:);%\scale
            % disp([var2 ' ' num2str(i) '. ' nsd(i,:) num2str(xcd(i,1:5)) '; ' num2str(xsd(j,1:5))]);
        end

        ff = [sub '\' var2 '_' num2str(y) '.txt'];
        fp = fopen(ff, 'w');
        for i = 1 : n2 + n3
            fprintf(fp,'%s', nsd(i,:));
            for j = 1 : days
                fprintf(fp,'\t%d',round(xsd(i,j)));
            end
            fprintf(fp, '\n');
            
        end
        fclose(fp);
        tout(k,:) = [v y n1 n2 n3 n2+n3 length(nsd)];
        disp([datestr(now) ' ' num2str(tout(k,:))]);
        k = k + 1;
        toc
    end
end
fclose(flp);
csvwrite([sub '_MergeghcnChina.csv'],tout);
