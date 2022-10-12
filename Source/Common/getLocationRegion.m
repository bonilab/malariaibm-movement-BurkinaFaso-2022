% getLocationRegion.m
%
% Get the region name and sort order / id from the file.
function [name, sort] = getLocationRegion(index)
    % Determine where the location file is
    filename = strrep(mfilename('fullpath'), mfilename, 'bfa_regions.csv');
    
    % Open and return the name and sort order
    data = readtable(filename);
    name = string(table2cell(data(index, 3)));
    sort = cell2mat(table2cell(data(index, 4)));
end