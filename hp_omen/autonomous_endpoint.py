"""
Autonomous Agent API Endpoint
Adds autonomous workflow capability to HP OMEN orchestrator
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import asyncio
import sys
import os

# Add shared directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from autonomous import execute_autonomous_workflow

router = APIRouter()


class AutonomousRequest(BaseModel):
    website_url: str
    auto_pr: bool = True


class AutonomousResponse(BaseModel):
    status: str
    message: str
    analysis_summary: dict
    tasks_generated: int
    tasks_completed: int
    tasks_failed: int
    prs_created: int
    report_file: str


@router.post("/v1/autonomous/analyze-and-fix", response_model=AutonomousResponse)
async def autonomous_analyze_and_fix(request: AutonomousRequest):
    """
    Autonomous workflow: Analyze website, generate tasks, execute them
    
    This endpoint triggers the complete autonomous agent workflow:
    1. Analyzes the website structure and content
    2. Compares against coaching industry standards
    3. Generates prioritized list of tasks
    4. Executes tasks autonomously
    5. Creates GitHub PRs for each completed task
    
    Args:
        request: AutonomousRequest with website_url and auto_pr flag
        
    Returns:
        AutonomousResponse with execution summary
    """
    try:
        print(f"\n🤖 Starting autonomous workflow for: {request.website_url}")
        
        # Execute autonomous workflow
        results = await execute_autonomous_workflow(
            website_url=request.website_url,
            auto_pr=request.auto_pr
        )
        
        # Extract summary
        analysis = results['analysis']
        tasks = results['tasks']
        execution = results['execution']
        
        # Build response
        response = AutonomousResponse(
            status="success",
            message=f"Autonomous workflow completed: {execution['completed']} tasks completed, {execution['prs_created']} PRs created",
            analysis_summary={
                "pages_found": analysis['pages_found'],
                "structure": analysis['structure'],
                "broken_links": len(analysis['broken_links']),
                "performance": analysis['performance']
            },
            tasks_generated=len(tasks),
            tasks_completed=execution['completed'],
            tasks_failed=execution['failed'],
            prs_created=execution['prs_created'],
            report_file=f"autonomous_report_{execution['start_time'].replace(':', '').replace('-', '')}.json"
        )
        
        print(f"✅ Autonomous workflow complete!")
        print(f"   Tasks completed: {execution['completed']}/{len(tasks)}")
        print(f"   PRs created: {execution['prs_created']}")
        
        return response
        
    except Exception as e:
        print(f"❌ Error in autonomous workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/v1/autonomous/analyze-only")
async def autonomous_analyze_only(request: AutonomousRequest):
    """
    Analyze website and generate task list (no execution)
    
    Args:
        request: AutonomousRequest with website_url
        
    Returns:
        Analysis and task list
    """
    try:
        from autonomous import analyze_website, TaskGenerator
        
        print(f"\n🔍 Analyzing website: {request.website_url}")
        
        # Analyze website
        analysis = await analyze_website(request.website_url)
        
        # Generate tasks
        generator = TaskGenerator()
        tasks = generator.generate_tasks(analysis)
        
        return {
            "status": "success",
            "analysis": {
                "url": analysis['url'],
                "pages_found": analysis['pages_found'],
                "structure": analysis['structure'],
                "features": analysis['features'],
                "broken_links": len(analysis['broken_links']),
                "performance": analysis['performance']
            },
            "tasks": [
                {
                    "id": t['id'],
                    "type": t['type'],
                    "priority": t['priority'],
                    "title": t['title'],
                    "description": t['description'],
                    "estimated_time": t.get('estimated_time', 'N/A')
                }
                for t in tasks
            ],
            "summary": generator.generate_task_summary(tasks)
        }
        
    except Exception as e:
        print(f"❌ Error in analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/v1/autonomous/status")
async def get_autonomous_status():
    """
    Get status of autonomous agent system
    
    Returns:
        System status
    """
    return {
        "status": "operational",
        "version": "1.0.0-mvp",
        "capabilities": [
            "website_analysis",
            "task_generation",
            "autonomous_execution",
            "github_pr_creation"
        ],
        "supported_industries": [
            "coaching",
            "consulting",
            "professional_services"
        ]
    }
