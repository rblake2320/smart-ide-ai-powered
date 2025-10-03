import os
import json
import re
from flask import Blueprint, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ai_bp = Blueprint("ai", __name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@ai_bp.route("/analyze-code", methods=["POST"])
def analyze_code():
    """Analyze code for security issues, optimizations, and testing suggestions"""
    try:
        data = request.get_json()
        code = data.get("code", "")
        language = data.get("language", "javascript")

        if not code:
            return jsonify({"error": "No code provided"}), 400

        # Create a comprehensive prompt for code analysis
        prompt = f"""
        Analyze the following {language} code and provide suggestions in three categories:
        
        1. SECURITY: Identify potential security vulnerabilities (SQL injection, XSS, etc.)
        2. OPTIMIZATION: Suggest performance improvements and better algorithms
        3. TESTING: Recommend test cases and edge cases to consider
        
        For each suggestion, provide:
        - Type (security/optimization/testing)
        - Line number (estimate based on code structure)
        - Severity (high/medium/low)
        - Description of the issue
        - Specific recommendation for improvement
        
        Code to analyze:
        ```{language}
        {code}
        ```
        
        Respond in JSON format with an array of suggestions:
        {{
            "suggestions": [
                {{
                    "type": "security",
                    "line": 9,
                    "severity": "high",
                    "message": "SQL injection vulnerability detected",
                    "recommendation": "Use parameterized queries instead of string concatenation"
                }}
            ]
        }}
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert code analyzer specializing in security, performance, and testing. Always respond with valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=2000,
        )

        # Parse the AI response
        ai_response = response.choices[0].message.content

        # Try to extract JSON from the response
        try:
            # Look for JSON in the response
            json_match = re.search(r"\{.*\}", ai_response, re.DOTALL)
            if json_match:
                suggestions_data = json.loads(json_match.group())
                return jsonify(suggestions_data)
            else:
                # Fallback: create structured response from text
                return jsonify(
                    {
                        "suggestions": [
                            {
                                "type": "analysis",
                                "line": 1,
                                "severity": "info",
                                "message": "AI analysis completed",
                                "recommendation": ai_response[:200] + "...",
                            }
                        ]
                    }
                )
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw response
            return jsonify(
                {
                    "suggestions": [
                        {
                            "type": "analysis",
                            "line": 1,
                            "severity": "info",
                            "message": "AI analysis completed",
                            "recommendation": ai_response[:200] + "...",
                        }
                    ]
                }
            )

    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


@ai_bp.route("/generate-tests", methods=["POST"])
def generate_tests():
    """Generate test cases for the provided code"""
    try:
        data = request.get_json()
        code = data.get("code", "")
        language = data.get("language", "javascript")

        if not code:
            return jsonify({"error": "No code provided"}), 400

        prompt = f"""
        Generate comprehensive test cases for the following {language} code.
        
        Create tests that cover:
        1. Normal functionality
        2. Edge cases
        3. Error conditions
        4. Boundary values
        5. Invalid inputs
        
        Code to test:
        ```{language}
        {code}
        ```
        
        Respond with JSON containing test cases:
        {{
            "tests": [
                {{
                    "name": "Test function with valid input",
                    "description": "Tests normal functionality",
                    "code": "// Test code here",
                    "expected": "expected result",
                    "category": "unit"
                }}
            ]
        }}
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert test engineer. Generate comprehensive test cases and respond with valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=2000,
        )

        ai_response = response.choices[0].message.content

        # Try to extract JSON from the response
        try:
            json_match = re.search(r"\{.*\}", ai_response, re.DOTALL)
            if json_match:
                tests_data = json.loads(json_match.group())
                return jsonify(tests_data)
            else:
                return jsonify(
                    {
                        "tests": [
                            {
                                "name": "AI Generated Test",
                                "description": "Test case generated by AI",
                                "code": ai_response[:300] + "...",
                                "expected": "See test code",
                                "category": "unit",
                            }
                        ]
                    }
                )
        except json.JSONDecodeError:
            return jsonify(
                {
                    "tests": [
                        {
                            "name": "AI Generated Test",
                            "description": "Test case generated by AI",
                            "code": ai_response[:300] + "...",
                            "expected": "See test code",
                            "category": "unit",
                        }
                    ]
                }
            )

    except Exception as e:
        return jsonify({"error": f"Test generation failed: {str(e)}"}), 500


@ai_bp.route("/security-scan", methods=["POST"])
def security_scan():
    """Perform detailed security analysis of code"""
    try:
        data = request.get_json()
        code = data.get("code", "")
        language = data.get("language", "javascript")

        if not code:
            return jsonify({"error": "No code provided"}), 400

        prompt = f"""
        Perform a comprehensive security analysis of this {language} code.
        
        Look for:
        1. SQL Injection vulnerabilities
        2. Cross-Site Scripting (XSS) issues
        3. Authentication/Authorization flaws
        4. Input validation problems
        5. Cryptographic issues
        6. Information disclosure
        7. OWASP Top 10 vulnerabilities
        
        Code to analyze:
        ```{language}
        {code}
        ```
        
        Respond with JSON:
        {{
            "security_score": 85,
            "issues": [
                {{
                    "type": "SQL Injection",
                    "severity": "high",
                    "line": 9,
                    "description": "Direct string concatenation in SQL query",
                    "suggestion": "Use parameterized queries",
                    "cwe": "CWE-89"
                }}
            ],
            "recommendations": [
                "Implement input validation",
                "Use prepared statements"
            ]
        }}
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a cybersecurity expert specializing in code security analysis. Always respond with valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=2000,
        )

        ai_response = response.choices[0].message.content

        # Try to extract JSON from the response
        try:
            json_match = re.search(r"\{.*\}", ai_response, re.DOTALL)
            if json_match:
                security_data = json.loads(json_match.group())
                return jsonify(security_data)
            else:
                return jsonify(
                    {
                        "security_score": 75,
                        "issues": [
                            {
                                "type": "Security Analysis",
                                "severity": "info",
                                "line": 1,
                                "description": "AI security analysis completed",
                                "suggestion": ai_response[:200] + "...",
                                "cwe": "N/A",
                            }
                        ],
                        "recommendations": ["Review AI analysis results"],
                    }
                )
        except json.JSONDecodeError:
            return jsonify(
                {
                    "security_score": 75,
                    "issues": [
                        {
                            "type": "Security Analysis",
                            "severity": "info",
                            "line": 1,
                            "description": "AI security analysis completed",
                            "suggestion": ai_response[:200] + "...",
                            "cwe": "N/A",
                        }
                    ],
                    "recommendations": ["Review AI analysis results"],
                }
            )

    except Exception as e:
        return jsonify({"error": f"Security scan failed: {str(e)}"}), 500


@ai_bp.route("/chat", methods=["POST"])
def ai_chat():
    """AI chat assistant for coding help"""
    try:
        data = request.get_json()
        message = data.get("message", "")
        code_context = data.get("code_context", "")

        if not message:
            return jsonify({"error": "No message provided"}), 400

        # Build context-aware prompt
        context_prompt = ""
        if code_context:
            context_prompt = f"\n\nCurrent code context:\n```\n{code_context}\n```"

        prompt = f"""
        You are an AI coding assistant integrated into a Smart IDE. Help the developer with their question.
        
        User question: {message}{context_prompt}
        
        Provide helpful, concise, and actionable advice. If relevant to the code context, reference specific lines or functions.
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI coding assistant. Provide clear, concise, and actionable advice.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1000,
        )

        ai_response = response.choices[0].message.content

        return jsonify({"response": ai_response, "timestamp": "now"})

    except Exception as e:
        return jsonify({"error": f"Chat failed: {str(e)}"}), 500


@ai_bp.route("/optimize-code", methods=["POST"])
def optimize_code():
    """Generate optimized version of the provided code"""
    try:
        data = request.get_json()
        code = data.get("code", "")
        language = data.get("language", "javascript")

        if not code:
            return jsonify({"error": "No code provided"}), 400

        prompt = f"""
        Optimize the following {language} code for better performance, readability, and maintainability.
        
        Original code:
        ```{language}
        {code}
        ```
        
        Provide:
        1. Optimized version of the code
        2. Explanation of improvements made
        3. Performance benefits
        
        Respond in JSON format:
        {{
            "optimized_code": "// optimized code here",
            "improvements": [
                "Added memoization for better performance",
                "Improved error handling"
            ],
            "performance_gain": "Estimated 80% performance improvement"
        }}
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert software engineer specializing in code optimization. Always respond with valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=2000,
        )

        ai_response = response.choices[0].message.content

        # Try to extract JSON from the response
        try:
            json_match = re.search(r"\{.*\}", ai_response, re.DOTALL)
            if json_match:
                optimization_data = json.loads(json_match.group())
                return jsonify(optimization_data)
            else:
                return jsonify(
                    {
                        "optimized_code": ai_response,
                        "improvements": ["AI optimization analysis completed"],
                        "performance_gain": "See optimized code",
                    }
                )
        except json.JSONDecodeError:
            return jsonify(
                {
                    "optimized_code": ai_response,
                    "improvements": ["AI optimization analysis completed"],
                    "performance_gain": "See optimized code",
                }
            )

    except Exception as e:
        return jsonify({"error": f"Code optimization failed: {str(e)}"}), 500
