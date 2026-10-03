/-
  MeshCFO signed-ledger core — Lean 4 model (core library only).

  Models, following the code (not the README):

  * Part A — `AuditLedger` in `src/cme/audit/ledger.py`: an HMAC-SHA256
    chained JSONL ledger.  A record's signature is
    `HMAC(key, canonical_json(record) + prev_sig)` where the canonical form
    covers every field except `sig` itself (so it covers the stored
    `prev_sig` as well).  Hash/HMAC and record bodies are abstracted:
    bodies and signatures are natural numbers, the MAC is an arbitrary
    function `mac : Nat → Nat → Nat` (body ↦ prev_sig ↦ sig), and the
    genesis prev_sig `""` is modelled as `0`.  All chain theorems hold for
    *every* `mac`, i.e. they are structural and need no cryptographic
    assumption; where a security reading needs one (key secrecy), the
    theorem statement says exactly what is and is not certified.

  * Part B — `DecisionLedger` in `src/cme/hardening.py` (ll. 258–300): an
    append-only JSONL whose read path re-checks an *unkeyed* SHA-256 of
    the entry body against the stored digest, plus a structure-only
    envelope validation.  There is no chaining and no key.

  * Part C — the CHP decision gate (`src/cme/hardening.py`
    `ChpDecisionGate`, wired in `src/cme/cfo_os/orchestrator.py run`):
    R0 gate → foundation/parity → human-lock policy → durable writes,
    and the third-party validation transition of
    `src/cme/chp/validators.py`.
-/

namespace MeshCFO

/-! ## Part A — the HMAC-chained audit ledger -/

/-- One stored ledger line: record body (all fields except `sig`,
    abstracted), the stored `prev_sig`, and the stored `sig`. -/
structure Entry where
  body : Nat
  prev : Nat
  sig  : Nat
deriving DecidableEq, Repr

/-- `GENESIS_PREV_SIG = ""` (ledger.py:46), modelled as `0`. -/
def genesis : Nat := 0

section AuditLedger

variable (mac : Nat → Nat → Nat)

/-- The signing step of `AuditLedger.append` (ledger.py:118–122): the new
    line stores `prev := <sig of current last line>` and
    `sig := HMAC(key, canonical(record) + prev)`. -/
def signEntry (b p : Nat) : Entry :=
  ⟨b, p, mac b p⟩

/-- The sig a reader of the file sees at the tail: the fold that returns
    the last entry's stored `sig`, or the starting value for the empty
    ledger.  This is `_last_sig_unlocked` (ledger.py:187–200) on a
    well-formed file: it reads the *stored* sig of the last line, never a
    recomputation. -/
def lastSigFrom : Nat → List Entry → Nat
  | p, [] => p
  | _, e :: es => lastSigFrom e.sig es

/-- Stored sig of the last line, genesis for the empty ledger. -/
def lastSig (L : List Entry) : Nat := lastSigFrom genesis L

/-- `AuditLedger.append` (ledger.py:90–123) as a state transition on the
    list of stored lines: exactly one freshly signed line is added at the
    end, chained onto the previously stored tail sig. -/
def appendEntry (L : List Entry) (b : Nat) : List Entry :=
  L ++ [signEntry mac b (lastSig L)]

/-- The chain invariant that `verify` checks, relative to an expected
    starting prev_sig: every line's stored `prev_sig` equals the previous
    line's stored `sig` (genesis for the first), and every line's stored
    `sig` recomputes as the MAC of its body and its stored prev_sig. -/
def ChainedFrom : Nat → List Entry → Prop
  | _, [] => True
  | p, e :: es =>
      e.prev = p ∧ e.sig = mac e.body e.prev ∧ ChainedFrom e.sig es

/-- The chain invariant for a whole ledger file. -/
def Chained (L : List Entry) : Prop := ChainedFrom mac genesis L

/-- `AuditLedger.verify` (ledger.py:156–185), modelled on a well-formed
    (parseable) file: walk with `expected_prev`; at each line check the
    link (`stored_prev = expected_prev`) and the content
    (`recomputed = stored_sig`); return the first bad index, or `none`.
    (The code folds both checks into one failure index per line, exactly
    as here; unparseable input is handled separately in the code with
    `(False, 0)` — see NOTES.) -/
def verifyFrom : Nat → List Entry → Option Nat
  | _, [] => none
  | p, e :: es =>
      if e.prev = p ∧ e.sig = mac e.body e.prev then
        (verifyFrom e.sig es).map (· + 1)
      else
        some 0

/-- `verify` on a whole ledger: `none` here is the code's `(True, None)`. -/
def verify (L : List Entry) : Option Nat := verifyFrom mac genesis L

/-- **Soundness and completeness of `verify`.**  `verify` reports the
    chain intact if and only if the stored lines satisfy the chain
    invariant — no line is accepted that violates a link or a signature,
    and no conforming ledger is rejected. -/
theorem verifyFrom_none_iff :
    ∀ (p : Nat) (L : List Entry),
      verifyFrom mac p L = none ↔ ChainedFrom mac p L := by
  intro p L
  induction L generalizing p with
  | nil => simp [verifyFrom, ChainedFrom]
  | cons e es ih =>
    by_cases h : e.prev = p ∧ e.sig = mac e.body e.prev
    · have h1 : verifyFrom mac p (e :: es)
          = (verifyFrom mac e.sig es).map (· + 1) := by
        simp only [verifyFrom, if_pos h]
      rw [h1]
      constructor
      · intro hv
        have hne : verifyFrom mac e.sig es = none :=
          Option.map_eq_none_iff.mp hv
        exact ⟨h.1, h.2, (ih e.sig).mp hne⟩
      · intro hc
        have hne : verifyFrom mac e.sig es = none := (ih e.sig).mpr hc.2.2
        simp [hne]
    · have h1 : verifyFrom mac p (e :: es) = some 0 := by
        simp only [verifyFrom, if_neg h]
      rw [h1]
      constructor
      · intro hv; cases hv
      · intro hc; exact absurd ⟨hc.1, hc.2.1⟩ h

/-- Whole-ledger form of `verifyFrom_none_iff`. -/
theorem verify_none_iff (L : List Entry) :
    verify mac L = none ↔ Chained mac L :=
  verifyFrom_none_iff mac genesis L

/-- **First-bad-index correctness.**  When `verify` fails at index `i`,
    the first `i` lines form a valid chain, and line `i` is present and
    fails its link or signature check against the running tail sig of
    that valid prefix — so the reported index is indeed the *earliest*
    tampered line, as the docstring promises. -/
theorem verifyFrom_some_first_bad :
    ∀ (p : Nat) (L : List Entry) (i : Nat),
      verifyFrom mac p L = some i →
      ChainedFrom mac p (L.take i) ∧
      ∃ e rest, L = L.take i ++ e :: rest ∧
        (e.prev ≠ lastSigFrom p (L.take i) ∨
         e.sig ≠ mac e.body e.prev) := by
  intro p L
  induction L generalizing p with
  | nil =>
    intro i h
    simp [verifyFrom] at h
  | cons e es ih =>
    intro i h
    by_cases hc : e.prev = p ∧ e.sig = mac e.body e.prev
    · have h1 : verifyFrom mac p (e :: es)
          = (verifyFrom mac e.sig es).map (· + 1) := by
        simp only [verifyFrom, if_pos hc]
      rw [h1] at h
      obtain ⟨j, hj, rfl⟩ := Option.map_eq_some_iff.mp h
      obtain ⟨hchain, e', rest, hdecomp, hfail⟩ := ih e.sig j hj
      have htake : (e :: es).take (j + 1) = e :: es.take j := rfl
      have hfull : e :: es = (e :: es.take j) ++ e' :: rest := by
        rw [List.cons_append, ← hdecomp]
      refine ⟨?_, e', rest, ?_, ?_⟩
      · rw [htake]
        exact ⟨hc.1, hc.2, hchain⟩
      · rw [htake]
        exact hfull
      · rw [htake]
        -- lastSigFrom p (e :: take) steps to lastSigFrom e.sig (take)
        show (e'.prev ≠ lastSigFrom e.sig (es.take j) ∨
              e'.sig ≠ mac e'.body e'.prev)
        exact hfail
    · have h1 : verifyFrom mac p (e :: es) = some 0 := by
        simp only [verifyFrom, if_neg hc]
      rw [h1] at h
      have hi : i = 0 := by cases h; rfl
      subst hi
      refine ⟨trivial, e, es, by simp, ?_⟩
      -- the goal's `lastSigFrom p (take 0 …)` is `p` by definition
      by_cases hp : e.prev = p
      · right
        intro hs
        exact hc ⟨hp, hs⟩
      · left
        exact hp

/-- Appending one line is a pure extension: the old ledger is a prefix
    of the new one (**append-only prefix preservation**). -/
theorem appendEntry_prefix (L : List Entry) (b : Nat) :
    L <+: appendEntry mac L b :=
  ⟨[signEntry mac b (lastSig L)], rfl⟩

/-- Appending grows the ledger by exactly one line. -/
theorem appendEntry_length (L : List Entry) (b : Nat) :
    (appendEntry mac L b).length = L.length + 1 := by
  simp [appendEntry]

/-- One-step form of the chain invariant over an append: a list extended
    by a single line is chained iff the original was chained and the new
    line links onto the running tail sig and is correctly signed. -/
theorem chainedFrom_append_singleton :
    ∀ (p : Nat) (L : List Entry) (e : Entry),
      ChainedFrom mac p (L ++ [e]) ↔
      ChainedFrom mac p L ∧ e.prev = lastSigFrom p L ∧
        e.sig = mac e.body e.prev := by
  intro p L
  induction L generalizing p with
  | nil =>
    intro e
    simp [ChainedFrom, lastSigFrom]
  | cons e₀ es ih =>
    intro e
    have step : ∀ (q : Nat),
        ChainedFrom mac q ((e₀ :: es) ++ [e])
          = ChainedFrom mac q (e₀ :: (es ++ [e])) := fun _ => rfl
    rw [step]
    constructor
    · intro h
      obtain ⟨h1, h2, h3⟩ := h
      obtain ⟨htail, hprev, hsig⟩ := (ih e₀.sig e).mp h3
      exact ⟨⟨h1, h2, htail⟩, hprev, hsig⟩
    · intro h
      obtain ⟨⟨h1, h2, htail⟩, hprev, hsig⟩ := h
      exact ⟨h1, h2, (ih e₀.sig e).mpr ⟨htail, hprev, hsig⟩⟩

/-- **Append preserves the chain.**  Appending to a chained ledger with
    `AuditLedger.append`'s signing step yields a chained ledger — the
    honest write path can never break the invariant `verify` checks. -/
theorem appendEntry_chained (L : List Entry) (b : Nat)
    (h : Chained mac L) : Chained mac (appendEntry mac L b) := by
  have h2 := (chainedFrom_append_singleton mac genesis L
    (signEntry mac b (lastSig L))).mpr ⟨h, rfl, rfl⟩
  exact h2

/-- Any prefix of a chained ledger is chained (relative form). -/
theorem chainedFrom_take :
    ∀ (n p : Nat) (L : List Entry),
      ChainedFrom mac p L → ChainedFrom mac p (L.take n) := by
  intro n
  induction n with
  | zero => intro p L _; trivial
  | succ n ih =>
    intro p L h
    cases L with
    | nil => trivial
    | cons e es =>
      have htake : (e :: es).take (n + 1) = e :: es.take n := rfl
      rw [htake]
      exact ⟨h.1, h.2.1, ih e.sig es h.2.2⟩

/-- **Counterexample — tail truncation is invisible to `verify`.**
    Deleting any suffix of a chained ledger leaves a ledger that
    `verify` reports intact.  This refutes the module docstring's claim
    (ledger.py:19–22) that "deletion … break[s] the chain": only
    *interior* deletion does (and even that only when the neighbouring
    stored sigs differ — see NOTES).  Nothing in the ledger records its
    own length or a head/tail commitment, so the last lines can be
    dropped without detection. -/
theorem verify_take_none (L : List Entry) (n : Nat)
    (h : Chained mac L) : verify mac (L.take n) = none :=
  (verify_none_iff mac _).mpr (chainedFrom_take mac n genesis L h)

/-- Building a ledger by repeated appends (the honest history) — and,
    read adversarially, the forgery construction: with knowledge of the
    key, *any* list of bodies can be turned into a verifying chain. -/
def buildFrom : List Entry → List Nat → List Entry
  | L, [] => L
  | L, b :: bs => buildFrom (appendEntry mac L b) bs

/-- Every ledger built by appends from a chained start is chained. -/
theorem buildFrom_chained :
    ∀ (L : List Entry) (bs : List Nat),
      Chained mac L → Chained mac (buildFrom mac L bs) := by
  intro L bs
  induction bs generalizing L with
  | nil => intro h; exact h
  | cons b bs ih =>
    intro h
    exact ih _ (appendEntry_chained mac L b h)

/-- **What `verify` actually certifies: internal consistency, not
    provenance.**  For every list of record bodies whatsoever there is a
    ledger over exactly those bodies that `verify` accepts.  Combined
    with `resolve_key` (ledger.py:49–51) falling back to the published
    `TEST_DEFAULT_KEY` whenever `AUDIT_LEDGER_KEY` is unset, anyone can
    manufacture a "valid" history in a default-configured deployment. -/
theorem build_verifies (bs : List Nat) :
    verify mac (buildFrom mac [] bs) = none :=
  (verify_none_iff mac _).mpr (buildFrom_chained mac [] bs trivial)

end AuditLedger

/-! ## Part B — the CHP decision ledger (`DecisionLedger`) -/

section DecisionLedger

/-- One decision-ledger entry, abstracted: the sealed `body`, the stored
    `body_sha256`, and the `decision_id`.  (The stored `envelope` is
    validated only for structure — hardening.py:28–31 — and is never
    cross-checked against the body by `_checked`, so it plays no role in
    the integrity predicate; see NOTES.) -/
structure DEntry where
  body : Nat
  digest : Nat
  decisionId : Nat
deriving DecidableEq, Repr

variable (sha : Nat → Nat)

/-- `DecisionLedger._checked`'s integrity flag (hardening.py:286–300):
    the stored digest recomputes from the stored body.  The digest is
    *unkeyed* SHA-256 over a public encoding — no secret is involved. -/
def integrityValid (e : DEntry) : Bool := sha e.body == e.digest

/-- The integrity flag is exactly "digest matches body" — sound and
    complete with respect to that predicate, by construction.  The
    question is what that predicate is worth; the next theorems answer
    it. -/
theorem integrityValid_iff (e : DEntry) :
    integrityValid sha e = true ↔ sha e.body = e.digest := by
  simp [integrityValid]

/-- **Counterexample — the digest check is forgeable by anyone.**
    For every body there is an entry, over that body, that passes the
    integrity check: just store the (publicly computable) digest of the
    forged body.  Unlike the Part A ledger, no key stands between an
    attacker with file-write access and a fully "valid" rewritten
    record — the check detects only edits that forget to recompute the
    digest (exactly the case the repo's own tamper test exercises,
    tests/test_chp_hardening.py:159–195). -/
theorem forge_entry_passes (b : Nat) :
    ∃ e : DEntry, e.body = b ∧ integrityValid sha e = true :=
  ⟨⟨b, sha b, 0⟩, rfl, by simp [integrityValid]⟩

/-- The read path's acceptance of a whole file is *pointwise*: a file is
    accepted iff each entry individually passes.  There is no chaining,
    no length commitment, and no cross-entry check in `_checked`. -/
def allValid (L : List DEntry) : Prop :=
  ∀ e ∈ L, integrityValid sha e = true

/-- Pointwise acceptance is monotone under taking subsets of entries:
    deleting, truncating, or reordering entries of an accepted file
    leaves an accepted file.  Contrast Part A, where interior deletion
    breaks the chain (but tail truncation, per `verify_take_none`, does
    not). -/
theorem allValid_of_subset {L L' : List DEntry}
    (hsub : ∀ e ∈ L', e ∈ L) (h : allValid sha L) : allValid sha L' :=
  fun e he => h e (hsub e he)

/-- Deleting entries cannot make an accepted decision ledger
    unacceptable — so deletion is undetectable by the read path. -/
theorem allValid_take (L : List DEntry) (n : Nat) (h : allValid sha L) :
    allValid sha (L.take n) :=
  allValid_of_subset sha (fun e he => List.mem_of_mem_take he) h

/-- Reordering entries is likewise undetectable. -/
theorem allValid_perm {L L' : List DEntry} (hp : List.Perm L L')
    (h : allValid sha L) : allValid sha L' :=
  allValid_of_subset sha (fun e he => hp.symm.subset he) h

/-- `DecisionLedger.get` (hardening.py:278–284): scan from the newest
    entry backwards, return the first whose `decision_id` matches —
    later entries shadow earlier ones (by design, for lock events). -/
def dget : List DEntry → Nat → Option DEntry
  | [], _ => none
  | e :: es, id =>
      match dget es id with
      | some x => some x
      | none => if e.decisionId = id then some e else none

/-- An appended entry for a decision id is exactly what `get` returns
    for that id, whatever history precedes it. -/
theorem dget_shadow :
    ∀ (L : List DEntry) (e : DEntry),
      dget (L ++ [e]) e.decisionId = some e := by
  intro L
  induction L with
  | nil =>
    intro e
    simp [dget]
  | cons x xs ih =>
    intro e
    have h1 : (x :: xs) ++ [e] = x :: (xs ++ [e]) := rfl
    rw [h1]
    have h2 : dget ((x :: (xs ++ [e])) ) e.decisionId
        = (match dget (xs ++ [e]) e.decisionId with
           | some y => some y
           | none => if x.decisionId = e.decisionId then some x else none) := rfl
    rw [h2, ih e]

/-- **Counterexample — shadowing + forgeability compose.**  For any
    existing decision history and any forged body, an appended entry
    exists that (a) is what `get` returns for the victim decision id and
    (b) passes the integrity check.  The decision ledger therefore
    provides no authenticity for the record a reader actually sees,
    only protection against digest-stale edits. -/
theorem shadow_forge (L : List DEntry) (b id : Nat) :
    ∃ e : DEntry, e.decisionId = id ∧ e.body = b ∧
      integrityValid sha e = true ∧ dget (L ++ [e]) id = some e := by
  refine ⟨⟨b, sha b, id⟩, rfl, rfl, by simp [integrityValid], ?_⟩
  have h := dget_shadow (L := L) (e := ⟨b, sha b, id⟩)
  exact h

end DecisionLedger

/-! ## Part C — the CHP decision gate -/

section Gate

/-- Session status in the vendored CHP protocol
    (`src/cme/chp/models.py`), restricted to the states the gate flow
    uses. -/
inductive Status where
  | exploring
  | provisionalLock
  | locked
deriving DecidableEq, Repr

/-- `ValidationResult` of a third-party validation. -/
inductive VRes where
  | confirm
  | reject
deriving DecidableEq, Repr

/-- `apply_third_party_validation` (src/cme/chp/validators.py:8–16):
    CONFIRM sets the case LOCKED, anything else sends it back to
    EXPLORING — with **no check of the current status**. -/
def applyTPV (s : Status) (r : VRes) : Status :=
  match r with
  | .confirm => .locked
  | .reject => .exploring

/-- The transition itself has no PROVISIONAL_LOCK precondition: from
    *any* status, a CONFIRM yields LOCKED.  The provisional-lock
    precondition exists only in the gate's control flow (`harden`
    assigns PROVISIONAL_LOCK at hardening.py:484 and `run` calls `lock`
    after the policy check).  Any other caller of the vendored function
    can lock a case that was never provisionally locked. -/
theorem applyTPV_confirm_any (s : Status) :
    applyTPV s .confirm = .locked := rfl

/-- Exhibition of the missing precondition. -/
theorem applyTPV_no_precondition :
    ∃ s : Status, s ≠ .provisionalLock ∧ applyTPV s .confirm = .locked :=
  ⟨.exploring, by simp, rfl⟩

/-- The abstract facts the gate chain in `CFOOperatingSystem.run`
    (src/cme/cfo_os/orchestrator.py) consults before the durable writes:
    R0 verdict, parity mismatch (from `harden`), foundation verdict,
    the human-lock setting, and whether a confirmer was named. -/
structure SessionFacts where
  r0Pass : Bool
  parityMismatch : Bool
  foundationPass : Bool
  requireLock : Bool
  confirmed : Bool
deriving Repr

/-- Whether the durable decision record (and the `cfo_artifact` audit
    entry) are written: the conjunction of every guard on the `run`
    path — `open_r0` refuses unless R0 passed (hardening.py:324–339);
    `harden` refuses a parity mismatch (hardening.py:441–448);
    `enforce_lock_policy` refuses a non-PASS foundation verdict and,
    when the human lock is required, an unnamed confirmer
    (hardening.py:489–508).  `record` and the artifact append sit after
    all three in `run`. -/
def recordSealed (f : SessionFacts) : Bool :=
  f.r0Pass && !f.parityMismatch && f.foundationPass &&
    (!f.requireLock || f.confirmed)

/-- **The gate property for durable decision records.**  If the decision
    record was sealed, then R0 passed, parity did not mismatch, the
    foundation verdict was PASS, and a confirmer was named whenever the
    human lock was required. -/
theorem recordSealed_guards (f : SessionFacts)
    (h : recordSealed f = true) :
    f.r0Pass = true ∧ f.parityMismatch = false ∧
    f.foundationPass = true ∧ (f.requireLock = true → f.confirmed = true) := by
  obtain ⟨r0, par, fou, req, conf⟩ := f
  cases r0 <;> cases par <;> cases fou <;> cases req <;> cases conf <;>
    simp_all [recordSealed]

/-- The audit-ledger writes of a `run`, in order, as event names
    (src/cme/cfo_os/orchestrator.py): an R0 refusal is itself audited
    (`_chp_guarded`, ll. 266–281); the mesh orchestration then writes one
    `recommendation` entry per agent turn plus a `board_narrative`
    (via `EnterpriseOrchestrator._audit_turn`/`_audit_workflow`,
    src/cme/orchestrator.py:172–206) **before** `harden` and
    `enforce_lock_policy` run; a later refusal appends `chp_rejected`;
    only a fully passing run appends `cfo_artifact`. -/
def auditTrace (f : SessionFacts) (turns : List Nat) : List String :=
  if f.r0Pass = false then ["chp_rejected"]
  else
    turns.map (fun _ => "recommendation") ++ ["board_narrative"] ++
      if f.parityMismatch then ["chp_rejected"]
      else if recordSealed f then ["cfo_artifact"] else ["chp_rejected"]

/-- **Counterexample — the lock gate does not guard all ledger writes.**
    A session that passes R0, runs the mesh, and is then *refused* by
    the foundation/lock policy (so `recordSealed` is false and nothing
    reaches the decision ledger — cf. the repo's own test at
    tests/test_chp_hardening.py:63–79, which asserts only the decision
    ledger side) has nevertheless already written its per-agent
    `recommendation` entries into the signed audit ledger, and by
    append-only prefix preservation (Part A) they stay there.  The
    comment at orchestrator.py:200 — "refusals land before anything
    durable is written" — is true of the decision record and the
    `cfo_artifact` entry, but false of the audit ledger's turn
    entries, which are written mid-flight, ungated. -/
theorem refused_run_still_writes_recommendations
    (f : SessionFacts) (t : Nat) (ts : List Nat)
    (hr0 : f.r0Pass = true) (hpar : f.parityMismatch = false)
    (href : recordSealed f = false) :
    "recommendation" ∈ auditTrace f (t :: ts) ∧
    "cfo_artifact" ∉ auditTrace f (t :: ts) := by
  have hif : ¬ (f.r0Pass = false) := by simp [hr0]
  unfold auditTrace
  rw [if_neg hif, hpar, href]
  simp

end Gate

end MeshCFO
