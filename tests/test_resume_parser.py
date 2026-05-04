from frontend.services.resume_parser import detect_experience_level


def test_detect_experience_level():
    assert detect_experience_level("Senior software engineer") == "Senior"
    assert detect_experience_level("Looking for entry level roles") == "Junior"
    assert detect_experience_level("Experienced developer") == "Mid"
    assert detect_experience_level("") == "Mid"
    assert detect_experience_level("Junior then Senior") == "Junior"
    assert detect_experience_level("Senior then Junior") == "Junior"
