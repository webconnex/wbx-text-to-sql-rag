"""
Prompt Templates Optimized for Amazon Nova Pro
Ensures consistent SQL generation with security constraints
"""

class NovaProPrompts:
    """
    Optimized prompts for Amazon Nova Pro model
    """
    
    @staticmethod
    def get_base_prompt(question: str, account_id: int) -> str:
        """
        Base prompt template for Nova Pro
        
        Args:
            question: User's natural language question
            account_id: Account ID for multi-tenancy
            
        Returns:
            Formatted prompt string
        """
        return f"""You are a SQL expert. Generate a READ-ONLY SQL query for the question below.

DATABASE: Amazon Redshift
SCHEMA: wbx_data.webconnex

TABLES:
- wbx_data.webconnex.customer (id, account_id, email, date_created, date_deleted)
- wbx_data.webconnex.invoice (id, account_id, amount, billing_date, status)
- wbx_data.webconnex.registration (id, account_id, customer_id, total, date_completed, status)
- wbx_data.webconnex.account (id, name, email)
- wbx_data.webconnex.form (id, account_id, name)

MANDATORY RULES (ALL MUST BE FOLLOWED):
1. Query MUST start with SELECT
2. MUST include: WHERE account_id = {account_id}
3. MUST include: LIMIT 1000 (or less if user specifies)
4. MUST use full table names: wbx_data.webconnex.tablename
5. For active records: Add AND date_deleted IS NULL

QUESTION: {question}

SQL:"""

    @staticmethod
    def get_aggregation_prompt(question: str, account_id: int) -> str:
        """
        Prompt for aggregation queries (SUM, COUNT, AVG)
        
        Args:
            question: User's natural language question
            account_id: Account ID for multi-tenancy
            
        Returns:
            Formatted prompt string
        """
        return f"""Generate a SQL query with aggregation functions.

DATABASE: Amazon Redshift (wbx_data.webconnex schema)

QUESTION: {question}

REQUIREMENTS:
1. Use appropriate aggregation: COUNT(*), SUM(amount), AVG(total)
2. Include: WHERE account_id = {account_id}
3. Add GROUP BY if needed
4. Include: LIMIT 1000
5. For active records: AND date_deleted IS NULL

Return ONLY the SQL query:"""

    @staticmethod
    def get_temporal_prompt(question: str, account_id: int) -> str:
        """
        Prompt for time-based queries
        
        Args:
            question: User's natural language question
            account_id: Account ID for multi-tenancy
            
        Returns:
            Formatted prompt string
        """
        return f"""Generate a SQL query for time-based analysis.

DATABASE: Amazon Redshift (wbx_data.webconnex schema)

QUESTION: {question}

TIME FUNCTIONS:
- CURRENT_DATE for today
- DATE_TRUNC('month', date_field) for monthly grouping
- EXTRACT(year FROM date_field) for year extraction
- date_field >= CURRENT_DATE - INTERVAL '30 days' for last 30 days

REQUIREMENTS:
1. Use proper date functions
2. Include: WHERE account_id = {account_id}
3. Include: LIMIT 1000
4. Full table names: wbx_data.webconnex.tablename

SQL:"""

    @staticmethod
    def get_join_prompt(question: str, account_id: int) -> str:
        """
        Prompt for queries requiring JOINs
        
        Args:
            question: User's natural language question
            account_id: Account ID for multi-tenancy
            
        Returns:
            Formatted prompt string
        """
        return f"""Generate a SQL query with table joins.

DATABASE: Amazon Redshift (wbx_data.webconnex schema)

QUESTION: {question}

RELATIONSHIPS:
- customer.account_id → account.id
- registration.customer_id → customer.id
- registration.account_id → account.id
- invoice.account_id → account.id

REQUIREMENTS:
1. Use appropriate JOIN type (INNER, LEFT)
2. Include: WHERE account_id = {account_id} (on main table)
3. Include: LIMIT 1000
4. Full table names in JOINs

SQL:"""

    @staticmethod
    def get_ranking_prompt(question: str, account_id: int) -> str:
        """
        Prompt for TOP N or ranking queries
        
        Args:
            question: User's natural language question
            account_id: Account ID for multi-tenancy
            
        Returns:
            Formatted prompt string
        """
        return f"""Generate a SQL query for ranking/top results.

DATABASE: Amazon Redshift (wbx_data.webconnex schema)

QUESTION: {question}

REQUIREMENTS:
1. Use ORDER BY for ranking
2. Include: WHERE account_id = {account_id}
3. Use appropriate LIMIT (e.g., LIMIT 10 for top 10)
4. Consider window functions if needed: ROW_NUMBER(), RANK()
5. Full table names: wbx_data.webconnex.tablename

SQL:"""

    @staticmethod
    def get_security_check_prompt(sql: str) -> str:
        """
        Prompt to validate SQL security
        
        Args:
            sql: Generated SQL query
            
        Returns:
            Security validation prompt
        """
        return f"""Validate this SQL query for security:

{sql}

Check:
1. Is it READ-ONLY (no DELETE, DROP, UPDATE, INSERT)?
2. Does it have account_id filter?
3. Does it have LIMIT clause?
4. Uses wbx_data.webconnex schema?

If ANY security issue found, respond: "BLOCKED: [reason]"
If secure, respond: "APPROVED"

Result:"""

    @staticmethod
    def classify_query_type(question: str) -> str:
        """
        Classify the query type to select appropriate prompt
        
        Args:
            question: User's natural language question
            
        Returns:
            Query type: 'aggregation', 'temporal', 'join', 'ranking', 'base'
        """
        question_lower = question.lower()
        
        # Check for aggregation keywords
        if any(word in question_lower for word in ['total', 'sum', 'count', 'average', 'avg', 'how many']):
            return 'aggregation'
        
        # Check for temporal keywords
        if any(word in question_lower for word in ['today', 'yesterday', 'month', 'year', 'date', 'when', 'last', 'this']):
            return 'temporal'
        
        # Check for ranking keywords
        if any(word in question_lower for word in ['top', 'best', 'worst', 'highest', 'lowest', 'most', 'least']):
            return 'ranking'
        
        # Check for potential joins
        if any(word in question_lower for word in ['customer', 'invoice', 'registration']) and \
           any(word in question_lower for word in ['with', 'and their', 'including']):
            return 'join'
        
        return 'base'

    @staticmethod
    def get_optimized_prompt(question: str, account_id: int) -> str:
        """
        Get the most appropriate prompt based on query type
        
        Args:
            question: User's natural language question
            account_id: Account ID for multi-tenancy
            
        Returns:
            Optimized prompt for the query type
        """
        query_type = NovaProPrompts.classify_query_type(question)
        
        if query_type == 'aggregation':
            return NovaProPrompts.get_aggregation_prompt(question, account_id)
        elif query_type == 'temporal':
            return NovaProPrompts.get_temporal_prompt(question, account_id)
        elif query_type == 'join':
            return NovaProPrompts.get_join_prompt(question, account_id)
        elif query_type == 'ranking':
            return NovaProPrompts.get_ranking_prompt(question, account_id)
        else:
            return NovaProPrompts.get_base_prompt(question, account_id)


class PromptExamples:
    """
    Example prompts and expected outputs for training
    """
    
    EXAMPLES = [
        {
            "question": "How many active customers do we have?",
            "sql": "SELECT COUNT(*) as active_customers FROM wbx_data.webconnex.customer WHERE account_id = {account_id} AND date_deleted IS NULL LIMIT 1000;"
        },
        {
            "question": "What's our total revenue this month?",
            "sql": "SELECT SUM(amount) as total_revenue FROM wbx_data.webconnex.invoice WHERE account_id = {account_id} AND DATE_TRUNC('month', billing_date) = DATE_TRUNC('month', CURRENT_DATE) LIMIT 1000;"
        },
        {
            "question": "Show me top 10 customers by lifetime value",
            "sql": """SELECT c.id, c.email, SUM(r.total) as lifetime_value 
                     FROM wbx_data.webconnex.customer c 
                     JOIN wbx_data.webconnex.registration r ON c.id = r.customer_id 
                     WHERE c.account_id = {account_id} AND c.date_deleted IS NULL 
                     GROUP BY c.id, c.email 
                     ORDER BY lifetime_value DESC 
                     LIMIT 10;"""
        },
        {
            "question": "How many registrations were completed today?",
            "sql": "SELECT COUNT(*) as registrations_today FROM wbx_data.webconnex.registration WHERE account_id = {account_id} AND DATE(date_completed) = CURRENT_DATE AND status = 1 LIMIT 1000;"
        },
        {
            "question": "List customers who registered in the last 30 days",
            "sql": "SELECT id, email, date_created FROM wbx_data.webconnex.customer WHERE account_id = {account_id} AND date_created >= CURRENT_DATE - INTERVAL '30 days' AND date_deleted IS NULL ORDER BY date_created DESC LIMIT 1000;"
        }
    ]
    
    @staticmethod
    def get_examples_for_context(question: str, account_id: int, limit: int = 3) -> str:
        """
        Get relevant examples for context
        
        Args:
            question: User's question
            account_id: Account ID
            limit: Number of examples to return
            
        Returns:
            Formatted examples string
        """
        examples_str = "\nEXAMPLES:\n"
        for i, example in enumerate(PromptExamples.EXAMPLES[:limit], 1):
            sql_with_account = example['sql'].replace('{account_id}', str(account_id))
            examples_str += f"{i}. Question: {example['question']}\n   SQL: {sql_with_account}\n\n"
        
        return examples_str