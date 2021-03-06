import numpy as np
from model_framework import *
#from model_fit import *
import time

# Process model for the EKF
def A(dt):
    return np.array([[1, dt, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])

def process_model(x, dt):
    #dt = 0.01 # data sampling rate: 100 Hz
    return A(dt) @ x

## Load control model & coefficients (for OSL implementation)
c_model = model_loader('Control_model.pickle')
#with open('Psi/Psi_knee_G.pickle', 'rb') as file:#_withoutNan
#    Psi_knee = pickle.load(file)
#with open('Psi/Psi_ankle_G.pickle', 'rb') as file:
#    Psi_ankle = pickle.load(file)
with open('New_Psi/Psi_kneeAngles.pickle', 'rb') as file:
    Psi_knee = pickle.load(file)
with open('New_Psi/Psi_ankleAngles.pickle', 'rb') as file:
    Psi_ankle = pickle.load(file)

## Load model coefficients
def load_Psi(subject = 'Generic'):
    if subject == 'Generic':
        #with open('Psi/Psi_thigh_Y_G.pickle', 'rb') as file:
        with open('New_Psi/Psi_globalThighAngles.pickle', 'rb') as file:
            Psi_globalThighAngles = pickle.load(file)
        
        with open('Psi/Psi_force_Z_G.pickle', 'rb') as file:
            Psi_force_Z = pickle.load(file)
        
        with open('Psi/Psi_force_X_G.pickle', 'rb') as file:
            Psi_force_X = pickle.load(file)
        
        with open('Psi/Psi_moment_Y_G.pickle', 'rb') as file:
            Psi_moment_Y = pickle.load(file)
        
        #with open('Psi/Psi_thighVel_2hz_G.pickle', 'rb') as file:
        with open('New_Psi/Psi_globalThighVelocities.pickle', 'rb') as file:
            Psi_globalThighVelocities = pickle.load(file)

        #with open('Psi/Psi_atan2_G.pickle', 'rb') as file:
        with open('New_Psi/Psi_atan2.pickle', 'rb') as file:
            Psi_atan2 = pickle.load(file)

    else:
        with open('Psi/Psi_thigh_Y.pickle', 'rb') as file:
            p = pickle.load(file)
            Psi_globalThighAngles = p[subject]
        with open('Psi/Psi_force_Z.pickle', 'rb') as file:
            p = pickle.load(file)
            Psi_force_Z = p[subject]
        with open('Psi/Psi_force_X.pickle', 'rb') as file:
            p = pickle.load(file)
            Psi_force_X = p[subject]
        with open('Psi/Psi_moment_Y.pickle', 'rb') as file:
            p = pickle.load(file)
            Psi_moment_Y = p[subject]
        with open('Psi/Psi_thighVel_2hz.pickle', 'rb') as file:
            p = pickle.load(file)
            Psi_globalThighVelocities = p[subject]
        with open('Psi/Psi_atan2.pickle', 'rb') as file:
            p = pickle.load(file)
            Psi_atan2 = p[subject]
           
    Psi = {'global_thigh_angle': Psi_globalThighAngles, 'force_Z': Psi_force_Z, 'force_X': Psi_force_X, 'moment_Y': Psi_moment_Y,
           'global_thigh_angle_vel': Psi_globalThighVelocities, 'atan2': Psi_atan2}
    return Psi

def warpToOne(phase):
    phase_wrap = np.remainder(phase, 1)
    while np.abs(phase_wrap) > 1:
        phase_wrap = phase_wrap - np.sign(phase_wrap)
    return phase_wrap

def wrapTo2pi(ang):
    ang = ang % (2*np.pi)
    return ang

def phase_error(phase_est, phase_truth):
    # measure error between estimated and ground-truth phase
    if abs(phase_est - phase_truth) < 0.5:
        return abs(phase_est - phase_truth)
    else:
        return 1 - abs(phase_est - phase_truth)

def joints_control(phases, phase_dots, step_lengths, ramps):
    joint_angles = c_model.evaluate_h_func([Psi_knee, Psi_ankle], phases, phase_dots, step_lengths, ramps)
    return joint_angles
    
class myStruct:
    pass

class extended_kalman_filter:
    def __init__(self, system, init):
        # Constructor
        # Inputs:
        #   system: system and noise models
        #   init:   initial state mean and covariance
        self.f = system.f  # process model
        self.A = system.A  # system matrix Jacobian
        self.Q = system.Q  # process model noise covariance

        self.h = system.h  # measurement model
        self.R = system.R  # measurement noise covariance
        
        self.x = init.x  # state mean
        self.Sigma = init.Sigma  # state covariance

    def prediction(self, dt):
        # EKF propagation (prediction) step
        self.x = self.f(self.x, dt)  # predicted state
        self.x[0, 0] = warpToOne(self.x[0, 0]) # wrap to be between 0 and 1
        self.Sigma = self.A(dt) @ self.Sigma @ self.A(dt).T + self.Q  # predicted state covariance

    def correction(self, z, Psi, arctan2 = False, steady_state_walking = False):
        # EKF correction step
        # Inputs:
        #   z:  measurement

        # evaluate measurement Jacobian at current operating point
        H = self.h.evaluate_dh_func(Psi, self.x[0,0], self.x[1,0], self.x[2,0], self.x[3,0])
        
        # predicted measurements
        self.z_hat = self.h.evaluate_h_func(Psi, self.x[0,0], self.x[1,0], self.x[2,0], self.x[3,0])

        ### Jacobian test#########################################################
        #print("HPH=",  H @ self.Sigma @ H.T)
        #print("R=", self.R)
        #z2 = self.h.evaluate_h_func(Psi, self.x[0,0]-0.01, self.x[1,0]-0.01, self.x[2,0]+0.01, self.x[3,0]-0.01)
        #print(z2 - self.z_hat)
        #print(H @ np.array([[-0.01], [-0.01], [0.01], [-0.01]]))
        ###########################################################################

        if arctan2:
            H[-1, 0] += 2*np.pi
            self.z_hat[-1] += self.x[0,0] * 2 * np.pi
            # wrap to 2pi
            self.z_hat[-1] = wrapTo2pi(self.z_hat[-1]) #self.z_hat[-1] % (2*np.pi) # 
                    
        # innovation
        z = np.array([z]).T
        self.v = z - self.z_hat
        
        if arctan2:
            # wrap to pi
            self.v[-1] = np.arctan2(np.sin(self.v[-1]), np.cos(self.v[-1]))

        R = self.R
        
        # Detect kidnapping event
        self.MD = np.sqrt(self.v.T @ np.linalg.inv(self.R) @ self.v) # Mahalanobis distance
        #if steady_state_walking:
            #if self.MD > np.sqrt(25):
                #self.Sigma += np.diag([2e-5, 2e-4, 4e-3, 4])
                #self.Sigma += np.diag([0, 1e-7, 1e-7, 0])
        
        # innovation covariance
        S = H @ self.Sigma @ H.T + R

        # filter gain
        K = self.Sigma @ H.T @ np.linalg.inv(S)

        # correct the predicted state statistics
        self.x = self.x + K @ self.v
        self.x[0, 0] = warpToOne(self.x[0, 0])

        I = np.eye(np.shape(self.x)[0])
        self.Sigma = (I - K @ H) @ self.Sigma
        
    def state_saturation(self, saturation_range):
        phase_dots_max = saturation_range[0]
        phase_dots_min = saturation_range[1]
        step_lengths_max = saturation_range[2]
        step_lengths_min = saturation_range[3]
        
        #if self.x[0, 0] > 1:
        #    self.x[0, 0] = 1
        #elif self.x[0, 0] < 0:
        #    self.x[0, 0] = 0
        
        if self.x[1, 0] > phase_dots_max:
            self.x[1, 0] = phase_dots_max
        elif self.x[1, 0] < phase_dots_min:
            self.x[1, 0] = phase_dots_min

        if self.x[2, 0] > step_lengths_max:
            self.x[2, 0] = step_lengths_max
        elif self.x[2, 0] < step_lengths_min:
            self.x[2, 0] = step_lengths_min

        if self.x[3, 0] > 10:
            self.x[3, 0] = 10
        elif self.x[3, 0] < -10:
            self.x[3, 0] = -10
    