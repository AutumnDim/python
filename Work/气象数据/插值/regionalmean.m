function [yst,qst] = regionalmean(dt,sd,ms,year,days)
nn = fix(days/8)+1;
y = zeros([length(sd) 47]);
q = zeros([length(sd) 47]);
j = 1;
[n m] = size(dt);
for i = 1 : n
    dti = dt(i,:);
    dti = dti(dti < 30000);
    n1 = length(dti);
    if n1 <= 1. * days
        y(i,47) = -9999;
    else
        if ms == 1
            y(i,47) = mean(dti);
        else
            y(i,47) = mean(dti)*days;
        end
    end
    q(i,47) = n1;
    
    for j = 1 : nn
        d1 = (j - 1) * 8 + 1;
        d2 = min(j * 8, days);
        dn = d2-d1+1;
        xd = dt(i,d1:d2);
        
        x1 = find(xd < 30000);
        n1 = length(x1);
        
        if n1 <= 0.9*dn
            y(i,j) = -9999;
        else
            if ms == 1
                y(i,j) = mean(xd);
            else
                y(i,j) = mean(xd)*dn;
            end
        end
        q(i,j) = n1;
    end
end

stat = unique(sd(:,1:2),'rows');
% disp(stat);
str0 = sd(strmatch('CH',sd(:,1:2)),:);
chsd = str2num(str0(:,3:11));
rgsd = 50:59;

[nst m] = size(stat);
yst = []; qst=[];
% Each country
for i = 1 : nst
    nsx = find(strmatch(stat(i,:),sd(:,1:2)));
    yst(i,1) = i * 100;
    yst(i,2) = year;
    qst(i,1:2)= [i*100 year];
    for j = 1 : 47
        xst = y(nsx,j);
        xsj = xst(xst>-9900);
        qsj(i,j+2) = length(xst);
        yst(i,j+2) = mean(xsj);
%         yst(i,j+2+47) = std(xsj);
%         yst(i,j+2+94) = min(xsj);
%         yst(i,j+2+141) = max(xsj);
    end
end
for i = 1 : length(rgsd)
    rg = ['CH0000' num2str(rgsd(i))];
    nsx = find(strmatch(rg,sd(:,1:8)));
    yst(i+nst,1) = rgsd(i);
    yst(i+nst,2) = year;
    qst(i+nst,1:2)= [i*100 year];
    for j = 1 : 47
        xst = y(nsx,j);
        xsj = xst(xst>-9900);
        qsj(i+nst,j+2) = length(xst);
        yst(i+nst,j+2) = mean(xsj);
%         yst(i+nst,j+2+47) = std(xsj);
%         yst(i+nst,j+2+94) = min(xsj);
%         yst(i+nst,j+2+141) = max(xsj);
    end
end
















