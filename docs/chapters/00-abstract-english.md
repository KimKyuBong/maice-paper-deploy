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

**Methods**: Fifty-eight grade 2 high school students were randomly assigned to Agent mode (clarification-included, n=28) or Freepass mode (immediate-answer only, n=30) in a three-week A/B test (October 20-November 8, 2024; 284 valid sessions). To mutually complement methodological limitations, we employed dual evaluation: LLM evaluation (N=284) for large-scale pattern detection and teacher preliminary evaluation (N=100) for educational validity verification. A QAC (Question-Answer-Context) checklist with 8 items (40 points) was evaluated by three independent AI models (Gemini-2.5-Flash, Claude-4.5-Haiku, GPT-5-mini) and two external mathematics teachers. Inter-rater reliability: LLM Cronbach's α=0.868, teachers r=0.644, LLM-teacher r=0.743 (p<0.001).

**Results**: Through LLM-teacher dual evaluation, clarification effects were mutually verified. (1) **LLM evaluation (N=284, 3-model average)**: Agent mode showed significant superiority in C2 (learning support) (Agent 2.31 vs Freepass 2.02, +0.30 points, **p=0.002**, d=0.376) with very large effects for lower-achievers (Q1 C2: +0.49, **p=0.001**, d=0.840; Q1 overall: +2.46, p=0.033, d=0.511). (2) **Teacher preliminary evaluation (N=100)**: Agent mode was significantly higher in overall score (+2.25 points, **p=0.031**, d=0.307) with very large effects for Q1 (+6.91 points, **p=0.009**, d=1.117). High LLM-teacher correlation (r=0.743) confirmed directional consistency. However, teacher evaluation is preliminary (2 evaluators, 100 samples); replication with 10+ evaluators and 300+ samples is needed. (3) **Student self-assessment convergence (N=40)**: 20-item survey showed high scores in AI interaction quality (4.38/5.0), concept understanding (4.36/5.0), and questioning ability (4.13/5.0), with 68.6% preferring question-guided approach (reasons: "improves thinking" 42%, "deeper understanding" 25%). Objective evaluations (LLM·teacher) converged with subjective perceptions (student survey).

**Conclusions**: Question clarification processes enhance learning support, particularly for lower-achieving students (LLM d=0.840, teacher d=1.117). Four independent evidence sources (LLM objective evaluation, teacher expert evaluation, learner self-assessment, qualitative evidence) converged to strengthen validity. This study: (1) validated Dewey's "problem clarification" stage as an effective method through A/B testing (LLM p=0.002, teacher p=0.031), (2) demonstrated practical effects in supporting lower-achieving students by shifting AI educational tool design from immediate-answer centered to question-clarification centered, and (3) presented an LLM-teacher dual evaluation model combining large-scale objective assessment with expert validity verification, along with an extensible research platform enabling teacher-led prompting design. However, participants from a software development-specialized high school with extensive AI experience may limit generalization to students with less AI familiarity.

---

**Keywords**: question clarification, AI agent, reflective thinking, mathematical induction, multi-agent system, Dewey, educational gap reduction, teacher-led research, prompting design

