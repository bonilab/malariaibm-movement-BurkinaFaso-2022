% diagnostic_plots.m
%
% Various functions that can be used to create plots for survey data as
% well as simuation data.

% Plot the data from the survey
plot_survey_bar('Shared/bfa_survey_mapped.csv')
plot_survey_heatmap('Shared/bfa_survey_mapped.csv')

% Plot the data from the simulation
plot_trips_heatmap('data/rho-0.25-cellular.csv', 'data/rho-0.25-district-map.csv');

function [] = plot_survey_bar(filename)
    data = csvread(filename, 1, 0);

    % Filter out Boulkiemde (4), Zoundweogo (22), Leraba (27)
    data = data(data(:, 1) ~= 4, :);
    data = data(data(:, 1) ~= 22, :);
    data = data(data(:, 1) ~= 27, :);

    % Data to keep Kadiogo (14), Kourweogo (16), Bazega (21)
    plot = zeros(size(unique(data(:, 1)), 1), 45);

    ndx = 1;
    for source = transpose(unique(data(:, 1)))
        filtered = data(data(:, 1) == source, :);
        disp(sprintf("District %d, count: %d", source, size(filtered, 1)));
        for destination = 1:45
            plot(ndx, destination) = sum(filtered(:, 2) == destination);
        end
        ndx = ndx + 1;
    end

    X = categorical({'Kadiogo', 'Kourweogo', 'Bazega'});
    X = reordercats(X, {'Kadiogo', 'Kourweogo', 'Bazega'});
    bar(X, plot);
    title('Burkina Faso Movement from Source to Destination District');
    ylabel('Count of Trips');
end

% Generate a heatmap of the survey data
function [] = plot_survey_heatmap(filename)
    % Load the data
    data = csvread(filename, 1, 0);

    % Prepare the plot, 45 districts in mapping
    plot = zeros(45, 45);

    % Single incriment
    for ndx = 1:size(data, 1)
        source = data(ndx, 1);
        destination = data(ndx, 2);
        plot(source, destination) = plot(source, destination) + 1;
    end
    
    % Repace zero with NaN since true zero was not recorded
    plot(plot == 0) = NaN;
    
    % Load the district names
    names = readtable('../Common/bfa_districts.csv');

    % Prepare the heatmap
    hm = heatmap(plot);
    hm.MissingDataColor = [1.0 1.0 1.0];
    hm.Title = 'Burkina Faso Movement from Source to Destination District';
    hm.YLabel = 'Source District';
    hm.YDisplayLabels = table2cell(names(:, 3));
    hm.XLabel = 'Destination District';
    hm.XDisplayLabels = table2cell(names(:, 3));
    
    graphic = gca;
    graphic.FontSize = 24;
end

% Plot a heat map of all of the trips as recorded from the simuation.
function [] = plot_trips_heatmap(filename, map_filename)
    TRIPS = 4; DESTINATION = 6;

    % Load the data
    data = csvread(filename, 1, 0);
    mapping = csvread(map_filename, 1, 0);
    X = 4; Y = 5;

    % Prepare the "map" for the trips
    rows = max(mapping(:, X) + 1);
    cols = max(mapping(:, Y) + 1);

    % Zero out the matrix
    map = NaN(rows, cols);

    % Note the interdistrict movement to the given location
    for index = transpose(unique(data(:, DESTINATION)))
        row = mapping(mapping(:, 3) == index, X) + 1;
        col = mapping(mapping(:, 3) == index, Y) + 1;
        map(row, col) = sum(data(data(:, DESTINATION) == index, TRIPS));
    end

    % Plot the heatmap
    hm = heatmap(map, 'Colormap', parula);
    hm.MissingDataColor = [1.0 1.0 1.0];
    hm.Title = "Modeled Trips to Destination Cell Cumulative for One Month";
    hm.XDisplayLabels = repmat(' ', cols, 1); 
    hm.YDisplayLabels = repmat(' ', rows, 1);
    grid off;
    graphic = gca;
    graphic.FontSize = 26;
end