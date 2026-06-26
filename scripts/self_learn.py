#!/usr/bin/env python3
"""
SAP Router Self-Learning Engine v4.0 (Hermes-style context adaptation)

Builds internal knowledge from environment interactions:
- Tracks MCP latency and reliability → prefers faster paths
- Remembers successful action patterns → reuses proven routes
- Learns SAP system quirks (version, patch level, available features)
- Stores project-specific patterns in MEMORY.md LEARN section
- Adapts routing weights based on historical success rates

Philosophy: "eval first, then act" (Andrej Karpathy)
Measure what works, double down on what succeeds, avoid what fails.
"""
import re
import argparse
from pathlib import Path
from datetime import datetime

SKILL_DIR = Path(__file__).resolve().parent.parent
LEARN_FILE = SKILL_DIR / "MEMORY.md"

# Learning decay: recent interactions weight more
DECAY_HALF_LIFE_HOURS = 24
MAX_OBSERVATIONS = 200

def _decay_weight(last_used_str, half_life_hours=DECAY_HALF_LIFE_HOURS):
    """Calculate decay weight based on time since last use. Recent = higher weight."""
    try:
        last_used = datetime.fromisoformat(last_used_str)
        elapsed = datetime.now() - last_used
        hours = elapsed.total_seconds() / 3600
        return 2.0 ** (-hours / half_life_hours)
    except Exception:
        return 0.5  # Neutral weight on parse error


class SelfLearnEngine:
    """Tracks, learns from, and adapts to SAP environment interactions."""

    def __init__(self, memory_file=None):
        self.memory_file = Path(memory_file or LEARN_FILE)
        self.observations = []
        self.mcp_stats = {}       # mcp_name → {latency_ms, success_rate, last_error}
        self.route_success = {}   # action_type → {total, success, fail}
        self.system_features = {} # Discovered SAP system capabilities
        self.learned_patterns = {} # User preference patterns

    def load_history(self):
        """Parse existing MEMORY.md for learned context."""
        if not self.memory_file.exists():
            return

        content = self.memory_file.read_text(encoding='utf-8')
        in_learn = False

        for line in content.split('\n'):
            line = line.strip()

            if line.startswith('## LEARN'):
                in_learn = True
                continue
            elif line.startswith('## ') and line != '## LEARN':
                in_learn = False
                continue

            if not in_learn:
                continue

            # Parse learning entries
            if line.startswith('- mcp:'):
                m = re.match(r'- mcp:(\w+)\s+latency:(\d+)ms\s+success:([\d.]+)\s+last:(\S+)', line)
                if m:
                    self.mcp_stats[m.group(1)] = {
                        'latency_ms': int(m.group(2)),
                        'success_rate': float(m.group(3)),
                        'last_used': m.group(4),
                    }

            elif line.startswith('- route:'):
                m = re.match(r'- route:(\w+)\s+total:(\d+)\s+ok:(\d+)\s+fail:(\d+)', line)
                if m:
                    self.route_success[m.group(1)] = {
                        'total': int(m.group(2)),
                        'ok': int(m.group(3)),
                        'fail': int(m.group(4)),
                    }

            elif line.startswith('- sys:'):
                m = re.match(r'- sys:(\S+)\s+(.+)', line)
                if m:
                    self.system_features[m.group(1)] = m.group(2)

            elif line.startswith('- pattern:'):
                m = re.match(r'- pattern:(\S+)\s+(\w+)\s+(.+)', line)
                if m:
                    self.learned_patterns[m.group(1)] = {
                        'preferred_route': m.group(2),
                        'note': m.group(3),
                    }

    def record_mcp_call(self, mcp_name, latency_ms, success, error=None):
        """Record an MCP call outcome for learning."""
        if mcp_name not in self.mcp_stats:
            self.mcp_stats[mcp_name] = {
                'latency_ms': latency_ms,
                'success_rate': 1.0 if success else 0.0,
                'last_used': datetime.now().isoformat()[:19],
                'total_calls': 1,
                'success_count': 1 if success else 0,
            }
            return

        stats = self.mcp_stats[mcp_name]
        # Exponential moving average for latency
        alpha = 0.3
        stats['latency_ms'] = int(alpha * latency_ms + (1 - alpha) * stats['latency_ms'])

        # Update success rate
        stats['total_calls'] += 1
        if success:
            stats['success_count'] += 1
        stats['success_rate'] = stats['success_count'] / stats['total_calls']
        stats['last_used'] = datetime.now().isoformat()[:19]

        if error:
            stats['last_error'] = str(error)[:200]

    def record_route_outcome(self, action_type, success):
        """Track routing decision outcomes."""
        if action_type not in self.route_success:
            self.route_success[action_type] = {'total': 0, 'ok': 0, 'fail': 0}
        self.route_success[action_type]['total'] += 1
        if success:
            self.route_success[action_type]['ok'] += 1
        else:
            self.route_success[action_type]['fail'] += 1

    def discover_system_features(self, probe_results):
        """Learn SAP system capabilities from probe results."""
        # Auto-detect from healthcheck or diagnostic output
        if isinstance(probe_results, dict):
            for key, value in probe_results.items():
                if key not in ('timestamp', 'overall_status', 'mcp_checks'):
                    self.system_features[key] = str(value)

    def record_pattern(self, trigger, preferred_route, note=""):
        """Record a learned user preference pattern."""
        self.learned_patterns[trigger] = {
            'preferred_route': preferred_route,
            'note': note,
        }

    def get_best_mcp(self, candidates, prefer_low_latency=True):
        """Select best MCP from candidates based on learned stats."""
        best = None
        best_score = -1

        for candidate in candidates:
            stats = self.mcp_stats.get(candidate, {})
            if not stats:
                best = candidate  # No data → try it
                break

            # Score: high success rate, low latency
            success = stats.get('success_rate', 0.5)
            latency = stats.get('latency_ms', 1000)

            if success < 0.5:
                continue  # Skip unreliable MCPs

            score = success * 100 - (latency / 100 if prefer_low_latency else 0)
            if score > best_score:
                best_score = score
                best = candidate

        return best or (candidates[0] if candidates else None)

    def get_route_confidence(self, action_type):
        """Return confidence score for a routing strategy."""
        stats = self.route_success.get(action_type)
        if not stats or stats['total'] < 3:
            return 0.5  # Neutral — not enough data
        return stats['ok'] / stats['total']

    def adapt_route(self, action, primary_route):
        """Adapt routing based on learned success rates."""
        action_type = action.split('_')[0] if '_' in action else action[:3]

        # Check if this action type has a learned pattern
        confidence = self.get_route_confidence(action_type)

        stats = self.route_success.get(action_type)
        if confidence < 0.3 and stats:
            # This route fails a lot — suggest alternatives
            return {
                **primary_route,
                'adapted': True,
                'confidence': confidence,
                'warning': f"Route {action_type} has {stats['fail']}/{stats['total']} failures. Consider alternative approach.",
            }

        if confidence > 0.8:
            return {**primary_route, 'adapted': False, 'confidence': confidence, 'note': 'High-confidence route'}

        return {**primary_route, 'adapted': False, 'confidence': confidence}

    def persist(self):
        """Write learned context to MEMORY.md LEARN section."""
        if not self.memory_file.exists():
            return

        content = self.memory_file.read_text(encoding='utf-8')

        # Build LEARN section
        learn_lines = ["## LEARN"]

        if self.system_features:
            for key, value in sorted(self.system_features.items()):
                learn_lines.append(f"- sys:{key} {value}")

        if self.mcp_stats:
            for name in sorted(self.mcp_stats):
                stats = self.mcp_stats[name]
                weight = _decay_weight(stats.get('last_used', ''))
                learn_lines.append(
                    f"- mcp:{name} latency:{stats['latency_ms']}ms "
                    f"success:{stats['success_rate']:.2f} last:{stats['last_used']} "
                    f"decay:{weight:.2f}"
                )

        if self.route_success:
            for action in sorted(self.route_success):
                stats = self.route_success[action]
                learn_lines.append(
                    f"- route:{action} total:{stats['total']} "
                    f"ok:{stats['ok']} fail:{stats['fail']}"
                )

        if self.learned_patterns:
            for trigger, pattern in sorted(self.learned_patterns.items()):
                learn_lines.append(
                    f"- pattern:{trigger} {pattern['preferred_route']} {pattern['note']}"
                )

        learn_section = '\n'.join(learn_lines)

        # Replace or add LEARN section
        if '## LEARN' in content:
            content = re.sub(
                r'## LEARN.*?(?=## |\Z)', learn_section + '\n\n', content,
                flags=re.DOTALL
            )
        else:
            # Insert before PENDING section
            if '## PENDING' in content:
                content = content.replace('## PENDING', learn_section + '\n\n## PENDING')
            else:
                content += '\n' + learn_section + '\n'

        self.memory_file.write_text(content, encoding='utf-8')

    def get_context_for_prompt(self):
        """Generate compressed context string for LLM prompt injection."""
        parts = []

        if self.mcp_stats:
            best_mcps = sorted(
                self.mcp_stats.items(),
                key=lambda x: x[1].get('success_rate', 0),
                reverse=True
            )[:5]
            parts.append("MCP_RELIABILITY: " + ", ".join(
                f"{n}={s['success_rate']:.0%}" for n, s in best_mcps
            ))

        if self.system_features:
            parts.append("SYS: " + " ".join(
                f"{k}={v}" for k, v in sorted(self.system_features.items())[:5]
            ))

        if self.learned_patterns:
            parts.append("PATTERNS: " + ", ".join(
                f"{k}→{v['preferred_route']}" for k, v in sorted(self.learned_patterns.items())[:5]
            ))

        return " | ".join(parts) if parts else ""


def main():
    parser = argparse.ArgumentParser(description="SAP Self-Learning Engine v4.0")
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # record-mcp — log an MCP call
    record_mcp = subparsers.add_parser('record-mcp', help='Record MCP call outcome')
    record_mcp.add_argument('--mcp', required=True, help='MCP server name')
    record_mcp.add_argument('--latency', type=int, required=True, help='Latency in ms')
    record_mcp.add_argument('--success', choices=['true', 'false'], required=True)
    record_mcp.add_argument('--error', help='Error message if failed')
    record_mcp.add_argument('--memory-file', default=str(LEARN_FILE))

    # record-route — log a routing outcome
    record_route = subparsers.add_parser('record-route', help='Record routing outcome')
    record_route.add_argument('--action', required=True, help='Action type')
    record_route.add_argument('--success', choices=['true', 'false'], required=True)
    record_route.add_argument('--memory-file', default=str(LEARN_FILE))

    # best-mcp — get best MCP from candidates
    best_mcp = subparsers.add_parser('best-mcp', help='Get best MCP from candidates')
    best_mcp.add_argument('--candidates', required=True, help='Comma-separated MCP names')
    best_mcp.add_argument('--memory-file', default=str(LEARN_FILE))

    # context — get compressed prompt context
    context = subparsers.add_parser('context', help='Get learned context for prompt injection')
    context.add_argument('--memory-file', default=str(LEARN_FILE))

    # persist — force persist learned data
    persist = subparsers.add_parser('persist', help='Persist learned data to MEMORY.md')
    persist.add_argument('--memory-file', default=str(LEARN_FILE))

    # discover — record system feature discovery
    discover = subparsers.add_parser('discover', help='Record discovered system feature')
    discover.add_argument('--feature', required=True, help='Feature name')
    discover.add_argument('--value', required=True, help='Feature value')
    discover.add_argument('--memory-file', default=str(LEARN_FILE))

    args = parser.parse_args()
    engine = SelfLearnEngine(args.memory_file if hasattr(args, 'memory_file') else str(LEARN_FILE))
    engine.load_history()

    if args.command == 'record-mcp':
        engine.record_mcp_call(args.mcp, args.latency, args.success == 'true', args.error)
        engine.persist()
        print(f"Recorded MCP call: {args.mcp} latency={args.latency}ms success={args.success}")

    elif args.command == 'record-route':
        engine.record_route_outcome(args.action, args.success == 'true')
        engine.persist()
        confidence = engine.get_route_confidence(args.action)
        print(f"Recorded route: {args.action} success={args.success} confidence={confidence:.2f}")

    elif args.command == 'best-mcp':
        candidates = [c.strip() for c in args.candidates.split(',')]
        best = engine.get_best_mcp(candidates)
        print(f"Best MCP among {candidates}: {best}")
        if best in engine.mcp_stats:
            stats = engine.mcp_stats[best]
            print(f"  success_rate={stats['success_rate']:.2f} latency={stats['latency_ms']}ms")

    elif args.command == 'context':
        ctx = engine.get_context_for_prompt()
        if ctx:
            print(ctx)
        else:
            print("(no learned context yet)")

    elif args.command == 'persist':
        engine.persist()
        print("Learned context persisted to MEMORY.md")

    elif args.command == 'discover':
        engine.system_features[args.feature] = args.value
        engine.persist()
        print(f"Discovered: {args.feature}={args.value}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
