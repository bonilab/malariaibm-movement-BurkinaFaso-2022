function [results] = loadDirectory(directory, trim) 
    % Prepare the results
    results = zeros(3, 46, 100);
    index = 1;

    % Make sure the directory name is valid
    if ~endsWith(directory, "/")
        directory = append(directory, "/");
    end
    
    % Load the data
    files = dir(strcat(directory, '*.csv'));
    for name = { files.name }
        data = csvread(strcat(directory, char(name)));
        results(:, :, index) = data;
        index = index + 1;
    end

    if trim
        % Trim the first col
        results = results(:, 2:46, :);
    end
end