from genlayer import *

class GenMarket(gl.Contract):
    creator: Address
    market_question: str
    evidence_url: str
    outcomes: dict
    total_pool: u256
    bets: dict
    resolved: bool
    winning_outcome: str
    dispute_active: bool
    dispute_reason: str

    def __init__(self, question: str, initial_evidence: str):
        self.creator = gl.message.sender_address
        self.market_question = question
        self.evidence_url = initial_evidence
        self.outcomes = {"YES": u256(0), "NO": u256(0)}
        self.total_pool = u256(0)
        self.bets = {}
        self.resolved = False
        self.winning_outcome = ""
        self.dispute_active = False
        self.dispute_reason = ""

    @gl.public.write
    def place_bet(self, choice: str) -> None:
        assert not self.resolved, "Market is already resolved"
        assert choice in ["YES", "NO"], "Choice must be YES or NO"
        assert gl.message.value > 0, "Bet amount must be greater than zero"

        user_key = f"{gl.message.sender_address}_{choice}"
        current_user_bet = self.bets.get(user_key, u256(0))
        self.bets[user_key] = current_user_bet + gl.message.value

        current_outcome_total = self.outcomes.get(choice, u256(0))
        self.outcomes[choice] = current_outcome_total + gl.message.value
        self.total_pool = self.total_pool + gl.message.value

    @gl.public.write
    def resolve_market(self) -> None:
        assert not self.resolved, "Market is already resolved"
        
        prompt = f"""
        Inspect the real-world outcome for the following prediction market:
        Question: {self.market_question}
        Evidence URL: {self.evidence_url}

        Based on the current verifiable facts from the provided URL or web data, decide the result.
        Output ONLY one word: YES or NO.
        """

        ai_result = gl.exec_prompt(prompt).strip().upper()
        
        if ai_result in ["YES", "NO"]:
            self.winning_outcome = ai_result
        else:
            self.winning_outcome = "YES"

        self.resolved = True

    @gl.public.write
    def raise_dispute(self, reason: str) -> None:
        assert self.resolved, "Market must be resolved first to dispute"
        assert not self.dispute_active, "Dispute is already active"
        assert gl.message.sender_address == self.creator, "Only market creator can raise initial dispute"

        self.dispute_reason = reason
        self.dispute_active = True

        prompt = f"""
        A dispute has been raised regarding the market resolution:
        Market Question: {self.market_question}
        Previous Winning Outcome: {self.winning_outcome}
        Dispute Reason: {self.dispute_reason}
        Evidence URL: {self.evidence_url}

        Re-evaluating all available evidence carefully.
        Did the previous decision match reality? If correct, re-confirm the winner. If wrong, switch to the other outcome.
        Output ONLY one word: YES or NO.
        """

        dispute_decision = gl.exec_prompt(prompt).strip().upper()

        if dispute_decision in ["YES", "NO"]:
            self.winning_outcome = dispute_decision
        
        self.dispute_active = False

    @gl.public.write
    def claim_winnings(self) -> None:
        assert self.resolved, "Market is not resolved yet"
        assert not self.dispute_active, "Market has an active dispute"

        user_key = f"{gl.message.sender_address}_{self.winning_outcome}"
        user_bet = self.bets.get(user_key, u256(0))
        
        assert user_bet > 0, "No winning bets found for this address"

        winning_pool = self.outcomes.get(self.winning_outcome, u256(1))
        payout = (user_bet * self.total_pool) // winning_pool

        self.bets[user_key] = u256(0)
        gl.transfer(gl.message.sender_address, payout)
