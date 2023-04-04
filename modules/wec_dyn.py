# Calculates the body motion RAO based on the wave exciting force RAO
# Inputs: frequency, wave exciting force RAO, Added Mass, Added Damping, Hydrostatic Restoring, mass, pto damping
# Outputs: heave motion RAO, pto stiffness

def wec_dyn(omega,F,A,B,C,m,d):
    k = (omega**2)*(m+A) - C    #   Calculate Optimal PTO stiffness
    XI = F/(-(A+m)*omega**2 + (B+d)*omega*1j + C+k)
    return XI,k
