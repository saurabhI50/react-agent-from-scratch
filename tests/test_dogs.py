
from app.tools.dogs import average_dog_weight


def test_scottish_terrier_weight():
    result = average_dog_weight("Scottish Terrier")
    assert result == "Scottish Terrier weighs an average of 22 lbs."


def test_border_collie_weight():
    result = average_dog_weight("Border Collie")
    assert result == "Border Collie weighs an average of 37 lbs."


def test_breed_lookup_is_case_insensitive():
    result = average_dog_weight("border collie")
    assert "37 lbs" in result


def test_unknown_breed():
    result = average_dog_weight("Unknown Breed")
    assert "Unknown breed" in result
