import math


#FIX: hard difficulty is harder than normal
def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 200
    return 1, 100


def is_float(raw: str):
    try:
        float(raw)
    except ValueError:
        return False
    return True


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        value = int(raw)
    except ValueError:
        if "." in raw and is_float(raw):
            return False, None, "Decimals aren't allowed. Enter a whole number."
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    """
    Compare guess to secret and return (outcome, message).

    outcome examples: "Win", "Too High", "Too Low"
    """
    if guess == secret:
        return "Win", "🎉 Correct!"

    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    return "Too Low", "📈 Go HIGHER!"


#FIX: winning always scores more than losing
#FIX: wider ranges are worth more points
def update_score(
    current_score: int,
    outcome: str,
    attempt_number: int,
    range_size: int = 100,
):
    """Update score based on outcome, attempt number, and range size."""
    # Wrong guesses are already penalized by the shrinking win bonus,
    # so they don't also subtract points.
    if outcome == "Win":
        points = 100 - 10 * (attempt_number - 1)
        if points < 10:
            points = 10
        # Scaled by how many guesses the range needs, so 1-100 is worth 1x.
        multiplier = math.log2(range_size) / math.log2(100)
        return current_score + round(points * multiplier)

    return current_score
