function [y,q,sd] = meanbydoy(xx, sd, dn, week,ms)

% ff = 'meteo/Daily8012Filled/PRE/PRE_2005_filled.csv';
% xx = meteo[stations days]
% sd = stations(stations,:)
% dn = 365,days
% week = 8;
% ms = 1 for mean 0 for sum
nn = fix(dn/week)+1;

y = zeros([length(sd) 46]);
q = zeros([length(sd) 46]);

for i = 1 : length(sd)
    for j = 1 : nn
        d1 = (j - 1) * 8 + 1;
        d2 = min(j * 8,dn);
        dw = d2 - d1 + 1;
        
        xd = xx(i,d1:d2);
        
        x1 = find(xd < 30000);
        n1 = length(x1);
        
        if n1 <= 0.6 * dw
            y(i,j) = -9999;
        else
            if ms == 1
                y(i,j) = mean(xd);
            else
                y(i,j) = sum(xd);
            end
        end
        q(i,j) = n1;
    end
end
