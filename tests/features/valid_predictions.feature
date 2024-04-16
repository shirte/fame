Feature: Valid predictions

  Scenario Outline: Predictions are valid
    Given a random seed set to <seed>
    And the input type is '<input_type>'
    And a list of <num_molecules> random molecules, where <num_none> entries are None
    And the representations of the molecules
    And the Fame model
    And the metabolism phase is '<metabolism_phase>'

    When the model generates predictions for the molecule representations
    And The subset of the result where the input was not None is considered

    Then the result should be a pandas DataFrame
    And The result should contain the columns:
            atom
            is_som
            probability_0
            probability_1
            ad_score
    And the value in column 'is_som' should have type 'bool'
    And the value in column 'probability_0' should be between 0 and 1
    And the value in column 'probability_1' should be between 0 and 1
    And the value in column 'ad_score' should be between 0 and 1


  Examples:
  | seed | metabolism_phase | num_molecules | num_none | input_type |
  | 1    | phase_1          | 10            | 0        | smiles     |
  | 2    | phase_1          | 10            | 1        | smiles     |
  | 3    | phase_1          | 10            | 2        | smiles     |
  | 4    | phase_1          | 10            | 10       | smiles     |
  | 1    | phase_2          | 10            | 0        | smiles     |
  | 2    | phase_2          | 10            | 1        | smiles     |
  | 3    | phase_2          | 10            | 2        | smiles     |
  | 4    | phase_2          | 10            | 10       | smiles     |
  | 1    | phase_1_and_2    | 10            | 0        | smiles     |
  | 2    | phase_1_and_2    | 10            | 1        | smiles     |
  | 3    | phase_1_and_2    | 10            | 2        | smiles     |
  | 4    | phase_1_and_2    | 10            | 10       | smiles     |
