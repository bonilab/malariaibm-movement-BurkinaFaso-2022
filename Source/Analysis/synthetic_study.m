% synthetic_study.m
%
% This script is intended to generate synthetic "surveys" of movements in
% Burkina Faso based upon the equation in Marshall et al. (2018)
addpath('Shared');
clear;

% Make sure the output path exists
if ~exist('out', 'dir'), mkdir('out'); end

study(1000)

function [] = study(trials)

    % Load the data used for the trials
    [distances, populations] = loadData();
    
    % Sweep the rhos for the given number of trials
    results = [];
    for rho = 0.05:0.05:1.8
        lookup = generateLookup(distances, populations, rho);
        directory = sprintf('rho-%.2f', rho);
        mkdir(directory);

        % Conduct the trials
        for count = 1:trials
           trial(directory, count, lookup);
        end

        % Calcluate the MSE
        mse = calc_mse(directory);

        % Zip the data, move it to the archive, delete the old directory
        file = append(directory, '.zip');
        zip(file, directory);
        movefile(file, 'out');
        rmdir(directory, 's');

        results = [results; rho mse ];
    end

	% Save the sumary reuslts to disk
    csvwrite('out/rho-results.csv', results);

    % Plot the summary results
    plot(results(:, 1), results(:, 2));
    title('Sweep of Rho Values, Synehetic versus Survey Data');
    xlabel('Rho value');
    ylabel('Mean Squared Error');
end

function [mse] = calc_mse(directory)
    data = loadDirectory(append(directory, "/"), false);
    
    mse = 0;
    for province = [ 13 15 20 ]
        % Prepare the sample
        sample = squeeze(data(data(:, 1) == province, :, :));
        sample(1, :) = [];
        sample = transpose(sample);
        points = getSurveyPoints(province);
        
        % Calculate the MSE
        for ndx = 1:45
            mse = mse + (sample(ndx) - points(ndx))^2;
        end
    end
    mse = mse / (45 * 3);
end

% Perform the trial
function [] = trial(directory, count, lookup) 
    % Kadiogo (13) / 403, Kourweogo (15) / 503, Bazega (20) / 387
    SAMPLING = [ 13 403; 15 503; 20 387 ];

    results = zeros(3, 46);
    for source = 1:size(SAMPLING, 1)
        results(source, 1) = SAMPLING(source, 1);
        for sample = 1:SAMPLING(source, 2)
            district = getDistrict(lookup(source, 2:end));
            results(source, district + 1) = results(source, district + 1) + 1;
        end
    end
    csvwrite(sprintf('%s/synthentic_%03d.csv', directory, count), results);
end

% Get a random district based upon the values provided
function [district] = getDistrict(values)
    % Get a random value
    value = rand;
    
    % Check the first index
    if value <= values(1); district = 1; return; end
    
    % Scan the rest, will return 45 if we check them all
    for district = 2:45
        if value <= values(district); return; end
    end
end

% Load the data from disk and align it.
function [distances, populations] = loadData() 
    % Load the population data, align the columns such that,
    % 1 = FID, 2 = population
    populations = csvread('../Common/bfa_2006_pop.csv', 1, 0);
    populations = populations(:, 2:3);

    % Load the distance data, align the columns such that,
    % 1 = source FID, 2 = destination FID, 3 = distance in KM
    distances = csvread('Shared/marshall_survey_centroid.csv', 1, 0);
    distances = distances(:, [2:3 6]);

    % Shift to one indexed
    distances(:, 2) = distances(:, 2) + 1;
    populations(:, 1) = populations(:, 1) + 1;
end

% Get the bounding dimension, where 0 is width and 1 is length,
% and 2 is the mean of the two
function [distance] = get_bound(fid, dimension)
    bounding = csvread('Shared/bfa_survey_bounding.csv', 1, 0);
    FID = 1; WIDTH = 2; LENGTH = 3;
    
    filter = bounding(bounding(:, FID) == fid, :);
    if dimension == 0
        distance = filter(1, WIDTH);
    elseif dimension == 1
        distance = filter(1, LENGTH);
    elseif dimension == 2
        distance = (filter(1, WIDTH) + filter(1, LENGTH)) / 2;
    else
        error("Invalid dimension");
    end
end

% Prepare the lookup table
function [lookup] = generateLookup(distances, populations, rho)
    % 1 = source FID, 2 to 46 - probablity where index is destination FID
    lookup = zeros(3, 46); row = 1;
    for source = transpose(unique(distances(:, 1)))
        lookup(row, 1) = source;
        for column = 1:45
            % Get the distance
            filtered = distances(distances(:, 1) == source, :);
            filtered = filtered(filtered(:, 2) == column, :);
            if size(filtered, 1) ~= 0
                distance = filtered(1, 3);
            else
                distance = get_bound(source, 2);               
            end
            
            % Get the population
            population = populations(populations(:, 1) == column, 2);

            % Calculate
            lookup(row, column + 1) = model(population, distance, rho);
        end
        row = row + 1;
    end
    
    % Update the values so we can scan then after a random draw
    for row = 1:size(lookup, 1)
        values = lookup(row, 2:end);
        total = sum(values);
        values(1) = values(1) / total;
        for column = 2:size(values, 2)
            values(column) = values(column - 1) + values(column) / total;
        end
        lookup(row, 2:end) = values;
    end
end

% Gravity model with kernel function per Marshall et al. (2018)
function [result] = model(pop, dist, rho)
    r = 1.342; a = 1.27; 
    
    p = 10^rho;
    
    % Replace above to test for log_e
    %p = exp(rho);
    
    
    kernel = (1 + (dist / p))^(-a);
    result = pop^r * kernel;
end