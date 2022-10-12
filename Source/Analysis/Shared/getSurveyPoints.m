function [points] = getSurveyPoints(index)
    survey = csvread('marshall_processed.csv', 1, 0);
    survey = survey(survey(:, 1) == index, 2:3);
    points = zeros(1, 45);
    for ndx = 1:45
        result = survey(survey(:, 1) == ndx, 2);
        if isempty(result); result = 0; end
        points(ndx) = result;
    end
end