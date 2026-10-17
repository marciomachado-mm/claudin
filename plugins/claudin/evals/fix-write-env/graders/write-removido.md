---
type: regex
target: { source: file, path: .claude/settings.json }
pattern: 'Write\(\.env\)'
match: not_contains
---
