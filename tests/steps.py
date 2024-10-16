from pytest_bdd import given, parsers, when

from fame import Fame3Model


@given("the Fame model", target_fixture="predictor")
def model():
    return Fame3Model()


@given(parsers.parse("the input type is '{input_type}'"), target_fixture="input_type")
def input_type(input_type):
    return input_type


@given(
    parsers.parse("the metabolism phase is '{metabolism_phase}'"),
    target_fixture="metabolism_phase",
)
def metabolism_phase(metabolism_phase):
    return metabolism_phase

@when(
    parsers.parse("the model generates predictions for the molecule representations"),
    target_fixture="predictions",
)
def predictions(representations, predictor, input_type, metabolism_phase):
    return predictor.predict(
        representations,
        input_type=input_type,
        metabolism_phase=metabolism_phase,
        output_format="record_list",
    )