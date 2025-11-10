function [yi si ys m_complet] = completeness(sd, x, r,dn)
%% remove station whose days is less than 90%
k = 1;
[n m] = size(x);
yi = []; si = [];m_complet = 0;
for j = 1 : n
    xj = x(j,:);
    xn = sum(xj ~= 32766)/length(xj);
    if xn >= r
        yi(k,:) = xj;
        si(k,:) = sd(j,:);
        dt = xj(xj < 32766);
        ys(k,:) = [x(j,1) mean(dt) mean(dt)*dn std(dt) max(dt) min(dt) length(dt)];
        k = k + 1;
    end    
end
m_complet = k - 1;
% FOR loop of each station

