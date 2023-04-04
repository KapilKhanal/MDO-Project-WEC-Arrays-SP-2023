# Gets the Hydrostatic Coefficients
import capytaine as cpt
import meshmagick
import meshmagick.mesh as mm
if version.parse(meshmagick.__version__) < version.parse('3.0'):
    import meshmagick.hydrostatics as hs
else:
    import meshmagick.hydrostatics_old as hs
from capytaine.bem.airy_waves import froude_krylov_force
from scipy.linalg import block_diag

import numpy as np

def run(bodies,omega):
    solver = cpt.BEMSolver()
    FK = np.zeros(len(bodies))
    C = np.zeros(len(bodies))
    for i in range(len(bodies)):
        body = bodies(i)
        hsd = hs.Hydrostatics(mm.Mesh(body.mesh.vertices, body.mesh.faces)).hs_data
        KHS = block_diag(0,0,hsd['stiffness_matrix'],0)
        C[i] = KHS[2,2]
        test = cpt.DiffractionProblem(body=body, omega=omega, wave_direction=0.)
        FK[i] = froude_krylov_force(test)['Heave']
    return FK,C