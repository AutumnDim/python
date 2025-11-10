% function readFCERN
close all; clear all; clc;
wks = '\\192.168.204.55\data\Workspace\';

fsite = [wks 'STSZHANGLI\CERN\张多才提供CNERN和CERN台站站点位置.xls'];
[~,sid,~] = xlsread(fsite,'cern站点位置', 'B2:B40');
[lat,~,~] = xlsread(fsite,'cern站点位置', 'D2:D40');
[lon,~,~] = xlsread(fsite,'cern站点位置', 'C2:C40');
[elv,~,~] = xlsread(fsite,'cern站点位置', 'F2:F45');
% sid{strcmp(sid,'BNF')} = 'XSBN';
sid{strcmp(sid,'MXF')} = 'MX';
sid{strcmp(sid,'QYA')} = 'QYZ';

% fxls = [wks 'MeteoGrid\Stations\森林站气象数据.xlsx'];
fxls = [wks 'MeteoGrid\Stations\CERN\温度-森林站输入数据-11个站-2001-2015xlsx'];

[st,sheets,fmt] = xlsfinfo(fxls);
ns = length(sheets);
geo = [];
for i = 1 : ns
    disp(sheets{i});
    [dat,txt,raw] = xlsread(fxls,sheets{i});
    site = raw(2);
    js = find(strcmp(sid, site{1}) > 0);
    geo(i,:) = [lat(js),lon(js),elv(js)];
    
    hdr = raw(1,:);
    nd = size(dat,1);
    flg(3) = find(strcmp(hdr, 'MEAN002')>0);
    flg(2) = find(strcmp(hdr, 'MAX0002')>0);
    flg(1) = find(strcmp(hdr, 'MIN0002')>0);
    flg(4) = find(strcmp(hdr, 'Pre003')>0);
    XT = [];
    for v = 1 : 4
        for j = 1 : nd
            s0 = raw{j+1,flg(v)};
            if ~isnan(s0)
                if ischar(s0)
                    XT(j,v) = str2num(s0);
                else
                    XT(j,v) = s0;
                end
            else
                XT(j,v) = -99.99;
            end
        end
    end
    fcsv = [wks 'MeteoGrid\Stations\CERN\tmp_CERN_' site{1} '.csv'];
    disp(fcsv);
    disp([min(dat(:,1)), max(dat(:,1))]);
    
    fp = fopen(fcsv, 'w');
    fprintf(fp, '%.4f,%.4f\n', geo(i,1), geo(i,2));
    fclose(fp);
    
    xdt = [dat(:,1:3),XT];
    
    dlmwrite(fcsv,xdt,'delimiter',',','-append');   
end