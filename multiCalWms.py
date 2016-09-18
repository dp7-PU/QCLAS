from specCal import calWms, plotWms
import matplotlib.pyplot as plt
import numpy as np
import hapi

def main():
    hapi.db_begin_pickle('.\\Data')
    laserSpec = {'fMod': 40e3, 'fRamp': 50, 'fS': 1e6, 'aRamp': 600, 'aMod': 290,
                 'tMod': 0.00385, 'tRamp': 0.00665, 'laserDC': 12.35, 'c2p': 10,
                 'fCut': 800, 'phase': 180.0, 'central_wavelength': 1103.55}
    nu = np.linspace(1102, 1105, 1000)
    cList = [-6e-9]
    # cList = [200e-9]
    gasList = []
    # for c in cList:
        # gasList.append({'gas': 'NH3', 'l': 6000, 'p': 1013, 't': 296, 'c': c})

    gasList.append({'gas': 'C2H4', 'l': 3, 'p': 66, 't': 300, 'c': 0.015})

    gasList.append({'gas': 'C2H4', 'l': 3, 'p': 66, 't': 280, 'c': 0.015})

    wmsResults = calWms(gasList, nu, 'Voigt', 2,
                        method='Simulation with parameters', laserSpec=laserSpec,
                        diag=False)

    fig = plt.figure(dpi=100)
    ax = fig.add_subplot(111)
    plotWms(ax, wmsResults, showTotal=True)
    plt.show()

if __name__=='__main__':
    main()