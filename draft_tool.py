import streamlit as st
import pandas as pd
import io
import re

# ======================================================================================
# Data and Configuration
# ======================================================================================

# This is a constant list of positions used to create the tabs on the UI
# We add "Overall" as the first tab for the new feature
UI_TABS = ['Overall', 'QB', 'RB', 'WR', 'TE', 'K/DST']
POSITIONS = ['QB', 'RB', 'WR', 'TE', 'K', 'DST'] # Used for backend logic

# Player data from the previous report, now in CSV format
PLAYER_DATA_CSV = """Position,Tier,Player,Team,Target Bid,Max Bid
QB,Tier 1: The Untouchables,Josh Allen,BUF,62,68
QB,Tier 1: The Untouchables,Lamar Jackson,BAL,60,66
QB,Tier 1: The Untouchables,Jalen Hurts,PHI,57,63
QB,Tier 2: Elite QB1s,Joe Burrow,CIN,51,56
QB,Tier 2: Elite QB1s,Jayden Daniels,WAS,49,54
QB,Tier 2: Elite QB1s,Patrick Mahomes,KC,47,52
QB,Tier 2: Elite QB1s,Kyler Murray,ARI,45,50
QB,Tier 3: Foundational QB2s,Dak Prescott,DAL,38,42
QB,Tier 3: Foundational QB2s,Brock Purdy,SF,35,39
QB,Tier 3: Foundational QB2s,Jared Goff,DET,32,36
QB,Tier 3: Foundational QB2s,Justin Fields,NYJ,29,33
QB,Tier 3: Foundational QB2s,Bo Nix,DEN,27,31
QB,Tier 4: Critical QB3s / High-Upside QB2s,Justin Herbert,LAC,21,24
QB,Tier 4: Critical QB3s / High-Upside QB2s,Jordan Love,GB,19,22
QB,Tier 4: Critical QB3s / High-Upside QB2s,C.J. Stroud,HOU,18,20
QB,Tier 4: Critical QB3s / High-Upside QB2s,Trevor Lawrence,JAX,16,18
QB,Tier 4: Critical QB3s / High-Upside QB2s,Baker Mayfield,TB,14,16
QB,Tier 4: Critical QB3s / High-Upside QB2s,Caleb Williams,CHI,12,14
QB,Tier 5: Value Bench Stashes,Matthew Stafford,LAR,8,9
QB,Tier 5: Value Bench Stashes,Tua Tagovailoa,MIA,7,8
QB,Tier 5: Value Bench Stashes,J.J. McCarthy,MIN,5,6
QB,Tier 5: Value Bench Stashes,Geno Smith,LV,4,5
QB,Tier 5: Value Bench Stashes,Drake Maye,NE,3,4
QB,Tier 5: Value Bench Stashes,Aaron Rodgers,PIT,2,3
QB,Tier 5: Value Bench Stashes,Michael Penix Jr.,ATL,1,2
QB,Tier 5: Value Bench Stashes,Bryce Young,CAR,1,1
RB,Tier 1: Non-PPR Titans,Saquon Barkley,PHI,48,53
RB,Tier 1: Non-PPR Titans,Derrick Henry,BAL,46,51
RB,Tier 1: Non-PPR Titans,Bijan Robinson,ATL,45,50
RB,Tier 2: Elite RB1s,Jahmyr Gibbs,DET,41,45
RB,Tier 2: Elite RB1s,Christian McCaffrey,SF,39,43
RB,Tier 2: Elite RB1s,Jonathan Taylor,IND,37,41
RB,Tier 2: Elite RB1s,Josh Jacobs,GB,35,39
RB,Tier 3: Rock-Solid Starters,Kyren Williams,LAR,29,32
RB,Tier 3: Rock-Solid Starters,De'Von Achane,MIA,27,30
RB,Tier 3: Rock-Solid Starters,Ashton Jeanty,LV,25,28
RB,Tier 3: Rock-Solid Starters,Breece Hall,NYJ,24,27
RB,Tier 3: Rock-Solid Starters,Joe Mixon,HOU,22,25
RB,Tier 3: Rock-Solid Starters,James Cook,BUF,19,22
RB,Tier 4: High-Floor Flex Plays,Chuba Hubbard,CAR,17,19
RB,Tier 4: High-Floor Flex Plays,James Conner,ARI,15,17
RB,Tier 4: High-Floor Flex Plays,Kenneth Walker III,SEA,13,15
RB,Tier 4: High-Floor Flex Plays,David Montgomery,DET,11,12
RB,Tier 4: High-Floor Flex Plays,Alvin Kamara,NO,9,10
RB,Tier 4: High-Floor Flex Plays,Bucky Irving,TB,8,9
RB,Tier 4: High-Floor Flex Plays,D'Andre Swift,CHI,6,7
RB,Tier 5: High-Upside Bench Targets,Chase Brown,CIN,3,4
RB,Tier 5: High-Upside Bench Targets,Javonte Williams,DAL,3,4
RB,Tier 5: High-Upside Bench Targets,Jaylen Warren,PIT,2,3
RB,Tier 5: High-Upside Bench Targets,Rhamondre Stevenson,NE,2,3
RB,Tier 5: High-Upside Bench Targets,Tony Pollard,TEN,1,2
RB,Tier 5: High-Upside Bench Targets,Zach Charbonnet,SEA,1,2
RB,Tier 5: High-Upside Bench Targets,Tyjae Spears,TEN,1,1
RB,Tier 5: High-Upside Bench Targets,Omarion Hampton,LAC,1,1
RB,Tier 5: High-Upside Bench Targets,Isiah Pacheco,KC,1,1
WR,Tier 1: Alpha Touchdown Scorers,Ja'Marr Chase,CIN,44,49
WR,Tier 1: Alpha Touchdown Scorers,Justin Jefferson,MIN,42,47
WR,Tier 1: Alpha Touchdown Scorers,CeeDee Lamb,DAL,41,46
WR,Tier 2: Elite WR1s,Puka Nacua,LAR,34,38
WR,Tier 2: Elite WR1s,Nico Collins,HOU,32,36
WR,Tier 2: Elite WR1s,A.J. Brown,PHI,30,34
WR,Tier 2: Elite WR1s,Amon-Ra St. Brown,DET,28,31
WR,Tier 3: High-End WR2s,Drake London,ATL,25,28
WR,Tier 3: High-End WR2s,Malik Nabers,NYG,23,26
WR,Tier 3: High-End WR2s,Tyreek Hill,MIA,21,23
WR,Tier 3: High-End WR2s,Brian Thomas Jr.,JAC,19,21
WR,Tier 3: High-End WR2s,D.K. Metcalf,PIT,16,18
WR,Tier 3: High-End WR2s,Tee Higgins,CIN,14,16
WR,Tier 4: Value Starters,Mike Evans,TB,12,14
WR,Tier 4: Value Starters,Davante Adams,LAR,11,12
WR,Tier 4: Value Starters,Terry McLaurin,WAS,10,11
WR,Tier 4: Value Starters,D.J. Moore,CHI,8,9
WR,Tier 4: Value Starters,Marvin Harrison Jr.,ARI,7,8
WR,Tier 4: Value Starters,George Pickens,DAL,5,6
WR,Tier 5: High-Upside Bench Fliers,Jameson Williams,DET,3,4
WR,Tier 5: High-Upside Bench Fliers,Xavier Worthy,KC,3,4
WR,Tier 5: High-Upside Bench Fliers,Rashee Rice,KC,2,3
WR,Tier 5: High-Upside Bench Fliers,Ladd McConkey,LAC,2,3
WR,Tier 5: High-Upside Bench Fliers,Courtland Sutton,DEN,1,2
WR,Tier 5: High-Upside Bench Fliers,Jayden Reed,GB,1,2
WR,Tier 5: High-Upside Bench Fliers,Chris Godwin,TB,1,1
WR,Tier 5: High-Upside Bench Fliers,DeAndre Hopkins,TEN,1,1
WR,Tier 5: High-Upside Bench Fliers,Christian Watson,GB,1,1
TE,Tier 1: The True Difference-Makers,Brock Bowers,LV,24,27
TE,Tier 1: The True Difference-Makers,George Kittle,SF,22,25
TE,Tier 2: Set-and-Forget Starters,Trey McBride,ARI,16,18
TE,Tier 2: Set-and-Forget Starters,Sam LaPorta,DET,13,15
TE,Tier 2: Set-and-Forget Starters,Mark Andrews,BAL,11,13
TE,Tier 3: The Blob / Late-Round Values,Travis Kelce,KC,8,9
TE,Tier 3: The Blob / Late-Round Values,David Njoku,CLE,6,7
TE,Tier 3: The Blob / Late-Round Values,Jake Ferguson,DAL,4,5
TE,Tier 3: The Blob / Late-Round Values,Dallas Goedert,PHI,3,4
TE,Tier 3: The Blob / Late-Round Values,Jonnu Smith,MIA,2,3
TE,Tier 3: The Blob / Late-Round Values,T.J. Hockenson,MIN,1,2
TE,Tier 3: The Blob / Late-Round Values,Evan Engram,DEN,1,1
TE,Tier 3: The Blob / Late-Round Values,Tucker Kraft,GB,1,1
TE,Tier 3: The Blob / Late-Round Values,Pat Freiermuth,PIT,1,1
K,Tier 1: The Only Tier,Kicker (K),N/A,1,1
DST,Tier 1: The Only Tier,Defense (DST),N/A,1,1
"""

# League Configuration
NUM_TEAMS = 10
BUDGET_PER_TEAM = 200
ROSTER_SPOTS = 15
STARTER_NEEDS = {'QB': 2, 'RB': 2, 'WR': 3, 'TE': 1, 'FLEX': 1, 'K': 1, 'DST': 1}


# ======================================================================================
# Helper Functions
# ======================================================================================

def initialize_state():
    """Sets up the initial state of the draft if it doesn't exist."""
    if 'initialized' in st.session_state:
        return

    player_df = pd.read_csv(io.StringIO(PLAYER_DATA_CSV))
    player_df['Status'] = 'Available'
    player_df['Drafted By'] = ''
    player_df['Price'] = 0
    player_df['Surplus'] = 0
    player_df['Original Target Bid'] = player_df['Target Bid']
    player_df['Original Max Bid'] = player_df['Max Bid']
    player_df['Value Points'] = player_df['Max Bid'] - 1
    
    st.session_state.player_data = player_df
    st.session_state.teams = {f"Team {i+1}": {'budget': BUDGET_PER_TEAM, 'roster': [], 'surplus': 0, 'players_drafted': 0} for i in range(NUM_TEAMS)}
    st.session_state.draft_log = []

    total_discretionary_budget = (NUM_TEAMS * BUDGET_PER_TEAM) - (NUM_TEAMS * ROSTER_SPOTS)
    total_value_points = player_df[player_df['Value Points'] > 0]['Value Points'].sum()
    
    st.session_state.inflation = {
        'remaining_budget': total_discretionary_budget,
        'remaining_value': total_value_points,
        'inflation_rate': 1.0
    }
    st.session_state.initialized = True

def update_inflated_values():
    """Recalculates player values based on current inflation."""
    player_df = st.session_state.player_data
    
    if st.session_state.inflation['remaining_value'] > 0:
        new_inflation_rate = st.session_state.inflation['remaining_budget'] / st.session_state.inflation['remaining_value']
        st.session_state.inflation['inflation_rate'] = new_inflation_rate
    else: 
        st.session_state.inflation['inflation_rate'] = 0

    available_mask = player_df['Status'] == 'Available'
    for idx, player in player_df[available_mask].iterrows():
        original_value_points = player['Value Points']
        if original_value_points > 0:
            new_max_bid = (original_value_points * st.session_state.inflation['inflation_rate']) + 1
            player_df.loc[idx, 'Max Bid'] = round(new_max_bid)
            
            original_proportion = player['Original Target Bid'] / player['Original Max Bid'] if player['Original Max Bid'] > 0 else 0
            new_target_bid = new_max_bid * original_proportion
            player_df.loc[idx, 'Target Bid'] = round(new_target_bid)
        else:
            player_df.loc[idx, 'Max Bid'] = 1
            player_df.loc[idx, 'Target Bid'] = 1
            
    st.session_state.player_data = player_df

def draft_player(player_name, team_name, price):
    """Handles the logic of drafting a player."""
    player_df = st.session_state.player_data
    player_series = player_df[player_df['Player'] == player_name]
    if player_series.empty:
        st.error(f"Player '{player_name}' not found.")
        return

    player_index = player_series.index[0]
    
    team_budget = st.session_state.teams[team_name]['budget']
    roster_size = len(st.session_state.teams[team_name]['roster'])
    spots_to_fill = ROSTER_SPOTS - roster_size
    max_bid_for_team = team_budget - (spots_to_fill - 1) if spots_to_fill > 0 else team_budget
    if price > max_bid_for_team:
        st.error(f"{team_name} cannot afford this bid. Their max possible bid is ${max_bid_for_team}.")
        return

    player_max_bid = player_df.loc[player_index, 'Max Bid']
    player_position = player_df.loc[player_index, 'Position']
    surplus = player_max_bid - price
    
    player_df.loc[player_index, 'Status'] = 'Drafted'
    player_df.loc[player_index, 'Drafted By'] = team_name
    player_df.loc[player_index, 'Price'] = price
    player_df.loc[player_index, 'Surplus'] = surplus

    st.session_state.teams[team_name]['budget'] -= price
    st.session_state.teams[team_name]['roster'].append({'Player': player_name, 'Price': price, 'Position': player_position})
    st.session_state.teams[team_name]['surplus'] += surplus
    st.session_state.teams[team_name]['players_drafted'] += 1

    pick_num = len(st.session_state.draft_log) + 1
    st.session_state.draft_log.insert(0, f"Pick {pick_num}: {team_name} drafted {player_name} for ${price} (Surplus: ${surplus}).")

    player_value_points = player_df.loc[player_index, 'Value Points']
    st.session_state.inflation['remaining_budget'] -= (price - 1)
    if player_value_points > 0:
        st.session_state.inflation['remaining_value'] -= player_value_points

    update_inflated_values()
    st.success(f"Successfully drafted {player_name} to {team_name} for ${price}.")
    st.session_state.nominated_player = None

def undo_last_pick():
    """Undoes the most recent draft pick."""
    if not st.session_state.draft_log:
        st.warning("No picks to undo.")
        return

    last_pick_str = st.session_state.draft_log.pop(0)
    match = re.match(r"Pick \d+: (.*) drafted (.*) for \$(\d+)", last_pick_str)
    if not match:
        st.error("Could not parse last pick. Unable to undo.")
        st.session_state.draft_log.insert(0, last_pick_str)
        return
        
    team_name, player_name, price_str = match.groups()
    price = int(price_str)

    player_df = st.session_state.player_data
    player_series = player_df[player_df['Player'] == player_name]
    if player_series.empty:
        st.error(f"Cannot find player '{player_name}' to undo draft pick.")
        return
        
    player_index = player_series.index[0]
    player_surplus = player_df.loc[player_index, 'Surplus']

    st.session_state.teams[team_name]['budget'] += price
    st.session_state.teams[team_name]['roster'] = [p for p in st.session_state.teams[team_name]['roster'] if p['Player'] != player_name]
    st.session_state.teams[team_name]['surplus'] -= player_surplus
    st.session_state.teams[team_name]['players_drafted'] -= 1

    player_value_points = player_df.loc[player_index, 'Value Points']
    st.session_state.inflation['remaining_budget'] += (price - 1)
    if player_value_points > 0:
        st.session_state.inflation['remaining_value'] += player_value_points
        
    player_df.loc[player_index, 'Status'] = 'Available'
    player_df.loc[player_index, 'Drafted By'] = ''
    player_df.loc[player_index, 'Price'] = 0
    player_df.loc[player_index, 'Surplus'] = 0

    update_inflated_values()
    st.info(f"Undid last pick: {player_name} to {team_name}.")

def get_need_level_html(position, num_owned):
    """Generates HTML for a color-coded need level based on position."""
    required = STARTER_NEEDS.get(position, 1) # Get required starters, default to 1
    
    if num_owned == 0:
        need = "Critical"
        color = "#ff4d4d"  # Red
    elif num_owned < required:
        need = "High"
        color = "#ffc107"  # Amber
    elif num_owned == required:
        need = "Medium"
        color = "#5cb85c"  # Green
    else: # num_owned > required
        need = "Low"
        color = "#5bc0de"  # Info Blue

    return f'<span style="color: {color}; font-weight: bold;">{need}</span>'


# ======================================================================================
# UI Layout
# ======================================================================================

st.set_page_config(layout="wide", page_title="Auction Draft Tool")

initialize_state()

if 'nominated_player' not in st.session_state:
    st.session_state.nominated_player = None

with st.sidebar:
    st.header("⚙️ League Setup")
    st.write("Edit your league's team names here.")
    current_teams = list(st.session_state.teams.keys())
    new_team_names = {}
    for i, team in enumerate(current_teams):
        new_name = st.text_input(f"Team {i+1} Name", value=team, key=f"team_name_{i}")
        if new_name != team:
            new_team_names[team] = new_name
    if st.button("Update Team Names"):
        updated_teams = st.session_state.teams.copy()
        for old_name, new_name in new_team_names.items():
            if new_name and new_name not in updated_teams:
                updated_teams[new_name] = updated_teams.pop(old_name)
        st.session_state.teams = updated_teams
        st.rerun()

st.title("🏆 Fantasy Football Auction Draft Tool")

player_df = st.session_state.player_data
available_players_df = player_df[player_df['Status'] == 'Available']

st.session_state.nominated_player = st.selectbox(
    "Nominate a Player (type to search)", 
    options=available_players_df['Player'].sort_values().tolist(),
    index=None,
    placeholder="Type player name to begin..."
)

if st.session_state.nominated_player:
    hub_container = st.container(border=True)
    with hub_container:
        p_info, p_next, p_controls, p_teams = st.columns([1.2, 1.2, 1, 3])

        nominated_player_data = player_df[player_df['Player'] == st.session_state.nominated_player].iloc[0]
        player_pos = nominated_player_data['Position']

        with p_info:
            st.header(f"On the Block")
            st.subheader(f"{nominated_player_data['Player']}")
            st.markdown(f"**Position:** {player_pos} | **Team:** {nominated_player_data['Team']}")
            st.markdown(f"**Tier:** {nominated_player_data['Tier']}")
            st.metric(label="Target Bid", value=f"${nominated_player_data['Target Bid']}")
            st.metric(label="Max Bid", value=f"${nominated_player_data['Max Bid']}")

        with p_next:
            st.header("Next Best Available")
            next_best_df = available_players_df[
                (available_players_df['Position'] == player_pos) & 
                (available_players_df['Player'] != st.session_state.nominated_player)
            ].sort_values(by='Max Bid', ascending=False).head(3)
            if next_best_df.empty:
                st.write(f"No other {player_pos}s available.")
            else:
                for _, player in next_best_df.iterrows():
                    st.markdown(f"**{player['Player']}** ({player['Team']})")
                    st.markdown(f"Target: **${player['Target Bid']}** | Max: **${player['Max Bid']}**")
                    st.divider()
        
        with p_controls:
            st.header("Execute Draft")
            winning_team = st.selectbox("Winning Team", options=list(st.session_state.teams.keys()), key="winning_team_hub")
            winning_price = st.number_input("Winning Price ($)", min_value=1, value=10, step=1, key="winning_price_hub")
            if st.button("Draft Player", use_container_width=True, type="primary"):
                draft_player(st.session_state.nominated_player, winning_team, winning_price)
                st.rerun()

        with p_teams:
            st.header(f"Team Analysis ({player_pos} Focus)")
            
            html_parts = [
                '<table><thead><tr>',
                '<th>Team</th><th>Need</th><th>Roster</th><th>Budget</th><th>Max Bid</th>',
                '</tr></thead><tbody>'
            ]
            for name, data in st.session_state.teams.items():
                spots_left = ROSTER_SPOTS - len(data['roster'])
                max_bid = data['budget'] - (spots_left - 1) if spots_left > 0 else data['budget']
                
                players_at_pos = [p for p in data['roster'] if p.get('Position') == player_pos]
                roster_display = ", ".join([p['Player'] for p in players_at_pos]) if players_at_pos else "<i>None</i>"
                
                need_html = get_need_level_html(player_pos, len(players_at_pos))

                html_parts.append(f'<tr><td>{name}</td><td>{need_html}</td><td>{roster_display}</td><td>${data["budget"]}</td><td>${max_bid}</td></tr>')

            html_parts.append('</tbody></table>')
            st.markdown("".join(html_parts), unsafe_allow_html=True)

st.markdown("---")

col1, col2, col3 = st.columns([1.2, 2, 1.5])

with col1:
    st.header("⚙️ Controls & Metrics")
    if st.button("Undo Last Pick", use_container_width=True):
        undo_last_pick()
        st.rerun()
    st.markdown("---")
    inflation_rate = st.session_state.inflation['inflation_rate']
    inflation_percent = (inflation_rate - 1) * 100
    st.metric(label="Current Market Inflation", value=f"{inflation_percent:.2f}%", 
              help="Positive means players are going for more than their initial value. Negative means you can get bargains.")
    
    st.subheader("Team Tendencies")
    tendency_data = []
    for name, data in st.session_state.teams.items():
        players_drafted = data['players_drafted']
        avg_surplus = data['surplus'] / players_drafted if players_drafted > 0 else 0
        tendency_data.append({
            "Team": name,
            "Total Surplus": data['surplus'],
            "Avg. Surplus/Player": avg_surplus
        })
    tendency_df = pd.DataFrame(tendency_data)
    st.dataframe(tendency_df.style.format({
        "Total Surplus": "${:}",
        "Avg. Surplus/Player": "${:.2f}"
    }), use_container_width=True, hide_index=True)


with col2:
    st.header("📋 Draft Board")
    tabs = st.tabs(UI_TABS)
    for i, tab_name in enumerate(UI_TABS):
        with tabs[i]:
            # --- Overall Tab Logic ---
            if tab_name == 'Overall':
                pos_df = available_players_df.sort_values(by='Max Bid', ascending=False).head(50)
                st.subheader("Top 50 Best Available")
            # --- Positional Tab Logic ---
            else:
                if tab_name == 'K/DST':
                    pos_df = player_df[player_df['Position'].isin(['K', 'DST'])]
                else:
                    pos_df = player_df[player_df['Position'] == tab_name]
            
            if pos_df.empty:
                st.write(f"No more players available.")
                continue

            if tab_name != 'Overall':
                 tiers = sorted(pos_df['Tier'].unique())
                 for tier in tiers:
                    st.subheader(f"{tier}")
                    tier_df = pos_df[pos_df['Tier'] == tier].sort_values(by='Max Bid', ascending=False)
                    st.dataframe(tier_df[['Player', 'Team', 'Status', 'Drafted By', 'Price', 'Target Bid', 'Max Bid']], use_container_width=True, hide_index=True)
            else: # Render the overall tab
                st.dataframe(pos_df[['Player', 'Position', 'Team', 'Target Bid', 'Max Bid']], use_container_width=True, hide_index=True)

with col3:
    st.header("🏈 League Status")
    league_tabs = st.tabs(["Team Rosters", "Draft Log"])
    with league_tabs[0]:
        for team_name, data in st.session_state.teams.items():
            spots_left = ROSTER_SPOTS - len(data['roster'])
            max_bid = data['budget'] - (spots_left - 1) if spots_left > 0 else data['budget']
            expander_title = f"{team_name} | Budget: ${data['budget']} | Max Bid: ${max_bid} | Surplus: ${data['surplus']}"
            with st.expander(expander_title):
                if not data['roster']:
                    st.write("No players drafted yet.")
                else:
                    roster_df = pd.DataFrame(data['roster'])
                    roster_df = roster_df[['Player', 'Price']]
                    roster_df.columns = ['Player', 'Price ($)']
                    st.dataframe(roster_df.style.format({'Price ($)': '${:}'}), use_container_width=True, hide_index=True)
    with league_tabs[1]:
        if not st.session_state.draft_log:
            st.write("No picks made yet.")
        else:
            log_container = st.container(height=500)
            for pick in st.session_state.draft_log:
                log_container.text(pick)