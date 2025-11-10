% %% filling 1980's
% for dy = 1 : 46
%     jday = (dy - 1) * 8 + 1;
%     ff = ['H:\Workspace\China1km\albedo\BSA1982' num2str(jday, '%03d'), '.flt'];
%     fout = ['H:\Workspace\China1km\albedo\BSA1980' num2str(jday, '%03d'), '.flt'];
%     [s1, s2] = system(['copy ' ff ' ' fout]);
% end
% %% filling 1981001~161
% for dy = 1 : 21
%     jday = (dy - 1) * 8 + 1;
%     ff = ['H:\Workspace\China1km\albedo\BSA1982' num2str(jday, '%03d'), '.flt'];
%     fout = ['H:\Workspace\China1km\albedo\BSA1981' num2str(jday, '%03d'), '.flt'];
%     [s1, s2] = system(['copy ' ff ' ' fout]);
% end
% %% filling 2018's
% for dy = 1 : 46
%     jday = (dy - 1) * 8 + 1;
%     ff = ['H:\Workspace\China1km\albedo\BSA2017' num2str(jday, '%03d'), '.flt'];
%     fout = ['H:\Workspace\China1km\albedo\BSA2018' num2str(jday, '%03d'), '.flt'];
%     [s1, s2] = system(['copy ' ff ' ' fout]);
% end
%% filling 1994's
for dy = 34 : 46
    jday = (dy - 1) * 8 + 1;
    f1 = ['H:\Workspace\China1km\albedo\BSA1993' num2str(jday, '%03d'), '.flt'];
    fp = fopen(f1, 'r');
    x1 = fread(fp, [4998, 4088], 'float32');
    fclose(fp);
    
    f2 = ['H:\Workspace\China1km\albedo\BSA1995' num2str(jday, '%03d'), '.flt'];
    fp = fopen(f2, 'r');
    x2 = fread(fp, [4998, 4088], 'float32');
    fclose(fp);
    
    dat = (x1 + x2) * 0.5;
    
    fout = ['H:\Workspace\China1km\albedo\BSA1994' num2str(jday, '%03d'), '.flt'];
    
    figure(1);
    imagesc(dat', [0, 10000]);
    colorbar('horizonal');
    
    
    fp = fopen(fout, 'w');
    fwrite(fp, dat, 'float32');
    fclose(fp);
end

    
    % xdat = dat / 100;
    %
% ff = 'H:\Workspace\China1km\Parameters\lat';
% fp = fopen(ff, 'r');
% dat = fread(fp, [4998, 4088], 'int16');
% fclose(fp);
%
% xdat = dat / 100;
%
% imagesc(xdat', [0, 55]);
% colorbar('horizonal');
%
% ff = 'H:\Workspace\China1km\Parameters\LAT_China1km.flt';
% fp = fopen(ff, 'w');
% fwrite(fp, xdat, 'float32');
% fclose(fp);