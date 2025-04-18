Feature: Consistent predictions

  Scenario Outline: Predictions stay consistent with previous versions
    Given an input molecule specified by '<input_smiles>'
    And the Fame model
    And the metabolism phase is '<metabolism_phase>'
    
    When the model generates predictions for the molecule representations
    And the subset of the result where the input was not None is considered
    
    Then the value in column 'name' should be equal to '<name>'
    And when 'atom_id' is <atom_id> the value in column 'atom' should be <atom>
    And when 'atom_id' is <atom_id> the value in column 'is_som' should be <is_som>
    And when 'atom_id' is <atom_id> the value in column 'probability_0' should be <probability_0>
    And when 'atom_id' is <atom_id> the value in column 'probability_1' should be <probability_1>
    And when 'atom_id' is <atom_id> the value in column 'ad_score' should be <ad_score>

    Examples:
    | metabolism_phase | input_smiles                                                                                                  | name                     | atom_id | atom     | is_som | probability_0 | probability_1 | ad_score |
    | phase_1_and_2    | C1=NC2=C(N1COCCO)N=C(NC2=O)N Aciclovir                                                                        | Aciclovir                | 9       | 'O.10'   | False  | 0.199         | 0.801         | 0.417    |
    | phase_1_and_2    | C1=NC2=C(N1COCCO)N=C(NC2=O)N Aciclovir                                                                        | Aciclovir                | 12      | 'N.13'   | False  | 0.144         | 0.856         | 0.42     |
    | phase_1_and_2    | C1=CC(=C(C=C1[As]=[As]C2=CC(=C(C=C2)O)N)N)O.Cl.Cl Arsphenamine (Salvarsan)                                    | Arsphenamine (Salvarsan) | None    | None     | None   | None          | None          | None     |
    | phase_1_and_2    | C1CNP(=O)(OC1)N(CCCl)CCCl Cyclophosphamide                                                                    | Cyclophosphamide         | 11      | 'C.12'   | True   | 0.972         | 0.028         | 0.956    |
    | phase_1_and_2    | C1CNP(=O)(OC1)N(CCCl)CCCl Cyclophosphamide                                                                    | Cyclophosphamide         | 13      | 'Cl.14'  | False  | 0.004         | 0.996         | 0.956    |
    | phase_1_and_2    | C[C@H]1[C@H]([C@H](C[C@@H](O1)O[C@H]2C[C@@](Cc3c2c(c4c(c3O)C(=O)c5cccc(c5C4=O)OC)O)(C(=O)CO)O)N)O Doxorubicin | Doxorubicin              | 38      | 'O.39'   | True   | 0.589         | 0.411         | 1.0      |
    | phase_1_and_2    | C[C@H]1[C@H]([C@H](C[C@@H](O1)O[C@H]2C[C@@](Cc3c2c(c4c(c3O)C(=O)c5cccc(c5C4=O)OC)O)(C(=O)CO)O)N)O Doxorubicin | Doxorubicin              | 28      | 'O.29'   | False  | 0.000         | 1.000         | 0.991    |
    | phase_1_and_2    | O=S(=O)(N)c1c(Cl)cc2c(c1)S(=O)(=O)NCN2 Hydrochlorothiazide                                                    | Hydrochlorothiazide      | 3       | 'N.4'    | False  | 0.335         | 0.665         | 0.595    |
    | phase_1_and_2    | O=S(=O)(N)c1c(Cl)cc2c(c1)S(=O)(=O)NCN2 Hydrochlorothiazide                                                    | Hydrochlorothiazide      | 11      | 'S.12'   | False  | 0.02          | 0.98          | 0.576    |
    | phase_1_and_2    | C[C@H]1COc2c3n1cc(c(=O)c3cc(c2N4CCN(CC4)C)F)C(=O)O Levofloxacin                                               | Levofloxacin             | 18      | 'N.19'   | True   | 0.84          | 0.16          | 0.857    |
    | phase_1_and_2    | C[C@H]1COc2c3n1cc(c(=O)c3cc(c2N4CCN(CC4)C)F)C(=O)O Levofloxacin                                               | Levofloxacin             | 3       | 'O.4'    | False  | 0.008         | 0.992         | 0.71     |
    | phase_1_and_2    | CC1=C(C(=O)N(N1C)C2=CC=CC=C2)N(C)CS(=O)(=O)[O-].O.[Na+] Metamizole (Sulpyrine)                                | Metamizole (Sulpyrine)   | None    | None     | None   | None          | None          | None     |
    | phase_1_and_2    | CC1=C(C(C(=C(N1C=O)C)C(=O)OC)C2=CC=CC=C2[N+](=O)[O-])C(=O)OC Nifedipine                                       | Nifedipine               | 20      | 'N.21'   | True   | 0.412         | 0.588         | 0.588    |
    | phase_1_and_2    | CC1=C(C(C(=C(N1C=O)C)C(=O)OC)C2=CC=CC=C2[N+](=O)[O-])C(=O)OC Nifedipine                                       | Nifedipine               | 8       | 'O.9'    | False  | 0.024         | 0.976         | 0.459    |
    | phase_1_and_2    | OC=1c3ccccc3OC(=O)C=1C(CC)c2ccccc2 Phenprocoumon                                                              | Phenprocoumon            | 6       | 'C.7'    | True   | 0.768         | 0.232         | 0.944    |
    | phase_1_and_2    | OC=1c3ccccc3OC(=O)C=1C(CC)c2ccccc2 Phenprocoumon                                                              | Phenprocoumon            | 16      | 'C.17'   | False  | 0.016         | 0.984         | 1.0      |
    | phase_1_and_2    | O=C1COCCN1c2ccc(cc2)N3C[C@@H](OC3=O)CNC(=O)c4ccc(s4)Cl Rivaroxaban                                            | Rivaroxaban              | 17      | 'C.18'   | True   | 0.868         | 0.132         | 0.682    |
    | phase_1_and_2    | O=C1COCCN1c2ccc(cc2)N3C[C@@H](OC3=O)CNC(=O)c4ccc(s4)Cl Rivaroxaban                                            | Rivaroxaban              | 28      | 'Cl.29'  | False  | 0.016         | 0.984         | 0.675    |
    | phase_1_and_2    | CN1CCN(Cc2ccc(cc2)C(=O)Nc3ccc(C)c(Nc4nccc(n4)c5cccnc5)c3)CC1 Imatinib                                         | Imatinib                 | 1       | 'N.2'    | True   | 0.888         | 0.112         | 0.785    |
    | phase_1_and_2    | CN1CCN(Cc2ccc(cc2)C(=O)Nc3ccc(C)c(Nc4nccc(n4)c5cccnc5)c3)CC1 Imatinib                                         | Imatinib                 | 6       | 'C.7'    | False  | 0.004         | 0.996         | 0.828    |
    

