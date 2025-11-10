function [gid, geo, data] = LookCoincident(sd, s1, x1)
% clc;tic
[n m] = size(x1);
% n = 10;
dc = []; k = 1; m = 1;
gid = []; geo = []; data = [];
for i = 1 : n
    dx = [];c = 1;
    for j = i+1 : n-1
        dx(c) = ((s1(i,1) - s1(j,1)) ^ 2 + (s1(i,2) - s1(j,2)) ^ 2) ^ 0.5;
        if dx(c) < 0.2
            dc(m,:) = [i j];
            disp(['i. ' num2str(i) ' ' (sd(i,:)) ' '  num2str(s1(i,:), '%10.2f'), '  ', num2str(dx(c))]);
            disp(['j. ' num2str(j) ' ' (sd(j,:)) ' '  num2str(s1(j,:), '%10.2f'), '  ', num2str(dx(c))]);
            % disp(num2str([m, i,j,sd(i),sd(j), s1(i,:), s1(j, :)], '%8.0f'))
            m = m + 1;
        end
        c = c + 1;
    end
end
if m - 1 > 0
    k = 1;
    for i = 1 : n
        if isempty(find(dc(:,2)==i, 1))
            gid(k,:) = sd(i,:);
            geo(k,:) = s1(i,:);
            data(k,:) = x1(i,:);
            k = k + 1;
        % else
            % disp(['c. ' num2str(i) ' ' (sd(i,:)) ' '  num2str(s1(i,:))]);
        end 
    end
else
    gid = sd; geo = s1; data = x1;
end
% m0 = length(s1) - length(geo);
% toc