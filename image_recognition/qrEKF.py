import numpy as np
import Shared
from math import cos, sin, tan, atan2, sqrt

MaxDBSize = 10
RHO = 0.5
gravity = 9.807
sigmaFPmeas = 0.03
sigmaFPang = 0.09
sigmaFPinvD = 2
sigmaPOS = 0.015
PI = 3.1415926535
FOVU = Shared.data.FOVU
FOVV = Shared.data.FOVV
SensorU = Shared.data.sensorU
SensorV = Shared.data.sensorV

def contains(list, filter):
    for x in list:
        if filter(x):
            return True
        else:
            return False

def euler2dcm321(phi, theta, psi):
    DCM = np.empty((3, 3))
    DCM[0][0] = cos(theta)*cos(psi)
    DCM[0][1] = cos(theta)*sin(psi)
    DCM[0][2] = -sin(theta)
    DCM[1][0] = -cos(phi)*sin(psi) + sin(phi)*sin(theta)*cos(psi)
    DCM[1][1] = cos(phi)*cos(psi) + sin(phi)*sin(theta)*sin(psi)
    DCM[1][2] = sin(phi)*cos(theta)
    DCM[2][0] = sin(phi)*sin(psi) + cos(phi)*sin(theta)*cos(psi)
    DCM[2][1] = -sin(phi)*cos(psi) + cos(phi)*sin(theta)*sin(psi)
    DCM[2][2] = cos(phi)*cos(theta)
    return DCM

def fpLocEstPos(fpState):
    px = fpState.pos[0]
    py = fpState.pos[1]
    pz = fpState.pos[2]
    psi = fpState.psi
    theta = fpState.theta
    rho = fpState.rho

    X = px + cos(theta)*cos(psi)/rho
    Y = py + cos(theta)*sin(psi)/rho
    Z = pz - sin(theta)/rho

    return [X,Y,Z]

class fpMeas():

    def __init__(self, id, u, v):
        self.fpPixLoc = np.array([u, v])   # Pixel location of fp seen; (u,v) as fraction of screen
        self.id = id

class fpState():

    def __init__(self, id, state, conf):
        self.id = id
        self.pos = np.array([state[0], state[1], state[2]])
        self.psi = state[3]
        self.theta = state[4]
        self.rho = state[5]
        self.P = np.zeros((6, 6), dtype=float)
        self.conf = conf

class qrEKF():

    def __init__(self):
        self.dbSize = 0              # Current size of db of tracked fp
        self.numCorresponded = 0
        self.confThresh = 50
        self.fpStateDB = []
        self.fpR = np.array([[sigmaFPmeas**2, 0], [0, sigmaFPmeas**2]])
        self.fpQ = np.zeros((6,6))
        #self.fpStateDB = [fpState(None, None, -1) for _ in range(MaxDBSize)]

    def ComputeCinvD(self, state, in2camDCM, hcam, vPos):
        px = state[0]
        py = state[1]
        pz = state[2]
        psi = state[3]
        theta = state[4]
        rho = state[5]

        focU = SensorU / (SensorU * tan(FOVU / 2))
        focV = SensorV / (SensorU * tan(FOVV / 2))
        fpPixEst = np.array([focU * hcam[1] / hcam[0],
                             focV * hcam[2] / hcam[0]])

        dzdrI = np.array([[-fpPixEst[0]/hcam[0], focU/hcam[0], 0],
                         [-fpPixEst[1]/hcam[0], 0, focV/hcam[0]]])

        dzdrC = np.matmul(dzdrI, in2camDCM)
        dzdPa = dzdrC*rho

        dmdPsi = np.array([-sin(psi)*cos(theta), cos(psi)*cos(theta), 0])
        dmdTheta = np.array([-cos(psi)*sin(theta), -sin(psi)*sin(theta), -cos(theta)])
        drdRho = np.array([px - vPos[0], py - vPos[1], pz - vPos[2]])

        dzdPsi = np.matmul(dzdrC, dmdPsi)
        dzdTheta = np.matmul(dzdrC, dmdTheta)
        dzdRho = np.matmul(dzdrC, drdRho)

        Cfp = np.array([[dzdPa[0][0], dzdPa[0][1], dzdPa[0][2], dzdPsi[0], dzdTheta[0], dzdRho[0]],
                       [dzdPa[1][0], dzdPa[1][1], dzdPa[1][2], dzdPsi[1], dzdTheta[1], dzdRho[1]]])

        return Cfp

    def measUpdate(self, pos, att, qrMeas):

        camx = pos[0]
        camy = pos[1]
        camz = pos[2]
        roll = att[0]
        pitch = att[1]
        yaw = att[2]
        in2camDCM = euler2dcm321(roll, pitch, yaw)
        cam2inDCM = in2camDCM.transpose()
        focU = SensorU/(SensorU*tan(FOVU/2))
        focV = SensorV/(SensorU*tan(FOVV/2))
        for i in range(len(qrMeas)):
            if not any(fp.id == qrMeas[i].id for fp in self.fpStateDB):#contains(self.fpStateDB, lambda fp:fp.id == qrMeas[i].id):
                #for j in range(MaxDBSize):
                #if self.fpStateDB[j].conf < self.confThresh:
                # Feature point state given as:    y = [xa, ya, za, psi, theta, rho]
                # Set anchor position(inertial) to estimated vehicle location(inertial)
                temp_pos = pos      #self.fpStateDB[j].pos = pos    Inertial x,y,z
                temp_rho = RHO      #self.fpStateDB[j].rho = RHO    inverse depth

                # Use measurement model to determine elevation(theta) and azimuth(psi)
                # where: (hx, hy, hz) = is the ray from anchor point to fp in camera frame(frd)

                hx = 1/(sqrt(1 + (qrMeas[i].fpPixLoc[0]/focU)**2 + (qrMeas[i].fpPixLoc[1]/focV)**2))
                hy = qrMeas[i].fpPixLoc[0]/(focU*sqrt(1 + (qrMeas[i].fpPixLoc[0]/focU)**2 + (qrMeas[i].fpPixLoc[1]/focV)**2))
                hz = qrMeas[i].fpPixLoc[1]/(focV*sqrt(1 + (qrMeas[i].fpPixLoc[0]/focU)**2 + (qrMeas[i].fpPixLoc[1]/focV)**2))
                cam2fpCAM = np.array([hx, hy, hz])
                cam2fpIN = np.matmul(cam2inDCM, cam2fpCAM)
                temp_psi= atan2(cam2fpIN[1], cam2fpIN[0])       #self.fpStateDB[j].psi = atan2(cam2fpIN[1], cam2fpIN[0])     #Azimuth psi
                temp_theta = atan2(-cam2fpIN[2], sqrt(cam2fpIN[0]**2 + cam2fpIN[1]**2))     #self.fpStateDB[j].theta = atan2(-cam2fpIN[2], sqrt(cam2fpIN[0]**2 + cam2fpIN[1]**2))    # Elevation theta

                # Create new fp state
                temp_state = fpState(qrMeas[i].id, np.array([temp_pos[0], temp_pos[1], temp_pos[2], temp_psi,
                                                             temp_theta, temp_rho]), self.confThresh)

                #Initialise state estimate covariance matrix for new fp
                temp_state.P[0][0] = sigmaPOS ** 2      #self.fpStateDB[j].P[0][0] = sigmaPOS**2
                temp_state.P[1][1] = sigmaPOS ** 2      #self.fpStateDB[j].P[1][1] = sigmaPOS**2
                temp_state.P[2][2] = sigmaPOS ** 2      #self.fpStateDB[j].P[2][2] = sigmaPOS**2
                temp_state.P[3][3] = sigmaFPang ** 2    #self.fpStateDB[j].P[3][3] = sigmaFPang**2
                temp_state.P[4][4] = sigmaFPang ** 2    #self.fpStateDB[j].P[4][4] = sigmaFPang**2
                temp_state.P[5][5] = sigmaFPinvD ** 2   #self.fpStateDB[j].P[5][5] = sigmaFPinvD**2

                self.fpStateDB.append(temp_state)

                #Initialise confidence of new fp
                #self.fpStateDB[j].conf = self.confThresh
                #self.fpStateDB[j].id = qrMeas[i].id
            else:
                # Determine which feature point will be updated
                for fp in self.fpStateDB:
                    if fp.id == qrMeas[i].id:
                        px = fp.pos[0]
                        py = fp.pos[1]
                        pz = fp.pos[2]
                        psi = fp.psi
                        theta = fp.theta
                        rho = fp.rho

                        # Find the position vector of fp wrt camer, hcam (in camera frame)
                        m = np.array([cos(psi)*cos(theta), sin(psi)*cos(theta), -sin(theta)])
                        hin = np.array([rho*(px - camx) + m[0],
                                        rho*(py - camy) + m[1],
                                        rho*(pz - camz) + m[2]])
                        hcam = np.matmul(in2camDCM, hin)

                        # Make sure we're not finding a singularity
                        if hcam[0] > 0.01:
                            fpPixEst = np.array([focU*hcam[1]/hcam[0],
                                                 focV*hcam[2]/hcam[0]])
                            if (fpPixEst[0] > -1) and (fpPixEst[0] < 1) and \
                                (fpPixEst[1] > -SensorV/SensorU) and (fpPixEst[1] < SensorV/SensorU):

                                residual = np.array([qrMeas[i].fpPixLoc[0] - fpPixEst[0],
                                                     qrMeas[i].fpPixLoc[1] - fpPixEst[1]])

                                Cfp = self.ComputeCinvD(np.array([px, py, pz, psi, theta, rho]), in2camDCM, hcam, pos)
                                CfpP = np.matmul(Cfp, fp.P)
                                CfpPCfpT = np.matmul(CfpP, np.transpose(Cfp))

                                Rt = np.add(CfpPCfpT, self.fpR)
                                Rt_inv = np.linalg.inv(Rt)
                                Kgain = np.matmul(np.transpose(CfpP), Rt_inv)

                                xCorr = np.matmul(Kgain, residual)
                                for k in range(3):
                                    fp.pos[k] = fp.pos[k] + xCorr[k]
                                fp.psi = fp.psi + xCorr[3]
                                fp.theta = fp.theta + xCorr[4]
                                fp.rho = fp.rho + xCorr[5]

                                KCP = np.matmul(Kgain, CfpP)
                                for j in range(6):
                                    for k in range(j):
                                        fp.P[j][k] = fp.P[j][k] - KCP[j][k]
                                for j in range(6):
                                    for k in range(j):
                                        fp.P[k][j] = fp.P[j][k]

                        break

    def procUpdate(self, dt):
        for fp in self.fpStateDB:
            for j in range(6):
                for k in range(6):
                    fp.P[j][k] = fp.P[j][k] + self.fpQ[j][k]*dt
