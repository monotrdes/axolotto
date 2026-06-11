"""
bot_state_machine.py — Player bot thread logic.

Each bot runs in its own thread via ThreadPoolExecutor. It loops:
  1. Choose an action category by personality weights
  2. Pick a specific action within that category
  3. Report the action zone → execute action → stay visible for a realistic duration
  4. Brief idle think-time
  5. Periodically refresh owned axolotitos/boards/boosters

Key design: actions report their zone BEFORE executing, then sleep for a
visible_duration that simulates the real-world time the action would take
(e.g. 3-8s for a match, 0.5-2s for a shop purchase).  This makes the
AdminChaosLiveViz dashboard show realistic activity density instead of
99% idle dots.
"""
import time
import threading
from typing import Callable, Optional
from datetime import datetime, timezone

from chaos_types import (
    SecurityIncident, IncidentSeverity, ACTION_CATEGORIES, _rng,
)
from runtime_state import (
    record_incident, increment_counter, increment_stat,
    report_activity, remove_activity,
)
from bot_actions import (
    action_buy_random_booster,
    action_open_booster,
    action_buy_vip,
    action_play_match,
    action_feed_axolotito,
    action_sleep_axolotito,
    action_wake_axolotito,
    action_claim_daily_reward,
    action_claim_vip_frj,
    action_equip_cave_item,
    action_register_multiplayer,
    action_roll_gashapon,
    action_roll_gashapon_ticket,
    action_expand_cave,
    action_melt_random_card,
    action_list_board_for_sale,
    action_buy_random_market_board,
    refresh_bot_state,
    action_stake_axolotito,
    action_unstake_axolotito,
)


class PlayerBot:
    """Encapsulates a single simulated player running in a thread.

    Not a threading.Thread subclass — its run() method is submitted to
    ThreadPoolExecutor as a plain callable.
    """

    def __init__(
        self,
        thread_id: str,
        user_id: str,
        personality: dict,
        duration_seconds: float,
        stop_event: threading.Event,
    ):
        self.thread_id = thread_id
        self.user_id = user_id
        self.personality = personality
        self.duration = duration_seconds
        self.stop_event = stop_event

        # Player state (refreshed periodically)
        self.axolotito_ids: list[int] = []
        self.idle_axo_ids: list[int] = []
        self.staked_axo_ids: list[int] = []
        self.sleeping_axo_ids: list[int] = []
        self.board_ids: list[int] = []
        self.booster_inv_ids: list[int] = []
        self.tutorial_completed: bool = False

        # Counters
        self.actions_taken = 0
        self.last_refresh = 0.0
        self.refresh_interval = 10.0  # refresh player state every 10s

    def run(self) -> dict:
        """Main bot loop. Returns final stats dict."""
        start = time.monotonic()

        # ── Staggered start: random initial delay so bots don't all begin at once ──
        initial_delay = _rng.uniform(0.0, min(8.0, self.duration * 0.15))
        print(f"[DEBUG] {self.thread_id}: starting in {initial_delay:.1f}s (uid={self.user_id[:25]}...)", flush=True)
        self.stop_event.wait(initial_delay)
        if self.stop_event.is_set():
            remove_activity(self.thread_id)
            return {"thread_id": self.thread_id, "actions_taken": 0}

        # Initial state fetch
        report_activity(self.thread_id, "idle", "inicializando", "bot", self.personality["name"])
        self._refresh_state()
        print(f"[DEBUG] {self.thread_id}: state refreshed (axos={len(self.axolotito_ids)} boards={len(self.board_ids)} boosters={len(self.booster_inv_ids)})", flush=True)

        while not self.stop_event.is_set():
            elapsed = time.monotonic() - start
            if elapsed > self.duration:
                break

            # Choose an action (zone, description, callable, visible_duration)
            chosen = self._choose_action()
            if chosen is None:
                report_activity(self.thread_id, "idle", "sin acción disponible", "bot", self.personality["name"])
                self.stop_event.wait(0.15)
                continue

            zone, desc, action_fn, visible_duration = chosen

            # ── Report activity BEFORE executing — stays visible for visible_duration ──
            report_activity(self.thread_id, zone, desc, "bot", self.personality["name"])

            # Execute the real action (fast DB call)
            if self.actions_taken == 0:
                print(f"[DEBUG] {self.thread_id}: executing {zone}/{desc} (visible={visible_duration:.1f}s)...", flush=True)

            result = action_fn()

            if self.actions_taken == 0:
                ok = result.get('ok') if isinstance(result, dict) else 'not-dict'
                print(f"[DEBUG] {self.thread_id}: result ok={ok}", flush=True)

            self.actions_taken += 1

            # Classify unexpected results
            self._classify_result(result)

            # Periodic state refresh (during the visible window to save time)
            if time.monotonic() - self.last_refresh > self.refresh_interval:
                self._refresh_state()

            # ── Stay visible in this action zone for the minimum duration ──
            # This simulates the real-world time the action takes and makes the
            # admin dashboard show realistic activity patterns.
            if self.stop_event.wait(visible_duration):
                break  # stop_event was set during visible wait

            # ── Brief transition to idle between actions ──
            # Think-time is short — the visible_duration IS the main pacing mechanism.
            report_activity(self.thread_id, "idle", "pensando", "bot", self.personality["name"])
            brief_idle = _rng.uniform(0.02, 0.25)
            if self.stop_event.wait(brief_idle):
                break

        # ── Cleanup: remove this bot from the live activity map ──
        remove_activity(self.thread_id)
        print(f"[DEBUG] {self.thread_id}: finished ({self.actions_taken} actions)", flush=True)
        return {
            "thread_id": self.thread_id,
            "actions_taken": self.actions_taken,
            "axolotitos": len(self.axolotito_ids),
            "boards": len(self.board_ids),
        }

    def _refresh_state(self) -> None:
        """Refresh the bot's knowledge of its owned assets."""
        state = refresh_bot_state(self.user_id)
        if isinstance(state, dict):
            axos_info = state.get("axolotitos", [])
            self.axolotito_ids = [axo["id"] for axo in axos_info]
            self.idle_axo_ids = [axo["id"] for axo in axos_info if axo["status"] == "idle"]
            self.staked_axo_ids = [axo["id"] for axo in axos_info if axo["status"] in ("studying", "resting")]
            self.sleeping_axo_ids = [axo["id"] for axo in axos_info if axo["status"] == "sleeping"]
            
            self.board_ids = state.get("board_ids", [])
            self.booster_inv_ids = state.get("booster_inv_ids", [])
            self.tutorial_completed = state.get("tutorial_completed", False)
        self.last_refresh = time.monotonic()

    def _choose_action(self) -> Optional[tuple[str, str, Callable[[], dict], float]]:
        """Weighted random action selection. Returns (zone, description, callable, visible_duration)."""
        if not self.tutorial_completed:
            from bot_actions import action_progress_tutorial
            dur = _rng.uniform(1.2, 2.5)  # Simulate think/play time for tutorial step
            return ("tutorial", "Haciendo tutorial", lambda: action_progress_tutorial(self.user_id), dur)

        weights = {
            "shop": self.personality.get("shop_weight", 0.25),
            "game": self.personality.get("game_weight", 0.25),
            "care": self.personality.get("care_weight", 0.25),
            "decor": self.personality.get("decor_weight", 0.25),
        }
        categories = list(weights.keys())
        w = [weights[c] for c in categories]
        try:
            category = _rng.choices(categories, weights=w, k=1)[0]
        except Exception as e:
            print(f"[DEBUG] {self.thread_id}: choices() failed: {e}", flush=True)
            return None

        if self.actions_taken == 0:
            print(f"[DEBUG] {self.thread_id}: category={category}", flush=True)

        if category == "shop":
            return self._pick_shop_action()
        elif category == "game":
            return self._pick_game_action()
        elif category == "care":
            return self._pick_care_action()
        elif category == "decor":
            return self._pick_decor_action()
        return None

    def _pick_shop_action(self) -> Optional[tuple[str, str, Callable[[], dict], float]]:
        """Pick a shop action. Returns (zone, description, callable, visible_duration)."""
        uid = self.user_id
        choice = _rng.random()

        if choice < 0.20 and self.booster_inv_ids:
            inv_id = _rng.choice(self.booster_inv_ids)
            dur = _rng.uniform(0.6, 1.8)
            return ("shop", "Abriendo booster", lambda: action_open_booster(uid, inv_id), dur)
        elif choice < 0.40:
            dur = _rng.uniform(0.8, 2.0)
            return ("shop", "Comprando booster", lambda: action_buy_random_booster(uid), dur)
        elif choice < 0.55:
            dur = _rng.uniform(0.8, 2.5)
            tier = _rng.choice(["common", "premium"])
            return ("gashapon", f"Gashapon {tier} (FRJ)", lambda t=tier: action_roll_gashapon(uid, t), dur)
        elif choice < 0.67:
            dur = _rng.uniform(0.5, 2.0)
            tier = _rng.choice(["common", "premium"])
            return ("gashapon", f"Gashapon {tier} (ticket)", lambda t=tier: action_roll_gashapon_ticket(uid, t), dur)
        elif choice < 0.78:
            dur = _rng.uniform(0.3, 1.0)
            return ("daily", "Reclamo diario", lambda: action_claim_daily_reward(uid), dur)
        elif choice < 0.88:
            dur = _rng.uniform(0.3, 0.8)
            return ("daily", "VIP FRJ claim", lambda: action_claim_vip_frj(uid), dur)
        elif choice < 0.95:
            dur = _rng.uniform(0.8, 2.0)
            return ("shop", "Comprando en mercado", lambda: action_buy_random_market_board(uid), dur)
        else:
            vip_tier = self.personality.get("vip_tier")
            if vip_tier:
                dur = _rng.uniform(1.0, 3.0)
                return ("shop", f"Comprando VIP {vip_tier}", lambda: action_buy_vip(uid, vip_tier), dur)
            dur = _rng.uniform(0.8, 2.0)
            return ("shop", "Comprando booster", lambda: action_buy_random_booster(uid), dur)

    def _pick_game_action(self) -> Optional[tuple[str, str, Callable[[], dict], float]]:
        """Pick a game action. Returns (zone, description, callable, visible_duration).

        Game matches get longer visible durations (3-8s) to simulate real match length.
        Bots without axolotitos are stuck — they can't play. We mark them as blocked.
        """
        uid = self.user_id
        
        # Prefer using idle axolotitos for playing matches
        idle_axos = self.idle_axo_ids
        if not idle_axos:
            # If all are staked or sleeping, maybe unstake one or wake one up?
            if self.staked_axo_ids and _rng.random() < 0.5:
                axo_id = _rng.choice(self.staked_axo_ids)
                dur = _rng.uniform(0.5, 1.5)
                return ("staking", "Unstakeando axo para jugar", lambda: action_unstake_axolotito(axo_id, uid), dur)
            elif self.sleeping_axo_ids and _rng.random() < 0.5:
                axo_id = _rng.choice(self.sleeping_axo_ids)
                dur = _rng.uniform(0.3, 1.0)
                return ("care", "Despertando axo para jugar", lambda: action_wake_axolotito(axo_id, uid), dur)
                
            # Fallback if no idle axolotitos can be readied
            dur = _rng.uniform(0.5, 1.5)
            choice = _rng.random()
            if choice < 0.5:
                return ("gashapon", "Gashapon (sin axo libre)", lambda: action_roll_gashapon(uid, "common"), dur)
            else:
                return ("shop", "Comprando (sin axo libre)", lambda: action_buy_random_booster(uid), dur)

        axo_id = _rng.choice(idle_axos)
        choice = _rng.random()

        if choice < 0.55:
            # Solo match: 3-7 seconds visible
            room = _rng.choice(["rookie", "champion"])
            play_style = self.personality.get("play_style", "rookie")
            room = play_style if play_style in ("rookie", "champion") else room
            dur = _rng.uniform(3.0, 7.0)
            return ("solo_game", f"Jugando {room}", lambda: action_play_match(
                axolotito_id=axo_id, user_id=uid, room_name=room,
                multiplier=1, bot_enabled=False,
            ), dur)
        elif choice < 0.85:
            # Multiplayer registration + match: 4-8 seconds visible
            board_ids = self.board_ids
            if not board_ids:
                dur = _rng.uniform(3.0, 6.0)
                room = _rng.choice(["rookie", "champion"])
                return ("solo_game", f"Jugando {room}", lambda: action_play_match(
                    axolotito_id=axo_id, user_id=uid, room_name=room,
                ), dur)
            selected_boards = board_ids[:min(3, len(board_ids))]
            rt = _rng.choice(["rookie", "champion"])
            dur = _rng.uniform(4.0, 8.0)
            return ("multiplayer", f"Registrando {rt}", lambda: action_register_multiplayer(
                axolotito_id=axo_id, user_id=uid, board_ids=selected_boards, room_type=rt,
            ), dur)
        else:
            # Gashapon as a game-adjacent activity
            dur = _rng.uniform(1.0, 3.0)
            tier = _rng.choice(["common", "premium"])
            return ("gashapon", f"Gashapon {tier}", lambda t=tier: action_roll_gashapon(uid, t), dur)

    def _pick_care_action(self) -> Optional[tuple[str, str, Callable[[], dict], float]]:
        """Pick a care action. Returns (zone, description, callable, visible_duration)."""
        uid = self.user_id
        
        # Care actions are only valid for idle or sleeping axolotitos.
        idle_axos = self.idle_axo_ids
        sleeping_axos = self.sleeping_axo_ids
        
        if not idle_axos and not sleeping_axos:
            dur = _rng.uniform(0.3, 1.0)
            return ("daily", "Sin axos libres — daily", lambda: action_claim_daily_reward(uid), dur)

        if sleeping_axos and (not idle_axos or _rng.random() < 0.3):
            axo_id = _rng.choice(sleeping_axos)
            dur = _rng.uniform(0.3, 1.0)
            return ("care", "Despertando axo", lambda: action_wake_axolotito(axo_id, uid), dur)
            
        axo_id = _rng.choice(idle_axos)
        choice = _rng.random()

        if choice < 0.60:
            food = _rng.choice(["pellet", "worm", "shrimp"])
            dur = _rng.uniform(0.5, 1.5)
            return ("care", f"Alimentando ({food})", lambda: action_feed_axolotito(axo_id, uid, food), dur)
        else:
            dur = _rng.uniform(0.4, 1.2)
            return ("care", "Durmiendo axo", lambda: action_sleep_axolotito(axo_id, uid), dur)

    def _pick_decor_action(self) -> Optional[tuple[str, str, Callable[[], dict], float]]:
        """Pick a decor/cave/forge action. Returns (zone, description, callable, visible_duration)."""
        uid = self.user_id
        axo_ids = self.axolotito_ids

        if not axo_ids:
            dur = _rng.uniform(0.3, 0.8)
            return ("daily", "Sin axos — VIP claim", lambda: action_claim_vip_frj(uid), dur)

        # 1. Staking actions check
        if self.idle_axo_ids and _rng.random() < 0.35:
            # Put an axolotito to stake (studying or resting)
            axo_id = _rng.choice(self.idle_axo_ids)
            status = _rng.choice(["studying", "resting"])
            dur = _rng.uniform(0.5, 1.5)
            return ("staking", f"Stakeando axo ({status})", lambda: action_stake_axolotito(axo_id, uid, status), dur)

        if self.staked_axo_ids and _rng.random() < 0.25:
            # Take out of staking / claim reward
            axo_id = _rng.choice(self.staked_axo_ids)
            dur = _rng.uniform(0.5, 1.5)
            return ("staking", "Unstakeando axo", lambda: action_unstake_axolotito(axo_id, uid), dur)

        choice = _rng.random()

        if choice < 0.30:
            # Cave expansion
            dur = _rng.uniform(2.0, 5.0)
            return ("cave", "Expandiendo cueva", lambda: action_expand_cave(uid), dur)
        elif choice < 0.55:
            # Equip cave decor item
            dec_axo = _rng.choice(self.idle_axo_ids) if self.idle_axo_ids else _rng.choice(axo_ids)
            dur = _rng.uniform(0.5, 2.0)
            return ("cave", "Decorando cueva", lambda: action_equip_cave_item(dec_axo, uid), dur)
        elif choice < 0.78:
            # Card melter / forge
            dur = _rng.uniform(1.0, 3.0)
            return ("cave", "Fundiendo cartas", lambda: action_melt_random_card(uid), dur)
        else:
            # P2P market — list board for sale
            dur = _rng.uniform(1.0, 2.5)
            return ("shop", "Vendiendo en mercado", lambda: action_list_board_for_sale(uid), dur)

    def _classify_result(self, result: dict) -> None:
        """Classify action result and record incidents for unexpected outcomes."""
        if result.get("ok"):
            return

        code = result.get("error_code", 0)
        detail = result.get("detail", "")

        # 400, 402, 403, 404, 409, 422 are expected business rejections
        # (insufficient funds, energy depleted, permission denied, duplicate, etc.)
        if code in (400, 402, 403, 404, 409, 422):
            return  # Expected — no incident

        # 500 or unknown errors are concerning
        if code == 500:
            record_incident(SecurityIncident(
                severity=IncidentSeverity.WARNING,
                category="bot_action_500",
                description=f"Bot {self.thread_id} got HTTP 500 from action",
                status_code=500,
                detail=detail[:200],
                timestamp=datetime.now(timezone.utc).isoformat(),
                thread_id=self.thread_id,
            ))
            increment_stat("bot_500s")
        elif code != 0:
            # Unexpected non-standard error code
            record_incident(SecurityIncident(
                severity=IncidentSeverity.WARNING,
                category="bot_action_unexpected_code",
                description=f"Bot {self.thread_id} got unexpected code {code}",
                status_code=code,
                detail=detail[:200],
                timestamp=datetime.now(timezone.utc).isoformat(),
                thread_id=self.thread_id,
            ))
