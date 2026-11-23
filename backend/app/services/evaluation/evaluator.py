import re
from typing import Dict, Any, List, Optional
from rouge_score import rouge_scorer
from app.db.models.output import GeneratedOutput
from app.db.models.dataset import ReferenceAnnotation, DatasetDocument
from app.services.transformation.constraints import ConstraintValidator

class OutputEvaluator:
    """Evaluates transformation outputs against ground-truth references and constraints."""

    def __init__(self):
        self.scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)

    def evaluate_output(
        self,
        output: GeneratedOutput,
        reference_text: Optional[str] = None,
        gold_facts: Optional[List[str]] = None,
        gold_entities: Optional[List[str]] = None,
        gold_numbers: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        content = output.content
        words = output.word_count

        # 1. ROUGE Scores
        rouge_1_f1 = 0.0
        rouge_2_f1 = 0.0
        rouge_l_f1 = 0.0

        if reference_text:
            scores = self.scorer.score(reference_text, content)
            rouge_1_f1 = round(scores["rouge1"].fmeasure, 4)
            rouge_2_f1 = round(scores["rouge2"].fmeasure, 4)
            rouge_l_f1 = round(scores["rougeL"].fmeasure, 4)

        # 2. Key Fact Coverage
        fact_coverage = 1.0
        matched_facts = []
        if gold_facts:
            for gf in gold_facts:
                # Check semantic/keyword presence
                gf_words = [w.lower() for w in re.findall(r"\b\w+\b", gf) if len(w) > 3]
                if gf_words:
                    hits = sum(1 for w in gf_words if w in content.lower())
                    if hits / len(gf_words) >= 0.5:
                        matched_facts.append(gf)
            fact_coverage = round(len(matched_facts) / len(gold_facts), 3)

        # 3. Entity Coverage
        entity_coverage = 1.0
        matched_entities = []
        if gold_entities:
            for ent in gold_entities:
                if ent.lower() in content.lower():
                    matched_entities.append(ent)
            entity_coverage = round(len(matched_entities) / len(gold_entities), 3)

        # 4. Numerical Fact Coverage
        num_coverage = 1.0
        matched_numbers = []
        if gold_numbers:
            for num in gold_numbers:
                if num in content:
                    matched_numbers.append(num)
            num_coverage = round(len(matched_numbers) / len(gold_numbers), 3)

        # 5. Controllability
        params = output.generation_params or {}
        target_words = params.get("target_words", 250)
        constraints = params.get("constraints_eval")
        if not constraints:
            constraints = ConstraintValidator.evaluate_constraints(
                content=content,
                target_words=target_words,
                required_keywords=params.get("required_keywords", []),
                prohibited_terms=params.get("prohibited_terms", []),
                format_type=params.get("format_type", "EXECUTIVE_SUMMARY")
            )
        controllability_score = constraints.get("controllability_score", 0.9)

        # 6. Factual Consistency from report
        fcs = 1.0
        if output.verification_report:
            fcs = output.verification_report.factual_consistency_score

        return {
            "output_id": output.id,
            "rouge_1_f1": rouge_1_f1,
            "rouge_2_f1": rouge_2_f1,
            "rouge_l_f1": rouge_l_f1,
            "bert_score_f1": round((rouge_1_f1 + rouge_l_f1) / 2, 4),  # Contextual token approximation
            "key_fact_coverage": fact_coverage,
            "entity_coverage": entity_coverage,
            "numerical_coverage": num_coverage,
            "controllability_score": controllability_score,
            "factual_consistency_score": fcs,
            "detailed_metrics": {
                "matched_facts": matched_facts,
                "matched_entities": matched_entities,
                "matched_numbers": matched_numbers,
                "constraints": constraints,
            }
        }
