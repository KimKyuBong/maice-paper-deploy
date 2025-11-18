# Abstract (English)

## Design and Development of an AI Agent Supporting Question Clarification in Mathematics Learning: Focusing on Mathematical Induction for High School Grade 2

By Kim Kyu-bong  
Major in AI Convergence Education  
Graduate School of Education, Pusan National University  
Supervised by Professor [Name]

---

## Abstract

Despite the widespread adoption of generative AI in education, poor question quality hinders effective learning. A pilot study (n=385) found that 72.3% of student questions lacked learning context, and current immediate-answer approaches (termed "Freepass" mode) fail to support students' thinking processes. Question quality strongly correlated with answer quality (r=0.691, p<0.001), indicating that question clarification is a key mechanism for improving learning outcomes.

This study designed and developed MAICE (Mathematical AI Chatbot for Education), a multi-agent system based on Dewey's reflective thinking theory (1910) and Bloom's knowledge taxonomy (Anderson & Krathwohl, 2001). MAICE employs five independent AI agents (QuestionClassifier, QuestionImprover, AnswerGenerator, LearningObserver, FreeTalker) that collaborate to classify questions into Bloom's K1-K4 types (factual-conceptual-procedural-metacognitive knowledge), systematically clarify unclear questions following Dewey's five-stage reflective thinking process, and provide differentiated answers tailored to question types.

**Methods**: Fifty-eight grade 2 high school students were randomly assigned to Agent mode (clarification-included, n=28) or Freepass mode (immediate-answer only, n=30) in a three-week A/B test (October 20-November 8, 2024; 284 valid sessions). To mutually complement methodological limitations, we employed dual evaluation: LLM evaluation (N=284) for large-scale pattern detection and teacher evaluation (N=100) for educational validity verification. A QAC (Question-Answer-Context) checklist with 8 items (40 points) was evaluated by three independent AI models (Gemini-2.5-Flash, Claude-4.5-Haiku, GPT-5-mini) and two external mathematics teachers. Inter-rater reliability: LLM Cronbach's α=0.872, teachers ICC=0.716, LLM-teacher r=0.754 (p<0.001).

**Results**: Through LLM-teacher dual evaluation and qualitative analysis (1,589 dialogue logs), clarification effects were confirmed. (1) **LLM evaluation (N=284, 3-model average)**: Agent mode showed significant superiority in C2 (learning support) (+0.28 points, **p=0.004**, d=0.353) with very large effects for lower-achievers (Q1 C2: **p<0.001**, d=0.855). (2) **Teacher evaluation (N=100)**: Agent mode showed the same directional pattern with significant differences in the answer domain (+1.28 points, **p=0.017**, d=0.488) and very large effects for Q1 (overall: +6.32 points, **p=0.013**, d=0.992). High LLM-teacher correlation (r=0.754) confirmed complementary evaluation is viable. (3) **Qualitative analysis (1,589 dialogue logs)**: Six high-scoring sessions (32-34 points) all included Bloom's higher knowledge dimensions (K2-K4). Session 156 (Q1 lower-achiever, 34.33 points, 1st place) showed three-stage knowledge progression (K2→K3→K4) and attempted all five Dewey stages, confirming the qualitative mechanism of lower-achiever effects. LLM evaluation scores were supported by teacher evaluation (r=0.754), Bloom/Dewey theoretical coherence, and student self-assessment convergence for educational validity. (4) **Student survey (N=47)**: High satisfaction with AI interaction quality (4.37/5.0), concept understanding (4.39/5.0), and system satisfaction (4.62/5.0). A/B preference analysis (N=44) showed 68.4% preferred clarification approach.

**Conclusions**: Question clarification processes enhance learning support, particularly showing short-term effects for lower-achieving students (Q1 C2: d=0.855). As exploratory evidence from a specific context (grade 2, mathematical induction, SW-specialized high school), this study demonstrated the feasibility of implementing Dewey's theory in AI systems. The study presented a complementary LLM-teacher dual evaluation model combining large-scale pattern detection with expert validation, and an extensible teacher-collaborative research platform. Key limitations: (1) limited to a specific context (grade 2, mathematical induction, SW-specialized high school with extensive AI experience), (2) system design limitations (insufficient learning context collection, single-turn session issues, metacognitive ability prerequisite), (3) evaluation constraints (rubric ambiguity, AI evaluation circularity, teacher sample N=2/100), and (4) response bias in student surveys. Replication studies across diverse contexts are needed.

---

**Keywords**: question clarification, AI agent, reflective thinking, mathematical induction, multi-agent system, Dewey, educational gap reduction, teacher-led research, prompting design

