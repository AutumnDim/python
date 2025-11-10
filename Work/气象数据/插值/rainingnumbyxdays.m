function [y,q,sd] = rainingnumbyxdays(xx, sid, dn, ms,c_r)
% meanbyxday(yf_daily, sta, year,dn, ms);
% ff = 'meteo/Daily8012Filled/PRE/PRE_2005_filled.csv';
% xx = meteo[stations days]
% sd = stations(stations,:)
% dn = 365,days
% week = 15;
% ms = 1 for mean 0 for sum
nj = unique(dn);
nn = length(nj);

y = zeros([nn length(sid)]);
q = zeros([nn length(sid)]);

for i = 1 : length(sid)
    for j = 1 : nn
        dw = sum(dn == nj(j));
        if c_r == 1
            xd = xx(i,dn == nj(j));
        else
            xd = xx(dn == nj(j), i);
        end
        x1 = xd(xd < 30000 & xd > -9000);
        n1 = length(x1);
        xr = (xd >= 0.001);
        if ms == 1
            y(j,i) = mean(xd);
        else
            y(j,i) = sum(xr);
        end        
        sd(j,i) = std(xd);
        q(j,i) = n1/dw;
    end
end

