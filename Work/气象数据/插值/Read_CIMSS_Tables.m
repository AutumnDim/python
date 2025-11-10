function [xid xdt n] = Read_CIMSS_Tables(ff,days)
if exist(ff, 'file')
    fip = fopen(ff, 'r');
    i = 1;
    xid = [];
    xdt = [];
    while fip > 0 && ~feof(fip)
        [gstr] = fscanf(fip,'%s',1);
        % disp([num2str(i) ' ' gstr]);
        if ~isempty(gstr)
           % [vr] = fscanf(fip,'%s',1);
           [gdat] = fscanf(fip,'%f',days+3);
           xid(i,:) = gstr;
           xdt(i,:) = gdat';
           i = i + 1;
        end
    end
    fclose(fip);
    n = i - 1;
else
   disp(['Read failure: ' ff]);
end   % IF file existedend
