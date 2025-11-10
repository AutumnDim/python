function [b, r, p, tp] = mypiecewise(x,y,brk)
n = size(x);
if n(1) < n(2)
    x = x';
end
n = size(y);
if n(1) < n(2)
    y = y';
end
m = length(brk);
ps = ones([2 5])*(-999); bs = ones([2 5])*(-999); rs = ones([2 1])*(32767);
if m > n
    return
end    
if min(brk) < min(x)
    brk(brk<min(x)) = min(x);
end
if max(brk) > max(x)
    brk(brk > max(x)) = max(x);
end
j = 1;
tpy=[];
for i = 1 : m
    % disp(i)
    x1 = x(x<brk(i));
    y1 = y(x<brk(i));
    n1 = length(x1);
    
    x2 = x(x>=brk(i));
    y2 = y(x>=brk(i));
    n2 = length(x2);
    if n1 > 3 && n2 > 3
        [b1, ~, r1, ~, p1] = regress(y1, [ones([n1,1]) x1]);
        [b2, ~, r2, ~, p2] = regress(y2, [ones([n2,1]) x2]);

        bs(j,:) = [b1(1) b1(2) b2(1) b2(2) sum(r1.^2)];
        ps(j,:) = [p1(1) p1(3) p2(1) p2(3) sum(r2.^2)];
        rs(j) = sum([r1; r2].^2);
        tpy(j) = brk(i);
        j = j + 1;
    end
end
r = min(rs);
tp = tpy(rs==r);
n = length(tp);
if n > 1
    tp = tp(1);
end
b = bs(tpy==tp,:);
p = ps(tpy==tp,:);


    
