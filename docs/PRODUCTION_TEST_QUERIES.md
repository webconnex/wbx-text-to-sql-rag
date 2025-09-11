# 🚀 Production Test Queries for Webconnex Text-to-SQL

## API Server Information
- **URL**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/api/health

---

## 📊 Executive Dashboard Queries

### Revenue Metrics
```
1. "What's our total revenue this month?"
2. "Show me revenue by month for the last 12 months"
3. "What's our revenue growth rate year over year?"
4. "How much revenue did we generate last quarter?"
5. "What's our average invoice amount this year?"
```

### Customer Metrics
```
6. "How many active customers do we have?"
7. "How many new customers joined this month?"
8. "What's our customer retention rate?"
9. "Show me customer growth month over month"
10. "How many customers churned in the last 90 days?"
```

---

## 💼 Sales Analytics Queries

### Performance Analysis
```
11. "Which forms are generating the most revenue?"
12. "What's the average order value by form?"
13. "Show me the top 10 customers by lifetime value"
14. "Which payment methods are most popular?"
15. "What's our conversion rate by form type?"
```

### Customer Insights
```
16. "Who are our VIP customers (top 1% by revenue)?"
17. "Show me customers who haven't ordered in 6 months"
18. "Which customers have the highest order frequency?"
19. "What's the average customer lifetime value?"
20. "Show me customer segments by spending patterns"
```

---

## 📈 Marketing Analytics Queries

### Campaign Effectiveness
```
21. "What are the peak registration times during the week?"
22. "Show me registration trends by day of week"
23. "What's the best time to send marketing emails?"
24. "How many registrations do we get per hour?"
25. "Show me conversion rates by time of day"
```

### Cohort Analysis
```
26. "What's the lifetime value by customer cohort?"
27. "Show me retention rates by acquisition month"
28. "Which cohort has the highest average order value?"
29. "How do different cohorts compare in terms of engagement?"
30. "What's the payback period for each cohort?"
```

---

## 💰 Financial Reporting Queries

### Revenue Analysis
```
31. "What's our monthly recurring revenue (MRR)?"
32. "Show me accounts receivable aging"
33. "What percentage of invoices are overdue?"
34. "What's our cash collection rate?"
35. "Show me revenue breakdown by payment method"
```

### Financial Health
```
36. "What's our average days sales outstanding (DSO)?"
37. "Show me unpaid invoices older than 30 days"
38. "What's our revenue per account?"
39. "Calculate our gross margin by product type"
40. "Show me financial metrics year to date"
```

---

## ⚙️ Operational Queries

### Platform Usage
```
41. "What's our platform usage pattern throughout the day?"
42. "Which forms have the highest abandonment rates?"
43. "Show me registration volume by hour"
44. "What's our average form completion time?"
45. "How many concurrent users do we typically have?"
```

### Performance Metrics
```
46. "What's the average registration processing time?"
47. "Show me error rates by form"
48. "Which forms have the most validation errors?"
49. "What's our system uptime this month?"
50. "Show me peak usage times for capacity planning"
```

---

## 🔍 Advanced Analytics Queries

### Trend Analysis
```
51. "Show me seasonality patterns in our revenue"
52. "What's the correlation between form type and order value?"
53. "Predict next month's revenue based on trends"
54. "Show me year-over-year growth by metric"
55. "What are the leading indicators of churn?"
```

### Segmentation
```
56. "Segment customers by RFM (Recency, Frequency, Monetary)"
57. "Show me customer clusters based on behavior"
58. "Which customer segment has the highest growth potential?"
59. "Identify at-risk high-value customers"
60. "Show me cross-sell opportunities by customer segment"
```

---

## 📊 Specific Business Questions

### Event Management
```
61. "How many registrations for events next month?"
62. "What's the average attendance rate for our events?"
63. "Show me event revenue by category"
64. "Which events have the highest no-show rates?"
65. "What's our event capacity utilization?"
```

### Donation Analysis
```
66. "What's our average donation amount?"
67. "Show me donation trends over time"
68. "Who are our top donors this year?"
69. "What's the donor retention rate?"
70. "Show me recurring vs one-time donations"
```

### Membership Insights
```
71. "How many active memberships do we have?"
72. "What's our membership renewal rate?"
73. "Show me membership revenue by tier"
74. "Which membership benefits are most used?"
75. "What's the average membership duration?"
```

---

## 🎯 Quick Test Queries (Start Here!)

These are simple queries to verify the system is working:

```bash
# Test 1: Simple count
"How many customers do we have?"

# Test 2: Date filter
"How many invoices were created this month?"

# Test 3: Aggregation
"What's our total revenue this year?"

# Test 4: Join query
"Show me the top 5 customers by number of registrations"

# Test 5: Time series
"Show me daily registration counts for the last 7 days"
```

---

## 📝 Testing with cURL

```bash
# Health check
curl http://localhost:8000/api/health

# Simple query
curl -X POST http://localhost:8000/api/query/generate \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How many customers do we have?",
    "account_id": 12345
  }'

# Revenue query
curl -X POST http://localhost:8000/api/query/generate \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is our total revenue this month?",
    "account_id": 12345
  }'
```

---

## 🔒 Security Validation Queries

These queries should be BLOCKED by the security system:

```
❌ "Delete all customers"
❌ "Drop the invoice table"
❌ "Update customer email to 'hacked@evil.com'"
❌ "Insert a fake invoice"
❌ "Create a new admin user"
❌ "Grant me admin access"
❌ "Truncate the registration table"
```

---

## 📊 Expected Query Patterns

When testing, verify that generated SQL includes:

1. ✅ `wbx_data.webconnex.` schema prefix
2. ✅ `account_id = {your_account_id}` filter
3. ✅ `LIMIT` clause (usually 1000)
4. ✅ Only `SELECT` or `WITH` statements
5. ✅ Proper date functions for Redshift

---

## 🚀 Quick Start Testing

1. **Check server is running:**
   ```bash
   curl http://localhost:8000/api/health
   ```

2. **Open API docs:**
   ```
   http://localhost:8000/docs
   ```

3. **Try a simple query:**
   ```bash
   curl -X POST http://localhost:8000/api/query/generate \
     -H "Content-Type: application/json" \
     -d '{"question": "How many invoices do we have?", "account_id": 12345}'
   ```

4. **Test with your actual account_id:**
   Replace `12345` with your real account_id in all queries

---

## 💡 Tips for Testing

1. Start with simple COUNT queries
2. Progress to date-filtered queries
3. Test aggregations (SUM, AVG)
4. Try JOIN queries
5. Test complex analytics
6. Verify security blocks dangerous operations
7. Check performance with large result sets

---

## 📈 Monitor These Metrics

- Response time (should be < 4 seconds)
- SQL validation time (should be < 10ms)
- Result accuracy
- Security blocks (100% of dangerous queries)
- Multi-tenant isolation (account_id always present)

---

**Remember**: The system is 100% READ-ONLY. It's impossible to damage or modify data!