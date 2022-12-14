import numpy as np
from ..physics.kinematic import kinematic
import random, copy

class spaceship:
    """
    Shape of vals
                [x]                 [v_x]
    position =  [y] [m], velocity = [v_y] [m/s]
                [z]                 [v_z]

                    [(F_x), (F_-x)]
    boosterforce =  [(F_y), (F_-y)] [N], dims = [(dim_x) (dim_y) (dim_z)] ONLY + OR -, NO VALUES!
                    [(F_z), (t_-z)]
                    
                       [(sigma_Fx)]
    boosterforceDev =  [(sigma_Fy)] [N]
                       [(sigma_Fz)]

    boosterforce is absolute.

    mass = [m] [kg]
    """

    def __init__(self, position: list = [0, 0, 0], mass: int = 1000, boosterforce: list = [[100, 100], [100, 100], [100, 100]], velocity: list = [0, 0, 0], boosterforceDev: list = [10.3, 10.3, 10.3], nPredict: int = 10, deltaT: float = 0.1):
        self._boosterforce = np.array(boosterforce) # [N]
        self.__mass = mass # [kg]
        self.__accelDev = np.array([[boosterforceDev[0]], [boosterforceDev[1]], [boosterforceDev[2]]])/mass
        self.__position = np.array([[position[0]], [position[1]], [position[2]]])
        self.__velocity = np.array([[velocity[0]], [velocity[1]], [velocity[2]]])

        self.__computer = boardcomputer(self, nPredict, deltaT)

    # getter/setter
    def setPosition(self, position):
        self.__position = np.array(position)
    def getPositionList(self):
        return self.__position.reshape(3).tolist()
    def getPosition(self):
        return self.__position

    def setVelocity(self, velocity):
        self.__velocity = np.array(velocity)
    def getVelocityList(self):
        return self.__velocity.reshape(3).tolist()
    def getVelocity(self):
        return self.__velocity

    def setMass(self, mass):
        #print(f"Spaceship->setMass: {mass}")
        self.__mass = mass
    
    def getMass(self):
        return self.__mass

    def setBoosterforce(self, boosterforce):
        #print(f"Spaceship->setBoosterforce: {boosterforce}")
        self._boosterforce = np.array(boosterforce)

    def getBoosterforce(self):
        return self._boosterforce.tolist()
    
    def setBoosterforceDeviation(self, var):
        #print(f"Spaceship->setAccelDevaition: accelVar pre: {self.__computer.accelVar} with variable var as: {np.sqrt(np.abs(self.__computer.accelVar))}")
        self.__accelDev = np.array(var)/self.__mass
        print(f"Spaceship->setBoosterforceDev: accelDev after: {self.__accelDev} with variable var as: {var} and mass {self.__mass}")
    def getBoosterforceDeviation(self):
        return self.__accelDev*self.__mass
    def getBoosterforceDeviationList(self):
        return (self.__accelDev*self.__mass).reshape(3).tolist()
        
    def getAcceleration(self, dims):
        a = np.zeros((3, 1))
        for idx in range(len(dims)):
            if dims[idx] == '-': 
                a[idx, 0] = -1*self._boosterforce[idx, 0]
            elif dims[idx] == '+':
                a[idx, 0] = self._boosterforce[idx, 1]
            else:
                a[idx, 0] = 0
        return a/self.__mass

    def setDeltaT(self, var):
        self.__computer.deltaT = var

    def getDeltaT(self):
        return self.__computer.deltaT
    
    def setNPrediction(self, val):
        #print("Spaceship->setNPrediction: val: %d" % (val))
        #print(f"Spaceship->setNPrediction: nPrediction pre: {self.__computer.nPrediction}")
        self.__computer.nPrediction = val
        #print(f"Spaceship->setNPrediction: nPrediction after: {self.__computer.nPrediction}")

    def getNPrediction(self):
        return self.__computer.nPrediction

    def getMeasurePoint(self):
        return self.__computer.measurePoint
    def getMeasurePointList(self):
        return self.__computer.measurePoint.reshape(3).tolist()

    def getPrediction(self):
        return self.__computer.predictVal
    
    def getDeviation(self):
        return self.__computer.sigma

    # calculating methods
    def calculatePosition(self, time, dim):
        a = self.getAcceleration(dim)
        for idx, elem in enumerate(a):
            a[idx] = random.gauss(elem, self.__accelDev[idx, 0])
            #a[idx] = np.random.normal(elem, self.__boosterforceDev)
            pass
        self.__position = kinematic.acceleration2position(a, time, self.__velocity, self.__position)
        self.__velocity = kinematic.acceleration2velocity(a, time, self.__velocity)
        #print('Spaceship calculatePosition: x=%f.1, y=%f.1, z=%f.1' %(self.__position[0,0],self.__position[1,0],self.__position[2,0]))
        return self.__position

    def sendCompute(self, dims: list, all: bool = False):
        self.__computer.compute(dims, all)

    def sendUpdate(self, dims: list, measureDeviation: list = [40, 40, 0]):
        x = random.gauss(self.__position[0].item(), measureDeviation[0])
        y = random.gauss(self.__position[1].item(), measureDeviation[1])
        z = random.gauss(self.__position[2].item(), measureDeviation[2])
        #x = np.random.normal(self.__position[0].item(), measureDeviation[0])
        #y = np.random.normal(self.__position[1].item(), measureDeviation[1])
        #z = np.random.normal(self.__position[2].item(), measureDeviation[2])
        #x = self.__position[0].item()
        #y = self.__position[1].item()
        #z = self.__position[2].item()
        #print("Spaceship->sendUpdate: measureDevaiation pre: ")
        #print(measureDevaition)
        #print("Spaceshipe->sendUpdate: measureDevbiation to measureVariance:")
        #print(l_measureVariance)

        self.__computer.update([x, y, z], measureDeviation)
        #print("Spaceship->sendUpdate: dims")
        #print(dims)
        accel = self.getAcceleration(dims)
        #print(f"Spaceship->sendUpdate: accel: {accel}")
        #print(f"Spaceship->sendUpdate: accelVar: {accelVar}")
        self.__computer.compute(accelDev= self.__accelDev, accel = accel, all = True)


class boardcomputer:
# to calculate predicted position, just call <<compute>>:
#   for all: bool=True
#   just next new prediction: bool=False
#   provide current control input
#
# to insert measure values, call <<update>>
#   give measure values and certainity values

    def __init__(self, spaceship: spaceship, predictPosition: int = 10, deltaT: float = 0.1):
        # Mittelwert des Systemzustandes
        position = spaceship.getPosition()
        velocity = spaceship.getVelocity()
        acceleration = np.zeros((3, 1))
        self.__x = np.bmat([[position], [velocity], [acceleration]])
        self.__deltaT = deltaT
        self.__measurepoint = position

        self.__newStorageAvaible = False

        # Covarianz des SS
        self.__P = np.eye(9)
        
        self.__nPredict = predictPosition
        self.__newNPredict = self.__nPredict
        self.__predict = [[], [], [], [], [], [], [], [], []]
        for i in range(predictPosition):
            for dim in range(9):
                self.__predict[dim].append(dim * predictPosition + i)

        self.__sigma = copy.deepcopy(self.__predict)
        self.__newPredict = copy.deepcopy(self.__predict)
        self.__newSigma = copy.deepcopy(self.__predict)
    
    #############################
    #### Getter/Setter

    @property
    def pos(self):
        return self.__x[0:3]

    @property    
    def vel(self):
        return self.__x[3:6]

    @property
    def accel(self):
        return self.__x[6:9]

    @property
    def x(self):
        return self.__x     # current state of the system

    @property
    def P(self):
        return self.__P     # current variance of the system

    @property
    def sigma(self):
        return self.__sigma # provides the standard deviation*3 of the past n iteration

    @property
    def predictVal(self):
        return self.__predict   # provides the estimated position of the past n iteration

    @property
    def deltaT(self):
        return self.__deltaT

    @deltaT.setter
    def deltaT(self, var):
        self.__deltaT = var

    @property
    def nPrediction(self):
        #print("Boardcomputer->nPrediction: getter called")
        return len(self.__predict[0])
    
    @nPrediction.setter
    def nPrediction(self, val: int):
        #print("Boardcomputer->nPrediction: val: %d" % (val))
        diff = val - self.__nPredict
        #print(f"Boardcomputer->nPrediction.setter: target is: {val}, current amount: {self.__nPredict}")
        #print(f"Boardcomputer->nPrediction.setter: difference {diff}")
        self.__newSigma = copy.deepcopy(self.__sigma)
        self.__newPredict = copy.deepcopy(self.__predict)
        #print(f"Boardcomputer->nPrediction.setter: old dim: {len(self.__newPredict[0])}")
        for idx in range(len(self.__newPredict)):
            if diff > 0:
                for k in range(diff): # add entries who are missing
                    #print(f"Boardcomputer->nPrediction.setter: {k}-iter of {diff} in dim {idx}")
                    self.__newPredict[idx].append(0)
                    self.__newSigma[idx].append(0)
            elif diff < 0:
                for k in range(-1*diff): # remove entries who are too much
                    #print(f"Boardcomputer->nPrediction.setter: {k}-iter of {diff} in dim {idx}")
                    self.__newPredict[idx].pop()
                    self.__newSigma[idx].pop()
        #print(f"Boardcomputer->nPrediction.setter: new dim rows: {len(self.__newPredict)}")
        #print(f"Boardcomputer->nPrediction.setter: new dim cols: {len(self.__newPredict[0])}")
        #print(f"Boardcomputer->nPrediction.setter: target was: {val}")

        self.__newNPredict = val
        self.__newStorageAvaible = True

    @property
    def measurePoint(self):
        return self.__measurepoint

    ################################
    ### Calculation methods

    def predict(self, deltaT: float, a_input: np.ndarray, aDeviation: np.ndarray) -> None:
        # inspired by CppMonk
        # x = F * x + G * u
        # P = F * P * F_t + G * G_t * a
        #print("Boardcomputer->predict: deltaT %f.1" % (deltaT))
        #print("Boardcomputer->predict: a_input:")
        #print(a_input)
        #print("Boardcomputer->predict: state vector x")
        #print(self.__x)
        #print(f"Boardcomputer->predict: Variance of aceleration: {aVariance}")
        #print(f"Boardcomputer->predict: Input of aceleration: {a_input}")
        
        F=np.bmat([[np.eye(3), np.eye(3)*deltaT, np.zeros((3, 3))],
                   [np.zeros((3, 3)), np.eye(3), np.zeros((3, 3))],
                   [np.zeros((3, 3)), np.zeros((3, 3)), np.zeros((3, 3))]])

        G = np.bmat([[0.5*np.eye(3)*deltaT**2],
                     [np.eye(3)*deltaT],
                     [np.eye(3)]])
                     
        aVarMat = np.array([[aDeviation[0, 0]**2, 0, 0],
                            [0, aDeviation[1, 0]**2, 0],
                            [0, 0, aDeviation[2, 0]**2]])
                    
        new_x = F.dot(self.__x) + G.dot(a_input)

        new_P = F.dot(self.__P).dot(F.T) + G.dot(aVarMat).dot(G.T)

        self.__x = new_x
        self.__P = new_P

    def update(self, measPos: list, measDev: list):
        # inspired by CppMonk
        # y = z - H * x
        # S = H * P * H_t
        # K = P * H_t * S_-1
        # x = x + K * y
        # P = (I - K * H) * P
        R = np.array([[measDev[0]**2, 0, 0],
                      [0, measDev[1]**2, 0],
                      [0, 0, measDev[2]**2]])

        self.__measurepoint = np.array([[measPos[0]],
                      [measPos[1]],
                      [measPos[2]]])

        H = np.bmat([np.eye(3), np.zeros((3, 3)), np.zeros((3, 3))])

        #print("Boardcomputer->update: H:")
        #print(H)
        #print("Boardcomputer->update: measure x:")
        #print(self.__measurepoint)
        #print("Boardcomputer->update: x:")
        #print(self.__x)
        y = self.__measurepoint - H.dot(self.__x)
        #print(f"Boardcomputer->update: outcome y: {y}")
        S = H.dot(self.__P).dot(H.T) + R
        #print(f"Boardcomputer->update: shape of P: {np.shape(self.__P)}, shape of H: {np.shape(H)}, shape of S: {np.shape(S)}")
        K = self.__P.dot(H.T).dot(np.linalg.inv(S))
        new_x = self.__x + K.dot(y)
        new_P = (np.eye(9)-K.dot(H)).dot(self.__P).dot((np.eye(9)-K.dot(H)).T)+K.dot(R).dot(K.T)

        self.__x = new_x
        self.__P = new_P

        #print("Boardcomputer->update: x:")
        #print(self.__x)

        # credits to CppMonk for explaing and showing how to code and test the kalman filter
        # he was also the one, who showed it how to visualize it!
        # https://www.youtube.com/watch?v=m5Bw1m8jJuY
        # also credits to https://www.kalmanfilter.net/default.aspx for helping to develop the model
        # and providing the sources to learn the concepts of the kalman filters

    def compute(self, accelDev: np.ndarray = None, accel: np.ndarray = None, all: bool = False):
        # updates the time for prediction and initialize the predictionAndFill
        # decide if just a new point gets calculated or all prediction gets updated
        if self.__newStorageAvaible:
            print("Boardcomputer->compute: update variable containers")
            self.__predict = copy.deepcopy(self.__newPredict)
            self.__sigma = copy.deepcopy(self.__newSigma)
            self.__nPredict = self.__newNPredict
            self.__newStorageAvaible = False

        if all == False: # calculate just next one position
            #print("Boardcomputer->compute: deltaT: %f0.1" % (self.__deltaT))
            self.predictAndFill(self.__deltaT, accel, accelDev)

        else: # update all predictions and its cetrainty
            for k in range(self.__nPredict):
                #print("Boardcomputer->compute: deltaT: %f0.1 in %d iter" % (self.__deltaT, k))
                self.predictAndFill(self.__deltaT, accel, accelDev)
        #print("Boardcomputer->compute: return")

    def predictAndFill(self, deltaT: float, a_input: np.ndarray, a_deviation: np.ndarray):
        # calculate the prediction and store it in the vectors
        predictStorage = self.__predict[:]
        sigmaStorage = self.__sigma[:]
        self.predict(deltaT, a_input, a_deviation)
        #print("Boardcomputer->predictAndFill: predict vector:")
        #print(self.__predict)
        #print("Boardcomputer->predictAndFill: sigma vector:")
        #print(self.__sigma)
        for dim in range(9): # 0:x, 1:y, 2:z 3:vx, 4:vy, 5:vz, 6:ax, 7:ay, 8:az
            #print(dim)
            #print(self.__x[dim, 0].item())
            #print(self.__predict[dim])
            predictStorage[dim].append(self.__x[dim, 0].item()) # append new position at the end
            #print(self.__predict[dim])
            predictStorage[dim].pop(0) # erase 1st element
            #print(self.__predict[dim])
            
            #print(self.__P[dim, dim].item())
            #print(self.__sigma[dim])
            sigmaStorage[dim].append(np.sqrt(np.abs(self.__P[dim, dim])).item() * 3) # convert to deviation and append 99% certainty of position at the end
            #print(self.__sigma[dim])
            sigmaStorage[dim].pop(0) # erase 1st element
            #print(self.__sigma[dim])
        #print(self.__predict)
        #print(self.__sigma)
        #print("return")

        self.__predict = predictStorage[:]
        self.__sigma = sigmaStorage[:]

        

if __name__ == '__main__':
    print('23')