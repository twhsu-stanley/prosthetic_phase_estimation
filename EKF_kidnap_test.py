import numpy as np
from EKF import *
from model_framework import *
from data_generators import *
from continuous_data import *
from model_fit import *

with open('Measurement_error_cov.pickle', 'rb') as file:
        R = pickle.load(file)

m_model = model_loader('Measurement_model.pickle')

def kidnap_test(subject, trial, side, ekf):
    dt = 1/100
    Psi = load_Psi(subject)
    phases, _, _, _ = Conti_state_vars(subject, trial, side)
    global_thigh_angle_Y, force_z_ankle, force_x_ankle, moment_y_ankle = load_Conti_measurement_data(subject, trial, side)

    z = np.array([[global_thigh_angle_Y],\
                  [force_z_ankle], \
                  [force_x_ankle],\
                  [moment_y_ankle]])
    z = np.squeeze(z)
    
    kidnap_index = 100 # step at which kidnapping occurs
    phase_kidnap = np.random.uniform(0, 1)
    phase_dot_kidnap = np.random.uniform(0.65, 1)
    step_length_kidnap = np.random.uniform(0.95, 1.4)
    ramp_kidnap = np.random.uniform(-10, 10)
    state_kidnap = np.array([[phase_kidnap], [phase_dot_kidnap], [step_length_kidnap], [ramp_kidnap]])

    x = []  # state estimate
    for i in range(np.shape(z)[1]):
        # kidnap
        if i == kidnap_index:
            ekf.x = state_kidnap

        ekf.prediction(dt)
        ekf.correction(z[:, i], Psi)
        x.append(ekf.x)
    x = np.array(x).squeeze()

    # evaluate robustness
    # compare x and ground truth:
    track = True
    track_tol = 0.05
    heel_strike_index = Conti_heel_strikes(subject, trial, side) - Conti_heel_strikes(subject, trial, side)[0]
    # start checking tracking after the 3rd stride
    for i in range(3, np.size(heel_strike_index)):
        if i != np.size(heel_strike_index) - 1:
            start = int(heel_strike_index[i]) + 10
            end = int(heel_strike_index[i+1]) - 10
            track = track and all(abs(phases[start:end] - x[start:end, 0]) < track_tol)
    
    return track

if __name__ == '__main__':
    subject = 'AB02'
    trial= 's1x2i5'
    side = 'right'
    phases, phase_dots, step_lengths, ramps = Conti_state_vars(subject, trial, side)

    # build the system
    sys = myStruct()
    sys.f = process_model
    sys.A = A
    sys.h = m_model
    sys.Q = np.diag([0, 1e-7, 1e-8, 1e-10]) # process model noise covariance  
    sys.R = R[subject] # measurement noise covariance

    # initialize the state
    init = myStruct()
    init.x = np.array([[phases[0]], [phase_dots[0]], [step_lengths[0]], [ramps[0]]])
    init.Sigma = np.diag([1e-14, 1e-14, 1e-14, 1e-14])
    
    ekf = extended_kalman_filter(sys, init)
                            
    print(kidnap_test(subject, trial, side, ekf))
    
    """
    # iterate through Q
    for Q_phase_dot in [1e-7]:
        for Q_step_length in [1e-8]:
            for Q_ramp in [1e-4, 1e-8, 1e-14]:
                sys.Q = np.diag([0, Q_phase_dot, Q_step_length, Q_ramp]) # process model noise covariance
                track_count = 0

                for subject in Conti_subject_names():
                    for trial in Conti_trial_names(subject):
                        for side in ['left', 'right']:
                            phases, phase_dots, step_lengths, ramps = Conti_state_vars(subject, trial, side)
                            sys.R = R[subject] 
                            init.x = np.array([[phases[0]], [phase_dots[0]], [step_lengths[0]], [ramps[0]]])
                            ekf = extended_kalman_filter(sys, init)
                            
                            if robustness_test(subject, trial, side, ekf) == True:
                                track_count = track_count + 1
    """
                
                

    
    