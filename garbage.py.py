import streamlit as st
import numpy as np
import time

st.set_page_config(page_title="Smart Trash Sorter Game", layout="centered")

# --- Q-Learning Logic ---
action_names = ["left", "stay", "right"]
state_names = ["🔋", "⬜", "⬜", "⬜", "⬜", "🗑️"]

def r(battery, garbage):
    battery_count = 10 if battery < 50 else 0
    garbage_count = 1 if garbage else 0
    return np.array([
        [0, battery_count, 0],
        [battery_count, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, garbage_count],
    ])

def t(state, action):
    if action == 1:
        return state
    elif action == 0:
        return max(state - 1, 0)
    elif action == 2:
        return min(state + 1, len(state_names) - 1)

def max_next_state_q(q, state):
    return max(q[state])

def calculate_q(rewards, gamma):
    q = np.zeros(rewards.shape)
    for _ in range(10):
        for i in range(len(rewards)):
            for j in range(len(rewards[i])):
                q[i][j] = rewards[i][j] + gamma * max_next_state_q(q, t(i, j))
    return q

def make_decision(q, state):
    best_action = np.argmax(q[state])
    if q[state][best_action] == 0:
        return 1  # stay
    return best_action

# --- Session Init ---
if 'battery' not in st.session_state:
    st.session_state.battery = 100
    st.session_state.garbage = True
    st.session_state.state = 2
    st.session_state.step = 0
    st.session_state.auto = False

st.title("🧠 Smart Trash Sorter ")
st.subheader("A Q-learning-powered AI agent")

# --- Grid Game Style View ---
def draw_grid():
    grid = ""
    for i in range(6):
        if i == st.session_state.state:
            grid += f"| 🤖 {state_names[i]} "
        else:
            grid += f"|    {state_names[i]} "
    grid += "|"
    st.markdown(grid)

                          # --- Battery UI ---
def battery_bar(level):
    color = "🟩" if level > 60 else "🟨" if level > 30 else "🟥"
    blocks = int(level / 10)
    return color * blocks + " " + str(level) + "%"

# --- Garbage Status ---
def garbage_display():
    return "🟢 Garbage Available" if st.session_state.garbage else "🔴 Garbage Collected"

# --- Action ---
def next_step():
    st.session_state.step += 1
    st.session_state.battery -= 10

    if st.session_state.garbage and st.session_state.state == len(state_names) - 1:
        st.session_state.garbage = False

    if st.session_state.state == 0:
        st.session_state.battery = 100
        st.session_state.garbage = True

    rewards = r(st.session_state.battery, st.session_state.garbage)
    q = calculate_q(rewards, gamma=0.5)
    action = make_decision(q, st.session_state.state)
    st.session_state.state = t(st.session_state.state, action)

# --- UI Section ---

draw_grid()

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"**Battery:** {battery_bar(st.session_state.battery)}")
with col2:
    st.markdown(f"**Garbage:** {garbage_display()}")

st.markdown(f"**Step:** `{st.session_state.step}`")

# --- Buttons ---
c1, c2, c3 = st.columns(3)
if c1.button("▶️ Next Step"):
    next_step()

if c2.button("🔁 Reset"):
    st.session_state.battery = 100
    st.session_state.garbage = True
    st.session_state.state = 2
    st.session_state.step = 0

if c3.button(" Auto Play (10 steps)"):
    for _ in range(10):
        next_step()
        time.sleep(0.1)
        st.session_state.rerun = True
st.stop()

st.caption("Built using Streamlit with ")
