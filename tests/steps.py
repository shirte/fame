from pytest_bdd import given, parsers

from fame import Fame3Model


@given("the Fame model", target_fixture="model")
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