# Token-Oriented Object Notation (TOON) Analysis for SIM API

## Current JSON Format

Currently, you're sending data to SIM.AI in standard JSON format:

```json
{
  "ticket_id": "CRB-7032",
  "summary": "Search results showing inconsistent data",
  "description": "Users are reporting that search functionality is returning different results for the same query when executed multiple times. This appears to be related to stale index data.",
  "status": "In Review",
  "priority": "High",
  "comments": "2024-01-15T10:30:00;John Doe;This is affecting multiple users\n2024-01-15T11:45:00;Jane Smith;Fix has been applied to the search index\n2024-01-15T14:20:00;Tech Lead;Monitoring for 24 hours before closing",
  "days_in_status": 3,
  "total_days_open": 7
}
```

## TOON Format Alternative

TOON (Token-Oriented Object Notation) uses a more compact representation:

```
ticket_id:CRB-7032|summary:Search results showing inconsistent data|description:Users are reporting that search functionality is returning different results for the same query when executed multiple times. This appears to be related to stale index data.|status:In Review|priority:High|comments:2024-01-15T10:30:00;John Doe;This is affecting multiple users
2024-01-15T11:45:00;Jane Smith;Fix has been applied to the search index
2024-01-15T14:20:00;Tech Lead;Monitoring for 24 hours before closing|days_in_status:3|total_days_open:7
```

## Token Count Comparison

### Example 1: Small Ticket (Minimal Data)

**JSON Format:**
```json
{
  "ticket_id": "CRB-7032",
  "summary": "Search bug",
  "description": "Stale index",
  "status": "Done",
  "priority": "High",
  "comments": "",
  "days_in_status": 3,
  "total_days_open": 7
}
```
- **Character count:** ~180 characters
- **Estimated tokens:** ~50-60 tokens

**TOON Format:**
```
ticket_id:CRB-7032|summary:Search bug|description:Stale index|status:Done|priority:High|comments:|days_in_status:3|total_days_open:7
```
- **Character count:** ~135 characters
- **Estimated tokens:** ~35-40 tokens
- **Token reduction:** ~25-33%

---

### Example 2: Medium Ticket (Typical Data)

**JSON Format:**
```json
{
  "ticket_id": "CRB-7032",
  "summary": "Search results showing inconsistent data across multiple queries",
  "description": "Users are reporting that search functionality is returning different results for the same query when executed multiple times. This appears to be related to stale index data that hasn't been properly refreshed.",
  "status": "In Review",
  "priority": "High",
  "comments": "2024-01-15T10:30:00;John Doe;This is affecting multiple users in production\n2024-01-15T11:45:00;Jane Smith;Fix has been applied to the search index\n2024-01-15T14:20:00;Tech Lead;Monitoring for 24 hours before closing",
  "days_in_status": 3,
  "total_days_open": 7
}
```
- **Character count:** ~630 characters
- **Estimated tokens:** ~160-180 tokens

**TOON Format:**
```
ticket_id:CRB-7032|summary:Search results showing inconsistent data across multiple queries|description:Users are reporting that search functionality is returning different results for the same query when executed multiple times. This appears to be related to stale index data that hasn't been properly refreshed.|status:In Review|priority:High|comments:2024-01-15T10:30:00;John Doe;This is affecting multiple users in production
2024-01-15T11:45:00;Jane Smith;Fix has been applied to the search index
2024-01-15T14:20:00;Tech Lead;Monitoring for 24 hours before closing|days_in_status:3|total_days_open:7
```
- **Character count:** ~565 characters
- **Estimated tokens:** ~140-155 tokens
- **Token reduction:** ~12-16%

---

### Example 3: Large Ticket (Heavy Comments)

**JSON Format:**
```json
{
  "ticket_id": "CRB-6977",
  "summary": "Attribution engine not tracking web and WhatsApp order events properly",
  "description": "The attribution engine is failing to capture order events from both web and WhatsApp channels. This is causing significant gaps in our analytics and making it impossible to properly attribute conversions to marketing campaigns. Multiple customers have reported this issue and it's affecting revenue tracking.",
  "status": "To Do",
  "priority": "Critical",
  "comments": "2024-01-10T09:00:00;Product Manager;This is blocking our Q1 analytics review\n2024-01-10T10:30:00;Backend Dev;Need to implement event listeners for both channels\n2024-01-10T14:00:00;QA Lead;Cannot test until implementation is complete\n2024-01-11T09:15:00;Tech Lead;Assigned to backend team, estimated 2 weeks\n2024-01-12T11:00:00;Customer Success;Multiple clients asking for ETA\n2024-01-13T16:30:00;Backend Dev;Still blocked on platform team dependencies",
  "days_in_status": 15,
  "total_days_open": 15
}
```
- **Character count:** ~1,100 characters
- **Estimated tokens:** ~280-320 tokens

**TOON Format:**
```
ticket_id:CRB-6977|summary:Attribution engine not tracking web and WhatsApp order events properly|description:The attribution engine is failing to capture order events from both web and WhatsApp channels. This is causing significant gaps in our analytics and making it impossible to properly attribute conversions to marketing campaigns. Multiple customers have reported this issue and it's affecting revenue tracking.|status:To Do|priority:Critical|comments:2024-01-10T09:00:00;Product Manager;This is blocking our Q1 analytics review
2024-01-10T10:30:00;Backend Dev;Need to implement event listeners for both channels
2024-01-10T14:00:00;QA Lead;Cannot test until implementation is complete
2024-01-11T09:15:00;Tech Lead;Assigned to backend team, estimated 2 weeks
2024-01-12T11:00:00;Customer Success;Multiple clients asking for ETA
2024-01-13T16:30:00;Backend Dev;Still blocked on platform team dependencies|days_in_status:15|total_days_open:15
```
- **Character count:** ~1,020 characters
- **Estimated tokens:** ~255-285 tokens
- **Token reduction:** ~9-11%

---

## Summary of Token Reduction

| Ticket Size | JSON Tokens | TOON Tokens | Reduction | Percentage |
|-------------|-------------|-------------|-----------|------------|
| Small       | 50-60       | 35-40       | 15-20     | 25-33%     |
| Medium      | 160-180     | 140-155     | 20-25     | 12-16%     |
| Large       | 280-320     | 255-285     | 25-35     | 9-11%      |

## Key Findings

### 1. **Token Reduction Varies by Content**
- **Structural overhead:** JSON has more structural characters (`{}`, `""`, `,`, `:`) which contribute to token count
- **Small tickets benefit most:** When data is minimal, structural overhead is proportionally larger
- **Large tickets benefit less:** When content is substantial, the structural overhead becomes less significant

### 2. **Average Token Reduction: 12-20%**
Based on your typical ticket data (medium-sized tickets with moderate comments), you can expect:
- **~15% average token reduction**
- For 168 tickets, if each uses ~170 tokens on average:
  - JSON: 168 × 170 = **28,560 tokens**
  - TOON: 168 × 145 = **24,360 tokens**
  - **Savings: ~4,200 tokens (15%)**

### 3. **Cost Implications**
If SIM.AI charges per token (typical pricing):
- At $0.002 per 1K tokens (example rate):
  - JSON cost: $0.057
  - TOON cost: $0.049
  - **Savings per batch: $0.008 (14%)**

### 4. **Trade-offs to Consider**

#### Advantages of TOON:
✅ Reduced token count (12-20% savings)
✅ Faster parsing for simple key-value data
✅ Smaller payload size (network efficiency)
✅ More human-readable for simple structures

#### Disadvantages of TOON:
❌ Not a standard format (requires custom parsing)
❌ No native support in most APIs/libraries
❌ Harder to handle nested objects or arrays
❌ Escaping special characters (`:`, `|`) becomes complex
❌ No schema validation tools
❌ Debugging is harder (no JSON formatters)
❌ **SIM.AI may not support it** - you'd need to verify

## Recommendation

### For Your Use Case:

**Stick with JSON** for the following reasons:

1. **API Compatibility:** SIM.AI likely expects JSON. Switching to TOON would require:
   - Confirming SIM.AI supports custom formats
   - Potentially modifying their workflow to parse TOON
   - Risk of breaking the integration

2. **Modest Savings:** 15% token reduction is nice but not game-changing
   - For 168 tickets: ~4,200 tokens saved
   - Cost savings: negligible (cents)

3. **Maintenance Burden:** Custom format adds complexity:
   - Need to escape special characters in descriptions/comments
   - Harder to debug issues
   - Future developers need to understand custom format

### Alternative Optimization Strategies:

Instead of TOON, consider these approaches for better token reduction:

#### 1. **Compress Redundant Data**
```python
# Instead of sending full timestamps in comments:
"comments": "2024-01-15T10:30:00;John;Comment 1\n2024-01-15T11:45:00;Jane;Comment 2"

# Use relative timestamps or abbreviate:
"comments": "D0-10:30;John;Comment 1\nD0-11:45;Jane;Comment 2"
```

#### 2. **Abbreviate Field Names** (if SIM.AI allows)
```python
payload = {
    "tid": key,           # ticket_id
    "sum": summary,       # summary
    "desc": description,  # description
    "st": status,         # status
    "pri": priority,      # priority
    "com": comments,      # comments
    "dis": days_in_status,
    "tdo": total_days_open
}
```
**Token reduction: ~10-15%** (similar to TOON but keeps JSON structure)

#### 3. **Remove Empty Fields**
```python
# Don't send fields with empty values
payload = {k: v for k, v in payload.items() if v}
```

#### 4. **Truncate Long Descriptions** (if acceptable)
```python
# Limit description to first 500 characters
description_text = description_text[:500]
```

#### 5. **Batch Processing** (if SIM.AI supports)
Send multiple tickets in one request instead of individual requests:
```python
{
  "tickets": [
    {"ticket_id": "CRB-1", ...},
    {"ticket_id": "CRB-2", ...}
  ]
}
```
This amortizes the request overhead across multiple tickets.

## Conclusion

**TOON can reduce tokens by 12-20%**, but for your use case:
- The savings are modest (~4,200 tokens for 168 tickets)
- JSON is the standard and safer choice
- Alternative optimizations (abbreviated keys, removing empty fields) can achieve similar savings while maintaining JSON compatibility

**Recommendation:** Keep using JSON and implement field name abbreviation + empty field removal for similar token reduction without the risks of a custom format.
