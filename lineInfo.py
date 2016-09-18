"""
Define nmolec class that stores information for all gas.

Da Pan, 02122016.
"""
import scipy.io as io
import os

molecWeight = {"N2O": 44.0055,
               "CO": 28.0101,
               "H2O": 18.0153,
               'C2H2': 26.0373,
               'NH3': 17.031,
               'C2H4': 28.05,
               'SO2': 64.064,
               'O3': 47.9982,
               'CO2': 44.0095,
               'N2': 28.01340}


class ngas:
    def __init__(self):
        self.T = []  # T is a list storing T for each gas
        self.P = []  # P is a list storing P for each gas
        self.molec = []  # Name list of molecules
        self.hinfo = {}  # A dict to store HITRAN info
        self.location = "./Data"  # Location of HITRAN line info files

    # TODO for now the function reads mat file, future version should read txt directly
    def __getinfo(self, molec):
        """ Get gas line information from mat files
        :param molec: molec name of gas
        :return: None
        Note: User is not recommended to use this function. Since it won't add
        """
        cwd = os.getcwd()
        os.chdir(self.location)

        molecset = set(molec)  # Get rid of redundancy for dict

        # Load mat file
        if molec not in self.hinfo.keys():
            self.hinfo[molec] = io.loadmat(molec + '.mat')

            # Get rid of MATLAB info
            self.hinfo[molec].pop('__version__')
            self.hinfo[molec].pop('__globals__')
            self.hinfo[molec].pop('__header__')

        os.chdir(cwd)

    def addgas(self, molec, T, P):
        """ Add single gas to the class.
        :param molec: molec name of the gas
        :param T: temperature of the gas
        :param P: pressure of the gas
        :return: None
        """
        if type(molec) == str:
            print("Please enter a gas name. For multiple gases, use setngas instead.")  # Prompt for correct input
        else:
            self.molec.append(molec)
            self.T.append(T)
            self.P.append(P)
            self.__getinfo(molec)

    def setngas(self, molecTable):
        """ Add multiple gases to the class,
        :param molecTable: list of tuble, e.g. [('NH3', 293.15, 1.013e5),
                                                ('H2O', 283.15, 1.015e5)]
        :return: None
        """
        for gas in molecTable:
            self.molec.append(gas[0])
            self.T.append(gas[1])
            self.P.append(gas[2])
            self.__getinfo(gas[0])

    def clear(self):
        """
        Clear all previously stored information
        """
        self.__init__()


def main():
    testline = ngas()
    testline.setngas([('NH3', 300, 1.013e5),
                      ('C2H4', 300, 30 / 760 * 1.013e5),
                      ('NH3', 293.15, 50 / 760 * 1.013e5)])
    print(testline.hinfo)
    print(testline.molec)
    print(testline.T)
    print(testline.P)

if __name__ == '__main__':
    main()
