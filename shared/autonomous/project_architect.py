"""
Project Architect - Enterprise-Level Project Understanding and Decomposition

Handles 6+ layer deep analysis, multi-modal requirements, complex interactions,
and foundational imperatives for complete platform development.
"""
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from .llm_retry import retry_with_exponential_backoff

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProjectArchitect:
    """
    Strategic layer above task executor - decomposes complex projects into
    architectural layers with proper sequencing and dependency management.
    """
    
    def __init__(
        self,
        llm_api_key: Optional[str] = None,
        llm_model: Optional[str] = None
    ):
        self.llm_api_key = llm_api_key or os.getenv("LLM_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        self.llm_model = llm_model or os.getenv("LLM_MODEL", "claude-sonnet-4-20250514")
        
    def analyze_project(
        self,
        project_requirements: str,
        project_name: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Deep 6-layer analysis of project requirements
        
        Returns comprehensive architectural blueprint with:
        - Layer decomposition (data → logic → API → UI → integrations → infrastructure)
        - Module identification and interactions
        - Foundational imperatives (security, scalability, etc.)
        - Execution plan with sequencing
        - Risk analysis and mitigation
        """
        logger.info(f"🏗️ Starting deep architectural analysis for: {project_name}")
        
        from anthropic import Anthropic
        client = Anthropic(api_key=self.llm_api_key)
        
        analysis_prompt = f"""You are a PRINCIPAL SOFTWARE ARCHITECT with 20+ years experience designing enterprise platforms.

PROJECT NAME: {project_name}

PROJECT REQUIREMENTS:
{project_requirements}

{f"ADDITIONAL CONTEXT: {json.dumps(additional_context, indent=2)}" if additional_context else ""}

═══════════════════════════════════════════════════════════════════════════════
YOUR MISSION: COMPLETE 6-LAYER DEEP ARCHITECTURAL ANALYSIS
═══════════════════════════════════════════════════════════════════════════════

You must analyze this project at SIX LEVELS OF DEPTH:

┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: STRATEGIC UNDERSTANDING                                            │
└─────────────────────────────────────────────────────────────────────────────┘

1.1 **Business Purpose & Value**
   - What problem does this platform solve?
   - Who are the users? (personas, needs, pain points)
   - What is the core value proposition?
   - What are the business goals and success metrics?

1.2 **Product Vision**
   - What is the end-state vision?
   - What makes this platform unique?
   - What are the key differentiators?
   - What is the user experience vision?

1.3 **Scope & Boundaries**
   - What is IN scope for MVP?
   - What is OUT of scope?
   - What are the must-have vs nice-to-have features?
   - What are the constraints (time, tech, resources)?

┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 2: ARCHITECTURAL DESIGN                                               │
└─────────────────────────────────────────────────────────────────────────────┘

2.1 **System Architecture**
   - What is the overall architecture pattern? (monolith, microservices, etc.)
   - What are the major system components?
   - How do components communicate?
   - What are the data flows?

2.2 **Technology Stack**
   - Frontend: Framework, state management, UI library
   - Backend: Server framework, API design (REST/tRPC/GraphQL)
   - Database: Type (SQL/NoSQL), schema design approach
   - Infrastructure: Hosting, CDN, caching, queue
   - Integrations: Third-party services (auth, payments, storage, etc.)

2.3 **Data Architecture**
   - What are the core domain entities?
   - What are the relationships between entities?
   - What are the data access patterns?
   - What are the data consistency requirements?

┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 3: MODULE DECOMPOSITION                                               │
└─────────────────────────────────────────────────────────────────────────────┘

3.1 **Core Modules** (Identify 5-15 major modules)
   For each module:
   - Module name and purpose
   - Key features within module
   - Dependencies on other modules
   - External service dependencies
   - Complexity estimate (simple/medium/complex)

3.2 **Module Interaction Map**
   - How do modules communicate?
   - What are the interaction patterns?
   - What are the shared resources?
   - What are the integration points?

3.3 **Cross-Cutting Concerns**
   - Authentication & Authorization
   - Error handling & logging
   - Validation & sanitization
   - Caching & performance
   - Monitoring & observability

┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 4: FOUNDATIONAL IMPERATIVES                                           │
└─────────────────────────────────────────────────────────────────────────────┘

4.1 **Security Requirements**
   - Authentication strategy (OAuth, JWT, session)
   - Authorization model (RBAC, ABAC)
   - Data protection (encryption, PII handling)
   - API security (rate limiting, CORS, CSRF)
   - Compliance requirements (GDPR, HIPAA, etc.)

4.2 **Scalability & Performance**
   - Expected load (users, requests, data volume)
   - Performance targets (response time, throughput)
   - Scaling strategy (vertical, horizontal, auto-scaling)
   - Caching strategy (CDN, Redis, in-memory)
   - Database optimization (indexing, sharding, replication)

4.3 **Reliability & Maintainability**
   - Error handling strategy
   - Logging and monitoring approach
   - Testing strategy (unit, integration, e2e)
   - Deployment strategy (CI/CD, blue-green, canary)
   - Documentation requirements

4.4 **User Experience**
   - Responsive design requirements
   - Accessibility standards (WCAG)
   - Internationalization needs
   - Offline capabilities
   - Progressive enhancement

┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 5: EXECUTION STRATEGY                                                 │
└─────────────────────────────────────────────────────────────────────────────┘

5.1 **Development Phases** (Break into 3-7 phases)
   For each phase:
   - Phase name and goal
   - Deliverables (what gets built)
   - Dependencies (what must be done first)
   - Estimated complexity
   - Success criteria

5.2 **Task Sequencing**
   - What must be built first? (foundation layer)
   - What can be built in parallel?
   - What depends on what?
   - What are the critical path items?

5.3 **Risk Mitigation**
   - What are the technical risks?
   - What are the integration risks?
   - What are the dependency risks?
   - What are the mitigation strategies?

┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 6: IMPLEMENTATION BLUEPRINT                                           │
└─────────────────────────────────────────────────────────────────────────────┘

6.1 **File Structure Design**
   - Directory organization
   - Module boundaries in code
   - Shared utilities location
   - Configuration management

6.2 **Database Schema Design**
   - Core tables and relationships
   - Indexing strategy
   - Migration approach
   - Seed data requirements

6.3 **API Design**
   - Endpoint structure
   - Request/response formats
   - Error handling patterns
   - Versioning strategy

6.4 **Integration Points**
   - External service integrations
   - Webhook handlers
   - Event-driven patterns
   - Message queue usage

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT (JSON)
═══════════════════════════════════════════════════════════════════════════════

Return a comprehensive JSON object with this structure:

{{
  "project_name": "{project_name}",
  "analysis_date": "ISO timestamp",
  
  "layer_1_strategic": {{
    "business_purpose": "...",
    "target_users": [...],
    "core_value": "...",
    "success_metrics": [...],
    "product_vision": "...",
    "scope": {{
      "mvp_features": [...],
      "future_features": [...],
      "constraints": [...]
    }}
  }},
  
  "layer_2_architecture": {{
    "system_pattern": "...",
    "components": [...],
    "tech_stack": {{
      "frontend": {{}},
      "backend": {{}},
      "database": {{}},
      "infrastructure": {{}},
      "integrations": {{}}
    }},
    "data_architecture": {{
      "core_entities": [...],
      "relationships": [...],
      "access_patterns": [...]
    }}
  }},
  
  "layer_3_modules": {{
    "core_modules": [
      {{
        "name": "...",
        "purpose": "...",
        "features": [...],
        "dependencies": [...],
        "complexity": "simple|medium|complex"
      }}
    ],
    "interaction_map": {{...}},
    "cross_cutting": {{...}}
  }},
  
  "layer_4_imperatives": {{
    "security": {{...}},
    "scalability": {{...}},
    "reliability": {{...}},
    "user_experience": {{...}}
  }},
  
  "layer_5_execution": {{
    "phases": [
      {{
        "phase": 1,
        "name": "...",
        "goal": "...",
        "deliverables": [...],
        "dependencies": [...],
        "estimated_complexity": "...",
        "success_criteria": [...]
      }}
    ],
    "task_sequencing": {{
      "foundation_layer": [...],
      "parallel_tracks": [[...]],
      "critical_path": [...]
    }},
    "risks": [
      {{
        "risk": "...",
        "impact": "high|medium|low",
        "mitigation": "..."
      }}
    ]
  }},
  
  "layer_6_implementation": {{
    "file_structure": {{...}},
    "database_schema": {{...}},
    "api_design": {{...}},
    "integration_points": {{...}}
  }}
}}

═══════════════════════════════════════════════════════════════════════════════

BE COMPREHENSIVE. BE SPECIFIC. BE STRATEGIC.

This analysis will guide the entire development process. Every detail matters.
Think like you're presenting to the CTO and lead engineers - they need to understand
the COMPLETE picture at every layer.
"""

        logger.info("🤔 Analyzing project architecture (this may take 2-3 minutes)...")
        
        # Use longer timeout for complex analysis
        response = retry_with_exponential_backoff(
            lambda timeout: client.messages.create(
                model=self.llm_model,
                max_tokens=16000,  # Large response needed for comprehensive analysis
                timeout=timeout,
                messages=[{
                    "role": "user",
                    "content": analysis_prompt
                }]
            ),
            max_retries=2,  # Reduce retries since each attempt is long
            timeout_per_request=300,  # 5 minutes per request
            max_total_time=600  # 10 minutes total
        )
        
        analysis_text = response.content[0].text if response.content else ""
        logger.info(f"✅ Architectural analysis complete ({len(analysis_text)} chars)")
        
        # Parse JSON from response
        try:
            # Extract JSON from markdown code blocks if present
            if "```json" in analysis_text:
                json_start = analysis_text.find("```json") + 7
                json_end = analysis_text.find("```", json_start)
                analysis_text = analysis_text[json_start:json_end].strip()
            elif "```" in analysis_text:
                json_start = analysis_text.find("```") + 3
                json_end = analysis_text.find("```", json_start)
                analysis_text = analysis_text[json_start:json_end].strip()
            
            analysis = json.loads(analysis_text)
            
            # Add metadata
            analysis["_metadata"] = {
                "analyzed_at": datetime.now().isoformat(),
                "analyzer_version": "1.0.0",
                "llm_model": self.llm_model
            }
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            # Return raw text as fallback
            return {
                "error": "Failed to parse structured analysis",
                "raw_analysis": analysis_text,
                "_metadata": {
                    "analyzed_at": datetime.now().isoformat(),
                    "error": str(e)
                }
            }
    
    def generate_execution_plan(
        self,
        architectural_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Convert architectural analysis into detailed execution plan
        
        Returns list of tasks in proper execution order with:
        - Task ID and description
        - Dependencies
        - Required files/modules
        - Acceptance criteria
        - Estimated complexity
        """
        logger.info("📋 Generating detailed execution plan from architecture...")
        
        from anthropic import Anthropic
        client = Anthropic(api_key=self.llm_api_key)
        
        plan_prompt = f"""You are a TECHNICAL PROJECT MANAGER converting architectural design into executable tasks.

ARCHITECTURAL ANALYSIS:
{json.dumps(architectural_analysis, indent=2)}

═══════════════════════════════════════════════════════════════════════════════
YOUR MISSION: CREATE DETAILED EXECUTION PLAN
═══════════════════════════════════════════════════════════════════════════════

Convert the 6-layer architectural analysis into a SEQUENCED list of executable tasks.

REQUIREMENTS:

1. **Proper Sequencing**
   - Foundation first (data models, core utilities)
   - Then business logic
   - Then API layer
   - Then UI components
   - Then integrations
   - Finally optimizations

2. **Clear Dependencies**
   - Each task must list what it depends on
   - No circular dependencies
   - Parallel tasks clearly marked

3. **Actionable Descriptions**
   - Clear, specific task descriptions
   - Concrete acceptance criteria
   - File paths and module names
   - Expected outcomes

4. **Realistic Complexity**
   - Estimate effort (simple: 1-2h, medium: 3-6h, complex: 1-2 days)
   - Identify high-risk tasks
   - Flag tasks needing research

OUTPUT FORMAT (JSON):

{{
  "execution_plan": [
    {{
      "task_id": "T001",
      "phase": 1,
      "title": "Setup database schema foundation",
      "description": "Create core database tables using Drizzle ORM...",
      "type": "foundation|feature|integration|optimization",
      "complexity": "simple|medium|complex",
      "estimated_hours": 2,
      "dependencies": [],
      "files_to_create": ["drizzle/schema.ts", "..."],
      "files_to_modify": [],
      "acceptance_criteria": [
        "All core tables created",
        "Relationships defined",
        "Migration runs successfully"
      ],
      "risks": [],
      "notes": "..."
    }}
  ],
  "parallel_tracks": [
    ["T005", "T006", "T007"]  // These can be done simultaneously
  ],
  "critical_path": ["T001", "T002", "T010", "T015"],  // Must be done in order
  "total_estimated_hours": 120
}}

═══════════════════════════════════════════════════════════════════════════════

Create 20-50 tasks depending on project complexity.
Be specific. Be actionable. Be realistic.
"""

        logger.info("🤔 Generating execution plan...")
        
        response = retry_with_exponential_backoff(
            lambda timeout: client.messages.create(
                model=self.llm_model,
                max_tokens=16000,
                timeout=timeout,
                messages=[{
                    "role": "user",
                    "content": plan_prompt
                }]
            )
        )
        
        plan_text = response.content[0].text if response.content else ""
        logger.info(f"✅ Execution plan generated ({len(plan_text)} chars)")
        
        # Parse JSON
        try:
            if "```json" in plan_text:
                json_start = plan_text.find("```json") + 7
                json_end = plan_text.find("```", json_start)
                plan_text = plan_text[json_start:json_end].strip()
            elif "```" in plan_text:
                json_start = plan_text.find("```") + 3
                json_end = plan_text.find("```", json_start)
                plan_text = plan_text[json_start:json_end].strip()
            
            plan = json.loads(plan_text)
            return plan["execution_plan"]
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse execution plan: {e}")
            return []
    
    def save_analysis(
        self,
        analysis: Dict[str, Any],
        output_path: str
    ):
        """Save architectural analysis to file"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        logger.info(f"💾 Architectural analysis saved to: {output_path}")
    
    def load_analysis(self, analysis_path: str) -> Dict[str, Any]:
        """Load architectural analysis from file"""
        with open(analysis_path, 'r') as f:
            return json.load(f)
