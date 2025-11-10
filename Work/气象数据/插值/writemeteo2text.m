function [n m] = writemeteo2text(year, varname, outway, sta, xx)

if ~exist([outway '\' varname],'dir')
    system(['mkdir ' outway '\' varname]);
end

ff = [outway '\' varname '\' varname '_' num2str(year) '.txt'];
fp = fopen(ff,'w');

[n m] = size(xx);
sta = char(sta);
for i = 1 : n
    fprintf(fp, '%s', sta(i,:));
    for j = 1 : m
        fprintf(fp, '\t%.2f', xx(i,j));
    end
    fprintf(fp,'\n');
end
fclose(fp);
