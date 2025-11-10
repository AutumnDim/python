close all; clear all; clc;
yr1 = 1980; yr2 = 2000;
np = 960; nl = 880;
wks = 'D:\STSZHANGLI\ShaoxGrid';

for i = 1 : 46
    jd = (i-1)* 8 + 1;
    % disp(jd);
    for yr = yr1 : yr2
        ff = [wks '\TAVG\TAVG_' num2str(yr * 1000 + i) '.flt'];
        if exist(ff, 'file')
            fp = fopen(ff, 'r');
            x0 = fread(fp, [np nl], 'float32');
            fclose(fp);    
            
            if yr == yr1
                x2 = x0;
                k = 1;
            else
                x2 = x2 + x0;
                k = k + 1;
            end
        end
    end
    disp([jd k])
    if k >= yr2 - yr1 + 1
        ff = [wks '\MTA\MTA_' num2str(jd, '9999%03d') '.flt'];
        fp = fopen(ff, 'w');
        fwrite(fp, x2/k, 'float32');
        fclose(fp);
    end
end