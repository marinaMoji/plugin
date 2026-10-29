# Stage E2 — Known limitations

- No automatic line-wrap kinsoku diagnostics.  
- No warichū internal-break detection.  
- Soft-break detection depends on paragraph `getString()` containing soft-break characters; if a host build omits them, `EXPLICIT_BREAK_BEFORE_NOTSTART` is deferred in practice (rule stays correct when breaks are visible).  
- Ruby readings are not treated as body punctuation (`getString` is base text); portion-level ruby presence is flagged only for context.  
- Kaeriten frames are not parsed; JP-context heuristics reduce false positives.  
- Multi-cell table selections may be `unsupported`.  
- Scholarly profiles not implemented.
