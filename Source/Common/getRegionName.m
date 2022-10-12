% getRegionName.m
%
% Get the region name and sort order / id from the file.
function [name, sort] = getRegionName(index)
    % Determine where the location file is
    filename = strrep(mfilename('fullpath'), mfilename, 'bfa_regions.csv');
    
    % Open and return the name and sort order
    data = readtable(filename);
    name = string(data(data.Sort == index, 3).ADM1_NAME{1});
    sort = index;
end