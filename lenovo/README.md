# Agent Ops (Self-host VM + PR-only)

This service is the minimum operational core for an AI software agent that can:
- accept a spec/prompt as a "run"
- enqueue work
- execute via a runner (mock runner for tests; OpenHands runner for real agents)
- persist audit results

OpenHands SDK is an OSS foundation explicitly built to run software agents with tools + workspaces.  
Docs: installation + concepts + examples are here. (See OpenHands SDK getting started.)  

## Why "PR-only" is the right default
The agent should never push to production directly. It should:
1) create a branch + commit changes
2) open a PR
3) CI deploys only after merge

This repo is the "control plane" for those actions.

## Local dev (Docker)
1. Copy `.env.example` to `.env`
