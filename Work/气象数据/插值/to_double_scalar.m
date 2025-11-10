
function v = to_double_scalar(x)
% 把任意单元转成标量double；非数值/空 -> NaN
    if isnumeric(x) && isscalar(x)
        v = double(x);
    elseif isstring(x) || ischar(x)
        s = strtrim(char(x));
        s = regexprep(s, '^\xEF\xBB\xBF', '');  % 去BOM
        s = regexprep(s, '[^\d\+\-\.eE]', '');  % 去掉非数值字符
        if isempty(s)
            v = NaN;
        else
            v = str2double(s);
        end
    else
        v = NaN;
    end
end
