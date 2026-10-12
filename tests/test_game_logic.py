from logic_utils import check_guess, parse_guess, update_score

# check_guess returns (outcome, message); the app shows the message as a hint.

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, message = check_guess(50, 50)
    assert outcome == "Win"
    assert "Correct" in message

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, message = check_guess(60, 50)
    assert outcome == "Too High"
    assert "LOWER" in message

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, message = check_guess(40, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message


# parse_guess returns (ok, guess_int, error_message).

def test_parse_valid_number():
    assert parse_guess("42") == (True, 42, None)

def test_parse_strips_surrounding_spaces():
    assert parse_guess(" 42 ") == (True, 42, None)

def test_parse_empty_input():
    assert parse_guess("") == (False, None, "Enter a guess.")

def test_parse_whitespace_only_counts_as_empty():
    assert parse_guess("   ") == (False, None, "Enter a guess.")

def test_parse_none():
    assert parse_guess(None) == (False, None, "Enter a guess.")

def test_parse_rejects_decimals():
    ok, value, err = parse_guess("4.5")
    assert not ok and value is None
    assert "Decimals" in err

def test_parse_rejects_text():
    assert parse_guess("abc") == (False, None, "That is not a number.")


# update_score: wins earn points scaled by range size; misses cost nothing.

def test_first_try_win_on_normal_range():
    assert update_score(0, "Win", attempt_number=1, range_size=100) == 100

def test_later_win_earns_fewer_points():
    assert update_score(0, "Win", attempt_number=3, range_size=100) == 80

def test_win_points_never_drop_below_minimum():
    assert update_score(0, "Win", attempt_number=20, range_size=100) == 10

def test_wrong_guess_does_not_change_score():
    assert update_score(0, "Too High", attempt_number=1) == 0
    assert update_score(0, "Too Low", attempt_number=1) == 0

def test_late_win_beats_a_loss():
    # Losing scores 0, so any win must be worth more.
    assert update_score(0, "Win", attempt_number=20, range_size=2) > 0

def test_wider_range_is_worth_more():
    easy = update_score(0, "Win", attempt_number=1, range_size=20)
    hard = update_score(0, "Win", attempt_number=1, range_size=200)
    assert easy < 100 < hard
