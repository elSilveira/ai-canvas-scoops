"""Reasoning Tracer for tracking and logging all reasoning steps."""

from datetime import datetime
from typing import List, Dict, Any, Optional
from src.models.reasoning_step import ReasoningStep


class ReasoningTracer:
    """Tracks and logs all reasoning steps for debugging."""

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = (
            session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.steps: List[ReasoningStep] = []
        self.start_time = datetime.now()
        self.metadata: Dict[str, Any] = {}

    def start_trace(
        self, session_id: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Start a new trace session."""
        self.session_id = session_id
        self.steps.clear()
        self.start_time = datetime.now()
        self.metadata = metadata or {}

        # Add initial step
        self.add_step(
            action="start_trace",
            input_data={"session_id": session_id, "metadata": self.metadata},
            output_data={},
            reasoning=f"Started new reasoning trace session: {session_id}",
        )

    def add_step(
        self,
        action: str,
        input_data: Any,
        output_data: Any,
        reasoning: str,
        game_context: Optional[str] = None,
        tool_calls: Optional[List[str]] = None,
    ) -> None:
        """Add a reasoning step to the trace."""
        step = ReasoningStep(
            step_number=len(self.steps) + 1,
            action=action,
            input_data=input_data
            if isinstance(input_data, dict)
            else {"data": input_data},
            output_data=output_data
            if isinstance(output_data, dict)
            else {"data": output_data},
            reasoning=reasoning,
            game_context=game_context,
            timestamp=datetime.now(),
            tool_calls=tool_calls,
        )
        self.steps.append(step)

    def add_tool_call(
        self, tool_name: str, parameters: Dict, result: Any, latency: float
    ) -> None:
        """Track MCP tool calls with performance metrics."""
        self.add_step(
            action=f"tool_call_{tool_name}",
            input_data={
                "tool": tool_name,
                "parameters": parameters,
                "latency_ms": latency * 1000,
            },
            output_data={"result": result, "success": True},
            reasoning=f"Called {tool_name} tool with {len(parameters)} parameters, completed in {latency * 1000:.1f}ms",
            tool_calls=[tool_name],
        )

    def add_error(
        self, action: str, error: Exception, context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add an error step to the trace."""
        self.add_step(
            action=f"error_{action}",
            input_data=context or {},
            output_data={
                "error_type": type(error).__name__,
                "error_message": str(error),
            },
            reasoning=f"Error occurred during {action}: {str(error)}",
        )

    def add_decision_point(
        self,
        decision: str,
        options: List[str],
        chosen: str,
        reasoning: str,
        confidence: float = None,
    ) -> None:
        """Add a decision point to the trace."""
        self.add_step(
            action="decision_point",
            input_data={
                "decision": decision,
                "options": options,
                "confidence": confidence,
            },
            output_data={"chosen": chosen},
            reasoning=reasoning,
        )

    def get_trace(self) -> List[ReasoningStep]:
        """Get the complete reasoning trace."""
        return self.steps.copy()

    def get_trace_summary(self) -> Dict[str, Any]:
        """Get a summary of the trace session."""
        total_time = (datetime.now() - self.start_time).total_seconds()

        # Count different types of actions
        action_counts = {}
        tool_calls = []
        errors = []

        for step in self.steps:
            action_type = step.action.split("_")[0]
            action_counts[action_type] = action_counts.get(action_type, 0) + 1

            if step.tool_calls:
                tool_calls.extend(step.tool_calls)

            if step.action.startswith("error_"):
                errors.append(step)

        return {
            "session_id": self.session_id,
            "total_steps": len(self.steps),
            "total_time_seconds": total_time,
            "action_counts": action_counts,
            "tool_calls": list(set(tool_calls)),
            "unique_tools_used": len(set(tool_calls)),
            "error_count": len(errors),
            "has_errors": len(errors) > 0,
            "start_time": self.start_time,
            "metadata": self.metadata,
        }

    def export_debug_report(self) -> str:
        """Generate human-readable debug report."""
        summary = self.get_trace_summary()

        report = "REASONING TRACE DEBUG REPORT\n"
        report += "=" * 50 + "\n\n"

        report += f"Session ID: {summary['session_id']}\n"
        report += f"Start Time: {summary['start_time']}\n"
        report += f"Total Duration: {summary['total_time_seconds']:.2f} seconds\n"
        report += f"Total Steps: {summary['total_steps']}\n"
        report += f"Tools Used: {', '.join(summary['tool_calls']) if summary['tool_calls'] else 'None'}\n"

        if summary["has_errors"]:
            report += f"⚠️  ERRORS DETECTED: {summary['error_count']}\n"
        else:
            report += "✅ No errors detected\n"

        report += "\nACTION BREAKDOWN:\n"
        for action, count in summary["action_counts"].items():
            report += f"  {action}: {count}\n"

        if summary["metadata"]:
            report += "\nSESSION METADATA:\n"
            for key, value in summary["metadata"].items():
                report += f"  {key}: {value}\n"

        report += "\n" + "=" * 50 + "\n"
        report += "DETAILED STEP-BY-STEP TRACE:\n"
        report += "=" * 50 + "\n\n"

        for step in self.steps:
            report += step.to_debug_string() + "\n"
            report += "-" * 30 + "\n"

        return report

    def export_timeline_view(self) -> str:
        """Export a timeline view of the reasoning trace."""
        if not self.steps:
            return "No steps in trace"

        timeline = "REASONING TIMELINE\n"
        timeline += "=" * 40 + "\n\n"

        for i, step in enumerate(self.steps):
            elapsed = (step.timestamp - self.start_time).total_seconds()

            # Visual indicator based on action type
            if step.action.startswith("error_"):
                indicator = "❌"
            elif step.action.startswith("tool_call"):
                indicator = "🔧"
            elif step.action.startswith("decision"):
                indicator = "🤔"
            else:
                indicator = "📋"

            timeline += (
                f"{elapsed:6.2f}s {indicator} Step {step.step_number}: {step.action}\n"
            )
            timeline += f"        {step.reasoning[:80]}{'...' if len(step.reasoning) > 80 else ''}\n"

            if step.game_context:
                timeline += f"        🎮 {step.game_context[:60]}{'...' if len(step.game_context) > 60 else ''}\n"

            timeline += "\n"

        return timeline

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics from the trace."""
        if not self.steps:
            return {"error": "No steps to analyze"}

        total_time = (
            self.steps[-1].timestamp - self.steps[0].timestamp
        ).total_seconds()

        # Calculate time between steps
        step_durations = []
        for i in range(1, len(self.steps)):
            duration = (
                self.steps[i].timestamp - self.steps[i - 1].timestamp
            ).total_seconds()
            step_durations.append(duration)

        # Tool call analysis
        tool_call_times = []
        for step in self.steps:
            if step.action.startswith("tool_call") and "latency_ms" in step.input_data:
                tool_call_times.append(step.input_data["latency_ms"])

        return {
            "total_processing_time": total_time,
            "average_step_duration": sum(step_durations) / len(step_durations)
            if step_durations
            else 0,
            "fastest_step": min(step_durations) if step_durations else 0,
            "slowest_step": max(step_durations) if step_durations else 0,
            "tool_call_count": len(tool_call_times),
            "average_tool_call_time": sum(tool_call_times) / len(tool_call_times)
            if tool_call_times
            else 0,
            "total_tool_call_time": sum(tool_call_times),
            "steps_per_second": len(self.steps) / total_time if total_time > 0 else 0,
        }

    def clear_trace(self) -> None:
        """Clear the current trace."""
        self.steps.clear()
        self.start_time = datetime.now()
        self.metadata.clear()

    def save_trace_to_file(self, filename: Optional[str] = None) -> str:
        """Save the trace to a file."""
        if not filename:
            filename = f"trace_{self.session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(filename, "w") as f:
            f.write(self.export_debug_report())

        return filename
