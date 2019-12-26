% James Jun 2019 Dec 26
% bug fixed: L3 on +jrclust/+curate/@CureateController/exportFiringRate.m

function exportFiringRate(obj)
    %EXPORTFIRINGRATE
    firingRates = obj.hClust.getFiringRates();
    jrclust.utils.exportToWorkspace(struct('firingRates', firingRates), obj.hCfg.verbose);
end