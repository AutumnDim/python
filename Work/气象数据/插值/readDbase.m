function [xid xdt n] = readDbase(ff,days)
if exist(ff, 'file')
    fip = fopen(ff, 'r');
    i = 1;
    xid = [];
    xdt = [];
    while fip > 0 && ~feof(fip)
        [gstr] = char(fscanf(fip,'%s',1));
        if length(gstr) > 0
           % [vr] = fscanf(fip,'%s',1);
           [gdat] = fscanf(fip,'%f',days);
           if length(gdat) == days
               xid(i,:) = gstr;
               xdt(i,:) = gdat';
               i = i + 1;
           end
        end
        % if i == 222
        %    disp(i)
        % end
    end
    fclose(fip);
    n = i - 1;
else
    xid = -9999; 
    xdt = 9999;
    n = 0;
   disp(['Read failure: ' ff]);
end   % IF file existedend
