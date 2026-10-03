# MeshCFO signed-ledger verification — notes

Model: `Ledger.lean` (Lean 4.34.1, core library only, no
`sorry`/`admit`/custom axioms; `#print axioms` on the headline theorems
shows at most `propext`, `Classical.choice`, `Quot.sound`).
Compile: `~/.elan/bin/lean Ledger.lean` (exit 0; only deprecation/lint
warnings).

Abstractions: record bodies and signatures are `Nat`; the HMAC is an
arbitrary function `mac : Nat → Nat → Nat` (body ↦ prev_sig ↦ sig) and
SHA-256 an arbitrary `sha : Nat → Nat`. Every Part A theorem holds for
*all* `mac`, so the chain results are structural — no cryptographic
assumption is smuggled in. The genesis prev_sig `""` is modelled as `0`.
JSON parsing is modelled as succeeding (the well-formed-file case);
parse-failure behaviour is covered in the risk notes, not the model.

---

## Part A — `AuditLedger` (`src/cme/audit/ledger.py`)

Scheme as implemented: `sig = HMAC-SHA256(key, canonical_json(record) +
prev_sig)` where `canonical_json` covers every field except `sig`
(ll. 54–64), i.e. the stored `prev_sig` is signed twice over (inside the
canonical form and appended to the message — harmless redundancy).
`append` reads the current tail sig and signs the new line onto it
(ll. 90–123, signing block ll. 118–122). `verify` walks the file
checking link then content per line and returns `(intact,
first_tampered_index)` (ll. 156–185).

| Model item | Source | Meaning |
|---|---|---|
| `Entry`, `signEntry` | ledger.py:90–123 | one stored line; the append signing step |
| `lastSigFrom`, `lastSig` | ledger.py:187–200 | `_last_sig_unlocked`: *stored* tail sig, genesis if file missing/empty |
| `appendEntry` | ledger.py:118–122 + 202–206 | append one signed line at the end |
| `ChainedFrom`, `Chained` | ledger.py:156–185 (the checks) | every `prev_sig` = previous line's `sig`; every `sig` recomputes |
| `verifyFrom`, `verify` | ledger.py:170–184 | first bad index, or `none` |
| `verifyFrom_none_iff`, `verify_none_iff` | — | **soundness + completeness**: `verify` accepts ⟺ the chain invariant holds. No accepted line violates a link or a signature; no conforming ledger is rejected |
| `verifyFrom_some_first_bad` | ledger.py:160–162 (docstring) | on failure at `i`: the first `i` lines are chained, line `i` exists and fails its link/sig check against the prefix's tail sig — the reported index really is the *earliest* bad line |
| `appendEntry_prefix` | ledger.py:202–206 | append is a pure extension: old ledger is a prefix of the new |
| `appendEntry_length` | — | append grows the file by exactly one line |
| `chainedFrom_append_singleton` | — | one-step chain characterisation over `++ [e]` |
| `appendEntry_chained` | — | the honest write path preserves the invariant `verify` checks |
| `chainedFrom_take` | — | any prefix of a chained ledger is chained |
| `verify_take_none` | vs ledger.py:19–22 | **counterexample**: tail truncation leaves `verify` reporting intact (see R1) |
| `buildFrom`, `buildFrom_chained`, `build_verifies` | — | any body list can be built into a verifying chain (see R2) |

## Part B — `DecisionLedger` (`src/cme/hardening.py:253–300`)

The CHP decision ledger is a second, weaker ledger: `append` just
writes a JSON line (ll. 260–265, no signature, no chain); reads
(`list`/`get`) re-validate per entry in `_checked` (ll. 286–300):
`envelope_valid` via the external `chp` package's
`validate_payload_envelope` — structure-only by the module's own
docstring (ll. 24–31) — and `integrity_valid` as an **unkeyed**
SHA-256 of the stored body compared to the stored digest (l. 298).

| Model item | Source | Meaning |
|---|---|---|
| `DEntry`, `integrityValid` | hardening.py:286–300 | the read-path integrity flag |
| `integrityValid_iff` | — | the flag is exactly "digest = sha(body)", by construction |
| `forge_entry_passes` | — | **counterexample**: for every body, an entry over it passes — store the publicly computable digest (see R3) |
| `allValid`, `allValid_of_subset`, `allValid_take`, `allValid_perm` | hardening.py:274–284 | acceptance is *pointwise* per entry: deletion/truncation/reordering of an accepted file stays accepted (see R4) |
| `dget`, `dget_shadow` | hardening.py:278–284 | `get` returns the *newest* entry for a decision id; an appended entry shadows all earlier ones |
| `shadow_forge` | — | **counterexample**: appended forged entry = what `get` returns for the victim id, and it passes integrity (see R3+R4) |

## Part C — the CHP decision gate

Gate chain in `CFOOperatingSystem.run`
(`src/cme/cfo_os/orchestrator.py:161–245`): R0 via `_chp_guarded`
(l. 166) → mesh orchestration (l. 176) → `harden` via `_chp_guarded`
(ll. 188–198) → `enforce_lock_policy` via `_chp_guarded` (ll. 201–203)
→ `gate.lock` if a confirmer is named (ll. 204–205) → audit
`cfo_artifact` append (l. 215) → `gate.record` into the decision
ledger (l. 227). Refusals inside `_chp_guarded` are themselves
appended to the audit ledger as `chp_rejected` and re-raised
(ll. 264–281).

| Model item | Source | Meaning |
|---|---|---|
| `Status`, `VRes`, `applyTPV` | src/cme/chp/validators.py:8–16 | CONFIRM → LOCKED, else → EXPLORING |
| `applyTPV_confirm_any`, `applyTPV_no_precondition` | validators.py:8–16 | the transition checks **no current status**: any status + CONFIRM = LOCKED (see R6) |
| `SessionFacts`, `recordSealed` | hardening.py:324–339, 441–448, 489–508 + orchestrator wiring | conjunction of all guards before the durable writes |
| `recordSealed_guards` | — | **gate property**: a sealed decision record ⟹ R0 passed ∧ no parity mismatch ∧ foundation PASS ∧ confirmer named whenever the human lock is required |
| `auditTrace` | cfo_os/orchestrator.py:161–245; cme/orchestrator.py:174–206 | the run's audit-ledger writes in order |
| `refused_run_still_writes_recommendations` | — | **counterexample**: a run refused by the lock policy still wrote its `recommendation` entries (see R5) |

Note on `lock`: `ChpDecisionGate.lock` (hardening.py:510–522) imports
`apply_third_party_validation` from the external
`consensus-hardening-protocol==0.1.1` package (pyproject.toml:25), not
from the vendored `src/cme/chp/validators.py` modelled here; the
vendored copy is what the repo itself contains, and the external one
was not inspected. The gate also *assigns* `chp_case.status =
SessionStatus.PROVISIONAL_LOCK` outright (hardening.py:485) rather
than transitioning it.

---

## Discrepancy / risk notes

**R1 — Tail truncation of the audit ledger is undetectable.**
The module docstring (ledger.py:19–22) claims "deletion, reordering,
or in-place edits break the chain". `verify_take_none` proves any
prefix of a chained ledger verifies intact: deleting the *last* k
lines is invisible, because the ledger carries no length, head, or
tail commitment. Interior deletion is caught only because the next
line's `prev_sig` then mismatches — and even that relies on the two
neighbouring stored sigs differing (true for HMAC except with
negligible probability, but it is a probabilistic fact, not a
structural one; the repo test at tests/test_audit_ledger.py:91–104
covers one interior case). Reordering two lines is likewise caught
only via the same sig-mismatch mechanism.

**R2 — Default deployments sign with a published key.**
`resolve_key` (ledger.py:49–53) falls back to `TEST_DEFAULT_KEY =
"meshcfo-test-audit-key"` (l. 43, printed in the public repo)
whenever `AUDIT_LEDGER_KEY` is unset. `build_verifies` shows a
verifying chain can be manufactured over *any* fabricated history
given the key — so in a default-configured deployment `verify`
certifies nothing about provenance, only internal consistency.
This is acknowledged in the docstring ("In production set
AUDIT_LEDGER_KEY") but nothing warns or refuses at runtime when the
default is in force.

**R3 — Decision-ledger "integrity" is unkeyed and forgeable.**
`_checked` (hardening.py:298) recomputes plain SHA-256 over the
stored body. `forge_entry_passes` / `shadow_forge`: anyone with
file-write access can rewrite a record's body, recompute the digest,
and the record reads `integrity_valid: true`; appending such a record
for an existing `decision_id` also makes it the record `get`
returns (newest shadows, hardening.py:278–284). The repo's tamper
test (tests/test_chp_hardening.py:159–195) only edits the body
*without* recomputing the digest — the one case the check catches.
Additionally, `_checked` never cross-checks the envelope against the
body: the two flags are computed independently, so a stale genuine
envelope can accompany a forged body. Mitigation would be an HMAC
(like Part A) or an asymmetric signature, plus hash-chaining.

**R4 — Decision ledger has no chain at all.**
Acceptance is pointwise (`allValid_of_subset`, `allValid_take`,
`allValid_perm`): entries can be deleted, truncated, or reordered
without any read-path signal, and `list(limit=100)` (l. 274) only
ever checks the newest 100 anyway. `DecisionLedger.append`
(ll. 260–265) also performs no validation itself — `record` /
`record_lock` (hardening.py:524–606) build well-formed entries, but
the append API accepts arbitrary dicts.

**R5 — The human-lock gate does not guard all audit-ledger writes.**
The comment at cfo_os/orchestrator.py:200 says "refusals land before
anything durable is written", and the repo test
(tests/test_chp_hardening.py:63–79) asserts a refused session leaves
the *decision ledger* empty. Both are true of the decision record
and the `cfo_artifact` audit entry (`recordSealed_guards`). But
`run` calls `self._mesh.orchestrate(...)` at l. 176 — *before*
`harden` (l. 188) and `enforce_lock_policy` (l. 201) — and
`EnterpriseOrchestrator` appends every agent turn
(`_audit_turn`, cme/orchestrator.py:174–191) and the board narrative
(`_audit_workflow`, ll. 192–206) to the *same* audit ledger during
orchestration, with no gate at all.
`refused_run_still_writes_recommendations` formalises that a
lock-refused session's recommendation entries are already durable
(and, by `appendEntry_prefix`, permanent). Separately, the plain
`EnterpriseOrchestrator` path (cme/orchestrator.py) has no gate
whatsoever: any agent recommendation is signed as-is. The gate is a
property of one call path in `CFOOperatingSystem.run`, not of the
ledger or of `AuditLedger.append` (a public, unguarded method).

**R6 — Third-party validation has no state precondition.**
`apply_third_party_validation` (validators.py:8–16) sets LOCKED on
any CONFIRM regardless of current status
(`applyTPV_no_precondition`), appends to `third_party_log`
unconditionally, and does not check that the validator differs from
the case owner/proposer. The PROVISIONAL_LOCK precondition is only a
control-flow convention of the gate (`harden` assigns the status at
hardening.py:485; `run` orders the calls). Also on REJECT the case
returns to EXPLORING and `locked_decisions` is *not* rolled back if
the same item was locked earlier — repeated validations accumulate.
(See the note in Part C: the gate imports this function from the
external CHP package; the vendored copy modelled here may differ
from the shipped 0.1.1 behaviour.)

**R7 — Audit-ledger tail handling on corrupt input.**
`_last_sig_unlocked` (ledger.py:187–200): if the last line is
unparseable JSON, the next append silently chains onto the *genesis*
prev_sig (l. 200), forking the chain (verify will report the corrupt
line first — `verify` maps read errors to `(False, 0)`,
ll. 165–168 — but the append itself succeeds and buries the fork
deeper). If the last line parses but lacks `sig`, prev becomes `""`
(l. 198) and the new line breaks the chain at its own index.
Relatedly, `verify` only catches `JSONDecodeError`/`OSError` around
`read_records`; a line that parses to a non-object (e.g. `42`) makes
`rec.get` raise `AttributeError` inside the loop, crashing `verify`
instead of returning `(False, i)`. Not modelled (model assumes
well-formed lines).

**R8 — `append_record` silently drops fields.**
`append_record` (ledger.py:125–138) rebuilds the record from the
named fields only; any extra keys in the caller's dict (including a
caller-supplied `prev_sig`/`sig`) are discarded without notice.
Callers expecting to import pre-signed records will silently get
freshly signed, content-reduced ones instead.

**R9 — Single-process assumption.**
The lock in `AuditLedger.append` (ledger.py:118) is a per-object
`threading.Lock`. Two `AuditLedger` instances (or processes) on the
same path can read the same tail sig concurrently and append sibling
lines with identical `prev_sig`, forking the chain; `verify` then
fails at the second sibling. The model (like the code's docstring)
assumes one serialised writer. `DecisionLedger` has the same shape
of issue for its append, minus the chain to break.

**Positive results worth stating.** Within its model, `verify` is
exactly right: sound, complete, and its first-bad index is the
earliest violating line (`verifyFrom_none_iff`,
`verifyFrom_some_first_bad`); the honest append path always
preserves the invariant (`appendEntry_chained`); and the CHP gate
provably keeps unconfirmed/below-floor/parity-mismatched sessions
out of the decision ledger (`recordSealed_guards`).
