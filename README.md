# Intelligent Research Topic Analysis and Agentic AI Research Assistant

## Overview

This project presents an Agentic AI Research Assistant designed to autonomously perform research based on open ended user queries. The system extends beyond traditional Natural Language Processing approaches by integrating Large Language Models with a structured, stateful workflow. It is capable of retrieving real time information from the web, synthesizing knowledge from multiple sources, and generating structured research reports.

The system is implemented using LangGraph for workflow orchestration, LangChain for LLM interaction, and Streamlit for deployment.

## Problem Statement

Traditional research workflows are manual, time consuming, and prone to bias. Classical NLP techniques such as TF IDF and LDA are limited to static datasets and lack semantic understanding and reasoning capabilities. This project addresses these limitations by building an autonomous agent capable of performing dynamic research tasks.

## Objectives

The main objectives of the project are as follows

Implement an agentic AI system capable of handling open ended research queries  
Design a multi step workflow using LangGraph  
Enable real time web search and multi source retrieval  
Generate structured research reports with proper source attribution  
Reduce hallucination through evidence grounded generation and validation  
Deploy the system using a web based interface  

## System Architecture

The system follows a graph based workflow consisting of three main nodes

Search Node retrieves relevant information from the web using search APIs  
Summary Node processes retrieved documents and generates a structured report using an LLM  
Validate Node checks the completeness of the generated report and controls retry logic  

A shared state object is passed between nodes, allowing the system to maintain memory across multiple steps.

## Key Concepts

Agentic AI  
The system behaves as an autonomous agent capable of reasoning and taking actions such as searching and validating  

Retrieval Augmented Generation  
The model generates responses based on retrieved external data instead of relying solely on internal knowledge  

State Management  
A centralized state object stores intermediate outputs such as retrieved documents and draft reports  

Validation Mechanism  
Ensures report completeness and triggers retries when necessary  

## Technology Stack

Programming Language Python  
Frontend Streamlit  
Workflow Orchestration LangGraph  
LLM Integration Groq with LLaMA models  
Search APIs DuckDuckGo or Tavily  
Libraries LangChain pandas json  

## Features

Accepts open ended research queries  
Performs live web search and document retrieval  
Generates structured reports including title abstract key findings sources and conclusion  
Implements retry logic for incomplete outputs  
Provides source grounded responses to reduce hallucination  

## Project Structure

agentai research  
app.py main Streamlit application  
graph state.py defines state schema  
graph nodes.py contains search summary and validation logic  
graph workflow.py defines LangGraph workflow  
utils search.py handles web search  
utils parser.py parses structured output  
utils display.py manages UI rendering  
requirements.txt dependencies  
README.md project documentation  

## Results

The system demonstrates improved research capabilities compared to classical NLP approaches. It is able to generate coherent and structured reports using real time data. The retry mechanism improves output completeness, and source attribution enhances reliability.

## Limitations

The system depends on free tier APIs which impose rate limits  
Web scraping may fail for restricted websites  
Latency is higher due to multi step processing  
State is not persistent and is limited to a single session  
Scalability for multiple users is not implemented  

## Future Work

Introduce multi agent collaboration for improved reasoning  
Implement source credibility scoring  
Add persistent memory using databases or vector stores  
Enable follow up queries with conversational context  
Support PDF export of generated reports  

## Conclusion

This project demonstrates the transition from traditional NLP systems to agentic AI architectures. By combining LLMs with structured workflows and real time data retrieval, the system achieves a higher level of intelligence, reliability, and usability in research tasks.
