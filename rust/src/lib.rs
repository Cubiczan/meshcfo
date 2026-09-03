use chrono::Utc;
use hmac::{Hmac, Mac};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sha2::Sha256;
use std::collections::HashMap;
use std::collections::BTreeMap;

type HmacSha256 = Hmac<Sha256>;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum Verdict {
    Pass,
    Fail,
    Halt,
    Reframe,
    Iterate,
    Converged,
    PhaseGateFail,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum SessionStatus {
    Exploring,
    Provisional,
    ProvisionalLock,
    Locked,
    Converged,
    Unresolved,
    ReframeRequired,
    Halt,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum ModelTier {
    Small,
    Mid,
    High,
    Frontier,
    Unknown,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GateEvaluation {
    pub results: HashMap<String, String>,
    pub verdict: Verdict,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModelParityCheck {
    pub origin: String,
    pub partner: String,
    pub delta: String,
    pub advisory: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FoundationDisclosure {
    pub weakest_assumptions: Vec<String>,
    pub invalidation_conditions: Vec<String>,
    pub key_vulnerability: String,
}

impl FoundationDisclosure {
    pub fn validate(&self) -> Vec<String> {
        let mut errors = Vec::new();
        if self.weakest_assumptions.is_empty() || self.weakest_assumptions.len() > 3 {
            errors.push("weakest_assumptions must include 1-3 items".to_string());
        }
        if self.invalidation_conditions.is_empty() || self.invalidation_conditions.len() > 2 {
            errors.push("invalidation_conditions must include 1-2 items".to_string());
        }
        if self.key_vulnerability.is_empty() {
            errors.push("key_vulnerability is required".to_string());
        }
        errors
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FoundationAttack {
    pub assumption_attacks: Vec<String>,
    pub invalidation_exploitation: Vec<String>,
    pub vulnerability_strike: String,
    pub foundation_score: i32,
    pub attack_summary: String,
}

impl FoundationAttack {
    pub fn validate(&self) -> Vec<String> {
        let mut errors = Vec::new();
        if self.assumption_attacks.is_empty() {
            errors.push("assumption_attacks is required".to_string());
        }
        if self.vulnerability_strike.is_empty() {
            errors.push("vulnerability_strike is required".to_string());
        }
        if !(0..=100).contains(&self.foundation_score) {
            errors.push("foundation_score must be between 0 and 100".to_string());
        }
        errors
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Dossier {
    pub core_problem: String,
    pub goal_state: Vec<String>,
    pub current_state: Vec<String>,
    pub prior_decisions: Vec<String>,
    pub constraints: Vec<String>,
    pub unknowns: Vec<String>,
    pub scope: Vec<String>,
    pub origin_direction: Vec<String>,
    pub prior_round_summary: Vec<String>,
    pub unknowns_carried: Vec<String>,
    pub foundation_score: Option<i32>,
    pub structural_vulnerabilities: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DecisionCase {
    pub decision_id: String,
    pub title: String,
    pub domain: String,
    pub created_at: String,
    pub owner: String,
    pub high_stakes: bool,
    pub origin_system: String,
    pub origin_model: String,
    pub partner_system: String,
    pub partner_model: String,
    pub dossier: Dossier,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CapitalAllocationInput {
    pub title: String,
    pub company: String,
    pub proposal_summary: String,
    pub investment_amount_usd: f64,
    pub expected_payback_months: i32,
    pub minimum_runway_months: i32,
    pub current_runway_months: i32,
    pub strategic_priorities: Vec<String>,
    pub key_risks: Vec<String>,
    pub expected_upside: Vec<String>,
    pub owner: String,
    pub origin_system: String,
    pub origin_model: String,
    pub partner_system: String,
    pub partner_model: String,
    pub decision_id: Option<String>,
    pub high_stakes: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FoundationScoreInput {
    pub kind: String,
    pub current_runway_months: i32,
    pub minimum_runway_months: i32,
    pub growth_assumption_pct: Option<f64>,
    pub churn_assumption_pct: Option<f64>,
    pub expected_payback_months: Option<i32>,
    pub key_risks_count: Option<usize>,
    pub investment_amount_usd: Option<f64>,
    pub revenue_drivers_count: Option<usize>,
    pub options_count: Option<usize>,
    pub open_questions_count: Option<usize>,
    pub strategic_risks_count: Option<usize>,
    pub recommended_option_index: Option<i32>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DepartmentMetricsInput {
    pub department_type: String,
    pub status: String,
    pub revenue_signals: Value,
    pub output: Value,
    pub approval_count: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ContextEntryInput {
    pub id: String,
    pub content: String,
    pub source_agent: String,
    pub timestamp: f64,
    pub importance: f64,
    pub access_count: usize,
    pub tags: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ContextSelectInput {
    pub query: String,
    pub k: usize,
    pub agent: Option<String>,
    pub short_term_ttl: f64,
    pub now: f64,
    pub entries: Vec<ContextEntryInput>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuditVerifyInput {
    pub key: String,
    pub records: Vec<Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "command", content = "input", rename_all = "snake_case")]
pub enum MeshRequest {
    EvaluateR0Gate {
        solvable: bool,
        scoped: bool,
        valid: bool,
        worth_it: bool,
    },
    EvaluatePhaseGate {
        round_number: i32,
        phase_one_status: SessionStatus,
    },
    FoundationVerdict { foundation_score: i32 },
    ValidateFoundationPair {
        disclosure: FoundationDisclosure,
        attack: FoundationAttack,
    },
    ComputeSig {
        key: String,
        record: Value,
        prev_sig: String,
    },
    ScoreFoundation { input: FoundationScoreInput },
    AssessModelParity {
        origin_model: String,
        partner_model: String,
    },
    BuildCapitalAllocationCase { payload: CapitalAllocationInput },
    DepartmentMetrics { input: DepartmentMetricsInput },
    SelectContext { input: ContextSelectInput },
    VerifyAuditChain { input: AuditVerifyInput },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "kind", content = "value", rename_all = "snake_case")]
pub enum MeshResponse {
    GateEvaluation(GateEvaluation),
    Verdict(Verdict),
    Errors(Vec<String>),
    ModelParityCheck(ModelParityCheck),
    Signature {
        sig: String,
    },
    FoundationScore {
        score: i32,
    },
    DepartmentMetrics {
        health_score: f64,
        revenue_signals: Value,
    },
    ContextSelection {
        selected_ids: Vec<String>,
    },
    AuditVerification {
        intact: bool,
        first_bad: Option<usize>,
    },
    CapitalAllocationCase {
        case: DecisionCase,
        disclosure: FoundationDisclosure,
        attack: FoundationAttack,
    },
}

pub fn handle_request(request: MeshRequest) -> MeshResponse {
    match request {
        MeshRequest::EvaluateR0Gate {
            solvable,
            scoped,
            valid,
            worth_it,
        } => MeshResponse::GateEvaluation(evaluate_r0_gate(solvable, scoped, valid, worth_it)),
        MeshRequest::EvaluatePhaseGate {
            round_number,
            phase_one_status,
        } => MeshResponse::Verdict(evaluate_phase_gate(round_number, phase_one_status)),
        MeshRequest::FoundationVerdict { foundation_score } => {
            MeshResponse::Verdict(foundation_verdict(foundation_score))
        }
        MeshRequest::ValidateFoundationPair { disclosure, attack } => {
            MeshResponse::Errors(validate_foundation_pair(&disclosure, &attack))
        }
        MeshRequest::ComputeSig { key, record, prev_sig } => {
            MeshResponse::Signature { sig: compute_sig(&key, &record, &prev_sig) }
        }
        MeshRequest::ScoreFoundation { input } => {
            MeshResponse::FoundationScore { score: score_foundation(&input) }
        }
        MeshRequest::AssessModelParity {
            origin_model,
            partner_model,
        } => MeshResponse::ModelParityCheck(assess_model_parity(&origin_model, &partner_model)),
        MeshRequest::BuildCapitalAllocationCase { payload } => {
            let (case, disclosure, attack) = build_capital_allocation_case(payload);
            MeshResponse::CapitalAllocationCase {
                case,
                disclosure,
                attack,
            }
        }
        MeshRequest::DepartmentMetrics { input } => {
            let metrics = department_metrics(input);
            MeshResponse::DepartmentMetrics {
                health_score: metrics.0,
                revenue_signals: metrics.1,
            }
        }
        MeshRequest::SelectContext { input } => {
            MeshResponse::ContextSelection {
                selected_ids: select_context(input),
            }
        }
        MeshRequest::VerifyAuditChain { input } => {
            let (intact, first_bad) = verify_audit_chain(input);
            MeshResponse::AuditVerification { intact, first_bad }
        }
    }
}

pub fn evaluate_r0_gate(solvable: bool, scoped: bool, valid: bool, worth_it: bool) -> GateEvaluation {
    let results = HashMap::from([
        ("Solvable".to_string(), if solvable { "PASS" } else { "FATAL" }.to_string()),
        ("Scoped".to_string(), if scoped { "PASS" } else { "FATAL" }.to_string()),
        ("Valid".to_string(), if valid { "PASS" } else { "FATAL" }.to_string()),
        ("Worth_it".to_string(), if worth_it { "PASS" } else { "FATAL" }.to_string()),
    ]);
    let verdict = if results.values().all(|v| v == "PASS") {
        Verdict::Pass
    } else {
        Verdict::Halt
    };
    GateEvaluation { results, verdict }
}

pub fn evaluate_phase_gate(round_number: i32, phase_one_status: SessionStatus) -> Verdict {
    if round_number <= 2 {
        return Verdict::Pass;
    }
    if matches!(
        phase_one_status,
        SessionStatus::ProvisionalLock | SessionStatus::Locked | SessionStatus::Converged
    ) {
        Verdict::Pass
    } else {
        Verdict::PhaseGateFail
    }
}

pub fn foundation_verdict(foundation_score: i32) -> Verdict {
    if foundation_score >= 70 {
        Verdict::Pass
    } else {
        Verdict::Reframe
    }
}

pub fn validate_foundation_pair(
    disclosure: &FoundationDisclosure,
    attack: &FoundationAttack,
) -> Vec<String> {
    let mut errors = disclosure.validate();
    errors.extend(attack.validate());
    if !disclosure.weakest_assumptions.is_empty() && !attack.assumption_attacks.is_empty() {
        if attack.assumption_attacks.len() < usize::min(3, disclosure.weakest_assumptions.len()) {
            errors.push("attack must address each disclosed weak assumption".to_string());
        }
    }
    errors
}

fn infer_tier(model_name: &str) -> ModelTier {
    let name = model_name.to_lowercase();
    if ["opus", "max", "frontier"].iter().any(|token| name.contains(token)) {
        return ModelTier::Frontier;
    }
    if ["gpt-5", "claude 4", "claude-4", "high"].iter().any(|token| name.contains(token)) {
        return ModelTier::High;
    }
    if ["sonnet", "4o", "mid", "gpt-4"].iter().any(|token| name.contains(token)) {
        return ModelTier::Mid;
    }
    if ["mini", "small", "haiku"].iter().any(|token| name.contains(token)) {
        return ModelTier::Small;
    }
    ModelTier::Unknown
}

pub fn assess_model_parity(origin_model: &str, partner_model: &str) -> ModelParityCheck {
    let origin_tier = infer_tier(origin_model);
    let partner_tier = infer_tier(partner_model);
    let (delta, advisory) = if origin_tier == ModelTier::Unknown || partner_tier == ModelTier::Unknown {
        (
            "MINOR".to_string(),
            Some("One or both model tiers are unknown. Treat parity as advisory only.".to_string()),
        )
    } else {
        let order = [ModelTier::Small, ModelTier::Mid, ModelTier::High, ModelTier::Frontier];
        let origin_idx = order.iter().position(|tier| *tier == origin_tier).unwrap();
        let partner_idx = order.iter().position(|tier| *tier == partner_tier).unwrap();
        let gap = origin_idx.abs_diff(partner_idx);
        match gap {
            0 => ("NONE".to_string(), None),
            1 => (
                "MINOR".to_string(),
                Some("Slight analytical weight difference. Monitor for dominance bias.".to_string()),
            ),
            _ => ("SIGNIFICANT".to_string(), None),
        }
    };
    ModelParityCheck {
        origin: origin_model.to_string(),
        partner: partner_model.to_string(),
        delta,
        advisory,
    }
}

pub fn build_capital_allocation_case(
    payload: CapitalAllocationInput,
) -> (DecisionCase, FoundationDisclosure, FoundationAttack) {
    let decision_id = payload
        .decision_id
        .clone()
        .unwrap_or_else(|| decision_id(&payload.title));
    let dossier = Dossier {
        core_problem: payload.proposal_summary.clone(),
        goal_state: vec![
            format!("Payback <= {} months", payload.expected_payback_months),
            format!("Runway stays >= {} months", payload.minimum_runway_months),
        ]
        .into_iter()
        .chain(payload.expected_upside.iter().take(2).cloned())
        .collect(),
        current_state: vec![
            format!("Current runway is {} months", payload.current_runway_months),
            format!("Proposed investment is ${:.0}", payload.investment_amount_usd),
        ],
        prior_decisions: vec![],
        constraints: vec![
            format!("Do not reduce runway below {} months", payload.minimum_runway_months),
            "Require a single accountable owner".to_string(),
        ],
        unknowns: vec![
            "Execution timing confidence".to_string(),
            "Benefit realization timing".to_string(),
        ],
        scope: vec![
            "Foundation attack".to_string(),
            "Spec lock".to_string(),
            "Implementation QA".to_string(),
        ],
        origin_direction: vec![
            "Prefer milestone-gated release of capital".to_string(),
            "Require explicit flip criteria before full commitment".to_string(),
        ],
        prior_round_summary: vec![],
        unknowns_carried: vec![],
        foundation_score: None,
        structural_vulnerabilities: vec![
            "Revenue timing may lag implementation spend".to_string(),
            "Strategic upside may be overstated relative to execution capacity".to_string(),
        ],
    };
    let mut case = DecisionCase {
        decision_id,
        title: payload.title.clone(),
        domain: "capital_allocation".to_string(),
        created_at: Utc::now().to_rfc3339(),
        owner: payload.owner.clone(),
        high_stakes: payload.high_stakes,
        origin_system: payload.origin_system.clone(),
        origin_model: payload.origin_model.clone(),
        partner_system: payload.partner_system.clone(),
        partner_model: payload.partner_model.clone(),
        dossier,
    };
    let disclosure = FoundationDisclosure {
        weakest_assumptions: vec![
            format!(
                "Expected payback in {} months is achievable",
                payload.expected_payback_months
            ),
            "Strategic upside is material enough to justify the spend".to_string(),
            "Organization can absorb implementation complexity without harming core execution".to_string(),
        ],
        invalidation_conditions: vec![
            format!(
                "Runway drops below {} months under downside conditions",
                payload.minimum_runway_months
            ),
            "Adoption or value realization slips by more than one planning cycle".to_string(),
        ],
        key_vulnerability: "The case depends on timing assumptions that may look disciplined in theory but fail in operating reality.".to_string(),
    };
    let score = foundation_score(&payload);
    let attack = FoundationAttack {
        assumption_attacks: vec![
            "Payback may be based on optimistic adoption rather than contracted demand.".to_string(),
            "Strategic upside may be real but not near-term enough for this capital window.".to_string(),
            "Execution load may crowd out current priorities and erode realized return.".to_string(),
        ],
        invalidation_exploitation: vec![
            "If spend lands before benefits, the runway floor can be breached quickly.".to_string(),
            "If adoption slips one planning cycle, the economics may fall outside hurdle tolerance.".to_string(),
        ],
        vulnerability_strike: "The proposal is most exposed where timing, not direction, carries the business case.".to_string(),
        foundation_score: score,
        attack_summary: "The case is directionally credible but timing-sensitive. It can proceed only if capital release is gated and downside triggers are explicit.".to_string(),
    };
    case.dossier.foundation_score = Some(score);
    (case, disclosure, attack)
}

fn decision_id(title: &str) -> String {
    let seed: String = title
        .chars()
        .map(|ch| if ch.is_ascii_alphanumeric() { ch.to_ascii_lowercase() } else { '-' })
        .collect();
    let trimmed = seed.trim_matches('-');
    format!("cap-{}", &trimmed[..trimmed.len().min(32)])
}

fn foundation_score(payload: &CapitalAllocationInput) -> i32 {
    let mut score = 78;
    if payload.current_runway_months < payload.minimum_runway_months + 3 {
        score -= 10;
    }
    if payload.expected_payback_months > 18 {
        score -= 8;
    }
    if payload.key_risks.len() >= 4 {
        score -= 4;
    }
    if payload.investment_amount_usd >= 5_000_000.0 {
        score -= 3;
    }
    score.clamp(55, 92)
}

fn score_foundation(input: &FoundationScoreInput) -> i32 {
    match input.kind.as_str() {
        "forecast" => {
            let mut score = 78;
            if input.current_runway_months < input.minimum_runway_months + 3 {
                score -= 10;
            }
            if input.growth_assumption_pct.unwrap_or(0.0) > 0.40 {
                score -= 6;
            }
            if input.churn_assumption_pct.unwrap_or(0.0) > 0.12 {
                score -= 5;
            }
            if input.revenue_drivers_count.unwrap_or(0) == 0 {
                score -= 6;
            }
            score.clamp(55, 92)
        }
        "investment" | "investment_case" => {
            let mut score = 78;
            if input.current_runway_months < input.minimum_runway_months + 3 {
                score -= 10;
            }
            if input.expected_payback_months.unwrap_or(18) > 18 {
                score -= 8;
            }
            if input.key_risks_count.unwrap_or(0) >= 4 {
                score -= 4;
            }
            if input.investment_amount_usd.unwrap_or(0.0) >= 5_000_000.0 {
                score -= 3;
            }
            score.clamp(55, 92)
        }
        "board" | "board_output" => {
            let mut score = 76;
            if input.options_count.unwrap_or(0) < 3 {
                score -= 8;
            }
            if input.open_questions_count.unwrap_or(0) == 0 {
                score -= 4;
            }
            if input.strategic_risks_count.unwrap_or(0) == 0 {
                score -= 4;
            }
            let options_count = input.options_count.unwrap_or(0);
            let recommended = input.recommended_option_index.unwrap_or(0);
            if recommended < 0 || recommended as usize >= options_count {
                score -= 6;
            }
            score.clamp(55, 92)
        }
        "capital_allocation" => {
            let mut score = 78;
            if input.current_runway_months < input.minimum_runway_months + 3 {
                score -= 10;
            }
            if input.expected_payback_months.unwrap_or(18) > 18 {
                score -= 8;
            }
            if input.key_risks_count.unwrap_or(0) >= 4 {
                score -= 4;
            }
            if input.investment_amount_usd.unwrap_or(0.0) >= 5_000_000.0 {
                score -= 3;
            }
            score.clamp(55, 92)
        }
        _ => 78,
    }
}

fn compute_sig(key: &str, record: &Value, prev_sig: &str) -> String {
    let canonical = canonicalize_record(record);
    let serialized = serde_json::to_string(&canonical).expect("canonical json serializes");
    let mut mac = HmacSha256::new_from_slice(key.as_bytes()).expect("hmac key is valid");
    mac.update(serialized.as_bytes());
    mac.update(prev_sig.as_bytes());
    hex::encode(mac.finalize().into_bytes())
}

fn canonicalize_record(value: &Value) -> Value {
    match value {
        Value::Object(map) => {
            let ordered: BTreeMap<String, Value> = map
                .iter()
                .filter(|(key, _)| key.as_str() != "sig")
                .map(|(key, value)| (key.clone(), canonicalize(value)))
                .collect();
            serde_json::to_value(ordered).expect("ordered map serializes")
        }
        _ => canonicalize(value),
    }
}

fn canonicalize(value: &Value) -> Value {
    match value {
        Value::Object(map) => {
            let ordered: BTreeMap<String, Value> = map
                .iter()
                .map(|(key, value)| (key.clone(), canonicalize(value)))
                .collect();
            serde_json::to_value(ordered).expect("ordered map serializes")
        }
        Value::Array(items) => Value::Array(items.iter().map(canonicalize).collect()),
        _ => value.clone(),
    }
}

fn department_metrics(input: DepartmentMetricsInput) -> (f64, Value) {
    let mut signals = input.revenue_signals.as_object().cloned().unwrap_or_default();
    match input.department_type.as_str() {
        "sales" => {
            let leads_count = input
                .output
                .get("leads")
                .and_then(Value::as_array)
                .map(|items| items.len())
                .unwrap_or(0) as u64;
            let lead_count = signals
                .get("lead_count")
                .and_then(Value::as_u64)
                .unwrap_or(0)
                + leads_count;
            let pipeline_value = signals
                .get("pipeline_value")
                .and_then(Value::as_u64)
                .unwrap_or(0)
                + leads_count * 5_000;
            signals.insert("lead_count".to_string(), Value::from(lead_count));
            signals.insert("pipeline_value".to_string(), Value::from(pipeline_value));
        }
        "content" => {
            let drafts_count = input
                .output
                .get("drafts")
                .and_then(Value::as_array)
                .map(|items| items.len())
                .unwrap_or(0) as u64;
            let content_outputs = signals
                .get("content_outputs")
                .and_then(Value::as_u64)
                .unwrap_or(0)
                + drafts_count;
            signals.insert("content_outputs".to_string(), Value::from(content_outputs));
        }
        _ => {}
    }

    let mut health_score: f64 = if input.status == "active" { 0.95 } else { 0.4 };
    if input.approval_count > 10 {
        health_score -= 0.1;
    }
    health_score = health_score.clamp(0.0, 1.0);
    (health_score, Value::Object(signals))
}

fn select_context(input: ContextSelectInput) -> Vec<String> {
    let q_tokens = token_counter(&input.query);
    let denom = (input.short_term_ttl * 2.0).max(1e-9);
    let mut scored: Vec<(f64, String, HashMap<String, usize>)> = Vec::new();
    let mut seen_counters: Vec<HashMap<String, usize>> = Vec::new();

    for entry in input.entries {
        let e_tokens = token_counter(&entry.content);
        if seen_counters.iter().any(|counter| cosine(&e_tokens, counter) > 0.85) {
            continue;
        }
        let semantic = cosine(&q_tokens, &e_tokens);
        let age = input.now - entry.timestamp;
        let recency = (-age / denom).exp();
        let freq = (entry.access_count as f64).ln_1p() / 5.0;
        let mut score = 0.5 * semantic + 0.2 * recency + 0.1 * freq + 0.2 * entry.importance;
        if input
            .agent
            .as_ref()
            .is_some_and(|agent| *agent == entry.source_agent)
        {
            score += 0.05;
        }
        scored.push((score, entry.id, e_tokens.clone()));
        seen_counters.push(e_tokens);
    }

    scored.sort_by(|a, b| b.0.partial_cmp(&a.0).unwrap_or(std::cmp::Ordering::Equal));
    scored.into_iter().take(input.k).map(|(_, id, _)| id).collect()
}

fn verify_audit_chain(input: AuditVerifyInput) -> (bool, Option<usize>) {
    let mut expected_prev = String::new();
    for (index, record) in input.records.iter().enumerate() {
        let stored_sig = record.get("sig").and_then(Value::as_str).unwrap_or("");
        let stored_prev = record.get("prev_sig").and_then(Value::as_str).unwrap_or("");
        if stored_prev != expected_prev {
            return (false, Some(index));
        }
        let recomputed = compute_sig(&input.key, record, stored_prev);
        if recomputed != stored_sig {
            return (false, Some(index));
        }
        expected_prev = stored_sig.to_string();
    }
    (true, None)
}

fn token_counter(text: &str) -> HashMap<String, usize> {
    let mut counter = HashMap::new();
    for token in text
        .split(|c: char| !c.is_ascii_alphanumeric() && c != '_')
        .filter(|token| {
            token.len() >= 2
                && token
                    .chars()
                    .next()
                    .is_some_and(|first| first.is_ascii_alphabetic())
        })
    {
        *counter.entry(token.to_lowercase()).or_insert(0) += 1;
    }
    counter
}

fn cosine(a: &HashMap<String, usize>, b: &HashMap<String, usize>) -> f64 {
    if a.is_empty() || b.is_empty() {
        return 0.0;
    }
    let dot: usize = a
        .iter()
        .map(|(token, count)| count * b.get(token).unwrap_or(&0))
        .sum();
    let na = a.values().map(|v| (*v as f64) * (*v as f64)).sum::<f64>().sqrt();
    let nb = b.values().map(|v| (*v as f64) * (*v as f64)).sum::<f64>().sqrt();
    if na == 0.0 || nb == 0.0 {
        0.0
    } else {
        dot as f64 / (na * nb)
    }
}
