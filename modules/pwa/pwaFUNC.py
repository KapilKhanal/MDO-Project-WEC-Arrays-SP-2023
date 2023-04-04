'''Plane wave approximation stuff slay!'''
def plane_wave(inputs):
    def generate_body(xyz):
        mesh1 = cpt.meshes.predefined.mesh_sphere(radius=2,center=(xyz[0],xyz[1],xyz[2]))
        body = cpt.FloatingBody(mesh1)
        body.add_translation_dof(name='Heave')
        body = body.immersed_part()
        body.name = f'{xyz[0]}_{xyz[1]}_{xyz[2]}'
        return body


    def get_results(problems):
        results = [solver.solve(pb, keep_details = True) for pb in sorted(problems)]
        return results


    #calculate angle theta_ij from centre of one body to other
    def theta_ij(X,Y): 
        x1,y1= X[0],X[1]
        x2,y2 = Y[0], Y[1]

        if x1 ==x2 and y1==y2:
            return 0
        if x2==x1:
            theta = np.pi/2
        else:
            theta = np.arctan((y2-y1)/(x2-x1))
        return theta


    #step 2
    def phi_j_star(phi_ij,theta,X,Y,z,k):

        '''phi_ij is the vector of all the effect at that body from all other bodies'''
        x,y = X[0],X[1]
        xj,yj = Y[0],Y[1]
        if x==xj and y==yj:
            return 0
        multiplier = np.exp((1j*k*(-1*np.abs(x-xj))*np.cos(theta)) + ((-1*np.abs(y-yj))*np.sin(theta)))
        print(f'the multiplier for {X}{Y} and {theta} is {multiplier}')
        res = phi_ij * multiplier #kz = 0 #e^kz = 1
        return res

    #{(10, 10, 0): {(10, 10, 0): 0,
      #(0, 0, 0): (8.415476709952118-2.9519008598532284j),
      #(5, 5, 0): (8.415476709952118-2.9519008598532284j),
      #(15, 15, 0): (8.415476709952118-2.9519008598532284j)

    def get_phistarj_sum(phi_starj,xyzees):
        xyz_phi = {xyz :[] for xyz in xyzees}
        for k,v in phi_starj.items():
            for s,m in v.items():
                print(f"thee value of m = {m}")
                xyz_phi[k].append(m)
            print("next xyz")
        print(xyz_phi.items())
        xyz_phi = {k:sum(v) for k,v in xyz_phi.items()}
        print("Afteer summation ")
        print(xyz_phi.items())
        return xyz_phi


    def solve(diff,diff_res, rad_res,new_potential,keep_details=True):
            """Solve the linear potential flow problem.
            Parameters
            ----------
            problem: LinearPotentialFlowProblem
                the problem to be solved
            keep_details: bool, optional
                if True, store the sources and the potential on the floating body in the output object
                (default: True)
            Returns
            -------
            LinearPotentialFlowResult
                an object storing the problem data and its results
            """
            diff_pot = diff_res.potential

            rad_pot = rad_res.potential
            potential = new_potential + diff_pot + rad_pot
            rho = 1000
            new_pressure = rho * potential
            # Actually, for diffraction problems: pressure over jω
            #           for radiation problems:   pressure over -ω²
            # The correction is done in `store_force` in the `result` object.

            new_forces = diff.body.integrate_pressure(new_pressure)

    #         if not keep_details:
    #             result = problem.make_results_container(new_forces)
    #         else:
    #             result = problem.make_results_container(new_forces, sources, new_potential, new_pressure)
            return new_forces

    p = 0
    omega = 1.1
    rho = 850 # density of our special material
    wave_amp = 1
    wave_num =  1.0/9.81


    N_bodies = 4
    max_iteration = 2*N_bodies #(dead or alive lol)

    # body_potential_at_neighbors = {body:(dict(zip(body_neighbors_locs[body], 
    #                                       airy_waves_potential(np.array(body_neighbors_locs[body]),diff_problems[body])))) for body in bodies}


    body_potential_at_neighbors = {body:{nbros : airy_waves_potential(np.array(body_neighbors_locs[body]),diff_problems[body])
                                                  for nbros in neighbors} for xyz,body in loc_to_body.items()}
    iterate = 0
    while iterate<max_iteration:
        # def get_all_other_phi(body_potential_at_neighbors):
        all_other_phi_each_loc = {xyz:{loc_bodies.get(d):k.get(xyz,0) for d,k in body_potential_at_neighbors.items()} for xyz in xyzees}
        print('iteration')
       # print(all_other_phi_each_loc)
        thetas = {k:{s:theta_ij(k,s) for s,m in v.items()} for k,v in all_other_phi_each_loc.items()}
        phi_starj = {xyz:{nbros:phi_j_star(all_other_phi_each_loc[xyz][nbros],thetas[xyz][nbros],nbros,xyz,z,wave_num) for nbros in neighbors} for xyz in xyzees}

        new_excitation = get_phistarj_sum(phi_starj,xyzees)
        # look at the new excitation amplitude and reject if the amplitude is bigger than the last two

    #     print(f"excitation for {iterate}")
        print(new_excitation)
    #     print("\n")


        body_potential_at_neighbors = {body:{nbros : airy_waves_potential(np.array(body_neighbors_locs[body]),diff_problems[body])+ phi_j_star(new_excitation[xyz],thetas[loc_bodies[body]][nbros],nbros,xyz,z,wave_num) 
                                                  for nbros in neighbors} for xyz,body in loc_to_body.items()}

       # print(new_excitation)

        iterate+=1

    new_potential = get_phistarj_sum(phi_starj,xyzees)

    new_results = {loc_to_body.get(loc):solve(diff_prob,diff_results[loc_to_body.get(loc)],rad_results[loc_to_body.get(loc)], sum(new_potential[loc])) for loc,diff_prob in loc_diff.items()}
    return new_results
