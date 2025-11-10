function [yx,ys,yns] = staselect(gid,dt,sd)


j = 1; k = 1;
[n m] = size(dt);
yx=[];ys=[];yns=[];
for i = 1 : n
   sdi = sd(i,:);
   ix = strmatch(sdi,gid);
   if ~isempty(ix)
       yx(j,:) = dt(i,:);
       ys(j,:) = sdi;
       j = j + 1;
   else
       yns(k,:) = sdi;
       k = k + 1;
   end
end
if k == 1
    yns=[];
end