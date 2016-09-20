import numpy as np
import matplotlib.pyplot as plt
import specCal

def main():
    nu = np.linspace(1103, 1105, 1000)
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)
    gasList = [{'gas': 'NH3', 'l': 2, 't': 293.15, 'p': 990, 'c': 300e-9},
               {'gas': 'NH3', 'l': 2, 't': 293.15, 'p': 990, 'c': 300e-9}]
    unitDict = {'c': 'V ratio', 'l': 'cm', 'p': 'hPa', 't': 'K'}
    results1 = specCal.calDas(gasList, nu, 'Voigt', 'Absorbance', unitDict=unitDict)
    print results1
    specCal.plotDas(ax1, results1, 'Absorbance')
    fig1.show()

if __name__=='__main__':
    main()