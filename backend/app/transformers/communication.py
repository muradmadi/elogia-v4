"""Transformer for communication/strategy data from enrichment payloads."""
from typing import Dict, Any, List, Optional


def _transform_architecture_element(element: Dict[str, Any]) -> Dict[str, Any]:
    """Transform a message element into ArchitectureElementView shape."""
    return {
        "text": element.get("text", ""),
        "rationale": element.get("whyItWorks"),
        "source": element.get("source"),
        "logic": element.get("logic"),
        "friction": element.get("friction"),
    }


def _transform_message_architecture(arch: Dict[str, Any]) -> Dict[str, Any]:
    """Transform message architecture into MessageArchitectureView shape."""
    return {
        "hook": _transform_architecture_element(arch.get("hook", {})),
        "bridge": _transform_architecture_element(arch.get("bridge", {})),
        "proof": _transform_architecture_element(arch.get("proof", {})),
        "ask": _transform_architecture_element(arch.get("ask", {})),
    }


def _transform_channel_format(fmt: Dict[str, Any]) -> Dict[str, Any]:
    """Transform channel format into ChannelFormatView shape."""
    return {
        "style": fmt.get("style", ""),
        "length": fmt.get("length", ""),
        "reasoning": fmt.get("reasoning"),
    }


def _transform_channel_timing(timing: Dict[str, Any]) -> Dict[str, Any]:
    """Transform channel timing into ChannelTimingView shape."""
    return {
        "best_time": timing.get("bestTime", ""),
        "avoid_time": timing.get("avoidTime", ""),
        "reasoning": timing.get("reasoning"),
    }


def _transform_channel_strategy(strategy: Dict[str, Any]) -> Dict[str, Any]:
    """Transform channel strategy into ChannelStrategyView shape."""
    return {
        "primary_channel": strategy.get("primaryChannel", ""),
        "secondary_channel": strategy.get("secondaryChannel", ""),
        "format": _transform_channel_format(strategy.get("format", {})),
        "timing": _transform_channel_timing(strategy.get("timing", {})),
    }


def _transform_angle_variants(variants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Transform angle variants into AngleVariantView shape."""
    return [
        {
            "angle_name": v.get("angleName", ""),
            "target_pain": v.get("targetPain", ""),
            "opening": v.get("opening", ""),
            "framing": v.get("framing", ""),
            "proof_point": v.get("proofPoint", ""),
            "cta": v.get("cta", ""),
        }
        for v in variants
        if isinstance(v, dict)
    ]


def _transform_risk_mitigation(risks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Transform risk mitigations into RiskMitigationView shape."""
    return [
        {
            "risk": r.get("risk", ""),
            "impact": r.get("impact", ""),
            "likelihood": r.get("likelihood", ""),
            "mitigation": r.get("mitigation", ""),
        }
        for r in risks
        if isinstance(r, dict)
    ]


def _transform_pain_solution_map(mappings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Transform pain solution mappings into PainSolutionMapView shape."""
    return [
        {
            "their_pain": m.get("theirPain", ""),
            "your_solution": m.get("yourSolution", ""),
            "evidence_level": m.get("evidenceLevel", ""),
            "connection_logic": m.get("connectionLogic", ""),
        }
        for m in mappings
        if isinstance(m, dict)
    ]


def _transform_strategic_positioning(positioning: Dict[str, Any]) -> Dict[str, Any]:
    """Transform strategic positioning into StrategicPositioningView shape."""
    return {
        "core_thesis": positioning.get("coreThesis", ""),
        "pain_solution_map": _transform_pain_solution_map(
            positioning.get("painSolutionMap", [])
        ),
    }


def transform_communication(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Transform raw communication payload into CommunicationSchema shape.

    Maps raw payload 6 fields to the canonical CommunicationSchema structure,
    including all nested view objects for outreach and communication strategy.
    """
    return {
        "notes": payload.get("notes"),
        "strategic_positioning": _transform_strategic_positioning(
            payload.get("strategicPositioning", {})
        ),
        "message_architecture": _transform_message_architecture(
            payload.get("messageArchitecture", {})
        ),
        "channel_strategy": _transform_channel_strategy(
            payload.get("channelStrategy", {})
        ),
        "angle_variants": _transform_angle_variants(
            payload.get("angleVariants", [])
        ),
        "risk_mitigation": _transform_risk_mitigation(
            payload.get("riskMitigation", [])
        ),
    }
