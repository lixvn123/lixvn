"""Safe SQLite-backed database interface for verified analytical tool queries."""

import re
import sqlite3
from typing import Any, Dict, List, Optional
from lixvn.errors import DatabaseQueryError


class SafeDatabase:
    """Provides a sandboxed, read-only analytical database interface backed by in-memory SQLite."""

    _UNSAFE_KEYWORDS = {
        "DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "TRUNCATE",
        "REPLACE", "CREATE", "GRANT", "REVOKE", "ATTACH", "DETACH",
    }

    def __init__(self, in_memory: bool = True) -> None:
        self.conn = sqlite3.connect(":memory:" if in_memory else ":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._initialize_seed_data()

    def _initialize_seed_data(self) -> None:
        """Sets up verified read schemas and realistic seed records for query demonstrations."""
        cursor = self.conn.cursor()
        
        # Customer churn analytical table
        cursor.execute("""
            CREATE TABLE customer_churn (
                customer_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                tenure_months INTEGER NOT NULL,
                plan_type TEXT NOT NULL,
                churn_risk_pct REAL NOT NULL,
                monthly_spend REAL NOT NULL,
                status TEXT NOT NULL
            )
        """)
        cursor.executemany("""
            INSERT INTO customer_churn VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            (101, "Acme Corp", 14, "Enterprise", 78.5, 4200.0, "at_risk"),
            (102, "Beta Retail", 36, "Pro", 12.0, 850.0, "active"),
            (103, "Gamma Tech", 8, "Pro", 84.0, 1100.0, "at_risk"),
            (104, "Delta Logistics", 48, "Enterprise", 5.2, 5600.0, "active"),
            (105, "Epsilon Media", 19, "Starter", 62.1, 350.0, "at_risk"),
            (106, "Zeta Financial", 24, "Enterprise", 18.4, 9100.0, "active"),
        ])

        # Server metrics telemetry table
        cursor.execute("""
            CREATE TABLE server_metrics (
                server_id TEXT PRIMARY KEY,
                region TEXT NOT NULL,
                cpu_pct REAL NOT NULL,
                memory_pct REAL NOT NULL,
                latency_ms INTEGER NOT NULL,
                status TEXT NOT NULL
            )
        """)
        cursor.executemany("""
            INSERT INTO server_metrics VALUES (?, ?, ?, ?, ?, ?)
        """, [
            ("srv-us-east-1", "us-east-1", 24.2, 48.1, 12, "healthy"),
            ("srv-us-west-2", "us-west-2", 31.0, 52.4, 18, "healthy"),
            ("srv-eu-west-1", "eu-west-1", 22.8, 44.0, 15, "healthy"),
            ("srv-ap-southeast-1", "ap-southeast-1", 89.4, 76.2, 110, "degraded"),
        ])

        # Security audit log table
        cursor.execute("""
            CREATE TABLE security_audit_log (
                log_id INTEGER PRIMARY KEY,
                action TEXT NOT NULL,
                actor TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)
        cursor.executemany("""
            INSERT INTO security_audit_log VALUES (?, ?, ?, ?, ?)
        """, [
            (1, "AUTH_LOGIN", "admin@lixvn.dev", "192.168.1.1", "SUCCESS"),
            (2, "SQL_QUERY", "analyst@lixvn.dev", "10.0.0.5", "VERIFIED"),
            (3, "ROLE_UPDATE", "security@lixvn.dev", "10.0.0.2", "APPROVED"),
        ])

        self.conn.commit()

    @staticmethod
    def _split_statements(sql: str) -> List[str]:
        """Splits SQL string into statements by semicolon, ignoring semicolons within quotes."""
        statements: List[str] = []
        current: List[str] = []
        in_single_quote = False
        in_double_quote = False
        i = 0
        n = len(sql)
        while i < n:
            ch = sql[i]
            if ch == "'" and not in_double_quote:
                if in_single_quote and i + 1 < n and sql[i + 1] == "'":
                    current.append("''")
                    i += 2
                    continue
                in_single_quote = not in_single_quote
                current.append(ch)
            elif ch == '"' and not in_single_quote:
                if in_double_quote and i + 1 < n and sql[i + 1] == '"':
                    current.append('""')
                    i += 2
                    continue
                in_double_quote = not in_double_quote
                current.append(ch)
            elif ch == ';' and not in_single_quote and not in_double_quote:
                stmt_str = "".join(current).strip()
                if stmt_str:
                    statements.append(stmt_str)
                current = []
            else:
                current.append(ch)
            i += 1
        remainder = "".join(current).strip()
        if remainder:
            statements.append(remainder)
        return statements

    def is_safe_query(self, query: Any) -> tuple[bool, Optional[str]]:
        """Validates that a SQL query is strictly a read operation without destructive side effects."""
        if not isinstance(query, str) or not query.strip():
            return False, "Query must be a non-empty string."

        cleaned = re.sub(r"--.*?$|/\*.*?\*/", "", query, flags=re.MULTILINE | re.DOTALL).strip()
        if not cleaned:
            return False, "Query is empty."

        # Parse statements respecting quotes
        statements = self._split_statements(cleaned)
        if not statements:
            return False, "Query is empty."
        if len(statements) > 1:
            return False, "Multiple SQL statements are not permitted in safe execution mode."

        stmt = statements[0]
        # Strip string literals before analyzing command and keywords
        stmt_no_literals = re.sub(r"'(?:''|[^'])*'|\"(?:\"\"|[^\"])*\"", "''", stmt)
        tokens = re.findall(r"\b[A-Za-z_]+\b", stmt_no_literals.upper())
        if not tokens:
            return False, "No valid SQL commands found."

        first_token = tokens[0]
        if first_token not in {"SELECT", "WITH", "EXPLAIN", "PRAGMA"}:
            return False, f"Statement '{first_token}' is not an authorized read operation."

        if first_token == "PRAGMA":
            allowed_pragmas = {"TABLE_INFO", "DATABASE_LIST", "TABLE_XINFO", "INDEX_LIST", "INDEX_INFO"}
            if len(tokens) < 2 or tokens[1] not in allowed_pragmas or "=" in stmt_no_literals:
                return False, "Dangerous or unauthorized PRAGMA statement is prohibited."

        # Scan for forbidden modification keywords
        found_unsafe = set(tokens).intersection(self._UNSAFE_KEYWORDS)
        if found_unsafe:
            return False, f"Prohibited modification keyword(s) detected: {', '.join(sorted(found_unsafe))}."

        return True, None

    def safe_execute(self, query: Any, raise_on_error: bool = False) -> Dict[str, Any]:
        """Executes verified read queries against the in-memory data warehouse."""
        is_safe, reason = self.is_safe_query(query)
        if not is_safe:
            error_msg = f"Unsafe query: {reason}"
            if raise_on_error:
                raise DatabaseQueryError(str(query), reason or "Unsafe query")
            return {"status": "error", "error": error_msg}

        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            col_names = [d[0] for d in cursor.description] if cursor.description else []
            rows: List[Dict[str, Any]] = [dict(zip(col_names, row)) for row in cursor.fetchall()]
            return {
                "status": "ok",
                "rows": rows,
                "row_count": len(rows),
                "columns": col_names,
            }
        except sqlite3.Error as e:
            error_msg = f"SQL execution error: {str(e)}"
            if raise_on_error:
                raise DatabaseQueryError(str(query), error_msg)
            return {"status": "error", "error": error_msg}

    def close(self) -> None:
        """Closes the underlying database connection."""
        self.conn.close()
