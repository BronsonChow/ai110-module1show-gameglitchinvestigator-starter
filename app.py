import random
import streamlit as st

def get_range_for_difficulty(difficulty: str):
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def parse_guess(raw: str):
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    if guess == secret:
        return "Win", "🎉 Correct!"

    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    if outcome == "Win":
        points = 100 - 10 * (attempt_number - 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score


def reset_game(low: int, high: int, attempt_limit: int):
    st.session_state.secret = random.randint(low, high)
    # Remembered so a settings change can start a fresh game.
    st.session_state.game_settings = (low, high, attempt_limit)
    st.session_state.attempts = 0
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []


def start_new_game(low: int, high: int, attempt_limit: int, guess_key: str):
    """Reset the game from a button callback, before widgets are instantiated."""
    reset_game(low, high, attempt_limit)
    st.session_state[guess_key] = ""
    st.session_state.new_game_started = True


def submit_guess(attempt_limit: int, guess_key: str):
    """Score one guess from a button callback, so the page renders fresh state.

    Messages are stashed in session_state rather than written here, because
    st.* output from a callback is discarded.
    """
    if st.session_state.status != "playing":
        return

    messages = []
    balloons = False

    st.session_state.attempts += 1

    raw_guess = st.session_state.get(guess_key, "")
    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(raw_guess)
        messages.append(("error", err))
    else:
        st.session_state.history.append(guess_int)

        outcome, message = check_guess(guess_int, st.session_state.secret)

        if st.session_state.get("show_hint", True):
            messages.append(("warning", message))

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            balloons = True
            st.session_state.status = "won"
            messages.append((
                "success",
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}",
            ))

    # Invalid guesses use up an attempt too, so check the limit for both.
    if (
        st.session_state.status == "playing"
        and st.session_state.attempts >= attempt_limit
    ):
        st.session_state.status = "lost"
        messages.append((
            "error",
            f"Out of attempts! "
            f"The secret was {st.session_state.secret}. "
            f"Score: {st.session_state.score}",
        ))

    st.session_state.last_result = {"messages": messages, "balloons": balloons}


st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}

# Keyed per difficulty so switching difficulty restores that difficulty's default range.
min_key = f"range_min_{difficulty}"
max_key = f"range_max_{difficulty}"
default_min, default_max = get_range_for_difficulty(difficulty)
current_min = st.session_state.get(min_key, default_min)
current_max = st.session_state.get(max_key, default_max)

# Each field's limit follows the other field, so min always stays below max.
# value= is passed explicitly because Streamlit checks it against the limits.
st.sidebar.markdown("**Range**")
min_col, max_col = st.sidebar.columns(2)
with min_col:
    low = st.number_input(
        f"Min (up to {current_max - 1})",
        value=current_min,
        max_value=current_max - 1,
        step=1,
        key=min_key,
    )
with max_col:
    high = st.number_input(
        f"Max ({current_min + 1} to 1000)",
        value=current_max,
        min_value=current_min + 1,
        max_value=1000,
        step=1,
        key=max_key,
    )

attempt_limit = st.sidebar.number_input(
    "Attempts allowed (1 to 20)",
    min_value=1,
    max_value=20,
    value=attempt_limit_map[difficulty],
    step=1,
    key=f"attempt_limit_{difficulty}",
)

if "secret" not in st.session_state:
    reset_game(low, high, attempt_limit)
elif st.session_state.get("game_settings") != (low, high, attempt_limit):
    # The old secret may be outside a new range, and a new attempt limit
    # shouldn't apply to a game already in progress, so start over.
    reset_game(low, high, attempt_limit)
    st.session_state.settings_changed = True

st.subheader("Make a guess")

if st.session_state.pop("settings_changed", False):
    st.success(
        f"Range is now {low} to {high} with {attempt_limit} attempts. "
        f"New game started."
    )

st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

guess_key = f"guess_input_{difficulty}"

with st.container(border=True):
    st.markdown("**Your guesses**")
    if st.session_state.history:
        # Inline code keeps raw (invalid) entries from being read as markdown.
        st.markdown(" &nbsp; ".join(
            f"**#{i}** `{str(g).replace('`', '')}`"
            for i, g in enumerate(st.session_state.history, start=1)
        ))
    else:
        st.caption("No guesses yet.")

# A form submits when Enter is pressed in the text input.
with st.form("guess_form"):
    st.text_input(
        "Enter your guess:",
        key=guess_key
    )
    st.form_submit_button(
        "Submit Guess 🚀",
        on_click=submit_guess,
        args=(attempt_limit, guess_key),
    )

col1, col2 = st.columns(2)
with col1:
    st.button(
        "New Game 🔁",
        on_click=start_new_game,
        args=(low, high, attempt_limit, guess_key),
    )
with col2:
    show_hint = st.checkbox("Show hint", value=True, key="show_hint")

if st.session_state.pop("new_game_started", False):
    st.success("New game started.")

last_result = st.session_state.pop("last_result", None)
if last_result:
    for kind, text in last_result["messages"]:
        getattr(st, kind)(text)
    if last_result["balloons"]:
        st.balloons()

if st.session_state.status != "playing":
    if not last_result:
        if st.session_state.status == "won":
            st.success(
                f"You already won. The secret was {st.session_state.secret}. "
                f"Start a new game to play again."
            )
        else:
            st.error(
                f"Game over. The secret was {st.session_state.secret}. "
                f"Start a new game to try again."
            )
    st.stop()

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
