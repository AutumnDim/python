close all; clear all; clc;
tic
wks = 'H:\Workspace\China1km\MeteoGrid';

yr1 = 1980; yr2 = 2010;

hdr = 'H:\Workspace\China1km\china1km.hdr';
prj = 'H:\Workspace\China1km\china1km.prj';

parfor dy = 1 : 46
    jday = (dy - 1) * 8 + 1;
    for yr = yr1 : yr2
        ff = [wks, '\TAVG\TAVG_', num2str(yr * 1000 + jday), '.flt'];
        fip = fopen(ff, 'r');
        dat = fread(fip, [4998, 4088], 'float32');
        fclose(fip);
        
        if yr == yr1
            mdt = dat;
        else
            mdt = mdt + dat;
        end
    end
    mdt = mdt / (yr2 - yr1 + 1);
    fout = [wks, '\MDT\MDT_', num2str(jday, '%03d'), '.flt'];
    fop = fopen(fout, 'w');
    fwrite(fop, mdt, 'float32');
    fclose(fop);
    
    fout = [wks, '\MDT\MDT_', num2str(jday, '%03d'), '.hdr'];
    [s1, s2] = system(['copy ' hdr ' ' fout]);
    
    fout = [wks, '\MDT\MDT_', num2str(jday, '%03d'), '.prj'];
    [p1, p2] = system(['copy ' prj ' ' fout]);
    
    bnd = quantile(mdt(dat > -900), [0.05, 0.95]);
    imagesc(mdt', bnd); axis off;
    colorbar('horizonal');
    fout = [wks, '\MDT\MDT_', num2str(jday, '%03d'), '.png'];
    saveas(gca, fout);
    disp(fout);
end
toc