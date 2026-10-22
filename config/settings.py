"""Configuration for the LVDetector framework.

This module is the single source of truth for API credentials, the system
prompt, the seven step prompts, and runtime defaults.
"""

import textwrap
from dataclasses import dataclass
from pathlib import Path

# ============================================================
# LLM API Configuration
# ============================================================
API_KEY = "YOUR_API_KEY"
BASE_URL = "YOUR_API_BASE_URL"
MODEL = "YOUR_MODEL"

# ============================================================
# System Prompt
# ============================================================
SYSTEM_PROMPT = textwrap.dedent("""\
You are a  vulnerability analysis assistant. We will break down the complete vulnerability analysis process into independent steps (one API call at a time).
Each step, your response should **only** return the content required by this step (keep it concise and formatted), and avoid any additional explanations.
If the output from the previous step is provided as context, please use it in this step but do not repeat the original text from the previous step unless you need to reference specific item numbers.
You should remember triggering the vulnerability is related to the range of the key variable's value.Sometimes the vulnerbility statement itself is not enough to trigger the vulnerability.
""")

# ============================================================
# Step Prompts
# ============================================================
PROMPT_STEP1 = '''Step 1: Here is function code：\n{code}.Your task is to identify all potential **triggering statements** (sinks) and **defective logic**.
- Scope: Include both explicit dangerous API calls (e.g., `memcpy`, `strcpy`, `system`, `malloc`) and implicit logical defects (e.g., integer overflow/underflow, unsafe pointer arithmetic, unchecked array indexing).
- Constraint: Adopt an "over-approximation" strategy. List ALL candidate statements **even if** they appear to be guarded by security checks or have valid ranges. Do not determine safety at this stage; strictly focus on identifying the existence of risky operations.
Output Format: No. + Vulnerability Type + Vulnerable Statement.'''

PROMPT_STEP2 = "Step 2: Based on the triggering statements listed in Step 1, list the involved 'key variables' for each statement. Format: Vulnerable type + Triggering statement -> Key variable list (comma-separated). Only provide the corresponding relationship."

PROMPT_STEP3 = '''Step 3: For each key variable listed in Step 2, determine its 'source variable'.Perform a backward data-flow analysis on the step 2 Key Variable to determine its origin.Trace the variable's lifecycle back to its definition point.
- If the variable is derived from local constants, hardcoded literals, or strictly defined internal states, mark it as [Known Source].
- If the variable is derived from function arguments, external API returns (e.g., read, recv), or global states, mark it as [Unknown Source].
Output Format:
Key Variable: which variable you are analyzing
Trace: <Brief description of the data flow>
Verdict: [Known Source] or [Unknown Source] Only provide the corresponding relationship.'''

PROMPT_STEP4 = '''Step 4: Analyze the control flow path leading to the Target Sink.Verify if there are any valid guard statements (if/switch/assert) that explicitly constrain the Key Variable "{KEY_VARS}" against the specific risk of the sink (e.g., buffer size limit).
- Ignore irrelevant checks (e.g., null-pointer checks that do not prevent overflow).
- Only consider checks that validly limit the variable's range or value.
Output Format:
- guard statements：which statements are the guard statements
- Analysis: <Brief analysis of existing checks and their efficacy>
- Verdict: [Guarded] or [Unguarded]'''

PROMPT_STEP5 = '''Step 5: Combine the information from the previous steps.Synthesize the findings from Step 1 and Step 2 to determine the semantic state of the function.
Apply the following reasoning logic:
1. If Source is [Unknown Source] AND Sink is [Unguarded] -> Output [Latent Vulnerability] (Risk depends on caller).
2. If Source is [Known Source] (and value is unsafe) which we call bad source AND Sink is [Unguarded] -> Output [Manifest Vulnerability].
3. If Sink is [Guarded] -> Output [Safe].
Output Format:
- Reasoning: <Combine Step 1 and Step 2 evidence to justify the conclusion>
- Final State: [Latent Vulnerability] / [Manifest Vulnerability] / [Safe]'''

PROMPT_STEP6 = "Step 6: If the user has also provided a diff file, analyze the relationship between the diff and each triggering statement (fix/introduction/irrelevant). Output format: No. Triggering statement -> diff relationship (fix/introduction/irrelevant), and provide 1-2 sentence reasons in parentheses. If no diff is provided, reply: no diff."

PROMPT_STEP7 = '''Step 7: Summarize the function-level status. If any vulnerability label is latent vulnerability, the function is a latent vulnerability function (is_latent: true, category: "latent vulnerability function"); If all labels are safe, it is a safe function (is_latent: false, category: "safe function"); If any is manifest vulnerability, it is a manifest vulnerability function (is_latent: false, category: "manifest vulnerability function"). Please output strictly in JSON format, with no Markdown or code fences: {"is_latent": true/false, "category": "...", "rationale": "your analysis here"} '''

# ============================================================
# Runtime Defaults
# ============================================================
PACKAGE_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = PACKAGE_ROOT.parent


@dataclass(frozen=True)
class RuntimeConfig:
    """Execution defaults shared by the CLI and services."""

    processes: int = 8
    max_tokens: int = 8005
    temperature: float = 0.5
    json_output_path: str = str(PACKAGE_ROOT / "outputs" / "analysis_result.json")
    jsonl_output_path: str = "analysis_conversation0.jsonl"
    default_json_input: str = str(
        PACKAGE_ROOT / "testdata(RQ1)" / "diverseVul_0_groundtruth(385).json"
    )


RUNTIME = RuntimeConfig()
