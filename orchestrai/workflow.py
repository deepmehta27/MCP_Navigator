from __future__ import annotations

from crewai import Task, Crew, Process
from pydantic import ValidationError

from orchestrai.schemas import ResearchPacket, TaskPlan, ExecutionResult
from orchestrai.agents import build_research_agent, build_planner_agent, build_executor_agent
from orchestrai.tool_runner import ToolRunner
from orchestrai.mcp_tools import get_tool_names

from eval.judge import judge_run


def _parse(model_cls, text: str):
    return model_cls.model_validate_json(text)


async def run_orchestration(user_goal: str, tools) -> ExecutionResult:
    # ----------------------------
    # 0. SETUP
    # ----------------------------
    research_agent = build_research_agent(tools)
    planner_agent = build_planner_agent(tools)
    executor_agent = build_executor_agent(tools)
    runner = ToolRunner(tools)
    
    print("Available MCP tools:", runner.list_tools())
    
    allowed_tools = ", ".join(get_tool_names(tools))

    # ----------------------------
    # 1. CREATE PLAN
    # ----------------------------
    plan_task = Task(
        description=(
            "You are the Task Planner.\n\n"
            "Create a task plan for the following goal.\n\n"
            "CRITICAL RULES (VIOLATION = FAILURE):\n"
            "1. Return ONLY valid JSON\n"
            "2. JSON MUST match this schema exactly:\n"
            f"{TaskPlan.model_json_schema()}\n\n"
            "3. You may ONLY use tool names from this list:\n"
            f"{allowed_tools}\n\n"
            "DO NOT invent tools.\n"
            "DO NOT use generic terms like 'browser', 'internet', or 'API'.\n"
            "If no tool is needed for a step, omit the tools field.\n\n"
            f"Goal: {user_goal}"
        ),
        expected_output="Valid JSON matching TaskPlan schema",
        agent=planner_agent,
    )

    planner_crew = Crew(
        agents=[planner_agent],
        tasks=[plan_task],
        process=Process.sequential,
        verbose=True,
    )

    raw_plan = planner_crew.kickoff()
    if not isinstance(raw_plan, str):
        raw_plan = str(raw_plan)

    # ----------------------------
    # SANITIZE PLANNER OUTPUT
    # ----------------------------
    raw_plan = raw_plan.strip()

    if raw_plan.startswith("```"):
        # remove ```json ... ``` fences
        raw_plan = raw_plan.strip("`").strip()
        if raw_plan.lower().startswith("json"):
            raw_plan = raw_plan[4:].strip()

    # ----------------------------
    # 2. VALIDATE PLAN (HARD GATE)
    # ----------------------------
    try:
        task_plan = TaskPlan.model_validate_json(raw_plan)
    except ValidationError as e:
        raise RuntimeError(
            f"Planner produced invalid TaskPlan.\n\n"
            f"Validation error:\n{e}\n\n"
            f"Raw output:\n{raw_plan}"
        )
        
    # Validate tool names against allowed tools
    allowed = set(get_tool_names(tools))
    print(f"\n✅ Allowed tools: {sorted(allowed)}")
    
    for step in task_plan.steps:
        for tool in step.tools or []:
            if tool not in allowed:
                raise RuntimeError(
                    f"\n❌ VALIDATION FAILED: Planner used invalid tool '{tool}' in step {step.step_id}.\n"
                    f"Allowed tools: {sorted(allowed)}\n\n"
                    f"Full plan:\n{task_plan.model_dump_json(indent=2)}"
                )
    
    print(f"✅ Plan validated: {len(task_plan.steps)} steps, all tools valid\n")

    # ----------------------------
    # 3. OPTIONAL RESEARCH STEP
    # ----------------------------
    research_task = Task(
        description=(
            "Research the goal using tools if needed and return JSON matching:\n"
            f"{ResearchPacket.model_json_schema()}\n\n"
            f"Goal: {user_goal}\n"
        ),
        expected_output="Valid JSON for ResearchPacket",
        agent=research_agent,
    )

    research_crew = Crew(
        agents=[research_agent],
        tasks=[research_task],
        process=Process.sequential,
        verbose=True,
    )

    research_output = research_crew.kickoff()
    if not isinstance(research_output, str):
        research_output = str(research_output)

    # ----------------------------
    # 4. EXPLICIT MCP TOOL EXECUTION (WEATHER INTENT)
    # ----------------------------
    weather_result = None
    if "weather" in user_goal.lower():
        try:
            # Smart city extraction - handles multiple patterns
            import re
            
            # Remove common filler words
            goal_clean = user_goal.lower()
            
            # Try pattern 1: "weather in CITY"
            match = re.search(r'\b(?:in|for)\s+([a-z\s]+?)(?:\s|$|,)', goal_clean)
            if match:
                city = match.group(1).strip()
            else:
                # Try pattern 2: "CITY weather"
                match = re.search(r'\b([a-z]+)\s+weather', goal_clean)
                if match:
                    city = match.group(1).strip()
                else:
                    # Try pattern 3: Last capitalized word (fallback)
                    words = user_goal.split()
                    city_candidates = [w for w in words if w and w[0].isupper() and len(w) > 2]
                    city = city_candidates[-1].lower() if city_candidates else "New York"
            
            # Clean up city name
            city = city.title()  # Capitalize properly
            
            # Call weather MCP tool directly
            print(f"\nCalling Weather MCP for {city}...")
            weather_result = await runner.call("get_weather", {"city": city})
            print(f"✅ Weather result: {weather_result}\n")
            
        except Exception as e:
            print(f" Weather tool failed: {e}\n")
            weather_result = None

    # ----------------------------
    # 5. RUN EXECUTOR (WITH TOOL RESULTS)
    # ----------------------------
    exec_description = (
        "You are the Action Executor.\n\n"
        "You MUST execute the following plan exactly.\n\n"
        f"Task Plan:\n{task_plan.model_dump_json(indent=2)}\n\n"
    )
    
    # Inject weather results if available
    if weather_result:
        exec_description += f"\nWeather data available:\n{weather_result}\n\n"
    
    exec_description += (
        "Rules:\n"
        "- Execute steps in order\n"
        "- Use only the tools listed per step\n"
        "- Use the provided weather data if applicable\n"
        "- If a step fails, report it clearly\n\n"
        f"Original user goal: {user_goal}"
    )
    
    exec_task = Task(
        description=exec_description,
        expected_output="Final answer for the user",
        agent=executor_agent,
    )

    executor_crew = Crew(
        agents=[executor_agent],
        tasks=[exec_task],
        process=Process.sequential,
        verbose=False,
    )

    # Execute with error handling
    try:
        raw_exec = executor_crew.kickoff()
        if not isinstance(raw_exec, str):
            raw_exec = str(raw_exec)
        execution_succeeded = True
        execution_errors = []
        
    except Exception as e:
        raw_exec = f"Execution failed: {str(e)}"
        execution_succeeded = False
        execution_errors = [str(e)]

    # ----------------------------
    # 6. EVALUATE WITH JUDGE
    # ----------------------------
    judge = judge_run(
        goal=user_goal,
        plan=task_plan.model_dump(),
        final_answer=raw_exec,
        trace=None,
    )

    print(f"\n📊 Judge scores: Success={judge.success}/5, Plan={judge.plan_quality}/5, Reasoning={judge.reasoning_quality}/5")
    print(f"Notes: {judge.notes}\n")

    # ----------------------------
    # 7. RETURN STRUCTURED RESULT
    # ----------------------------
    return ExecutionResult(
        goal=user_goal,
        completed=execution_succeeded,
        outputs={
            "plan": task_plan.model_dump(),
            "research": research_output,
            "judge": judge.model_dump(),
            "weather": weather_result if weather_result else None,
        },
        errors=execution_errors,
        final_answer=raw_exec,
    )
